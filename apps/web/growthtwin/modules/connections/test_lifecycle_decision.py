"""Synthetic, side-effect-free checks for closure decisions only."""

from dataclasses import FrozenInstanceError, replace

from django.test import SimpleTestCase

from .lifecycle_decision import (
    ClosureSnapshot,
    ExternalErasure,
    LocalErasure,
    LocalSecret,
    RemoteStop,
    RequestFacts,
    Revocation,
    Step,
    evaluate_closure,
)


class LifecycleDecisionTests(SimpleTestCase):
    def setUp(self):
        self.facts = RequestFacts(True, True, True, True)
        self.snapshot = ClosureSnapshot(
            barrier_confirmed=True,
            recovery_verified=True,
            in_flight=False,
            local_secret=LocalSecret.PRESENT,
        )

    def decide(self, **changes):
        return evaluate_closure(self.facts, replace(self.snapshot, **changes))

    def test_defaults_block_new_work_and_require_recovery(self):
        result = evaluate_closure(self.facts, ClosureSnapshot())
        self.assertEqual(result.next_steps, (Step.VERIFY_RECOVERY,))
        self.assertTrue(result.new_work_blocked)

    def test_invalid_request_proofs_disclose_no_snapshot_and_suggest_no_steps(self):
        for name in self.facts.__dataclass_fields__:
            result = evaluate_closure(
                replace(self.facts, **{name: False}), self.snapshot
            )
            self.assertEqual(result.next_steps, ())
            self.assertEqual(len(result.messages), 1)
            self.assertNotIn("Google", result.messages[0])

    def test_unconfirmed_barrier_prevents_stop_revoke_and_erasure(self):
        result = self.decide(barrier_confirmed=False, immediate_revoke=True)
        self.assertEqual(result.next_steps, (Step.ESTABLISH_BARRIER,))

    def test_restore_does_not_trust_old_successes(self):
        result = self.decide(
            recovery_verified=False,
            remote_stop=RemoteStop.CONFIRMED,
            revocation=Revocation.CONFIRMED,
            local_erasure=LocalErasure.COMPLETED,
        )
        self.assertEqual(result.next_steps, (Step.VERIFY_RECOVERY,))
        self.assertFalse(any("doğrulandı" in text for text in result.messages))

    def test_stop_is_preferred_before_revoke_when_possible(self):
        result = self.decide(
            remote_stop=RemoteStop.PENDING,
            stop_authorized=True,
            project_impact_confirmed=True,
        )
        self.assertIn(Step.STOP, result.next_steps)
        self.assertNotIn(Step.REVOKE, result.next_steps)

    def test_immediate_revoke_is_not_blocked_by_uncertain_stop(self):
        result = self.decide(
            remote_stop=RemoteStop.UNCERTAIN,
            stop_authorized=True,
            project_impact_confirmed=True,
            immediate_revoke=True,
        )
        self.assertIn(Step.REVOKE, result.next_steps)
        self.assertNotIn(Step.STOP, result.next_steps)
        self.assertIn("Uzak kampanyanın durduğu doğrulanamadı.", result.messages)

    def test_revocation_requires_confirmed_project_impact(self):
        for state in (Revocation.PENDING, Revocation.UNVERIFIED):
            result = self.decide(revocation=state, immediate_revoke=True)
            self.assertNotIn(Step.REVOKE, result.next_steps)
        self.assertIn(
            Step.REVOKE, self.decide(project_impact_confirmed=True).next_steps
        )

    def test_missing_or_error_secret_does_not_prove_revocation_or_allow_stop(self):
        for state in (LocalSecret.ABSENT, LocalSecret.ERROR):
            result = self.decide(
                local_secret=state,
                remote_stop=RemoteStop.UNCERTAIN,
                stop_authorized=True,
                project_impact_confirmed=True,
            )
            self.assertIn(Step.VERIFY_REVOCATION, result.next_steps)
            self.assertNotIn(Step.STOP, result.next_steps)
            self.assertNotIn(Step.REVOKE, result.next_steps)

    def test_confirmed_revocation_cannot_reenable_stop_or_refresh(self):
        result = self.decide(
            revocation=Revocation.CONFIRMED,
            remote_stop=RemoteStop.UNCERTAIN,
            stop_authorized=True,
        )
        self.assertIn(Step.REMOVE_LOCAL_SECRET, result.next_steps)
        self.assertNotIn(Step.STOP, result.next_steps)
        self.assertNotIn(Step.REVOKE, result.next_steps)
        self.assertTrue(result.new_work_blocked)

    def test_in_flight_requires_reconciliation_without_resend_or_erasure(self):
        result = self.decide(
            in_flight=True,
            stop_authorized=True,
            remote_stop=RemoteStop.UNCERTAIN,
            erasure_policy_verified=True,
            minimal_barrier_verified=True,
        )
        self.assertIn(Step.RECONCILE, result.next_steps)
        self.assertNotIn(Step.STOP, result.next_steps)
        self.assertNotIn(Step.ERASE_LOCAL, result.next_steps)
        self.assertTrue(result.new_work_blocked)

    def test_erasure_requires_each_positive_fact(self):
        ready = replace(
            self.snapshot,
            revocation=Revocation.CONFIRMED,
            local_secret=LocalSecret.ABSENT,
            erasure_policy_verified=True,
            minimal_barrier_verified=True,
        )
        self.assertIn(Step.ERASE_LOCAL, evaluate_closure(self.facts, ready).next_steps)
        for changes in (
            {"local_erasure": LocalErasure.BLOCKED},
            {"erasure_policy_verified": False},
            {"minimal_barrier_verified": False},
            {"in_flight": True},
            {"revocation": Revocation.UNVERIFIED},
            {"local_secret": LocalSecret.PRESENT},
        ):
            result = evaluate_closure(self.facts, replace(ready, **changes))
            self.assertNotIn(Step.ERASE_LOCAL, result.next_steps)
            self.assertIn(Step.REVIEW_ERASURE, result.next_steps)

    def test_local_completion_does_not_complete_other_outcomes(self):
        result = self.decide(
            local_erasure=LocalErasure.COMPLETED,
            recipient_erasure=ExternalErasure.PENDING,
            backup_erasure=ExternalErasure.UNVERIFIED,
            remote_stop=RemoteStop.UNCERTAIN,
        )
        self.assertIn("Alıcı kopyaları: temizlik bekliyor.", result.messages)
        self.assertIn("Yedek kopyaları: temizlik doğrulanamadı.", result.messages)
        self.assertIn("Uzak kampanyanın durduğu doğrulanamadı.", result.messages)
        self.assertNotIn(Step.ERASE_LOCAL, result.next_steps)

    def test_repeat_is_deterministic_and_inputs_remain_immutable(self):
        first = evaluate_closure(self.facts, self.snapshot)
        self.assertEqual(first, evaluate_closure(self.facts, self.snapshot))
        with self.assertRaises(FrozenInstanceError):
            self.snapshot.barrier_confirmed = False
        with self.assertRaises(FrozenInstanceError):
            first.new_work_blocked = False

    def test_strings_unknown_values_and_truthy_flags_are_rejected(self):
        for value in ("false", 1, None):
            with self.assertRaises(ValueError):
                RequestFacts(owner_verified=value)
            with self.assertRaises(ValueError):
                ClosureSnapshot(barrier_confirmed=value)
        for name in (
            "remote_stop",
            "revocation",
            "local_secret",
            "local_erasure",
            "recipient_erasure",
            "backup_erasure",
        ):
            with self.assertRaises(ValueError):
                ClosureSnapshot(**{name: "unknown"})
        with self.assertRaises(ValueError):
            evaluate_closure({}, self.snapshot)

    def test_every_evidence_state_keeps_new_work_blocked(self):
        for name, enum in (
            ("remote_stop", RemoteStop),
            ("revocation", Revocation),
            ("local_secret", LocalSecret),
            ("local_erasure", LocalErasure),
            ("recipient_erasure", ExternalErasure),
            ("backup_erasure", ExternalErasure),
        ):
            for state in enum:
                result = self.decide(**{name: state})
                self.assertTrue(result.new_work_blocked)
                self.assertEqual(len(result.messages), 6)
