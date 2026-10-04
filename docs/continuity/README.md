# Session continuity

This folder carries GrowthTwin's current working context between Codex chats, models, and people.

## Source of truth

- `STATE.md` is the compact, current handoff snapshot. Replace outdated snapshot details; do not turn it into a transcript.
- `PROJECT.md`, `ROADMAP.md`, and accepted ADRs remain the canonical project record. Update those when a decision or durable project status changes.
- The current user request and the repository's `AGENTS.md` instructions take precedence over this handoff note. Verify facts that may have changed, especially Git/PR state, provider quotas, and environment status.

## At the start of a session

1. Read `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, this file, and `STATE.md`.
2. Check the current branch, working-tree changes, latest commit, and linked pull request before editing.
3. Confirm the next action still matches the user's current request and the Phase 0 gates.

## At a milestone or handoff

Update `STATE.md` with only verified current facts: objective, completed work, branch/PR, checks actually run, remaining decisions/blockers, and one recommended next action. Update canonical docs when appropriate. Mark unverified information as unverified and include the date/time and timezone.

Never record API keys, passwords, access tokens, secret values, or private customer data here. If relevant, record only that a credential is stored in an approved secret store and whether it needs rotation. Do not copy credentials into another chat or model.

## Low-usage transition

- When the Codex usage tool shows 10% remaining or less, begin preparing the handoff; complete it by 5% remaining.
- At the threshold, check the live usage value, repository branch/worktree, latest commit, open PRs, and CI results. Resolve or clearly record in-flight work.
- Audit the canonical docs and fix only stale facts. Update `STATE.md` with the verified state and exactly one next action. Do not rewrite accurate documents or invent completion claims.
- End by generating one current, copy-ready Turkish prompt for the next AI chat. It should make the next chat read the required files and recheck current Git/PR facts before acting.
- If repository access or the usage limit is unavailable, say what could not be verified and do not present an unverified handoff as current.

## Copyable handoff prompt

> GrowthTwin projesini kaldığı yerden sürdür. Önce `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, `docs/continuity/README.md` ve `docs/continuity/STATE.md` dosyalarını bu sırayla oku; sonra dalı, çalışma ağacını, son commit'i, açık PR'ları ve CI durumunu yeniden doğrula. Teknik koordinatör olarak işi küçük adımlarla ilerlet; terminal işlerini kullanıcıya yaptırma. Ürün Türkiye'de reklam vermek isteyen farklı kişi ve işletmelere hitap eder; diş klinikleri yalnızca olası müşteri örneğidir. Omneky, marka ve brief alımından çok formatlı reklam üretimi, bağlı kanallarda kampanya yayını, birleşik raporlama ve sınırlar içindeki iyileştirme için uzun vadeli yetenek ölçütüdür; tüm özellik ve kanallar ilk sürüme girmez. Bu handoff talimatına göre Phase 0 tamamlanana kadar ürün özelliği başlatma. Her gerçek kanal/harcama için reklamverenin açık izni, bağlı hesabı ve uygulanabilir sert limitleri gerekir; belirsizlikte dur. Sentetik veri kullan; gizli bilgileri hiçbir yere yazma ve ücretli altyapı ekleme. `STATE.md` içindeki tek Next action adımından devam et, uygun dokümanları güncel tut ve ilerlemeyi anlaşılır Türkçe özetle.

If the next model cannot access the repository, provide it the current `STATE.md` text and the user's new request. The repository remains the durable source of truth; never include secrets in the pasted context.
