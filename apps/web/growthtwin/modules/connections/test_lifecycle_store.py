"""Focused isolated database checks; no preserved Google DB/grants are used."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from threading import Barrier
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, close_old_connections, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase, TransactionTestCase, skipUnlessDBFeature

from growthtwin.modules.workspaces.models import Workspace

from .lifecycle_codec import InvalidClosureState, decode_record, encode_record
from .lifecycle_decision import (
    ClosureSnapshot,
    LocalSecret,
    RemoteStop,
    Revocation,
    Step,
)
from .lifecycle_observation import Disposition, Observation
from .lifecycle_store import (
    ClosureConflict,
    create_synthetic_closure,
    get_synthetic_closure,
    issue_synthetic_ticket,
    observe_synthetic_closure,
)
from .lifecycle_ticket import IssuanceDisposition, TicketRequest
from .models import SyntheticClosureOperation, SyntheticClosureRequest


class StoreFixture:
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="closure-owner")
        self.other = get_user_model().objects.create_user(username="closure-other")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Synthetic")
        self.other_workspace = Workspace.objects.create(owner=self.other, name="Other")
        self.args = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=uuid4(),
            generation=uuid4(),
            request_id=uuid4(),
            snapshot=ClosureSnapshot(
                barrier_confirmed=True,
                recovery_verified=True,
                in_flight=False,
                project_impact_confirmed=True,
                local_secret=LocalSecret.PRESENT,
            ),
        )
        self.record = create_synthetic_closure(**self.args)
        self.request = TicketRequest(self.record.identity, 0, uuid4(), Step.REVOKE)

    def read(self, **changes):
        args = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            request_id=self.record.identity.request_id,
        )
        return get_synthetic_closure(**(args | changes))

    def issue(self, request=None, **changes):
        args = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            request=self.request if request is None else request,
        )
        return issue_synthetic_ticket(**(args | changes))

    def observe(self, event, **changes):
        args = dict(owner=self.owner, workspace_id=self.workspace.pk, event=event)
        return observe_synthetic_closure(**(args | changes))

    def event(self, record):
        return Observation(
            record.identity,
            record.revision,
            uuid4(),
            record.pending,
            Revocation.CONFIRMED,
        )


class SyntheticClosureStoreTests(StoreFixture, TestCase):
    def test_creation_reload_and_exact_replay_do_not_reset_progress(self):
        self.assertEqual(self.read(), self.record)
        issued = self.issue().record
        replay = create_synthetic_closure(**self.args)
        self.assertEqual(replay, issued)
        self.assertEqual(SyntheticClosureRequest.objects.count(), 1)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)

    def test_safe_default_snapshot_cannot_issue_work(self):
        safe = create_synthetic_closure(
            **(
                self.args
                | {
                    "connection_id": uuid4(),
                    "request_id": uuid4(),
                    "snapshot": ClosureSnapshot(),
                }
            )
        )
        result = self.issue(replace(self.request, identity=safe.identity))
        self.assertEqual(result.reason, "closure_evidence_unverified")
        self.assertEqual(SyntheticClosureOperation.objects.count(), 0)

    def test_connection_request_or_generation_cannot_be_replaced(self):
        for changes in (
            {"request_id": uuid4()},
            {"generation": uuid4()},
            {"snapshot": replace(self.args["snapshot"], immediate_revoke=True)},
            {"connection_id": uuid4()},
        ):
            with (
                self.subTest(changes=tuple(changes)),
                self.assertRaises(ClosureConflict),
            ):
                create_synthetic_closure(**(self.args | changes))
        self.assertEqual(self.read(), self.record)

    def test_anonymous_inactive_and_wrong_owner_denied_without_writes(self):
        issued = self.issue().record
        event = self.event(issued)
        for actor in (AnonymousUser(), self.other):
            with self.subTest(actor=type(actor).__name__):
                for call in (
                    lambda: self.read(owner=actor),
                    lambda: self.issue(owner=actor),
                    lambda: self.observe(event, owner=actor),
                    lambda: create_synthetic_closure(**(self.args | {"owner": actor})),
                ):
                    with self.assertRaises((PermissionDenied, Workspace.DoesNotExist)):
                        call()
        # A stale Python user instance cannot bypass the current active flag.
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        with self.assertRaises(Workspace.DoesNotExist):
            self.read()
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=True)
        self.assertEqual(self.read(), issued)

    def test_foreign_workspace_and_request_ids_do_not_cross_tenants(self):
        with self.assertRaises(Workspace.DoesNotExist):
            self.read(workspace_id=self.other_workspace.pk)
        with self.assertRaises(SyntheticClosureRequest.DoesNotExist):
            self.read(owner=self.other, workspace_id=self.other_workspace.pk)
        with self.assertRaises(ClosureConflict):
            create_synthetic_closure(
                **(
                    self.args
                    | {
                        "owner": self.other,
                        "workspace_id": self.other_workspace.pk,
                    }
                )
            )
        self.assertEqual(self.read(), self.record)

    def test_every_typed_identity_component_is_checked(self):
        for name in ("workspace_id", "connection_id", "generation"):
            request = replace(
                self.request, identity=replace(self.request.identity, **{name: uuid4()})
            )
            self.assertEqual(self.issue(request).reason, "identity_mismatch")
        with self.assertRaises(SyntheticClosureRequest.DoesNotExist):
            self.issue(
                replace(
                    self.request,
                    identity=replace(self.request.identity, request_id=uuid4()),
                )
            )
        self.assertEqual(SyntheticClosureOperation.objects.count(), 0)

    def test_issuance_roundtrip_and_repeat_are_one_durable_operation(self):
        first = self.issue()
        self.assertEqual(first.disposition, IssuanceDisposition.ISSUED)
        self.assertEqual(self.read(), first.record)
        second = self.issue()
        self.assertEqual(second.disposition, IssuanceDisposition.DUPLICATE)
        self.assertEqual(second.record, first.record)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)
        receipt = SyntheticClosureOperation.objects.get()
        self.assertEqual(receipt.pk, self.request.operation_id)
        self.assertEqual(receipt.issued_revision, 1)

    def test_stale_revision_and_unresolved_replacement_leave_state_unchanged(self):
        issued = self.issue().record
        stale = replace(self.request, operation_id=uuid4())
        self.assertEqual(self.issue(stale).reason, "revision_mismatch")
        replacement = replace(stale, expected_revision=issued.revision)
        self.assertEqual(self.issue(replacement).reason, "operation_unresolved")
        self.assertEqual(self.read(), issued)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)

    def test_operation_id_reuse_across_requests_rolls_back_both_writes(self):
        self.issue()
        another = create_synthetic_closure(
            **(
                self.args
                | {
                    "request_id": uuid4(),
                    "connection_id": uuid4(),
                }
            )
        )
        with self.assertRaises(ClosureConflict):
            self.issue(replace(self.request, identity=another.identity))
        self.assertEqual(self.read(request_id=another.identity.request_id), another)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)

    def test_observation_and_exact_event_replay_survive_reload(self):
        issued = self.issue().record
        event = self.event(issued)
        result = self.observe(event)
        self.assertEqual(result.disposition, Disposition.APPLIED)
        self.assertEqual(self.read(), result.record)
        self.assertEqual(result.record.snapshot.revocation, Revocation.CONFIRMED)
        self.assertEqual(result.record.snapshot.remote_stop, RemoteStop.NOT_REQUESTED)
        self.assertEqual(result.record.snapshot.local_secret, LocalSecret.PRESENT)
        self.assertEqual(self.observe(event).disposition, Disposition.DUPLICATE)
        self.assertEqual(self.read().revision, 2)
        self.assertEqual(self.issue().reason, "revision_mismatch")
        retired = replace(self.request, expected_revision=2)
        self.assertEqual(self.issue(retired).reason, "operation_already_observed")

    def test_conflicting_event_or_old_observation_is_rejected(self):
        issued = self.issue().record
        event = self.event(issued)
        self.assertEqual(
            self.observe(replace(event, expected_revision=0)).reason,
            "revision_mismatch",
        )
        current = self.observe(event).record
        self.assertEqual(
            self.observe(replace(event, value=Revocation.UNVERIFIED)).reason,
            "event_identity_conflict",
        )
        self.assertEqual(self.read(), current)

    def test_failed_cas_never_creates_a_receipt_or_changes_outcome(self):
        with patch("django.db.models.query.QuerySet.update", return_value=0):
            with self.assertRaises(ClosureConflict):
                self.issue()
        self.assertEqual(self.read(), self.record)
        self.assertFalse(SyntheticClosureOperation.objects.exists())
        issued = self.issue().record
        with patch("django.db.models.query.QuerySet.update", return_value=0):
            with self.assertRaises(ClosureConflict):
                self.observe(self.event(issued))
        self.assertEqual(self.read(), issued)

    def test_receipt_failure_rolls_back_revision_and_ticket(self):
        with patch.object(
            SyntheticClosureOperation.objects, "create", side_effect=IntegrityError
        ):
            with self.assertRaises(ClosureConflict):
                self.issue()
        self.assertEqual(self.read(), self.record)
        self.assertFalse(SyntheticClosureOperation.objects.exists())

    def test_database_prevents_second_request_for_same_connection(self):
        row = SyntheticClosureRequest.objects.get()
        with self.assertRaises(IntegrityError), transaction.atomic():
            SyntheticClosureRequest.objects.create(
                pk=uuid4(),
                workspace=self.workspace,
                connection_id=row.connection_id,
                generation=uuid4(),
                initial_snapshot=row.initial_snapshot,
                state=row.state,
            )

    def test_cascade_cannot_silently_erase_the_synthetic_barrier(self):
        self.issue()
        for obj in (self.workspace, self.owner, SyntheticClosureRequest.objects.get()):
            with self.assertRaises(ProtectedError):
                obj.delete()
        self.assertEqual(SyntheticClosureRequest.objects.count(), 1)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)

    def test_unsupported_corrupt_and_extra_payloads_fail_closed(self):
        original = encode_record(self.record)
        mutations = (
            lambda state: state.update(version=2),
            lambda state: state.update(version=True),
            lambda state: state.update(revision=True),
            lambda state: state.update(extra="forbidden text"),
            lambda state: state["snapshot"].update(barrier_confirmed="yes"),
            lambda state: state["snapshot"].update(local_secret="unknown"),
            lambda state: state.update(seen_events={}),
            lambda state: state.update(revision=8),
        )
        for mutate in mutations:
            state = deepcopy(original)
            mutate(state)
            SyntheticClosureRequest.objects.filter(
                pk=self.record.identity.request_id
            ).update(state=state)
            with self.assertRaises(InvalidClosureState):
                self.issue()
        self.assertFalse(SyntheticClosureOperation.objects.exists())

    def test_missing_or_mismatched_receipt_does_not_trust_state(self):
        self.issue()
        SyntheticClosureOperation.objects.update(source_step="stop")
        with self.assertRaises(InvalidClosureState):
            self.read()
        SyntheticClosureOperation.objects.all().delete()
        with self.assertRaises(InvalidClosureState):
            self.read()

    def test_codec_rejects_manual_unissued_ticket(self):
        issued = self.issue().record
        state = encode_record(issued)
        state["pending"]["source_step"] = None
        with self.assertRaises(InvalidClosureState):
            decode_record(issued.identity, state)

    def test_duplicate_observed_operation_cannot_hide_an_orphan_receipt(self):
        issued = self.issue().record
        observed = self.observe(self.event(issued)).record
        state = encode_record(observed)
        duplicate = deepcopy(state["seen_events"][0])
        duplicate["event_id"] = str(uuid4())
        state["seen_events"].append(duplicate)
        SyntheticClosureRequest.objects.filter(pk=observed.identity.request_id).update(
            state=state
        )
        SyntheticClosureOperation.objects.create(
            pk=uuid4(),
            request_id=observed.identity.request_id,
            source_step=Step.REVOKE,
            outcome="revocation",
            issued_revision=2,
        )
        with self.assertRaises(InvalidClosureState):
            self.read()

    def test_synthetic_store_never_reads_credentials_or_calls_provider(self):
        with (
            patch(
                "growthtwin.modules.connections.backend._read",
                side_effect=AssertionError,
            ),
            patch(
                "growthtwin.modules.connections.backend._post",
                side_effect=AssertionError,
            ),
        ):
            issued = self.issue().record
            self.observe(self.event(issued))
            self.read()


class PostgreSQLClosureRaceTests(StoreFixture, TransactionTestCase):
    @skipUnlessDBFeature("has_select_for_update")
    def test_competing_writers_persist_one_operation_and_one_revision(self):
        barrier = Barrier(2)

        def writer(operation_id):
            close_old_connections()
            try:
                owner = get_user_model().objects.get(pk=self.owner.pk)
                request = replace(self.request, operation_id=operation_id)
                barrier.wait(timeout=10)
                return issue_synthetic_ticket(
                    owner=owner, workspace_id=self.workspace.pk, request=request
                ).disposition
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(writer, (uuid4(), uuid4())))
        self.assertCountEqual(
            results, [IssuanceDisposition.ISSUED, IssuanceDisposition.REJECTED]
        )
        self.assertEqual(self.read().revision, 1)
        self.assertEqual(SyntheticClosureOperation.objects.count(), 1)
