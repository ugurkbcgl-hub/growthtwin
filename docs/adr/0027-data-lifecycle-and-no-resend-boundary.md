# ADR-0027 — Veri yaşam döngüsü ve tekrar gönderimi önleme sınırı

Date: 2026-10-19, Europe/Istanbul

Status: Accepted for design; production implementation and retention periods pending.

## Context

GrowthTwin Türkiye'de farklı sektörlerdeki reklamverenlere hizmet verecek.
Bugünkü yerel/sentetik akışta taslağı silmek, Google kampanyasını durdurmak ve
OAuth yetkisini iptal etmek farklı işlemlerdir. Üretim veri yaşam döngüsü yoktur.

Kod incelemesi: `site/models.py` oturuma bağlı taslakları CASCADE ile ilişkilendirir;
`clearsessions` çalışma alanı/Google kayıtlarını temizlemez. Çalışma alanındaki
kampanya taslağını silen view onay ister, sahibini kontrol eder; PROTECT nedeniyle
Google onay/gönderim kaydı varsa 409 döner. `GoogleDraftApproval.payload_json` ve
`GoogleDraftDispatch.payload_json` metin/plan snapshot'ları içerir. Bunlar
yalnız kişisel veri içermeyen olay kayıtları değildir.

`connections/backend.py::disconnect` Google revoke çağrısı başarılıysa yerel
grant dosyasını kaldırır; hata olursa kaldırma tamamlanmaz. Yerel dosyanın zaten
olmaması, Google'da yetkinin iptal edildiğini kanıtlamaz. Bugünkü kodda kalıcı bir
bağlantı-kapatma/silme isteği veya tüm işlemleri durduran yaşam döngüsü kilidi yoktur.
`draft_dispatch.py::perform` stop isteğiyle PAUSED gönderip geri okur; belirsizlikte
`uncertain` kaydeder. Silmek ya da token iptal etmek dış reklamı durdurmaz.

Bu karar kod incelemesi ve resmi kaynaklara dayanır; mevcut DB, grant, ledger,
Google hesabı veya kampanya üzerinde işlem yapılmadı.

## Decision

### 1. Dört ayrı işlem ve görünür sonuç

| Kullanıcının amacı | İşlem ve doğrulanacak sonuç | Bu işlemden çıkarılamayacak sonuç |
|---|---|---|
| Kampanyayı durdur | Yetkili hedefte ilgili kampanyayı PAUSED yap, doğru kaynak/hedefi geri oku; sonucu ve gözlem zamanını kaydet. | Veri silindi, token iptal edildi, önceki harcama iade edildi veya bütün hesap durdu. |
| GrowthTwin erişimini kes | Önce uygulamada ilgili bağlantıya yeni iş kabulünü kapat; token iptalini ve yerel secret kaldırmayı ayrı izle. | Uzak kampanya durdu veya Google'daki bütün veriler silindi. |
| Verilerimi sil | Sahipliği doğrulanmış istek, yeni işlem engeli, kategori bazlı hukuki değerlendirme ve doğrulanmış yerel/alıcı/yedek temizliği. | İstek alınır alınmaz bütün kopyalar yok oldu. |
| Çalışma alanını kapat | Tüm bağlantı/kampanya kapsamını göster; kapatma ve yukarıdaki alt işlemleri ilişkilendir. | Tek bir taslak ya da tarayıcı çerezi silindiğinde bu kapsam tamamlandı. |

Google revoke işlemi, projeye verilmiş kapsamları ve projedeki istemcilerin
token'larını etkileyebilir. Bu yüzden UI, bunu yalnız tek bir kampanyadan çıkış
gibi sunamaz. Üretimde proje/istemci/bağlantı paylaşım kapsamı doğrulanmalı,
etkilenebilecek bağlantılar açıklanmalı; yeni yetki talebi kullanıcı kararını
geri almak için otomatik başlatılmamalıdır. Test/üretim ayrımı korunur.

### 2. Gelecekteki uygulama sözleşmesi — mevcut kod değildir

- Kimliği doğrulanmış sahibin sunucu tarafında workspace/connection kapsamı
  kontrol edilir. CSRF, güncel sürüm ve tekrarları aynı isteğe bağlayan işlem
  kimliği gerekir. Başkasına ait ID veya GET hiçbir işlem başlatmaz.
