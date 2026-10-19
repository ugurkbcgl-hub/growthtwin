"""Synthetic reducer evidence only; no database, provider or callback execution."""

from dataclasses import FrozenInstanceError, replace
from uuid import uuid4

from django.test import SimpleTestCase

from .lifecycle_decision import (
    ClosureSnapshot,
    ExternalErasure,
    LocalErasure,
    LocalSecret,
    RemoteStop,
    RequestFacts,
    Revocation,
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


class LifecycleObservationTests(SimpleTestCase):
    def setUp(self):
        self.facts = RequestFacts(True, True, True, True)
        self.identity = ClosureIdentity(uuid4(), uuid4(), uuid4(), uuid4())
        self.ticket = PendingObservation(uuid4(), Outcome.REVOCATION)
        self.snapshot = ClosureSnapshot(
            recovery_verified=True,
            barrier_confirmed=True,
            in_flight=False,
        )
        self.record = ClosureRecord(self.identity, 3, self.snapshot, self.ticket)
        self.event = Observation(
            self.identity, 3, uuid4(), self.ticket, Revocation.CONFIRMED
        )

    def reduce(self, record=None, event=None):
        return reduce_observation(
            self.facts, record or self.record, event or self.event
        )

    def assert_rejected(self, record, event, reason):
        result = self.reduce(record, event)
        self.assertEqual(result.disposition, Disposition.REJECTED)
        self.assertEqual(result.reason, reason)
        self.assertIs(result.record, record)

    def test_matching_observation_changes_only_its_outcome_and_revision(self):
        result = self.reduce()
        self.assertEqual(result.disposition, Disposition.APPLIED)
        self.assertEqual(result.record.revision, 4)
        self.assertIsNone(result.record.pending)
        self.assertEqual(result.record.seen_events, (self.event,))
        self.assertEqual(
            result.record.snapshot,
            replace(self.snapshot, revocation=Revocation.CONFIRMED),
        )
        self.assertEqual(result.record.identity, self.identity)
        self.assertFalse(result.record.closed)
        self.assertEqual(self.record.revision, 3)

    def test_each_scope_and_generation_mismatch_is_rejected(self):
        for name in self.identity.__dataclass_fields__:
            with self.subTest(name=name):
                event = replace(
                    self.event, identity=replace(self.identity, **{name: uuid4()})
                )
                self.assert_rejected(self.record, event, "identity_mismatch")

    def test_every_missing_request_proof_rejects_without_mutation(self):
        for name in self.facts.__dataclass_fields__:
            result = reduce_observation(
                replace(self.facts, **{name: False}), self.record, self.event
            )
            self.assertEqual(result.reason, "request_unverified")
            self.assertIs(result.record, self.record)

    def test_old_and_future_revision_rejected(self):
        for revision in (0, 2, 4, 100):
            self.assert_rejected(
                self.record,
                replace(self.event, expected_revision=revision),
                "revision_mismatch",
            )

    def test_exact_replay_is_noop_but_event_id_content_conflict_is_rejected(self):
        applied = self.reduce().record
        replay = self.reduce(applied)
        self.assertEqual(replay.disposition, Disposition.DUPLICATE)
        self.assertIs(replay.record, applied)
        self.assert_rejected(
            applied,
            replace(self.event, value=Revocation.UNVERIFIED),
            "event_identity_conflict",
        )

    def test_unsolicited_or_wrong_operation_ticket_rejected(self):
        self.assert_rejected(
            replace(self.record, pending=None), self.event, "ticket_mismatch"
        )
        changed = replace(
            self.event, ticket=PendingObservation(uuid4(), Outcome.REVOCATION)
        )
        self.assert_rejected(self.record, changed, "ticket_mismatch")

    def test_late_completion_cannot_change_closed_record(self):
        self.assert_rejected(
            replace(self.record, closed=True), self.event, "request_closed"
        )

    def test_restore_or_barrier_uncertainty_rejects_success(self):
        for name in ("recovery_verified", "barrier_confirmed"):
            record = replace(
                self.record, snapshot=replace(self.snapshot, **{name: False})
            )
            self.assert_rejected(record, self.event, "closure_evidence_unverified")

    def test_second_result_for_same_revision_cannot_overwrite_first(self):
        applied = self.reduce().record
        other = replace(self.event, event_id=uuid4(), value=Revocation.UNVERIFIED)
        self.assert_rejected(applied, other, "revision_mismatch")

    def test_revocation_and_local_secret_success_never_regress(self):
        for outcome, old, new in (
            (Outcome.REVOCATION, Revocation.CONFIRMED, Revocation.UNVERIFIED),
            (Outcome.LOCAL_SECRET, LocalSecret.ABSENT, LocalSecret.PRESENT),
            (
                Outcome.RECIPIENT_ERASURE,
                ExternalErasure.CONFIRMED,
                ExternalErasure.UNVERIFIED,
            ),
            (
                Outcome.BACKUP_ERASURE,
                ExternalErasure.NOT_APPLICABLE,
                ExternalErasure.CONFIRMED,
            ),
        ):
            ticket = PendingObservation(uuid4(), outcome)
            record = replace(
                self.record,
                pending=ticket,
                snapshot=replace(self.snapshot, **{outcome.value: old}),
            )
            event = replace(self.event, ticket=ticket, value=new)
            self.assert_rejected(record, event, "transition_not_allowed")

    def test_blocked_or_unready_erasure_cannot_become_completed(self):
        ticket = PendingObservation(uuid4(), Outcome.LOCAL_ERASURE)
        ready = replace(
            self.snapshot,
            revocation=Revocation.CONFIRMED,
            local_secret=LocalSecret.ABSENT,
            erasure_policy_verified=True,
            minimal_barrier_verified=True,
        )
        event = replace(self.event, ticket=ticket, value=LocalErasure.COMPLETED)
        record = replace(self.record, pending=ticket, snapshot=ready)
        self.assertEqual(self.reduce(record, event).disposition, Disposition.APPLIED)
        for changes in (
            {"local_erasure": LocalErasure.BLOCKED},
            {"erasure_policy_verified": False},
            {"minimal_barrier_verified": False},
            {"in_flight": True},
        ):
            blocked = replace(record, snapshot=replace(ready, **changes))
            self.assert_rejected(blocked, event, "transition_not_allowed")

    def test_stop_confirmation_with_in_flight_work_is_rejected(self):
        ticket = PendingObservation(uuid4(), Outcome.REMOTE_STOP)
        record = replace(
            self.record,
            pending=ticket,
            snapshot=replace(
                self.snapshot, remote_stop=RemoteStop.UNCERTAIN, in_flight=True
            ),
        )
        event = replace(self.event, ticket=ticket, value=RemoteStop.CONFIRMED)
        self.assert_rejected(record, event, "transition_not_allowed")
        uncertain = self.reduce(record, replace(event, value=RemoteStop.UNCERTAIN))
        self.assertTrue(uncertain.record.snapshot.in_flight)

    def test_input_shapes_and_cross_outcome_values_are_strict(self):
        for revision in (True, -1, "3"):
            with self.assertRaises(ValueError):
                replace(self.event, expected_revision=revision)
        with self.assertRaises(ValueError):
            replace(self.event, value=RemoteStop.CONFIRMED)
        with self.assertRaises(ValueError):
            replace(self.ticket, outcome="revocation")
        with self.assertRaises(ValueError):
            replace(self.record, closed=1)
        with self.assertRaises(ValueError):
            replace(self.record, seen_events=[self.event])
        with self.assertRaises(ValueError):
            reduce_observation({}, self.record, self.event)

    def test_records_and_evidence_are_frozen(self):
        with self.assertRaises(FrozenInstanceError):
            self.record.closed = False
        with self.assertRaises(FrozenInstanceError):
            self.event.expected_revision = 4
