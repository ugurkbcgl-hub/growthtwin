# Açık kaynak aday araştırması — 23 Ekim 2026

Bu kayıt resmî upstream README/lisans/dokümanları ve 23 Ekim 2026 canlı GitHub API metadatasına dayanır. Hiçbir aday bu araştırmada kurulmadı, çalıştırılmadı veya Yaparo ile test edilmedi. `pushed_at` sürüm tarihi veya başarılı bakım kanıtı değildir. Seçim öncesi sabit sürümün bağımlılıkları, açık güvenlik kayıtları ve gerçek test kapsamı ayrıca incelenir. Yıldız sayısı puan ölçütü değildir.

Durumlar: **ilk deneme** = bir sonraki uygun ürün diliminde kıyaslanacak; **koşullu** = gereksinim kanıtlanınca; **izle** = bugün temel yapılmayacak; **kapsam dışı** = hedefi karşılamıyor veya kullanım koşulları net değil. Bunlar üretime kabul kararı değildir.

## 1. Editör, yükleme ve medya

| Repo / kaynak | Lisans ve 23 Ekim bakım sinyali | Yaparo kararı ve gerekçe |
|---|---|---|
| [Fabric.js](https://github.com/fabricjs/fabric.js) | MIT; arşivli değil; push 22 Ekim 2026. [README](https://raw.githubusercontent.com/fabricjs/fabric.js/master/README.md) | **İlk deneme.** Tuval, yazı, resim, dönüşüm ve export; kendi araç çubuğumuz/erişilebilirlik/sürüm yapımız gerekir. Hareketli master yerine sabit paket denenir. |
| [Konva](https://github.com/konvajs/konva) | MIT; arşivli değil; push 23 Ekim; 10.9.0 sürümü 15 Ekim. [Kayıt önerisi](https://konvajs.org/docs/data_and_serialization/Best_Practices.html) | **Alternatif.** Fabric seçimini karşılayan yedek; ikisini bir arada kullanma. Kendi uygulama durumunu saklama yaklaşımı taşınabilirlik için uygun. |
| [Uppy](https://github.com/transloadit/uppy) | MIT; arşivli değil; push 23 Ekim. [README](https://raw.githubusercontent.com/transloadit/uppy/main/README.md) | **İlk deneme.** Django sayfasında kendi endpoint'imize dosya yükleme; ücretli Transloadit işleme zorunlu değil. Uzak hesaplardan ithal ayrı sunucu/izin ister. |
| [Pillow](https://github.com/python-pillow/Pillow) | MIT-CMU; 13.0.0 sürümü 16 Ekim 2026. [Lisans](https://raw.githubusercontent.com/python-pillow/Pillow/main/LICENSE) | **İlk deneme.** Thumbnail/normalizasyon ve resim sınırları. Dosya güvenliği ve piksel/bellek sınırlaması ayrıca kurulacak. |
| [vue-fabric-editor](https://github.com/ikuaitu/vue-fabric-editor) | MIT; arşivli değil; push 21 Temmuz. [Paket](https://raw.githubusercontent.com/ikuaitu/vue-fabric-editor/main/package.json) Fabric 5.3/Vite 4; [README](https://raw.githubusercontent.com/ikuaitu/vue-fabric-editor/main/README-en.md) | **Hazır editör karşılaştırma adayı.** Araçları hazır olabilir; eski bağımlılık yükseltmesi/Türkçe UX/upstream yama maliyeti ölçülür. Ücretli backend/batch yetenekleri MIT frontend'e dahil varsayılmaz. |
| [react-design-editor](https://github.com/salgum1114/react-design-editor) | MIT; arşivli değil; push 11 Ekim. [Paket](https://raw.githubusercontent.com/salgum1114/react-design-editor/master/package.json) 0.2.1, Fabric 7.4, React 18–19 | **Hazır editör karşılaştırma adayı.** Küçük React adası mümkün; daha geniş bağımlılık yüzeyi var. Test script'i bulunması gerçek test yeterliliği sayılmaz. |
| [Tiptap](https://github.com/ueberdosis/tiptap) | Çekirdek MIT; push 23 Ekim; v3.32.0, 13 Ekim. [README](https://raw.githubusercontent.com/ueberdosis/tiptap/main/README.md) | **Koşullu.** Uzun biçimli marka rehberi/brief için; kısa reklam başlığına gereksiz. Pro/collaboration/AI özelliklerinin hepsi ücretsiz çekirdekte değildir. |
| [Docling](https://github.com/docling-project/docling) | Kod MIT; model lisansları ayrı; arşivli değil; push 23 Ekim. [Lisans](https://github.com/docling-project/docling/blob/main/LICENSE) | **İkinci materyal dilimi adayı.** PDF/DOCX'ten yapılandırılmış bilgi; çıktı kaynak sayfa/paragrafla bağlanır. Tüm model/formatlar aynı anda açılmaz. |
| [FFmpeg](https://github.com/FFmpeg/FFmpeg) | Push 23 Ekim; çoğunluk LGPL 2.1+; GPL/nonfree derleme seçenekleri sonucu değiştirir. [Lisans](https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/LICENSE.md) | **Video aşamasında.** Kesme, crop, yazı/altyazı/ses/export için izole işçi. Kesin binary/codec lisansı, kaynak kullanımı ve zaman sınırı incelenir. |
| [OpenCut](https://github.com/OpenCut-app/OpenCut) | MIT; push 24 Eylül. [README](https://raw.githubusercontent.com/OpenCut-app/OpenCut/main/README.md) yeniden yazım ve gelecek API/plugin işlerini bildiriyor; [classic](https://github.com/OpenCut-app/opencut-classic) arşivli, son push 17 Mayıs | **İzle.** Tam video editörü için güncel ve tamamlanmış temel kabul edilmez. |
| [Remotion](https://github.com/remotion-dev/remotion) | Özel lisans; push 23 Ekim; v4.0.538, 22 Ekim. [Lisans](https://raw.githubusercontent.com/remotion-dev/remotion/main/LICENSE.md) | **Koşullu ticari aday.** Şablon video üretimi yararlı olabilir; ücretsiz kullanım kuruluş büyüklüğü/kullanım biçimine bağlı. Koşulsuz açık kaynak temel sayılmaz. |
| [IMG.LY background-removal-js](https://github.com/imgly/background-removal-js) | AGPL-3.0; son push 18 Temmuz 2025. [README](https://raw.githubusercontent.com/imgly/background-removal-js/main/README.md) | **Özellik bazında izle.** Kod ve ağırlık hakkı, model indirme/telemetri ve bakım incelenir; bütün CreativeEditor SDK yerine geçmez. |
| [Penpot](https://github.com/penpot/penpot) | MPL-2.0; arşivli değil; push 23 Ekim. [README](https://raw.githubusercontent.com/penpot/penpot/develop/README.md) | **İç tasarım için koşullu.** Kendi sunucunda tasarım aracı olabilir; ilk müşteri editörüne bütün platformu gömmek fazla işletim getirir. |

Hazır editör denemesi aynı işi karşılaştırır: sentetik logo/fotoğraf → Türkçe başlık → crop/katman/undo → save/reopen → PNG. Kendi şema adaptörü, erişilebilirlik, bundle boyutu, font doğruluğu, güvenlik ve bir üst sürüme geçiş maliyeti değerlendirilir. İlk denemede Fabric ve **tek** hazır editör yeterlidir; tüm adaylar kurulmaz.

## 2. AI, kimlik, iş yürütme ve bakım

| Repo / kaynak | Lisans ve bakım sinyali | Karar |
|---|---|---|
| [PydanticAI](https://github.com/pydantic/pydantic-ai) | MIT; arşivli değil; push 23 Ekim. [README](https://raw.githubusercontent.com/pydantic/pydantic-ai/main/README.md) | **İlk AI denemesi.** Tipli çıktı/sağlayıcı bileşeni, mevcut doğrudan adaptörle kıyaslanır. Hosted Logfire/Gateway zorunlu yapılmaz; ajan shell/yayın yetkisi verilmez. |
| [LangGraph](https://github.com/langchain-ai/langgraph) | MIT; arşivli değil; push 23 Ekim. [README](https://raw.githubusercontent.com/langchain-ai/langgraph/main/README.md) | **Koşullu.** Dallanma/kalıcı devam ihtiyacı basit iş akışını aşarsa. Başlangıçta ikinci AI çatısı olmaz. |
| [Haystack](https://github.com/deepset-ai/haystack) | Apache-2.0; arşivli değil; push 23 Ekim. [README](https://raw.githubusercontent.com/deepset-ai/haystack/main/README.md) | **Koşullu.** Büyük belge kümesi/arama kanıtlanınca; küçük marka kartı için RAG/vector altyapısı kurulmaz. Telemetri ayarı ayrıca incelenir. |
| [LiteLLM](https://github.com/BerriAI/litellm) | Çekirdek MIT, enterprise ayrı; push 23 Ekim. [Kesin lisans sınırı](https://raw.githubusercontent.com/BerriAI/litellm/main/LICENSE) | **Koşullu.** Çok sağlayıcı/dağıtım olursa taşıma katmanı; Yaparo kredi defterinin veya veri politikasının sahibi olmaz. |
| [Celery](https://github.com/celery/celery) | [BSD-3-Clause](https://raw.githubusercontent.com/celery/celery/main/LICENSE); arşivli değil; push 22 Ekim. GitHub NOASSERTION sınıflandırması lisans yok demek değil | **İlk kuyruk adayı.** Async ürün dilimi gerektiğinde; worker/broker/maliyet ve [Windows desteği sınırı](https://raw.githubusercontent.com/celery/celery/main/README.rst) dikkate alınır. |
| [Dramatiq](https://github.com/Bogdanp/dramatiq) | [LGPL-3.0](https://github.com/Bogdanp/dramatiq/blob/master/COPYING.LESSER); push 15 Ekim | **Alternatif.** Celery ile aynı anda eklenmez; daha küçük iş kuyruğu ihtiyacında karşılaştırılır. |
| [Temporal](https://github.com/temporalio/temporal) | MIT sunucu; push 23 Ekim; [self-host işletimi](https://docs.temporal.io/self-hosted-guide) | **Sonraya bırak.** Uzun süreli karmaşık işlerde güçlü aday; başlangıç işletim maliyeti yüksek. Cloud zorunlu değil. |
| [django-allauth](https://github.com/pennersr/django-allauth) | [MIT](https://raw.githubusercontent.com/pennersr/django-allauth/main/LICENSE); GitHub mirror push 20 Ekim; kanonik [Codeberg](https://codeberg.org/allauth/django-allauth/) | **Kayıt/hesap dilimi adayı.** Tenant yetkileri ve reklam hesabı izinleri Yaparo'da kalır. |
| [dj-stripe](https://github.com/dj-stripe/dj-stripe) | MIT; arşivli değil; push 14 Ekim | **Seçilmedi.** Stripe eşleme aracı; Türkiye işletme kabulü veya sağlayıcıdan bağımsız kredi defteri değildir. |
| [django-money](https://github.com/django-money/django-money) | GitHub arşivli; README [Codeberg'e taşınmayı](https://codeberg.org/django-money/django-money) bildiriyor | **Gerekirse incele.** Arşivli diye terk edildiği söylenmez; cüzdan değildir. Mevcut tam sayı para birimi alt birimleri korunabilir. |
| [Renovate](https://github.com/renovatebot/renovate) | AGPL-3.0; arşivli değil; push 23 Ekim; [self-host yolu](https://docs.renovatebot.com/examples/self-hosting/) | **Bakım aracı adayı.** Güncelleme PR'ları için; üretim runtime bağımlılığı olmaz. Henüz otomasyon kurulmadı. |

## 3. Bütün ürün çatallama ve kanal seçenekleri

| Repo / kaynak | Doğrulanmış kapsam / lisans / bakım | Yaparo sonucu |
|---|---|---|
| [Postiz](https://github.com/gitroomhq/postiz-app) | Sosyal gönderi planlama/yayın/analiz; AGPL-3.0; push 23 Ekim, arşivli değil. [README](https://github.com/gitroomhq/postiz-app/blob/main/README.md) | Organik sosyal hizmet için sonraki aday. Ücretli reklam, kredi, hard spend ve satış ölçümü temelinin yerine geçmez. Next/Nest/Temporal ek işletim getirir; API ayrımı otomatik lisans muafiyeti değildir. |
| [Mixpost Lite](https://github.com/inovector/mixpost) | Lite MIT, PHP/Laravel/Vue; son push 16 Mart 2026; arşivli değil. [README](https://raw.githubusercontent.com/inovector/mixpost/main/README.md), [ticari sürüm koşulları](https://mixpost.app/terms-of-use) | Lite/Pro/Enterprise özellik ve lisansları ayrılır. Ücretli sürüm özellikleri MIT kaynakta varsayılmaz; bütün ürüne geçiş önerilmiyor. |
| [Dify](https://github.com/langgenius/dify) | [Değiştirilmiş Apache koşulları](https://raw.githubusercontent.com/langgenius/dify/main/LICENSE): çok kiracılı çalışma alanı ve marka koşulları | Müşterilere ayrı workspace sağlanan ürün çekirdeği için lisans değerlendirmesi gerekir. Hazır görsel AI araçları uğruna Yaparo domain'i taşınmaz. |
| [n8n](https://github.com/n8n-io/n8n) | [Sustainable Use / enterprise sınırı](https://raw.githubusercontent.com/n8n-io/n8n/master/LICENSE.md) | İç otomasyon kullanımından müşteri hizmetine gömme sonucuna atlanmaz. İlk ürün çekirdeği seçilmedi. |
| [Activepieces](https://github.com/activepieces/activepieces) | Community MIT; [enterprise ayrı](https://github.com/activepieces/activepieces/blob/main/packages/ee/LICENSE); push 23 Ekim; arşivli değil | Gelecekte iç süreç/bağlantı için incelenebilir. Embedded/multi-tenant yeteneklerin Community'de ve lisans kapsamında olduğu ayrıca kanıtlanmalı. |
| [OpenFrame AI](https://github.com/tapankumarpatro/openframe-ai) | Video reklam ajanları/canvas; Sustainable Use ve enterprise; son push 1 Temmuz | Kullanıcı ihtiyacına yakın görünse de ticari yeniden sunum kısıtları var. UI/iş fikri araştırması; kodu Yaparo'ya kopyalama veya temel seçimi yok. |
| [AdSim](https://github.com/sasankgamini/AdSim) | Sentetik persona/simülasyon; demo veri; son push 29 Mart; API metadatasında lisans yok | Kapsam dışı. Simülasyon sonuçları müşteri tahmini/gerçek performans kanıtı olamaz; kod kullanımı için lisans hakkı da doğrulanmadı. |
| [Google Ads Python](https://github.com/googleads/google-ads-python) | Resmî istemci, Apache-2.0; push 22 Ekim; arşivli değil | Google adaptöründe mevcut uygulamayla karşılaştır; izin/onay/niyet/tekrar önleme kuralları korunur. |
| [Meta Python Business SDK](https://github.com/facebook/facebook-python-business-sdk) | Push 21 Eylül; arşivli değil; [lisans](https://raw.githubusercontent.com/facebook/facebook-python-business-sdk/main/LICENSE) Facebook API'leriyle kullanıma özgü | Meta aşamasında resmî aday; MIT/Apache diye etiketlenmez. Uygulama erişimi ayrı gerekir. |
| [iyzipay-python](https://github.com/iyzico/iyzipay-python) | MIT; arşivli değil; son push 18 Şubat 2026 | Ödeme aşamasında Python 3.13/aktif API/3DS/webhook bakım incelemesi gerekir. Paket varlığı ticari kabul ve güncel uyumluluk kanıtı değildir. |

## 4. Karar yöntemi ve eksik araştırma

Zorunlu geçiş koşulları: kullanım lisansı uygun; müşteri verisi/anahtarı bizim sınırlarımızda; veri/export çıkışı mevcut; güvenlik/yama yolu anlaşılır; gerekli kullanım hosted lisans anahtarına bağlı değil; mevcut teknolojiyle uygulanabilir; kullanıcı çıktısı somut. Koşulu geçmeyen adaya popülerlik puanı eklenerek kabul verilmez.

Geçen adaylar aynı örnekte karşılaştırılır: müşteri görevini tamamlama, geliştirme/uyarlama işi, Türkçe/erişilebilirlik, toplam işletim maliyeti, bakım/upgrade ve taşınabilirlik. Sayısal puan denemeden önce uydurulmaz. İlk editör kararı için kaynak/bağımlılık lisans incelemesi ve sürüm pin'i Y02'de tamamlanacak; entegrasyon/performans/güvenlik denemesi Y03–Y06'da.

Kod lisansı, model ağırlığı, şablon/font/stok materyal hakkı, platform API koşulu ve ödeme/AI ticari sözleşmesi farklıdır. SBOM/yasal bildirimler exact sürüm ve kullanılan dosyalar üzerinden tutulur. Lisans yorumları kullanım mimarisi kesinleşmeden hukuki onay sayılmaz.

Araştırmada seçilmeyen bir proje sonsuza kadar reddedilmiş değildir. Kanonik repo taşınması, güvenlik olayı, lisans veya özellik değişimi yeniden değerlendirme tetikler. Son push tarihleri yukarıdaki denetimin anlık kayıtlarıdır; kurulumdan önce yeniden okunur.

## 5. İlk uygulama incelemesi — 23 Ekim 2026, 21:25 (+03)

Y02/Y03 henüz tamamlanmadı. Yerel Node 24.11.1 ve npm 11.6.2 doğrulandı.
Npm kayıt servisi Fabric **7.4.0**, MIT ve dağıtım bütünlük bilgisini döndürdü;
paket kurulmadı, çalışma kanıtı elde edilmedi.

Hazır aday [react-design-editor v0.2.1](https://github.com/salgum1114/react-design-editor/tree/b1a09dd700dbba95c6770ed91043d1228afaeea4)
özel geçici klasöre alındı; MIT lisansı kaynakta doğrulandı. Yayınlanan paket
Canvas/handler bileşenlerini sunuyor; tam araç çubuğu ve özellik panelleri demo
kaynağında. Dolayısıyla tam editörü doğrudan takıp kullanma varsayımı doğru değil.
Repo `.npmrc` ayarları lockfile üretimini kapatıyor ve legacy peer çözümüne izin
veriyor. Sabit sürümlü, yeniden üretilebilir bağımlılık kurulumu ayrıca incelenmeli.
`--ignore-scripts` ile başlayan kurulum kullanım eşiği devri nedeniyle kesildi;
kurulum başarıyla tamamlanmadı, build ve güvenlik taraması çalıştırılmadı.
Bu bulgular adayın elenmesi veya seçilmesi için yeterli değil.

Mevcut Yaparo kaynak eşlemesi: `workspaces/models.py` sahibi olan çalışma alanını;
`campaigns/models.py` marka adı ve metin yaratıcı sürümlerini tutuyor.
`assets/contracts.py` yalnız saf durum/izin sözleşmeleri içeriyor. Yeniden
kullanılabilir marka kiti, dosya deposu ve grafik sahne henüz bu modellerde yok.
Görsel deneme Google onay/gönderim kayıtlarından ayrı tutulmalı. Ayrıntılı Y01
haritası ve aynı görevde ölçülen karşılaştırma sonraki uygulamanın parçasıdır.


## 6. Devam eden oturumun çalışma kanıtı

Kullanıcı kullanım kontrolünü kaldırıp uygulamaya devam edilmesini istedi.
Fabric yerel denemesi artık çalışıyor; hazır adayın kurulumu da tamamlandı.
Önceki kesilmiş kurulum kaydı tarihsel olarak korunur. Güncel sürüm, lisans,
tarama, derleme ve tarayıcı sonuçları [editör denemesi raporunda](creative-editor-spike-results.md).
Hazır adayın bildirim derlemesi ve güvenlik kapıları geçmedi; tarayıcıda eş görev
kanıtı yok. Karşılaştırma tamamlandı veya üretim paketi seçildi diye yorumlanmamalı.