- İstek kalıcı kaydedilir ve kapsamın yeni create/enable/optimize/refresh işleri
  kapatılır. Hassas veri/secret normal işlere ve AI'ya açılmaz. Durdurma ve sınırlı
  mutabakat işleri yalnız amaçları ve mevcut izinleri içinde yürür.
- Kilit her dış çağrı öncesinde ve callback/token kaydetmeden önce denetlenir;
  callback nesli/sürümü kapanmış isteği yeniden etkinleştiremez. Tek süreç lock'ı
  üretim eşzamanlılık kanıtı değildir. Halihazırda gönderilmiş ağ isteği geri
  alınmış sayılmaz: geç yanıt veya timeout kaydedilip mutabakat beklenir.
- Erişim kesilmeden önce kampanyayı durdurma önerilir. Kullanıcı hemen erişim
  iptalini seçerse ya da izin zaten yoksa iptal bu nedenle engellenmez; uzak
  durdurma **doğrulanamadı** kalır ve reklam platformunda yapılacak işlem açıklanır.
  Yeni OAuth izni olmadan durdurma yapılmış gibi gösterilmez.
- Sonuçlar ayrı tutulur: `remote_stop` (not_requested / pending / confirmed /
  uncertain), `provider_revocation` (pending / confirmed / unverified),
  `local_secret` (present / absent / error), `local_erasure` (pending / partial /
  completed / blocked_with_reason), `recipient_erasure` ve `backup_erasure`
  (not_applicable / pending / confirmed / unverified). Bunlar tasarım değerleridir,
  mevcut model alanları değildir. Tek bir “tamamlandı” hepsinin yerine geçmez.
- Retry aynı istek/nesil üzerinden yalnız eksik alt adımı tamamlar. Belirsiz
  create yeniden gönderilmez. HTTP 200, dosya yokluğu veya yerel satır silinmesi
  farklı alt adımların başarısı yerine kullanılamaz. İstek takibi, neden ve tarih
  kullanıcıya gösterilir; hata genel bir “silindi” bildirimiyle örtülmez.

### 3. Kategori bazında saklama ve silme planı

Her üretim kategorisi için amaç, veri sorumlusu/işleyen rolü, dayanak, alıcılar,
erişim rolleri, başlangıç/bitiş tetikleyicisi, azami süre, imha yöntemi, yedek
etkisi ve kanıt sahibi belirlenmelidir. Aşağıdakiler süre atanmış politika değildir.

| Kategori | Tetikleyici / yöntem yönü | Açık karar ve tamamlanma kanıtı |
|---|---|---|
| Hesap, çalışma alanı ve oturum | Hesap kapatma, yetki değişimi veya oturum sonu; oturumları geçersiz kılma ve kapsamlı temizleme ayrı. | Üretim alanları, dayanak ve süre; başka workspace'leri etkilemeyen sahiplik/rol kontrolü. |
| Anonim sentetik taslak | Oturum bitişi ve cleanup işi; yalnız bu oturuma bağlı taslaklar. | Zamanlayıcının başarı/gecikme izlemesi; session expiry kesin fiziksel imha sayılmaz. |
| Brief, içerik geçmişi ve onay snapshot'ı | İlgili amaç/dayanak sona erdiğinde kategori bazlı temizleme; gelecekte kanıt içeriğini işlem engelinden ayırma. | Azami süre ve hukuki değerlendirme. Bugünkü append-only/PROTECT snapshot'ı doğrudan boşaltılmaz veya cascade'e çevrilmez. |
| Token, bağlantı ve yetki | İptal/kapatma/izin kaybı; revoke sonucu, yerel secret ve önbellek/in-flight kullanımını ayrı doğrulama. | Sağlayıcı kapsamı, iptal hatası yönetimi, credential yaşam süresi. Token log veya imha makbuzunda tutulmaz. |
| Tekrar gönderimi önleme kaydı | İstek/işlem kimliği ve hedef eşleşmesini gerektiği sürece asgari tut; aşağıdaki ayrı bariyeri tasarla. | Amaç/dayanak ve azami süre; key/hash/ID hâlâ ilişkilendirilebiliyorsa anonim kabul edilmez. Süresiz saklama varsayımı yok. |
| Erişim, güvenlik ve imha kanıtı | Amaç ve mevzuata göre ayrı süreler; asgari olay kimliği, kapsam, yöntem, tarih, sonuç/neden. | Ham brief, token, kimlik belgesi veya kişi listesi makbuza eklenmez. İmha kayıtlarının özel saklama hükmü tüm kampanya içeriğine uygulanmaz. |
| Yedek, kopya ve alıcı kayıtları | İmha isteğini canlı DB, yedek penceresi ve gerçek veri alıcıları için izleme. | Gerçek envanter, periyot, erişim/geri dönüş sınırları ve kanıt. GrowthTwin Google'ın bağımsız saklama yükümlülükleri adına “her yerden silindi” diyemez. |
| Ödeme/vergisel belgeler, dosya ve lead | İlgili hizmet henüz devrede değil; devreye girmeden ayrı kategori/amaç/rol belirlenir. | Ticari/mevzuat süreleri ayrıca incelenir. İlk kanal ham lead'i GrowthTwin'de saklamaz. |

