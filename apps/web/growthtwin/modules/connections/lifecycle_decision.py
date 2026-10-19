"""Pure synthetic closure decisions (ADR-0027); not a runtime authorization gate.

No persistence, HTTP, credentials, callbacks or deletion. The caller supplies
already-verified facts; this module cannot establish their truth or durability.
Existing Google TEST routes deliberately do not use this contract yet.
"""

from dataclasses import dataclass
from enum import StrEnum


class RemoteStop(StrEnum):
    NOT_REQUESTED = "not_requested"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    UNCERTAIN = "uncertain"


class Revocation(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    UNVERIFIED = "unverified"


class LocalSecret(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    ERROR = "error"


class LocalErasure(StrEnum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"
    BLOCKED = "blocked_with_reason"


class ExternalErasure(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    UNVERIFIED = "unverified"


class Step(StrEnum):
    VERIFY_RECOVERY = "verify_recovery"
    ESTABLISH_BARRIER = "establish_barrier"
    RECONCILE = "reconcile"
    STOP = "stop"
    REVOKE = "revoke"
    VERIFY_REVOCATION = "verify_revocation"
    REMOVE_LOCAL_SECRET = "remove_local_secret"
    REVIEW_ERASURE = "review_erasure"
    ERASE_LOCAL = "erase_local"


def _bools(value, names):
    if any(type(getattr(value, name)) is not bool for name in names):
        raise ValueError("Lifecycle facts must be explicit booleans.")


@dataclass(frozen=True)
class RequestFacts:
    """Synthetic proof assertions, not an implementation of auth/CSRF/ownership."""

    owner_verified: bool = False
    scope_verified: bool = False
    mutation_verified: bool = False
    revision_current: bool = False

    def __post_init__(self):
        _bools(self, self.__dataclass_fields__)


@dataclass(frozen=True)
class ClosureSnapshot:
    remote_stop: RemoteStop = RemoteStop.NOT_REQUESTED
    revocation: Revocation = Revocation.UNVERIFIED
    local_secret: LocalSecret = LocalSecret.ERROR
    local_erasure: LocalErasure = LocalErasure.PENDING
    recipient_erasure: ExternalErasure = ExternalErasure.UNVERIFIED
    backup_erasure: ExternalErasure = ExternalErasure.UNVERIFIED
    barrier_confirmed: bool = False
    recovery_verified: bool = False
    in_flight: bool = True
    stop_authorized: bool = False
    project_impact_confirmed: bool = False
    immediate_revoke: bool = False
    erasure_policy_verified: bool = False
    minimal_barrier_verified: bool = False

    def __post_init__(self):
        for name, kind in (
            ("remote_stop", RemoteStop),
            ("revocation", Revocation),
            ("local_secret", LocalSecret),
            ("local_erasure", LocalErasure),
            ("recipient_erasure", ExternalErasure),
            ("backup_erasure", ExternalErasure),
        ):
            if type(getattr(self, name)) is not kind:
                raise ValueError("Unknown lifecycle evidence state.")
        _bools(
            self,
            (
                "barrier_confirmed",
                "recovery_verified",
                "in_flight",
                "stop_authorized",
                "project_impact_confirmed",
                "immediate_revoke",
                "erasure_policy_verified",
                "minimal_barrier_verified",
            ),
        )


@dataclass(frozen=True)
class ClosureDecision:
    next_steps: tuple[Step, ...]
    messages: tuple[str, ...]
    # Closure-only contract: never approves create/enable/optimize/refresh/callback.
    new_work_blocked: bool = True


def evaluate_closure(facts: RequestFacts, snapshot: ClosureSnapshot) -> ClosureDecision:
    """Suggest bounded closure steps, never execute or mark outcomes completed.

    stop_authorized asserts a usable existing grant and verified resource/target.
    project_impact_confirmed asserts consent to the actual revocation scope.
    Returned steps are an unordered eligible set, NOT an execution schedule.
    Every real side effect would require a fresh durable authorization check.
    """
    if type(facts) is not RequestFacts or type(snapshot) is not ClosureSnapshot:
        raise ValueError("Typed lifecycle facts are required.")
    if not all(getattr(facts, name) for name in facts.__dataclass_fields__):
        return ClosureDecision((), ("İstek veya çalışma alanı yetkisi doğrulanamadı.",))
    if not snapshot.recovery_verified:
        return ClosureDecision(
            (Step.VERIFY_RECOVERY,),
            ("Kurtarma kanıtları doğrulanmalı; eski sonuçlar güncel kabul edilmedi.",),
        )
    if not snapshot.barrier_confirmed:
        return ClosureDecision(
            (Step.ESTABLISH_BARRIER,),
            ("Yeni işleri kapatan kalıcı engel henüz doğrulanmadı.",),
        )

    messages = [
        {
            RemoteStop.NOT_REQUESTED: "Uzak kampanyayı durdurma istenmedi.",
            RemoteStop.PENDING: "Uzak kampanyayı durdurma bekliyor.",
            RemoteStop.CONFIRMED: "Uzak kampanyanın durduğu doğrulandı.",
            RemoteStop.UNCERTAIN: "Uzak kampanyanın durduğu doğrulanamadı.",
        }[snapshot.remote_stop],
        {
            Revocation.PENDING: "Google yetki iptali bekliyor.",
            Revocation.CONFIRMED: "Google yetki iptali doğrulandı.",
            Revocation.UNVERIFIED: "Google yetki iptali doğrulanamadı.",
        }[snapshot.revocation],
        {
            LocalSecret.PRESENT: "Yerel yetki bilgisi hâlâ mevcut.",
            LocalSecret.ABSENT: "Yerel yetki bilgisi yok; bu Google iptalini kanıtlamaz.",
            LocalSecret.ERROR: "Yerel yetki bilgisinin durumu doğrulanamadı.",
        }[snapshot.local_secret],
        {
            LocalErasure.PENDING: "Yerel veri temizliği bekliyor.",
            LocalErasure.PARTIAL: "Yerel veri temizliği kısmen tamamlandı.",
            LocalErasure.COMPLETED: "Yerel veri temizliği kaydı tamamlandı; diğer kopyalar ayrı izlenir.",
            LocalErasure.BLOCKED: "Yerel veri temizliği için gerekçeli değerlendirme gerekiyor.",
        }[snapshot.local_erasure],
    ]
    for label, state in (
        ("Alıcı kopyaları", snapshot.recipient_erasure),
        ("Yedek kopyaları", snapshot.backup_erasure),
    ):
        messages.append(
            f"{label}: "
            + {
                ExternalErasure.NOT_APPLICABLE: "bu kapsamda uygulanmıyor.",
                ExternalErasure.PENDING: "temizlik bekliyor.",
                ExternalErasure.CONFIRMED: "temizlik doğrulandı.",
                ExternalErasure.UNVERIFIED: "temizlik doğrulanamadı.",
            }[state]
        )

    steps = []
    pending_stop = snapshot.remote_stop in {RemoteStop.PENDING, RemoteStop.UNCERTAIN}
    can_stop = (
        snapshot.stop_authorized
        and not snapshot.immediate_revoke
        and snapshot.local_secret is LocalSecret.PRESENT
        and snapshot.revocation is not Revocation.CONFIRMED
    )
    if snapshot.in_flight:
        messages.append(
            "Gönderilmiş işlem henüz çözümlenmedi; yeniden gönderim yapılamaz."
        )
        if can_stop:
            steps.append(Step.RECONCILE)
    if pending_stop and can_stop and not snapshot.in_flight:
        steps.append(Step.STOP)
    if snapshot.revocation is not Revocation.CONFIRMED:
        if snapshot.local_secret is not LocalSecret.PRESENT:
            steps.append(Step.VERIFY_REVOCATION)
        elif snapshot.project_impact_confirmed and (
            snapshot.immediate_revoke or not (pending_stop and can_stop)
        ):
            steps.append(Step.REVOKE)
    elif snapshot.local_secret is LocalSecret.PRESENT:
        steps.append(Step.REMOVE_LOCAL_SECRET)

    if snapshot.local_erasure is not LocalErasure.COMPLETED:
        ready = (
            snapshot.local_erasure is not LocalErasure.BLOCKED
            and snapshot.erasure_policy_verified
            and snapshot.minimal_barrier_verified
            and not snapshot.in_flight
            and snapshot.revocation is Revocation.CONFIRMED
            and snapshot.local_secret is LocalSecret.ABSENT
        )
        steps.append(Step.ERASE_LOCAL if ready else Step.REVIEW_ERASURE)
    return ClosureDecision(tuple(steps), tuple(messages))
