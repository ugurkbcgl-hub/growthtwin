"""Database-free synthetic issuance and reducer round trips."""

from dataclasses import FrozenInstanceError, replace
from uuid import uuid4

from django.test import SimpleTestCase

from .lifecycle_decision import (
    ClosureSnapshot,
    LocalErasure,
    LocalSecret,
    RemoteStop,
    RequestFacts,
    Revocation,
    Step,
)
from .lifecycle_observation import (
    ClosureIdentity,
    ClosureRecord,
    Disposition,
    Observation,
    Outcome,
    PendingObservation,
    reduce_observation,
)
from .lifecycle_ticket import IssuanceDisposition, TicketRequest, issue_ticket


class LifecycleTicketTests(SimpleTestCase):
    def setUp(self):
        self.facts = RequestFacts(True, True, True, True)
        self.identity = ClosureIdentity(uuid4(), uuid4(), uuid4(), uuid4())
        self.snapshot = ClosureSnapshot(
            barrier_confirmed=True,
            recovery_verified=True,
            in_flight=False,
            local_secret=LocalSecret.PRESENT,
            project_impact_confirmed=True,
            erasure_policy_verified=True,
            minimal_barrier_verified=True,
        )
        self.record = ClosureRecord(self.identity, 3, self.snapshot)
        self.request = TicketRequest(self.identity, 3, uuid4(), Step.REVOKE)

    def issue(self, record=None, request=None):
        return issue_ticket(self.facts, record or self.record, request or self.request)

    def assert_rejected(self, record, request, reason):
        result = self.issue(record, request)
        self.assertEqual(result.disposition, IssuanceDisposition.REJECTED)
        self.assertEqual(result.reason, reason)
        self.assertIs(result.record, record)

    def test_supported_steps_issue_typed_tickets_without_changing_evidence(self):
        for step, outcome, changes in (
            (Step.REVOKE, Outcome.REVOCATION, {}),
            (
                Step.VERIFY_REVOCATION,
                Outcome.REVOCATION,
                {"local_secret": LocalSecret.ABSENT},
            ),
            (
                Step.STOP,
                Outcome.REMOTE_STOP,
                {"remote_stop": RemoteStop.PENDING, "stop_authorized": True},
            ),
            (
                Step.REMOVE_LOCAL_SECRET,
                Outcome.LOCAL_SECRET,
                {"revocation": Revocation.CONFIRMED},
            ),
            (
                Step.ERASE_LOCAL,
                Outcome.LOCAL_ERASURE,
                {
                    "revocation": Revocation.CONFIRMED,
                    "local_secret": LocalSecret.ABSENT,
                },
            ),
        ):
            record = replace(self.record, snapshot=replace(self.snapshot, **changes))
            result = self.issue(record, replace(self.request, step=step))
            self.assertEqual(result.disposition, IssuanceDisposition.ISSUED)
            self.assertEqual(result.record.revision, 4)
            self.assertEqual(result.record.pending.outcome, outcome)
            self.assertEqual(result.record.pending.source_step, step)
            self.assertEqual(result.record.pending.issued_revision, 4)
            self.assertIs(result.record.snapshot, record.snapshot)
            self.assertEqual(result.record.identity, record.identity)
            self.assertEqual(result.record.seen_events, ())

    def test_missing_proof_and_each_identity_component_are_rejected(self):
        for name in self.facts.__dataclass_fields__:
            result = issue_ticket(
                replace(self.facts, **{name: False}), self.record, self.request
            )
            self.assertEqual(result.reason, "request_unverified")
            self.assertIs(result.record, self.record)
        for name in self.identity.__dataclass_fields__:
            request = replace(
                self.request, identity=replace(self.identity, **{name: uuid4()})
            )
            self.assert_rejected(self.record, request, "identity_mismatch")

    def test_closed_restore_and_barrier_checks_precede_issuance_or_replay(self):
        issued = self.issue().record
        self.assert_rejected(
            replace(issued, closed=True), self.request, "request_closed"
        )
        for name in ("recovery_verified", "barrier_confirmed"):
            record = replace(issued, snapshot=replace(issued.snapshot, **{name: False}))
            self.assert_rejected(record, self.request, "closure_evidence_unverified")

    def test_stale_and_future_revisions_rejected(self):
        for revision in (0, 2, 4, 99):
            self.assert_rejected(
                self.record,
                replace(self.request, expected_revision=revision),
                "revision_mismatch",
            )

    def test_exact_issuance_replay_is_noop_and_changed_step_is_conflict(self):
        issued = self.issue().record
        result = self.issue(issued)
        self.assertEqual(result.disposition, IssuanceDisposition.DUPLICATE)
        self.assertIs(result.record, issued)
        # Same mapped outcome still cannot disguise a different operation.
        self.assert_rejected(
            issued,
            replace(self.request, step=Step.VERIFY_REVOCATION),
            "operation_identity_conflict",
        )

    def test_unresolved_operation_is_not_replaced(self):
        issued = self.issue().record
        request = replace(self.request, expected_revision=4, operation_id=uuid4())
        self.assert_rejected(issued, request, "operation_unresolved")
        legacy = replace(
            self.record, pending=PendingObservation(uuid4(), Outcome.REVOCATION)
        )
        self.assert_rejected(legacy, self.request, "operation_unresolved")

    def test_observed_operation_id_cannot_be_reissued(self):
        issued = self.issue().record
        event = Observation(
            self.identity, 4, uuid4(), issued.pending, Revocation.CONFIRMED
        )
        observed = reduce_observation(self.facts, issued, event).record
        request = replace(self.request, expected_revision=5)
        self.assert_rejected(observed, request, "operation_already_observed")

    def test_unsupported_and_ineligible_steps_cannot_issue(self):
        for step in (
            Step.VERIFY_RECOVERY,
            Step.ESTABLISH_BARRIER,
            Step.RECONCILE,
            Step.REVIEW_ERASURE,
        ):
            self.assert_rejected(
                self.record, replace(self.request, step=step), "unsupported_step"
            )
        no_impact = replace(
            self.record, snapshot=replace(self.snapshot, project_impact_confirmed=False)
        )
        self.assert_rejected(no_impact, self.request, "step_not_eligible")
        self.assert_rejected(
            self.record,
            replace(self.request, step=Step.ERASE_LOCAL),
            "step_not_eligible",
        )

    def test_revoke_secret_removal_erasure_round_trip(self):
        record = self.record
        for step, value in (
            (Step.REVOKE, Revocation.CONFIRMED),
            (Step.REMOVE_LOCAL_SECRET, LocalSecret.ABSENT),
            (Step.ERASE_LOCAL, LocalErasure.COMPLETED),
        ):
            request = TicketRequest(self.identity, record.revision, uuid4(), step)
            issued = self.issue(record, request)
            self.assertEqual(issued.disposition, IssuanceDisposition.ISSUED)
            event = Observation(
                self.identity,
                issued.record.revision,
                uuid4(),
                issued.record.pending,
                value,
            )
            result = reduce_observation(self.facts, issued.record, event)
            self.assertEqual(result.disposition, Disposition.APPLIED)
            record = result.record
        self.assertEqual(record.revision, 9)
        self.assertEqual(record.snapshot.local_erasure, LocalErasure.COMPLETED)
        self.assertEqual(len(record.seen_events), 3)

    def test_immediate_revoke_has_separate_lane_without_overwriting_stop(self):
        initial = replace(
            self.record,
            snapshot=replace(
                self.snapshot, remote_stop=RemoteStop.PENDING, stop_authorized=True
            ),
        )
        stop = self.issue(initial, replace(self.request, step=Step.STOP)).record
        original_ticket = stop.pending
        late_stop = Observation(
            self.identity, stop.revision, uuid4(), original_ticket, RemoteStop.UNCERTAIN
        )
        urgent = replace(stop, snapshot=replace(stop.snapshot, immediate_revoke=True))
        revoke_request = TicketRequest(
            self.identity, urgent.revision, uuid4(), Step.REVOKE
        )
        issued = self.issue(urgent, revoke_request)
        self.assertEqual(issued.disposition, IssuanceDisposition.ISSUED)
        self.assertEqual(issued.record.pending, original_ticket)
        priority = issued.record.priority_pending
        self.assertEqual(priority.source_step, Step.REVOKE)
        self.assertEqual(
            self.issue(issued.record, revoke_request).disposition,
            IssuanceDisposition.DUPLICATE,
        )
        self.assertEqual(
            reduce_observation(self.facts, issued.record, late_stop).reason,
            "revision_mismatch",
        )
        second_revoke = replace(
            revoke_request,
            expected_revision=issued.record.revision,
            operation_id=uuid4(),
        )
        self.assert_rejected(issued.record, second_revoke, "operation_unresolved")
        event = Observation(
            self.identity,
            issued.record.revision,
            uuid4(),
            priority,
            Revocation.CONFIRMED,
        )
        observed = reduce_observation(self.facts, issued.record, event).record
        self.assertIsNone(observed.priority_pending)
        self.assertEqual(observed.pending, original_ticket)
        # Freshly correlated uncertainty retires the original ticket, not a resend.
        uncertainty = Observation(
            self.identity,
            observed.revision,
            uuid4(),
            original_ticket,
            RemoteStop.UNCERTAIN,
        )
        settled = reduce_observation(self.facts, observed, uncertainty).record
        self.assertIsNone(settled.pending)
        self.assertEqual(settled.snapshot.revocation, Revocation.CONFIRMED)

    def test_stop_result_first_preserves_priority_revocation_ticket(self):
        initial = replace(
            self.record,
            snapshot=replace(
                self.snapshot, remote_stop=RemoteStop.PENDING, stop_authorized=True
            ),
        )
        stop = self.issue(initial, replace(self.request, step=Step.STOP)).record
        urgent = replace(stop, snapshot=replace(stop.snapshot, immediate_revoke=True))
        request = TicketRequest(self.identity, urgent.revision, uuid4(), Step.REVOKE)
        issued = self.issue(urgent, request).record
        fresh_stop = Observation(
            self.identity,
            issued.revision,
            uuid4(),
            issued.pending,
            RemoteStop.UNCERTAIN,
        )
        observed = reduce_observation(self.facts, issued, fresh_stop).record
        self.assertIsNone(observed.pending)
        self.assertEqual(observed.priority_pending, issued.priority_pending)
        self.assertEqual(
            self.issue(observed, request).disposition, IssuanceDisposition.DUPLICATE
        )
        fresh_revoke = Observation(
            self.identity,
            observed.revision,
            uuid4(),
            observed.priority_pending,
            Revocation.CONFIRMED,
        )
        settled = reduce_observation(self.facts, observed, fresh_revoke).record
        self.assertIsNone(settled.priority_pending)
        self.assertEqual(settled.snapshot.remote_stop, RemoteStop.UNCERTAIN)
        self.assertEqual(settled.snapshot.revocation, Revocation.CONFIRMED)

    def test_blocked_erasure_remains_review_only(self):
        ready = replace(
            self.snapshot,
            revocation=Revocation.CONFIRMED,
            local_secret=LocalSecret.ABSENT,
            local_erasure=LocalErasure.BLOCKED,
        )
        record = replace(self.record, snapshot=ready)
        self.assert_rejected(
            record, replace(self.request, step=Step.ERASE_LOCAL), "step_not_eligible"
        )

    def test_strict_types_ticket_metadata_and_immutable_requests(self):
        for revision in (True, -1, "3"):
            with self.assertRaises(ValueError):
                replace(self.request, expected_revision=revision)
        with self.assertRaises(ValueError):
            replace(self.request, step="revoke")
        with self.assertRaises(ValueError):
            issue_ticket({}, self.record, self.request)
        with self.assertRaises(ValueError):
            PendingObservation(uuid4(), Outcome.REVOCATION, Step.REVOKE)
        with self.assertRaises(ValueError):
            PendingObservation(uuid4(), Outcome.REVOCATION, Step.REVOKE, 0)
        with self.assertRaises(ValueError):
            PendingObservation(uuid4(), Outcome.REVOCATION, Step.STOP, 3)
        with self.assertRaises(ValueError):
            replace(
                self.record,
                pending=PendingObservation(uuid4(), Outcome.REVOCATION, Step.REVOKE, 4),
            )
        with self.assertRaises(ValueError):
            replace(
                self.record,
                priority_pending=PendingObservation(
                    uuid4(), Outcome.REMOTE_STOP, Step.STOP, 3
                ),
            )
        with self.assertRaises(FrozenInstanceError):
            self.request.step = Step.STOP