Somut işleme dayanağı değerlendirilmeden “tüm verileri X gün sakla” varsayılanı
eklenmez. Bir hak talebi veya zorunlu imha, teknik tasarım eksik diye süresiz
ertelenemez: yetkili değerlendirme ve güvenli işlem yolu gerekir. Yeterli
mekanizma yoksa gerçek veri kabulü/yayın açılmaz. Bu belge hukuki uygunluk kararı
veya herkese açık nihai saklama politikası değildir.

### 4. Snapshot ile güvenlik bariyerini ayırma ve yedekten dönüş

Bugünkü TEST ledger'ları değişmeden korunur. Üretimde içerik snapshot'ı ile
yeniden gönderimi engelleyen asgari kontrol kaydı farklı yaşam döngülerine sahip
olmalıdır. Gelecekteki asgari bariyer; tenant/bağlantı nesli, rastgele işlem kimliği,
hedef eşleşmesi ve engel durumuyla tasarlanır. Ham kreatif, URL sorgusu veya token
bariyere konmaz. Gerekli ilişkilendirme mümkün olduğu sürece kişisel veri riski
ve saklama sınırı devam eder; hash almak tek başına anonimleştirme değildir.

Silme/iptal engel kaydı, geri yüklenen eski DB'den daha güncel ve güvenilir bir
kaynaktan kontrol edilebilmelidir. Aynı eski backup içindeki tombstone yeterli
değildir. Mekanizma ve kurtarma kanıtı henüz uygulanmadı; yeni servis seçilmiyor.
Restore karantinada yapılır: dış create/enable/refresh ve otomasyon kapalıdır.
Güncel silme/iptal günlüğü uygulanır, eski credential nesilleri engellenir, silinmiş
kopyalar tekrar temizlenir; belirsizlikte dış işlemler kapalı kalır. Restore'dan
sonra otomatik yeniden gönderim ya da eski token ile otomatik reconnect olmaz.

## Acceptance scenarios for implementation

1. Başka workspace/bağlantı ID'si, anonim istek, eski sürüm ve GET/CSRF hatası
   veri veya dış işlem üretmez; tekrar aynı işlem kimliğine döner.
2. Stop timeout'u ile revoke başarısı aynı akışta olursa “erişim kesildi, uzak
   durdurma doğrulanamadı” gösterilir; durduruldu/silindi denmez.
3. Revoke hatası, Google yetkisinin zaten kaldırılmış olması ve yerel dosyanın
   yokluğu ayrı ele alınır; engel kalıcıdır, otomatik refresh ile geri açılmaz.
4. Kapatmayla yarışan create/refresh/callback, geç yanıt ve process restart
   yeniden etkinleştirme/ikinci create yapmaz; amaç dışı yeni veri işlenmez.
5. İçerik silinse bile belirsiz dış işlem yeniden gönderilmez. Bariyerin kendi
   süre sonu da tasarlanır; kontrol kanıtı yoksa dış çağrı kapalı kalır.
6. Silme/iptal öncesi yedek izole geri yüklenir; güncel engeller ve tekrar imha
   uygulandıktan sonra dahi eski grant/onay otomatik yayın yetkisi kazanmaz.
7. Gerçek veri envanteri, süre/dayanak ve alıcı/yedek kanıtları eksikse bütün
   kapsam için tamamlandı yanıtı verilmez; gerekçeli parça sonuçları gösterilir.

Bu senaryolar henüz çalıştırılmadı. Bu PR dokümantasyondur; yeni model, migration,
UI, scheduler, token iptali veya silme işi eklemez. Sonraki küçük teknik adım:
yan etkisiz bir yaşam döngüsü karar sözleşmesi; yalnız sentetik değerlerden
izinli eylem ve kullanıcıya gösterilecek alt durumları üretir. DB/API/UI bağlantısı
ve gerçek silme bundan sonra, ayrı incelemeyle gelir.

