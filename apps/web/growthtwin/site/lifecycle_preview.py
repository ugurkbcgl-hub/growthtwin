"""Read-only, fixed synthetic scenarios; never load an account or call a provider."""

from dataclasses import replace
from uuid import UUID

from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_safe

from growthtwin.modules.connections.lifecycle_decision import (
    ClosureSnapshot,
    LocalErasure,
    LocalSecret,
    RemoteStop,
    RequestFacts,
    Revocation,
    Step,
    evaluate_closure,
)
from growthtwin.modules.connections.lifecycle_observation import (
    ClosureIdentity,
    ClosureRecord,
    Disposition,
    Observation,
    reduce_observation,
)
from growthtwin.modules.connections.lifecycle_ticket import (
    IssuanceDisposition,
    TicketRequest,
    issue_ticket,
)

SCENARIOS = (
    ("bekleyen", "Durdurma bekliyor"),
    ("acil", "Erişim kesildi, sonuç belirsiz"),
    ("tekrar", "Tekrarlanan istek"),
    ("kurtarma", "Kurtarma kontrolü"),
    ("temizlik", "Temizlik tamamlanmadı"),
)
STEP_LABELS = {
    Step.VERIFY_RECOVERY: "Geri yüklenen kayıtların güncelliği doğrulanmalı.",
    Step.ESTABLISH_BARRIER: "Yeni işlemleri engelleyen kapanış kaydı doğrulanmalı.",
    Step.RECONCILE: "Sonucu belirsiz işlemin durumu kontrol edilmeli.",
    Step.STOP: "Kampanyanın durumu platformdan doğrulanmalı.",
    Step.REVOKE: "Onaylanan kapsamda erişim iptali izlenmeli.",
    Step.VERIFY_REVOCATION: "Erişimin gerçekten iptal edildiği doğrulanmalı.",
    Step.REMOVE_LOCAL_SECRET: "Yerel yetki bilgisinin kaldırılması doğrulanmalı.",
    Step.REVIEW_ERASURE: "Veri temizliğinin koşulları ayrıca değerlendirilmeli.",
    Step.ERASE_LOCAL: "Yerel veri temizliğinin sonucu ayrıca doğrulanmalı.",
}


def scenario_details(key):
    """Compute demo results from constants, not browser-supplied evidence or IDs."""
    facts = RequestFacts(True, True, True, True)
    identity = ClosureIdentity(*(UUID(int=value) for value in (1, 2, 3, 4)))
    snapshot = ClosureSnapshot(
        barrier_confirmed=True,
        recovery_verified=True,
        in_flight=False,
        local_secret=LocalSecret.PRESENT,
        remote_stop=RemoteStop.PENDING,
        stop_authorized=True,
        project_impact_confirmed=True,
    )
    record = ClosureRecord(identity, 0, snapshot)
    stop_request = TicketRequest(identity, 0, UUID(int=5), Step.STOP)
    notes = []

    if key in {"bekleyen", "acil", "tekrar"}:
        issued = issue_ticket(facts, record, stop_request)
        if issued.disposition is not IssuanceDisposition.ISSUED:
            raise ValueError("Synthetic scenario no longer matches the contract.")
        record = issued.record
        notes.append(
            "Örnekte durdurma isteği kayda alındı."
            if key == "acil"
            else "Örnekte durdurma isteği kayda alındı; sonucu henüz gelmedi."
        )
        if key == "tekrar":
            replay = issue_ticket(facts, record, stop_request)
            if replay.disposition is not IssuanceDisposition.DUPLICATE:
                raise ValueError("Synthetic replay no longer matches the contract.")
            notes.append("Aynı istek tekrar geldi. İkinci işlem oluşturulmadı.")
        elif key == "acil":
            record = replace(
                record, snapshot=replace(record.snapshot, immediate_revoke=True)
            )
            request = TicketRequest(identity, record.revision, UUID(int=6), Step.REVOKE)
            priority = issue_ticket(facts, record, request)
            if priority.disposition is not IssuanceDisposition.ISSUED:
                raise ValueError("Synthetic priority no longer matches the contract.")
            record = priority.record
            for ticket, value, event_id in (
                (record.priority_pending, Revocation.CONFIRMED, 7),
                (record.pending, RemoteStop.UNCERTAIN, 8),
            ):
                event = Observation(
                    identity, record.revision, UUID(int=event_id), ticket, value
                )
                result = reduce_observation(facts, record, event)
                if result.disposition is not Disposition.APPLIED:
                    raise ValueError(
                        "Synthetic outcome no longer matches the contract."
                    )
                record = result.record
            notes.append(
                "Örnekte acil erişim iptali, durdurma sonucunu beklemeden ilerledi."
            )
            notes.append("Erişimin kesilmesi, reklamın durduğunun kanıtı değildir.")
    elif key == "kurtarma":
        record = replace(record, snapshot=replace(snapshot, recovery_verified=False))
        notes.append(
            "Örnekte eski bir yedek geri getirildi; kayıtların güncelliği henüz doğrulanmadı."
        )
    elif key == "temizlik":
        record = replace(
            record,
            snapshot=replace(
                snapshot,
                remote_stop=RemoteStop.UNCERTAIN,
                revocation=Revocation.CONFIRMED,
                local_secret=LocalSecret.ABSENT,
                local_erasure=LocalErasure.COMPLETED,
            ),
        )
        notes.append(
            "Örnekte yerel temizlik tamamlandı; alıcı ve yedek kopyaları henüz doğrulanmadı."
        )
    else:
        raise ValueError("Unknown synthetic scenario.")

    decision = evaluate_closure(facts, record.snapshot)
    # Do not offer a second normal action while its outcome is unresolved.
    if record.pending is not None or record.priority_pending is not None:
        next_checks = (
            "Mevcut isteğin sonucu beklenmeli; ikinci bir normal işlem başlatılmamalı.",
        )
    elif key == "temizlik":
        next_checks = ("Alıcı ve yedek kopyalarının temizliği ayrı ayrı doğrulanmalı.",)
    else:
        next_checks = tuple(STEP_LABELS[step] for step in decision.next_steps)
    return {
        "notes": tuple(notes),
        "messages": decision.messages,
        "next_checks": next_checks,
    }


@require_safe
def lifecycle_preview(request):
    key = request.GET.get("senaryo", "bekleyen")
    titles = dict(SCENARIOS)
    if key not in titles:
        raise Http404("Örnek bulunamadı.")
    return render(
        request,
        "site/lifecycle_preview.html",
        {
            "scenarios": SCENARIOS,
            "selected": key,
            "title": titles[key],
            **scenario_details(key),
        },
    )
