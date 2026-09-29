# Mevcut sistem denetimi ve altyapı hazırlık sırası

**Denetim tarihi:** 2026-09-29 13:38 (Europe/Istanbul)

**İncelenen kaynak:** `main` commit `60f39717fe3102fe764670e29023554368e6b2e3`; mevcut uygulama kaynakları ve [GrowthTwin ürün/hizmet blueprint'i](growthtwin-service-blueprint.md).
**Kapsam:** mevcut yazılımın yeni ürün yönüne uyumu ve kodlamadan önce gereken temel sınırlar. Bu belge yeni kanal, sağlayıcı, hizmet bedeli, garanti veya ürün kapsamı kararı vermez.

**Takip güncellemesi (2026-09-29):** Başlangıçtaki kod denetimi `60f3971` commit'inin snapshot'ıdır. Önceki takip güncellemesinde kaydedilen PR #108–#136 değişiklikleri korunur. PR #138 sağlayıcıdan bağımsız, tipli metrik sözleşmesini ekledi; PR #139 süreklilik belgelerini yeniledi; PR #140 tipli ve erişilemeyen metrikleri giriş yapılmış rapor ekranına bağladı ve planlanan kampanya tarihlerini açıkça etiketledi; PR #141 provider-neutral metrik anlamlarını belgeledi. PR #142 resmi Google Ads API v25 alanlarını Search adayı için eşledi; bu yalnızca dokümantasyon araştırmasıdır, hesap erişimi/API çağrısı içermedi. PR #143 erişilemeyen metrik durumlarını açık reason/provenance ile ayırdı. Main `6764c9c` commit'indedir; PR #143 zorunlu CI `36602784613` ve post-merge CI `36603066285` geçti. Giriş yapılmış rapor ekranı doğrulanmış bir kaynağa bağlı değildir ve gözlenmiş değer içermez. Search eşlemesinde reach desteklenmiyor, metin reklam etkileşimleri click'ten ayrı toplanmıyor ve dönüşüm teslim edilmiş lead anlamına gelmiyor. Gerçek reklamveren girdisi, hesap bağlantısı, yayın, harcama ve tahmin kapalıdır. Yedekleme/geri yükleme, rollback, staging E2E ve diğer yayın öncesi kontroller doğrulanmamıştır.

**Rapor kapsamı/tazelik araştırması (2026-09-29; belge PR incelemesinde):** Google'ın resmi rehberi segmented all-zero satırların ve metrik olmayan tarihlerin atlanabildiğini; clicks/impressions/cost için çoğu durumda saatlik freshness SLO, dönüşümlerde ise farklı gecikme ve olası sonradan düzeltmeler olduğunu belirtir. Bu bulgular bir fetch zamanını tamlık veya veri-güncellik kanıtı yapmaz. Ayrıntı ve kaynaklar [Google Search mapping](google-search-report-metric-mapping.md) içindedir. Henüz veri kapsamı/freshness evaluator'ı veya platform adapter'ı yoktur.

## 1. Mevcut sistemin kısa karşılığı

Şu anki web ürünü bir **sentetik kampanya deney prototipi**. Türkiye’de reklam hesabı bağlayıp kampanya yöneten ya da müşteri dokümanı alıp işleyen hazır bir SaaS değildir. Yerel geliştirme, Django/PostgreSQL ve GitHub CI temeli var; uygulama tarafındaki ürün/domain altyapısı yeni blueprint'in küçük bir parçası.

### Mevcut olan

- `apps/web/growthtwin/modules/content/planning.py`: HTTP ve veritabanından bağımsız `CampaignBrief`/`CampaignPlan` değerleri ve eksik brief alanları.
- `apps/web/growthtwin/modules/content/creative.py`: reklam iddiası uydurmayan, brief içeriğinden türetilmiş üç düzenlenebilir **sentetik metin** varyantı; üretken AI veya görsel/video üretimi değil.
- `apps/web/growthtwin/site/models.py`: anonim Django oturumuna bağlı `CampaignDraft`; amaç, brief, marka/kitle metni, integer günlük sınır, gün, metin varyantı ve kaynak hash'i. Bu kayıt geçici prototip içindir.
- `apps/web/growthtwin/modules/workspaces/models.py`: Django kullanıcı hesabına sahip tek kullanıcılı `Workspace`. `modules/assets/contracts.py` yalnız geçici saf durum/izin değerleri sunar; hiçbir asset'i saklamaz ve workspace erişim kontrolü yapmaz. Workspace onboarding/üyelik/rol akışı yok.
- Tek kampanyalı rehberli web ekranı; günlük harcama tavanı × gün aritmetiği; sabit mock pause ve sabit sentetik rapor. Formlar/çıktılar baştan sona kullanıcı hesabı veya platform verisiyle bağlı değil.
- Django/PostgreSQL yapılandırması, korumalı yerel geliştirme sırrı kurulumu, PostgreSQL CI, format/lint/dependency audit, migration check ve browser E2E içeren GitHub Actions. Son doğrulanan main CI `36574094362` başarılıydı.
- Onaylı Heroku staging var; sentetik veri amacıyla. Gerçek müşteri verisi, hesap bağlantısı, yayın veya ödeme için hazır sayılmaz. Staging son deploy revision/backup/restore/rollback durumu bu kod denetiminde yeniden doğrulanmadı.

### Yeni plana göre eksik olanlar

| Öncelik | Eksik sınır | Kodda görülen durum | Ürün etkisi ve hazırlık ihtiyacı |
|---|---|---|---|
| P0 | Hesap ve workspace sahipliği | Workspace sadece `owner` alanı içeriyor; session draft ayrı bir tabloda, üyelik ve tenant context yok. | Başka kullanıcının verisini görmeme, ekip rolleri ve workspace kapsamı, taslakların hesaba geçiş politikası. Var olan anonim taslakları kullanıcı workspace'ine otomatik taşımama kararı korunmalı. |
| P0 | Kampanya/medya-plan domain'i | Brief value'ları var, fakat durable Campaign/Plan, kanal/yerleşim/ad group ve plan varsayımı yok. Prototip günlük limitini para birimi olmadan pozitif tamsayı olarak tutuyor. | TRY/mikro-birim, kur ve platform harcaması ayrımı kararlaştırılmadan alanı gerçek fiyatmış gibi yeniden kullanma. Campaign tipi ve alanları ilk workflow seçimine göre belirlenmeli. |
| P0 | Kendi dosyası ve varlık kütüphanesi | Dosya yükleme, metin çıkarma, asset metadata/izin/provenance/sürüm/silme akışı yok. Storage basit `FileSystemStorage`; zararlı dosya taraması veya izole belge işleme yok. | Müşteri dokümanını almak güvenli değil; uploads önce sentetik/local test ve tehdit modeliyle tasarlanmalı. Orijinal korunmalı; AI/veri aktarımı görev başına kontrol edilmeli. |
| P0 | Fiyat/kredi | Kredi bakiyesi/ledger, bonus, tüketim, iade, paket satın alma veya GrowthTwin kampanya hizmet ücreti yok. | Owner fiyat çıpaları kredi maliyet defteri, idempotency ve tahsilattan ayrı ürün bedeli gerektirir; TRY/KDV/kur ve output başına maliyet çözülmeden ödeme/checkout yapılamaz. |
| P0 | Politika, consent ve harcama sınırı | PR #122 `approvals` içine saf sentetik önkoşul denetimi koydu; kanıtlar çağıran tarafından veriliyor. Yetkili kaynaktan doğrulama, kalıcı audit, atomik harcama rezervasyonu veya gerçek yayın gate'i yok. | Bu yerel sözleşme canlı eylem izni değildir. Reklamveren izni, kampanya/hesap toplam sınırı, zamanlama, içerik ve durdurma durumu her gerçek dış eylemden önce güvenilir sunucu kaynağından kontrol edilmelidir. |
| P1 | AI gateway ve çoklu içerik | `ai_gateway` boş paket; AI yok. Metin örnekleri deterministic. Görsel/video/document ingestion, sağlayıcı adapter'i, structured output ve kaynak izi yok. | Modality/provider seçilmedi. Önce saf sözleşmeler, synthetic benchmark ve sağlayıcı data/license şartları; provider implementasyonu sonra. |
| P1 | Reklam kanalı hesabı/yayın | `publishing` boş paket; OAuth/token vault/authorization/revoke/idempotency/outbox/reconciliation yok. | Türkiye API/app onayı gelmeden API bağlama/yayın yok. Harcama artırımı AI'ya bırakılamaz. |
| P1 | Lead yönlendirme | Reklamverenden GrowthTwin'e iş talebi ile reklamdan gelen lead için form/CRM/webhook/e-posta hedefi ya da kayıt modeli yok. | Amaç, veri alanı, alıcı, consent/role access, delivery/retry/audit ve silme netleşmeli. SMTP/CRM eklemek şu an erken ve ücretli olabilir. |
| P1 | Rapor, tahmin ve deney | `analytics` sağlayıcı paketi boş. PR #135/#140, yalnızca kullanıcı hesabına bağlı bir rapor kabuğu ve tipli erişilemeyen metrikler sunar; veri alımı, tahmin, kaynak güncelliği/tamlığı veya deney kaydı yoktur. | Platformların yerel metrik ve ilişkilendirme farkları kanallar arası kıyasları yanıltabilir. Kaynak ve dönem tamlığı doğrulanana kadar değerleri erişilemez tut; tahminleri gözlemden ayrı göster. ADR-0017 sağlayıcıdan bağımsız anlamsal kuralları kaydeder, platform/API doğrulaması değildir. |
| P2 | İşletim ve canlı dağıtım | Health endpoint DB'yi yokluyor ve Heroku revision env varsa gösteriyor; ancak bu denetimde staging revision/rollback/restore/E2E onaylanmadı. | Yerel/CI geliştirme temeli var; gerçek beta kapısı değil. Yeni cloud/add-on şart değil ve onaylanmış bütçeye dahil kabul edilmemeli. |

## 2. Temeller hazır mı?

| Hazırlık seviyesi | Durum |
|---|---|
| Yerel sentetik prototip geliştirme | **Hazır** — Windows + Python/Django/PostgreSQL çalışma akışı ve korumalı yerel secret bootstrap mevcut. |
| Kod kalitesi ve otomatik CI | **Hazır** — PR/main CI PostgreSQL üstünde uygulama kontrolleri ve browser E2E çalıştırıyor. Bu, ürün alanını veya prod hazır oluşunu kanıtlamaz. |
| Ürün/domain modelini genişletme | **Kısmen hazır** — `content` bağımsız değer tipleri ve boş adapter paketleri var; workspace ownership, campaign, asset, ledger, policy, publishing/reporting sözleşmeleri ve database modeli hazır değil. |
| Gerçek veri / gerçek müşteri dosyası | **Hazır değil** — amaç/alıcı/saklama/transfer, tenant yetkileri, upload güvenliği ve deletion/backup testleri eksik. |
| Reklam hesabı bağlama, yayın ve harcama | **Hazır değil** — platform/API app approval, server-side OAuth/token control, enforceable spend limits, idempotency, emergency stop ve reconciliation yok. |
| Ödeme/kredi satışı ve performans garantisi | **Hazır değil** — kredi hareket kaydı, fiyat/TRY/KDV/payment/provider cost, refund contract/unit economics yok. |

“Alt yapı hazır olsun” için ek ücretli altyapı açmak gerekmiyor. Var olan monolit/CI yerel kurucu işlere yeter. Yeni external service ancak ihtiyacı, veri sınıfı, sözleşmesi, maliyeti ve kapatma yolu belli olunca değerlendirilir.

## 3. Güvenli teknik hazırlık sırası

### Foundation 0 — Ürün sınırı / no-regret mimari

1. Blueprint karar defterindeki ilk hizmet/flow/lead alıcısı/provider/TRY pricing kararlarını ayrı ayrı göster; bilinmeyeni modelde kesinleştirme.
2. Mevcut `site.CampaignDraft`'ı açıkça session-owned sentetik prototipte tut. Authenticated/Workspace domain'iyle aynı Campaign tablosuymuş gibi kullanma; otomatik import/backfill yapma.
3. Modüller için application contracts, dependency direction, typed money/unit/currency/metric vocabulary ve `source/simulation/confidence/as_of` metadata yaklaşımını belirle. Gerçek campaign/asset/payment tablosunu seçimden önce kurma.

**Tamamlanma:** ARCHITECTURE/ADR içinde sahiplik, modül sınırı ve prototip-domain ayrımı net; varsayılan hiçbir yol gerçek dış etkiye veya ücretli provider'a gitmez.

### Foundation 1 — Identity, workspace ve tenant authorization

- Önce authentication/signup/owner-only veya ekip-member gereksinimi seçilir; sonra Workspace üyeliği/rol modeli tasarlanır.
- Her service/read/write çağrısı user/workspace context'i açıkça alır; ID ile kayıt yüklemede server-side access check uygulanır. Browser'dan gelen tenant ID tek başına yetki değildir.
- Kampanya/content verisi saklandığında hangi workspace'e ait olduğu zorunlu; deactivation, export, deletion ve audit kaydı belirlenir.
- **Kabul:** sentetik çoklu-user senaryosunda kullanıcı A, kullanıcı B'nin workspace/campaign/asset/report kaydını okuyamaz/değiştiremez; eski anonymous campaign'ler otomatik taşınmaz.

### Foundation 2 — Marka, kendi dosyası ve yaratıcı sürümü

- Brand facts ve uploaded asset, orijinal dosyadan ayrılır; file hash/type/size/source/license/consent/owner ve sürüm ilişkileri tutulur.
- Extension/MIME/signature/size limits, safe parser/OCR isolation, malware checking, prompt injection handling, PII flag/redaction ve failed processing states tasarlanır.
- Storage lokasyonu seçilmeden upload API açılmaz; gerekiyorsa local-only prototype güvenli dosya alanı kullanır, public media root kullanmaz.
- **Kabul:** sentetik dosyanın orijinali silinmez/üzerine yazılmaz; generated/adapted variant source/version/failure state ile ilişkilidir; user deletes asset and derivative according to retention contract.

### Foundation 3 — Campaign, plan, credits/fees ve policy contracts

- Campaign planı; objective/definition, audience/geography, dates, channels/placements, media budget/currency/caps, creative versions, consent, statuses ve action history'yi modüllere ayırır.
- Money integer minor units + ISO currency veya eşdeğer kesin aritmetik biçim; platform media, GrowthTwin service fee, credit purchase, tax ve FX kalemleri kesin ayrıdır.
- Credit ledger append-only events (grant, bonus, hold/reserve, consume, release/refund, adjustment), idempotency ve balance derivation ile tasarlanır. Fiyat/output-unit hesabı henüz açık olduğundan charge simulator/mock kalır.
- Deterministic policy check input/output policy version, rule, reason, affected creative/campaign version, timestamp içerir; fail closed.
- **Kabul:** pre-purchase total fiyat dökümü doğru para birimleriyle hesaplanır, duplicate request çift kredi düşmez, budget/consent eksikse external action authorized olmaz. Bunlar sentetik/fake adapter seviyesinde doğrulanır.

### Foundation 4 — Provider/channel/report/experiment ports

- `ai_gateway`, `publishing`, `analytics`, `approvals` ve ihtiyaç çıkarsa `assets`, `pricing`, `campaigns` modülleri resmi interface sahibi olur; platform payload/token logic core domain'e sızmaz.
- Tahmin ve rapor için metric code/name/source/definition, currency, date window, attribution, fetched-at, completeness, estimated-vs-observed ve confidence metadata gerekir.
- Lead delivery (form/CRM/webhook/e-mail), retry/deduplication/deletion ve audit destination contract'ı ancak ilk lead destination seçilince tanımlanır.
- Experiment kaydı hypothesis, one-variable definition, success/guard metrics, budget caps, sample/time window, platform experiment ID, result sufficiency ve approved scale action içerir.
- **Kabul:** interface contract'ları fake adapter ile test edilebilir; gerçek token, endpoint veya spend hiçbir automated testte kullanılmaz. Her adapter approval/feature map olmadan live status alamaz.

### Foundation 5 — Gerçek kanal/veri/ödeme için ayrı readiness

Product readiness, privacy/legal review, platform account/API approval, test advertiser sandbox, secure secret/token store, staging E2E, backup/restore, rollback, incident stop/revoke, support, price/provider unit economics ve ayrı owner approval'ı birlikte tamamlanmadan real data/paid publish açılmaz. Bu liste [ürün blueprint'inin readiness gate'i](growthtwin-service-blueprint.md#12-veri-güvenlik-ve-gerçek-veriye-geçiş-kapısı) ile tutarlı tutulur.

## 4. Şimdilik değiştirilmemesi gerekenler

- Kullanılan Django/PostgreSQL modüler monolit; bu denetimde yeni queue, object-storage service, vector DB, AI provider veya production host gereksinimi gösterilmedi.
- Mevcut anonymous demo drafts; onlar sentetik ve kısa süreli bir UX prototip sınırı. Yeni user-owned domain campaign'lere sessizce dönüştürülmez.
- Türkiye platform aday listesi; bir reklam hesabının ülkede bulunması, API SaaS erişimi/lead retrieval/forecast veya placement onayı değildir.
- Simulated report/pause, gerçek yayın veya analiz olarak gösterilmez.
- Yeni fiyat, sonuç/iade garantisi, kredi output rate, ilk sektör/hedef/kanal sahibi kararı yerine geçecek teknik varsayımlar yapılmaz.

## 5. Sonraki uygulama sırası

ADR-0008 ilk sentetik workflow ve teknik kanal adayını seçti. PR #110–#117 workspace sahipliği, kampanya taslağı ve provider-free planın ilk yerel kapsamını; PR #120–#121 ise dosya işlemi olmayan asset sözleşmesini oluşturdu. Bu kararlar gerçek veriye geçiş izni değildir.

PR #122, `approvals` içine sentetik eylemler için saf politika önkoşul denetimi ekledi: açık izin, hedef/kanal/içerik durumu, kampanya ve hesap toplam tavanları, uçuş tarihleri ve durdurma durumu. Bilinmeyen girdi kapalı kalıyor; sonuç yalnız yerel sentetik gözden geçirmeye uygunluk bildiriyor ve canlı yayına izin vermiyor. Sonraki küçük yerel adım, her değerlendirme için kaynağı ve gözlem zamanını açıklayan metadata sözleşmesidir. Bu metadata da çağıran tarafından sağlanacak ve doğrulanmamış sayılacaktır; kimlik doğrulama, güncellik garantisi, atomik bütçe rezervasyonu, kalıcı denetim veya dağıtım adapter'ı sunmaz. Güvenilir kanıt, denetim kaydı ve canlı readiness ayrı tasarım kapılarıdır.