### Pure decision implementation follow-up — 2026-10-19

`connections/lifecycle_decision.py` now evaluates frozen synthetic request facts
and independent typed evidence. It returns eligible closure steps and Turkish
outcome messages; it never approves new campaign/refresh/callback work. Unknown
types and truthy non-booleans are rejected; unverified request, recovery or
barrier facts prevent further suggestions. An explicit BLOCKED erasure remains
review-only, even if other conditions are ready. Immediate revocation does not
wait for stop/reconciliation. Missing local secret is not revocation evidence.

15 focused database-free tests passed, including defaults, proof rejection,
restore distrust, stop/revoke priority, project impact, secret absence, in-flight,
each erasure prerequisite, partial outcomes, repeat determinism and immutability.
These are decision tests, not execution of all production acceptance scenarios
above. That decision-only slice did not implement durable identity/revision, a transition reducer, concurrency,
timestamps/freshness verifier, actual auth/CSRF checks, retry job or erasure
executor was implemented. The caller-supplied assertions are not themselves
proof. The existing local TEST views do not import or use the contract.

Eligible steps are not an execution schedule or runtime permission; every real
effect would require fresh scoped, durable checks. Next implement a pure
request/generation/revision-bound observation reducer to reject stale/late
completion and replay, still without DB/API/UI or credential operations.

### Pure observation reducer follow-up — 2026-10-19

`connections/lifecycle_observation.py` now models a synthetic immutable closure
identity (workspace, connection, request and generation), revision, one pending
operation ticket and typed outcome evidence. It consumes a matching ticket,
changes only its outcome, increments revision and retains synthetic event evidence.
Exact replay is a no-op; same event ID with changed content is rejected. Old/future
revision, wrong scope/generation/ticket, closed request or unverified recovery/
barrier cannot update the record. Outcomes cannot reopen a grant or alter safety
flags. Terminal success is per closure request, not a live provider drift monitor.

14 new DB-free tests plus the 15 decision tests passed (29 total), with ruff and
independent read-only review finding no blocking issue. This demonstrates pure
state transitions, not atomic storage, runtime auth, provider evidence freshness,
safe remote retries or restart recovery. Pending tickets are assertions supplied
by a future authorized coordinator; this module does not issue them. The seen
event tuple is synthetic in-memory evidence, not a production retention policy.

The reducer is not imported by application views. No DB, migration, network,
credential, callback handler or deletion effect was added. Next: pure issuance
of pending tickets from eligible decision steps, binding scope/generation/revision
and preventing ticket replacement while an operation is unresolved. Keep that
coordinator synthetic before connecting any real executor or persistence.

## Consequences and official sources

Kullanıcıya dört farklı işlem sunulması, tek belirsiz “sil” düğmesinden daha çok
durum yönetimi gerektirir. Bunun karşılığı yanlış durdurma/silme sözü vermemek ve
kurtarma sonrası istenmeyen tekrar yayın riskini azaltmaktır. Saklama süreleri,
gerçek işletme kimliği, alıcılar ve hukuki inceleme açık üretim kapılarıdır.

Kaynaklar 19 Ekim 2026'da kontrol edildi:

- [Google OAuth token iptali](https://developers.google.com/identity/protocols/oauth2/web-server#tokenrevoke): proje kapsamı/istemciler ve başarılı iptal yanıtı. Bu, reklam durumu veya veri imhası kanıtı değildir.
- [KVKK imha yönetmeliği](https://www.kvkk.gov.tr/Icerik/5441/KISISEL-VERILERIN-SILINMESI-YOK-EDILMESI-VEYA-ANONIM-HALE-GETIRILMESI-HAKKINDA-YONETMELIK): amaç/dayanak ve azami muhafaza envanteri, imha yöntemi, süre tablosu ve kayıtlar. Madde 7(3) imha işlem kayıtları için diğer yükümlülükler hariç en az üç yıl der; bu tüm reklam içeriğini üç yıl saklama talimatı değildir. Somut uygulanabilir süre ve talep takvimi yetkin incelemeyle eşlenmelidir.
- [Google kullanıcı verisi politikası](https://developers.google.com/terms/api-services-user-data-policy) ve [sayfa gereksinimleri](../product/public-identity-page-requirements.md): doğru veri açıklamaları; mevcut taslak sayfalar üretim politikası olarak sunulmaz.
