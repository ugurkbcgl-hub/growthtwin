# GrowthTwin — ürün ve hizmet blueprint'i

**Durum:** Araştırma ve planlama taslağı; kullanıcı gereksinimlerini ve doğrulanmış kaynakları bir araya getirir. Buradaki öneriler, ayrıca “karar” diye işaretlenmedikçe nihai ticari, hukuki veya teknik karar değildir.

**Güncelleme:** 2026-09-29 (Europe/Istanbul)  
**Ürün amacı:** Türkiye'de reklam vermek isteyen birey ve kuruluşların reklam ihtiyacını anlamaktan içerik üretimi/iyileştirmesine, kampanya kurulumuna, yayına, performans raporuna ve güvenli optimizasyona kadar işini tek ve kolay kullanılan bir web ürününde tamamlaması.

## İlk dar ürün dilimi için karar (2026-09-29)

Kullanıcının karar yetkisini devretmesi üzerine, aşağıdaki seçim yerel sentetik ürün geliştirmesi için kabul edilmiştir; gerçek hesap/API erişimi, veri işleme, ödeme, reklam yayını veya reklam bütçesi izni değildir. Ayrıntılı teknik kapsam [ADR-0008](../adr/0008-first-mvp-google-search-leads.md) içindedir.

- **İlk senaryo:** Şehir içinde hizmet veren, düzenlemeye tabi olmayan bir işletmenin teklif/iletişim talebi toplaması. Prototip örneği sentetik Ankara ev bakım/onarım işletmesidir. Türkiye'de herkesin reklam verebilmesi uzun vadeli ürün hedefidir; bu tek workflow pazar veya sektör sınırı değildir.
- **İlk kanal adayı:** Google Ads Search. Kullanıcıların mevcut arama niyetiyle yerel hizmet araması, şehir/bölge hedeflemesi, Search kampanyasının API ile yönetilebilmesi ve keyword-plan forecast metrikleri bu akışa doğrudan uyar. Platformun GrowthTwin API kullanım izni henüz yoktur; Google Ads API test hesapları gerçek reklam sunmaz ve canlı metrik üretmez.
- **İlk dönüşüm yolu:** Reklamverenin kendi web sitesine tıklama. Lead formu, ham lead içe aktarma, CRM/e-posta/SMS teslimi ilk dilimde yoktur. Başarı, ancak reklamveren web sitesinde uygun şekilde kurulmuş dönüşüm ölçümü varsa Google'ın toplu dönüşüm metriğiyle gösterilir. Ölçüm yoksa lead sayısı hesaplanamaz; tahmin edilmez.
- **İlk içerik:** GrowthTwin üretimi düzenlenebilir metin başlık/açıklama ve arama terimi grupları. Müşteri dosya yükleme, görsel/video üretimi, kredi tahsilatı ve ücretli AI sağlayıcısı sonraki adımlardır; sentetik sahte veriden öteye geçmez.
- **İlk bütçe kuralı:** yalnız tarih aralığı belirli kampanya toplam bütçesi adayı. Google Ads Search bunu destekler. Günlük ortalama bütçede günlük limitin iki katına kadar aşım olabildiğinden günlük ortalama bütçe, kullanıcının katı toplam tavanının yerine gösterilmez. Canlı yayından önce API/hesapta toplam sınırın ve kampanya dışı hesap harcamasının kontrol edilebilirliği doğrulanmalıdır.
- **İlk ölçüm:** Kaynak ve zaman damgasıyla arama gösterimi, tıklama ve maliyet forecast'i; kampanya sonrası gerçek gösterim/tıklama/maliyet ve erişilebiliyorsa toplu dönüşüm. Forecast satış/lead garantisi değildir. Herhangi bir metrik kaynağı yoksa “hesaplanamıyor” gösterilir.
- **Sıralama:** Google Search ilk teknik aday; Meta ikinci kanal adayı (görsel erişim/yaratıcı çeşitlilik güçlü, ancak diğer işletmelerin hesaplarını yönetmek ve lead verisi okumak Meta erişim/inceleme şartlarına bağlı); TikTok üçüncü araştırma adayı (kısa video/kreatif testi için, Türkiye özelindeki GrowthTwin API ve lead sync yolu kanıtlanana kadar). Bu sıralama resmî API erişimi sağlandı anlamına gelmez.
- **Canlılık sınırı:** ilk yerel dikey dilimde yalnız sentetik campaign kayıtları ve bir sahte Google adapter'ı kullanılacak. Henüz adapter uygulanmış değil. Üretim API'si, gerçek müşteri/lead verisi, reklam hesabı, ödeme, publish veya harcama yoktur. Gerçek kanala geçiş blueprint'in readiness gate'i ve ayrı açık karara tabidir.

Bu öneri, Türkiye'ye özgü hukuki inceleme, ürün pazar doğrulaması, hesap/API onayı veya ticari fiyat kararı değildir. İlgili resmî teknik kaynaklar: [Google Search kampanyaları](https://developers.google.com/google-ads/api/docs/campaigns/search-campaigns/getting-started), [şehir/bölge hedefleme](https://developers.google.com/google-ads/api/docs/targeting/location-targeting), [keyword forecast](https://developers.google.com/google-ads/api/docs/keyword-planning/generate-forecast-metrics), [tarih aralıklı kampanya bütçesi](https://developers.google.com/google-ads/api/docs/campaigns/budgets/overview), [API erişim seviyeleri](https://developers.google.com/google-ads/api/docs/api-policy/access-levels), [test hesapları](https://developers.google.com/google-ads/api/docs/best-practices/test-accounts), [responsive search ad metin sınırları](https://support.google.com/google-ads/answer/7684791?hl=en), [Google bütçe aşımı](https://support.google.com/google-ads/answer/1704424?hl=en), [Meta Marketing API koleksiyonu](https://www.postman.com/meta/facebook-marketing-api/documentation/0zr4mes/facebook-marketing-api-mapi) ve [Meta lead izin referansı](https://developers.facebook.com/docs/permissions/reference/).

## 1. Ürün vaadi ve çalışma ilkeleri

GrowthTwin, sadece reklam metni yazan bir araç veya reklam ajansını taklit eden bir sohbet botu olmayacak. Hedef; yaratıcı üretim, medya planlama, kanal hesabı ve kampanya işlemleri, ölçüm ve öğrenme döngüsünü tek bir müşteri deneyiminde birleştiren bir reklam platformudur. Omneky uzun vadeli kabiliyet karşılaştırma noktasıdır; bütün rakip özellikleri veya her kanalı ilk sürüme alma taahhüdü değildir.

Sistemin desteklemesi gereken iki başlama biçimi:

1. **GrowthTwin ile üret:** Müşteri amacı, marka bilgisi ve brief verir; sistem strateji önerir, çoklu içerik üretir ve revizyona açar. İçerik üretimi kredi bakiyesinden ücretlenir.
2. **Kendi içeriğinle reklam ver:** Müşteri kendi metin, görsel, video, sunum ve marka dokümanını yükler; sistem bunları inceleyip kampanya formatına uyarlama/iyileştirme önerir. Mevcut dosya hiçbir zaman sessizce üzerine yazılmaz. Dosyanın reklam materyali olarak kullanımı ayrıca fiyatlandırılır; yalnızca yükleme, analiz, dönüştürme veya reklam lisansı ücretleri kararlaştırıldıktan sonra uygulanır.

Her iki yolda da sistem; öneri, tahmin, üretim, kullanıcı onayı, hesap yetkilendirmesi, yayın, ölçüm ve optimizasyon aşamalarını anlaşılır biçimde gösterir. Yeni kullanıcı basit rehberli akıştan ilerler; profesyonel kullanıcı aynı planın kanal, hedefleme, yerleşim, teklif, kreatif sürüm, ölçüm penceresi ve deney ayarlarını açabilir. Basit görünüm gelişmiş bilgiyi gizlemek yerine aşamalı gösterir.

**Kırmızı çizgiler:**

- Türkiye ilk pazardır; sağlık/klinik yalnızca olası dikeylerden biridir. Ürün bir sektöre sabitlenmez.
- Gerçek kişi, reklamveren, müşteri adayı (lead), reklam hesabı, ödeme, yayın ve harcama; sistemin tüm hazırlık ve güvenlik kapıları geçilmeden kullanılmaz. Bu çalışmada veri yalnızca sentetiktir.
- Müşteri reklam platformuna giden medya harcamasını GrowthTwin hizmet/üretim ücretinden ayrı görür. Platform tahminleri sonuç garantisi değildir.
- Yapay zekâ içerik önerir ve dönüştürür. Harcama sınırı, izin, durum geçişi ve yayın yetkisini deterministik sunucu kuralları uygular. Sistem izin/kanıt/limit yoksa durur.
- Müşteriyi elde tutma, birikmiş değer ve iyi hizmetle sağlanır; dosyayı dışa aktarmayı engelleme, yanıltıcı abonelik veya yapay kilitlenme kullanılmaz.

## 2. Kapsam: müşteriye sunulacak hizmetler

| Hizmet alanı | Müşterinin ihtiyacı | Üründeki karşılığı | İlk sürüm sınırı |
|---|---|---|---|
| Reklam talebi ve strateji | “Ne satıyorum, kime, hangi sonuç için reklam vereyim?” | Serbest dilli kısa brief, eksik bilgi soruları, amaç ve ölçülebilir başarı tanımı, strateji/kanal önerisi | Tek doğrulanmış kampanya yolculuğu; strateji gerekçeli ve değiştirilebilir |
| Marka ve kaynak arşivi | Belgelerimden, eski kampanyalarımdan ve mevcut içeriklerimden yararlan | Dosya/bağlantı alımı, marka bilgisi ve kaynak pasajlarını çıkarma, izin/kaynak bilgisi, sürümlü içerik kütüphanesi | Desteklenecek uzantı ve boyut sınırları dosya güvenliği tasarımında belirlenecek |
| Kreatif üretim ve iyileştirme | Yeni reklam üretmek, mevcut içeriği geliştirmek/formatlamak/çoğaltmak | Metin, görsel ve kısa video taslakları; platform oran/uzunluk varyantları; kaynak/iddia gösterimi; düzenleme ve sürüm geçmişi | Üretim formatı ve AI aracı testlerle seçilecek; yayın öncesi kullanıcıya görünür kontrol |
| Reklam uyumu ve kalite | Yanlış iddia, eksik açıklama, telif veya platform reddi riskini azalt | Kural tabanlı alan/format kontrolleri, kanıt isteyen iddia işaretleri, dikey/kanal politika kontrolleri, açıklanabilir engel | Otomatik kontrol hukuki onay yerine geçmez; belirsizlikte duraklat |
| Medya planı ve hesaplayıcı | Bütçeyle hangi kanalda ne kadar erişim/sonuç alabileceğini gör | Bütçeyi kanal/hedef/yerleşim/gün/adet ve platform ücretlerine ayır; aralık, varsayım, kaynağın tarihi ve belirsizliği göster | Veri olmayan metrikte sayı uydurma; tahmin yoksa “henüz tahmin edilemiyor” de |
| Kampanya kurulumu ve yayın | Hesabıma bağlanıp belirlediğim sınırda kampanya çalıştır | Hesap sahipliği/OAuth, yetki özeti, son kontrol, kullanıcı onayı, limitli yayın, durdurma ve işlem kaydı | Bir kanal/tek iş akışıyla başla; gerçek hesaba geçiş ayrıca readiness onayı ister |
| Lead teslimi | Reklamdan gelen talep doğru yere, güvenli biçimde ulaşsın | Kanala göre lead formu/CRM/webhook/e-posta teslimi, izin/amaç, tekrar deneme, durum kaydı, erişim ve silme | Önce reklamverene gelen iş talebi ile reklamdan doğan lead birbirinden ayrıştırılacak; ilk hedef belirlenmedi |
| Rapor ve analiz | Bir reklamı ayrıntılı, tüm reklamları toplu anla | Hedef/gerçekleşen, kanal, kreatif sürümü, harcama, gösterim, erişim, tıklama, dönüşüm/lead, atıf penceresi, açıklama ve dışa aktarma | Yalnızca bağlı kanaldan doğrulanabilen metrik gösterilir; tanımlar kanal bazında belirtilir |
| Deney ve optimizasyon | Farklı kreatifleri test et, iyiyi kontrollü yaygınlaştır | Hipotez, tek değişken, bütçe/örneklem, test süresi, sonuç güveni, onaylı kazananı kademeli artırma | API/kanal deney yetenekleriyle sınırla; yetersiz kanıtta kazanan ilan etme |
| Hesap, ekip ve destek | Profil, marka, kullanıcı/rol, faturalar, izin ve kampanyaları yönet | Workspace, rol/erişim, hesap bağlantısı/iptal, kullanım dökümü, destek ve hesap dışa aktarma/silme | Tenant izolasyonu, veri ömrü ve izin tasarımı tamamlanmadan gerçek veri yok |

## 3. Uçtan uca müşteri yolculuğu

1. **Başlangıç ve profil:** Kullanıcı birey/işletme/kurum türünü, marka adını, ülke/şehri, sektörünü ve ihtiyacını anlatır. Ürün sektör sorularını ihtiyaca göre açar; klinik gibi tek bir dikey varsaymaz.
2. **Hedef ve brief:** Hedef (ör. bilinirlik, trafik, satış, uygulama kurulumu, lead), teklif/ürün, hedef kitle, hizmet bölgesi, dönem, kullanıcı tarafından belirlenen bütçe tavanı ve başarı metriği netleşir. Kullanıcı bilmediğinde rehberli öneri alır; gerekli veri eksikse sistem tahminde bulunmak yerine tek tek sorar.
3. **Belge ve içerik:** Müşteri dosya yükleyebilir veya bağlanmış markalı kaynaktan seçim yapabilir. Sistem kaynağı, çıkarılan bilgiyi, dosya sahibini/kullanım hakkı beyanını ve seçili AI sağlayıcısına gönderilip gönderilmeyeceğini gösterir. Özel/kişisel veri tespit edilirse redaksiyon veya kullanmama seçeneği sunar. Orijinal korunur.
4. **Strateji ve kanal önerisi:** Sistem, kampanya amacıyla uyumlu Türkiye'de kullanılabilir kanalları, nedenleri, gereksinimleri, erişim/API durumunu ve alternatifleri sunar. “Türkiye'de reklam platformu var” ile “GrowthTwin burada onaylı API'ye sahip” ayrı etiketlenir.
5. **Plan ve ön izleme hesaplayıcısı:** Kullanıcı medya bütçesini, tarih aralığını ve kanal dağılımını değiştirir. Kanal bazında erişim/gösterim/tıklama/sonuç öngörü aralığı ve hesap yöntemi, veri tarihi, hedef kitle boyutu, gösterim sıklığı, kur/döviz/VAT varsayımı, GrowthTwin ücretleri, platformun doğrudan tahsilatı ve hariç kalemler gösterilir. Satın almadan detay açılabilir, senaryo kaydedilebilir/karşılaştırılabilir. Bu adım satın alma veya yayın değildir.
6. **Kreatif seçimi:** Müşteri GrowthTwin üretimini veya kendi kaynağını seçer. Aynı brief'ten alternatif başlık, metin, görsel/video taslağı, CTA ve kanal formatı görür. Hangi kaynakların kullanıldığı ve hangi iddianın onay beklediği görünür. Metin/görsel/video ücret tahmini kredi cinsinden gösterilir; kullanıcı başlamadan önce onaylar.
7. **Üretim, revizyon ve kontrol:** Her üretim ayrı kredi hareketi ve sürümdür. Müşteri editörle düzeltir, yeniden üretmeden önce mevcut düzenlemelerin korunacağı açıklanır. Marka/kanal/uyum kontrolü çalışır; başarısız veya belirsiz üretim yayın kuyruğuna geçmez.
8. **Satın alma ve izin:** Özet; üretim kredisi, kampanya/hizmet ücreti, seçilmiş platformlara ödenecek medya bütçesi, vergiler/kur, tahsilat zamanı, iptal/iade kuralları ve harcama tavanını ayrı satırlar hâlinde gösterir. Kullanıcı her reklam hesabı, kanal, içerik ve harcama için açık onay verir.
9. **Kurulum ve yayın:** Yetki kapsamı okunabilir gösterilir; token yalnızca sunucu tarafında güvenli saklanır, geri alma/bağlantıyı kesme ve “acil durdur” vardır. Son kontrol reklamı ve alıcı sayfasını kanala özel kurallardan geçirir. İdempotent eylem kaydı, zamanlama, limit ve hata/geri alma yolu kurulur. Herhangi bir tutarsızlıkta yayın yapılmaz.
10. **Canlı takip ve rapor:** Kullanıcı kampanya sayfasında durumu, hedef-gerçekleşen, kalan tahmini/harcanabilir bütçeyi, kanal/kreatif kırılımını, son güncelleme zamanını, veri kaynağını ve metrik açıklamalarını görür. Toplu rapor tüm kampanyaları birleştirir; platformlar arası metrikler aynıymış gibi normalize edilmez.
11. **Test, öğrenme, kademeli büyütme:** Başlangıçta başarı hipotezi ve metriği tanımlanır. Deney hücreleri kullanıcı tarafından onaylanan bütçe/kanal tavanı içinde kurulur. Yeterli süre/örneklem ve platformun deney sonucu olmadan sistem “kazanan” demez. Kazanan içeriğe bütçe artışı otomatik değil, önceden belirlenmiş artış sınırlarına ve müşterinin yetkisine bağlıdır.
12. **Durdurma, itiraz, silme ve tekrar kullanım:** Müşteri tek tuşla kampanyayı durdurur/hesap bağlantısını iptal eder, kayıtlarını dışa aktarır, kaynak dosyasını siler veya hesabı kapatır. Marka kütüphanesi ve geçmiş raporlar (müşterinin seçtiği saklama süresi içinde) sonraki kampanyada değer katar.

## 4. Deneyim modeli: yeni başlayan ve profesyonel

| Yeni başlayan için varsayılan | Profesyonel görünümde açılabilen ayrıntı |
|---|---|
| “Ne elde etmek istiyorsunuz?” dili ve örnek hedefler | Objective/optimization event, attribution window, conversion source |
| 3–5 gerekli soruyla plan | Hedefleme, yerleşim, teklif stratejisi, hariç tutma, frekans, cihaz ve bölge |
| Her terim için kısa açıklama ve önerilen varsayılan | Kanal, kampanya grubu, reklam, kreatif varyant hiyerarşisi |
| Toplam fiyat, medya bütçesi ve tahmin aralığı | Kanal başına günlük/ömür boyu bütçe, ücret/kur/VAT ve tahmin varsayımı |
| Otomatik kontroller ve tek onay ekranı | Kreatif test planı, eşik, test hücreleri, olay verisi ve API durumu |
| “Şu an çalışıyor / şu bilgi eksik / şu nedenle durdu” durumu | Hata kodu, platform yanıtı, audit trail, yeniden deneme ve rapor kaynağı |

İlk kullanımda sade görünüm varsayılan olur. Profesyonel görünüm aynı veri modelini kullanır; ayrı ve çelişen kampanya kuralları oluşturmaz. Her iki deneyimde de yayın, bütçe artırımı, lead verisi ve bağlantı izni için açık, bağlama özgü onay zorunludur.

## 5. Fiyatlandırma ve hesaplayıcı

### 5.1 Kararlaştırılmış fiyatlama niyeti

- İçerik üretimi krediyle fiyatlanacak; medya/reklam harcaması ayrı fiyatlanacak.
- İlk müşteriye, özellikle üretimi deneyimletecek ücretsiz başlangıç kredileri verilecek.
- Kullanıcının örnek verdiği paket çıpaları: **100 kredi = 10 USD**; **1.000 kredi satın alımında %20 bonusla 1.200 kredi = 100 USD**. Buradan nominal bir kredi değeri USD 0,10; bonus pakette efektif değer USD 0,0833/kredi olarak çıkar. Bunlar owner örneği/niyeti olarak kayıtlıdır; TRY fiyatı, vergi, ödeme akışı ve yayımlanacak kesin paket henüz belirlenmedi.
- Reklam/kampanya hizmeti fiyatı hedef ve kapsam büyüdükçe değişebilir; medya harcamasına eklenmez ve önceden açık hesaplanır.

### 5.2 Henüz kararlaştırılmayan ticari ayrıntılar

- Bir metin varyantı, görsel, video saniyesi/formatı, yeniden boyutlandırma, doküman okuma ve düzenlemenin kredi maliyeti; sağlayıcı maliyeti ve tekrar üretim politikası.
- USD referansından Türkiye'de TRY liste fiyatına kur kaynağı, fiyatın ne sıklıkla güncelleneceği, KDV/fatura, kart/ödeme sağlayıcısı/komisyon, iade ve kullanılmamış kredi süresi.
- Hediye kredinin miktarı, son kullanımı, kötüye kullanım önlemi ve kazanılan kredinin satın alınan krediye göre sırası.
- Kampanya hizmet bedelinin sabit/plan bazlı/yüzdesel bileşimi; minimum tutar; kanala göre servis; başarısız yayın ve platform harcamasının sorumluluğu.
- Reklamverenin medya bütçesini platforma doğrudan ödemesi mi, platform hesabında kendisinin harcaması mı; GrowthTwin üstünden medya tahsilatı ayrı bir finansal/operasyonel karardır.

**Fiyat ekranı kabul ölçütü:** Her ücretin kimin tarafından, ne zaman tahsil edildiği; vergiler/kur; dahil olan işler; kredi tüketim ön izlemesi; kullanılmayan kredinin durumu; iptal/iade şartı; tahminin ve hedefin garanti olmadığı; platforma gidecek medya parasının ayrılığı satın alma öncesi görülebilir olmalı. Fiyat hesaplayıcısı satın alma zorunluluğu doğurmamalı.

### 5.3 Ücret/iade garantisi önerisi — karar bekliyor

Kullanıcının ilkesi “müşterimiz sonuç almadığında GrowthTwin'in kazanmış görünmemesi” yönündedir. Bu, üründe görünür adalet ve sorumluluk hedefidir; ancak reklam etkileşimi/dönüşüm satış, teklif, açılış sayfası, sezonsallık, rakipler, hesap durumu ve platform açık artırması gibi GrowthTwin'in kontrol etmediği etkenlere bağlıdır. Bu nedenle “istenen etkileşim kesin sağlanır” şeklinde genel vaat, kanıt, atıf ve maliyet planı olmadan henüz güvenli bir ürün sözü değildir.

Önerilen yol:

1. **İlk aşamada:** Yayın kurulumunun doğru yapılması, onaylı bütçeyi aşmaması, belirlenen raporların zamanında sunulması gibi GrowthTwin'in kontrol edebildiği hizmet taahhütleri tanımlansın.
2. **Sonuç denemeleri:** Sentetik prototipten sonra ancak küçük, sözleşmeli ve ölçüm/atıf tanımı yapılmış pilotta performans ölçümü toplansın. Platformun iade ettiği medya harcaması dışındaki platform bütçesi GrowthTwin tarafından otomatik iade ediliyormuş gibi vaat edilmesin.
3. **Garanti kararı:** KPI (ör. doğrulanabilir gösterim, tıklama, nitelikli lead), hedef, atıf ve sayım penceresi, hariç durumlar, müşteri girdisi/sayfa/hizmet hazır oluşu, kanal kesintisi, sahte trafik, maksimum iade, rezerv ve tüketici reklam hukuku incelemesi yazılı kararlaştırılsın. Başlangıçta koşullu servis kredisi/iade seçeneği değerlendirilebilir; sonuç garantisi ancak kanıt ve birim ekonomi gösterirse açılır.

Bu öneri kullanıcı tarafından henüz kabul edilmiş veya hukuk/mali müşavir tarafından incelenmiş sayılmaz.

## 6. Türkiye kanalları: reklam kullanılabilirliği ve entegrasyon kapısı

Platformda reklam hesabı açabilmek, belli bir hedefleme/yerleşimi kullanabilmek, geliştirici API'sine yetki almak, API'yi müşterilere SaaS olarak sunabilmek ve Türkiye'de tüm kampanya hedeflerini desteklemek ayrı doğrulamalardır. Kaynaklar mevcut bir olasılık gösterir, GrowthTwin'in API erişimini/uygunluğunu kanıtlamaz.

### 6.1 Ön araştırma sonucu ve durum

| Kanal/ad network | Türkiye için doğrulanmış ilk bulgu | GrowthTwin açısından sonucu / açık doğrulama |
|---|---|---|
| Google Ads / YouTube | Google Ads lokasyon hedefleme sunar. YouTube için Google Ads API ReachPlanService bütçe/hedefe göre erişim ve gösterim tahmini verebilir; ancak yalnızca allowlist'e alınan hesaplara açıktır, ayrıca temsilci değerlendirmesi/lisans koşulları vardır. | Aday. Ads API developer-token erişimi ve ReachPlanService allowlist'ini ayrı sor; doğrudan arayüzün tahminini varsayılan ürün API'si sayma. |
| Meta Ads (Facebook/Instagram/Messenger/diğer yerleşimler) | Global Ads/Marketing API hizmeti ve reklam ürünleri mevcut. 2026'da Meta, Marketing API Access Tier ve uygulama inceleme koşullarını değiştirdi. Bu araştırmada GrowthTwin'in Türkiye hesapları için uygunluğu, API izni ve ilgili kampanya kapsamı doğrulanmadı. | Büyük aday, **entegrasyon doğrulaması açık**. Geliştirici uygulaması/izin incelemesi ve hesap bağlantısını araştır; “hazır” diye sunma. |
| TikTok Ads | Türkiye, self-serve Business Center reklam hesabı oluşturma listesinde. Yerleşim/hedefleme ülkeye ve kayıtlı hesap ülkesine bağlı; Türkiye kendi kayıtlı hesabı için desteklenen hedef pazarlardan. TikTok Ads kampanya hedefleri erişim, trafik, lead, dönüşüm vb. içerir. | Aday. TikTok for Business geliştirici uygulaması/Marketing API erişim ve onay, her kampanya amacı/placement/rapor metriğini ayrıca doğrula. |
| X Ads | X self-serve Ads ülkeleri listesinde Türkiye var. X A/B test kılavuzu kreatif testi ve test metriği/raporlamasını açıklar. | Aday ama ürün önceliği, API partner şartı, kısıtlı sektör politikası, dil/faturalama ve hesap yetkisi ayrıca doğrulanmalı. |
| LinkedIn Ads | Marketing API, LinkedIn tarafından incelenen program; API ve Marketing Data kullanım hakkı önceden onaya bağlı. | Profesyonel/B2B hizmet adayı. MDP başvurusu, privacy/security incelemesi, lead sync, müşteri/veri kullanım şartları ilk iş akışına göre doğrulanmalı. |
| Snapchat Ads | Bu blueprint araştırmasında güncel Türkiye self-serve ve Ads API erişimi yeterli resmi kaynakla doğrulanmadı. | Araştırma kuyruğu; doğrulanana kadar “desteklenen” olarak gösterme. |
| Pinterest Ads | Bu blueprint araştırmasında Türkiye hesap/faturalama, hedefleme ve API durumunu yeterli resmi kaynakla doğrulamadık. | Araştırma kuyruğu; önce Türkiye'de uygunluk ve API/partner şartı. |
| Microsoft Ads, Reddit Ads, Yandex ve yerel yayıncı/marketplace ağları | Türkiye reklam envanteri, yerel müşteri hesabı, API/SaaS partner yetkisi, rapor ve reklam politikaları bu incelemede tamamlanmadı. | Talep ve API kanıtı geldikçe puanla; isim listesi gerçek entegrasyon vaadi değildir. |

### 6.2 Kanal seçim puan kartı

Her aday aynı puanlama (1–5) ve kaynak ekiyle karşılaştırılmalı; puansız/kanıtsız kalem “bilinmiyor” olarak kalmalı:

1. Türkiye hedef kitlesinde erişim ve müşteri segmentleri.
2. Self-serve hesap açma, Türkiye tüzel/gerçek kişi faturalaması ve hedef ülke eşleşmesi.
3. API ürünü, OAuth izin kapsamı, app/partner review, müşteriye SaaS olarak sunum izni ve onay süresi.
4. Kampanya hedefi, format, yerleşim, şehir/yaş/dil hedefleme ve sektör politikası.
5. API ile kreatif oluşturma/güncelleme, yayın, durdurma, bütçe limiti ve idempotent geri alma.
6. Tahmin API'si, erişim/gösterim/tıklama/lead/satış rapor kapsamı, atıf penceresi ve veri dışa aktarımı.
7. Lead formu/Lead Sync/Webhook/CRM bağlantısı, consent alanları ve delivery/retry.
8. Para birimi, platformun tahsil ettiği medya harcaması, vergi/fatura, asgari bütçe ve kur riski.
9. Kreatif gereksinimi, reddedilme/itiraz süreci, destek kalitesi, SLA, API limitleri/versiyon değişim riski.
10. Müşteri için ürün değerine karşı geliştirme, onay, işletim ve bakım maliyeti.

Seçim ağırlıklarını kullanıcı araştırması sonrası ayarla. API erişimi mümkün değilse adayı ilk canlı destinasyon yapma. Kanal bağlantısı yokken hesaplayıcı gerçek platform tahmini yerine sentetik prototip/varsayımlı senaryo olarak açıkça etiketlenmeli.

### 6.3 Öncelikli kanal karşılaştırması (araştırma, nihai seçim değil)

Pazar payı/erişim üstünlüğü sıralaması yapılmadı: yerel reklamverenden kullanım, CPM/CPC, dönüşüm maliyeti, lead kalitesi veya platforma göre müşteri sayısı verisi toplanmadı. Self-serve ülke listesi ve dokümandaki özellikler Türkiye'de ekonomik olduklarını veya GrowthTwin API'sine açık olduklarını tek başına kanıtlamaz. Bu nedenle sahte 1–5 puan yerine kanıt ve eksik kanıt yazılır.

| Kanal | Sektörden bağımsız ürün işi | Türkiye/erişim kanıtı | API, tahmin ve ölçüm kanıtı | Öncelik ve karar eşiği |
|---|---|---|---|---|
| **Google Ads / Search ve YouTube** | Search ile çözüm/ürün arama niyetini; YouTube ile video/erişim hedefini karşılamak | Türkiye hedeflemesi mevcut. API Test erişimi yalnız test hesaplarında; Explorer/Basic/Standard ve permissible-use izinleri kademeli. Standard başvurusu uygulama incelemesi içerir. | Kampanya ölçümleri raporlanabilir. YouTube/Video Partners ReachPlanService özel allowlist, temsilci ve veri lisansı ister; Search tahmini ile video erişim tahmini aynı API/ürün değildir. | **P0 — ilk API fizibilite kontrolü.** Test erişimi, üretim token/izin, Search reporting/keyword planning, şehir hedefi ve müşterilere tool-as-a-service yetkisini doğrula. Arama niyeti ölçülebilirliği güçlü bir ürün hipotezi; tahmin kapsamı/erişimi açık. |
| **Meta Ads (Facebook/Instagram/Reels/Lead Ads)** | Görsel/video üretip sosyal yerleşimlerde deneme; yerleşik lead formu veya website dönüşümü | Meta'nın ürün sayfası Facebook/Instagram Reels ve Advantage yerleşimlerini gösteriyor. Bu taramada Türkiye hesap ülkesi/faturalama uygunluğu ve GrowthTwin entegrasyon izni resmi kaynaklarla kapanmadı. | Marketing API Access Tier/app review şartları 2026'da değişti. Türkiye için lead retrieval izni, tahmin endpoint'i ve rapor kapsamı bu taramada doğrulanmadı. | **P0 — ülke ve izin kanıtını hemen ara.** Business portfolio, app review/Marketing API Access Tier, gerekli permission ve Ads Insights/Lead Ads/yayın akışını test hesabında doğrula. Görsel üretim/lead senaryosuna ürün uyumu yüksek olabilir; API kapısı hâlâ açık. |
| **TikTok Ads** | Kısa video hook/format varyantı ve kontrollü deney; erişim, trafik, lead veya dönüşüm | Türkiye self-serve Business Center reklam hesabı açma listesinde. Hedef lokasyon/yerleşim kayıtlı hesabın ülkesine ve kampanya özelliğine bağlı. | API for Business dokümanları campaign/creative/audience, lead retrieval/webhook ve raporlama desteğini tarif ediyor. GrowthTwin developer app/izin onayı Türkiye için doğrulanmış değil. Yerleşik split test tek değişkenli; en az 7 gün öneriliyor. | **P1 — kreatif test alternatifi.** App/API erişimi, test hesabı, Türkçe creative specs, lead/report API ve TR placement uygunluğunu doğrula. Video üretim maliyeti ve müşteri talebi kanıtlanmadan ilk hizmet vaadi yapma. |
| **X Ads** | Seçilmiş topluluk/konu çevresinde metin, görsel ve video kampanyası/test | Self-serve reklamveren hesabı ülkeleri arasında Türkiye var. Hesap doğrulama, reklam kalite politikası, içerik/dil ve hassas sektör koşulları geçerli. | Ads Manager A/B testi görsel/video/metin/CTA varyantlarını ve Bayesian “win chance” raporunu destekliyor. Ads API feature erişimi ve SaaS izin kapsamı bu taramada doğrulanmadı. | **P2 — segmente bağlı.** Ads API access, Türkçe/sensitive category kuralları, ölçüm/faturalama ve kullanıcı talebi araştırılmalı. İlk genel MVP için seçme gerekçesi henüz yok. |
| **LinkedIn Ads** | B2B hizmet, şirket/karar verici ve profesyonel kitleye lead | Campaign Manager self-serve ürün; konum ve mesleki nitelik hedefleri sunuyor. Türkiye hesap/billing ayrıntısı bu turda ayrıca belgelenmedi. | Marketing API vetted program; API ve Marketing Data için developer/app vetting ve privacy/security review gerekir. Campaign/Lead Gen Forms/Lead Sync izin kapsamı başvuruya göre doğrulanmalı. | **P1 sadece B2B senaryosu seçilirse; aksi P2.** Türkiye audience büyüklüğü, API onayı, Lead Sync ve maliyet/lead kalite araştırılmadan genel ürüne alma. |

#### İnceleme sırası ve dar MVP hipotezi

1. **İlk iki aday:** Google Search ve Meta'yı aynı “Türkiye'deki bir hizmet işletmesi, seçtiği şehirde teklif/randevu talebi almak istiyor” *sektörsüz sentetik akışında* karşılaştır. Bu, dikey seçimi değildir; brief → mesaj/creative → yerel hedef → ölçülebilir lead → teslim → rapor döngüsünü inceleyen örnektir. Google Search aktif arama niyetini, Meta görsel kreatif/yerleşik lead formunu sınayan hipotezler olur. Gerçek kullanıcı/API kanıtı olmadan seçim yapılmış sayılmaz.
2. **Creative test alternatifi:** TikTok'u aynı örnek için video varyantı ve test seçeneği olarak kıyasla; gerekli Marketing API yetkisi ve ülke/placement doğrulanırsa değerlendirmeye al.
3. **Özel segmentler:** B2B talebi doğrulanırsa LinkedIn'i Google ile tekrar puanla; X'i müşteri segmenti/ürün araştırması bunu desteklerse ekle.
4. **Daha sonraki araştırma:** Snapchat, Pinterest, Microsoft, Yandex ve yerel yayıncı/marketplace ağı için Türkiye reklamveren uygunluğu + partner/API + hedef/rapor + gerçek müşteri talebi kanıtı gerekir.

Bu sıra “Türkiye'de en yaygın/başarılı kanal” iddiası değildir. Son seçim öncesinde (a) API/izin ve test kanıtı, (b) aynı hedef/bütçe ile platformların kendi planner/forecast çıktısı ve metric definitions, (c) müşteri segmenti kullanım araştırması, (d) lead teslimi/kalite ve maliyet ölçümü gerekir.

### 6.4 Tek karşılaştırma senaryosu: şehir bazlı hizmet talebi

**Senaryo:** dikey/kişi adı uydurulmayan sentetik profil: “Türkiye'deki bir hizmet işletmesi, seçtiği şehirde yeni müşteri/teklif talebi istiyor.” Bu senaryo sağlık, finans veya başka kontrollü bir dikey seçmez; ilk müşteri segmenti araştırmayla belirlenir.

- Amaç: nitelikli talep/lead (platform conversion event'i henüz seçilmedi).
- Bölge: kullanıcı şehir seçer; ilgili hesap/ülke için gerçek location targeting API ile doğrulanır.
- Dönem: örnek 14 gün, yalnızca hesaplayıcı tasarım parametresi.
- Sentetik brüt medya bütçesi: **5.000 TRY**, örnek dağılım Google Search **3.000 TRY**, Meta **2.000 TRY**. Oran strateji önerisi veya piyasa benchmark'ı değildir.
- Ortalama günlük dağılım: Google 3.000 / 14 = **214,29 TRY/gün**; Meta 2.000 / 14 = **142,86 TRY/gün**. Gerçek platform harcaması günlük sabit tutarla aynı olmayabilir; platformun günlük/ömür boyu tavanları ayrıca görünmelidir.
- Tahmin: seçilen hesap/şehir için güvenilir forecast kaynağı bağlanmadığından erişim, gösterim, tıklama, CPC/CPM, lead ve dönüşüm değerleri **HESAPLANMIYOR**. Kullanıcıya sahte sayılar/placeholder verilmez.
- GrowthTwin hizmet bedeli **S** (fiyat kararı açık); üretim tüketimi **K kredi** (iş başına kredi maliyeti açık). GrowthTwin bedeli = `S + credit_price(K)`. Medya bütçesi buna dahil değildir.
- Toplam örnek nakit: platformlara ayrı ödenecek medya **5.000 TRY** + GrowthTwin `S` + `K` üretim kredisinin bedeli + ödeme/kur/vergi kalemleri (henüz tarifelenmedi). Kim tahsil eder, hangi para birimi ve hangi tarihte gösterilir, ayrı ödeme kararıdır.
- Satın almadan önce kullanıcı kanal ekler/çıkarır, bütçe oranını değiştirir, senaryoyu kaydeder ve raporu dışa aktarır; hesap bağlama, ödeme veya yayın oluşmaz.

#### Hesaplayıcı gösterim kuralı

Kanalın resmi tahmin API/planlayıcısı erişilebilir ve bu kullanıma yetkiliyse, tahminin yanında ülke/hesap/hedef/format/tarih, veri tarihi, metrik tanımı ve varsayım gösterilir. Aksi durumda sadece yöntemi açıklayan taslak bulunur. Geçmiş kampanya verisi ancak kullanıcı izni ve yeterli örneklemle, tarih/hesap bağlamı belirtilerek kullanılabilir.

```text
gösterim tahmini = medya bütçesi ÷ varsayılan/ölçülen CPM × 1.000
tıklama tahmini = gösterim tahmini × varsayılan/ölçülen CTR
lead tahmini = tıklama tahmini × varsayılan/ölçülen landing-page conversion rate
lead maliyeti = ilgili medya payı ÷ gerçekleşen veya açıkça tahmin olan lead adedi
```

CPM, CTR ve dönüşüm oranı kaynak/tarih/güven bilgisi olmadan sayı üretmez. Platformlar arası tekil erişim, kanal erişimlerini toplamakla elde edilmiş gibi sunulmaz.

## 7. Medya hesaplayıcısı ve raporlama gereksinimi

### Girdiler

- Amaç ve optimizasyon olayı; tanımlı başarı metriği ve dönüşüm kaynağı.
- Hizmet/ürünün konumu ve hedefleme kısıtları; reklam kategorisine göre yaş/hedef kısıtı.
- Platform, kampanya türü, format/yerleşim, tarih/süre, medya bütçesi ve kullanıcı sınırları.
- Varsa platformun resmi tahmin API'si; yoksa geçmiş hesap verisi (ancak uygun izin ve yeterli örneklemle) veya yalnızca açık etiketli kıyas senaryosu.
- GrowthTwin içerik üretim kredisi, kampanya/servis ücreti, platform medya maliyeti ve vergi/kurun gösterim/ödeme ayrımı.

### Ekran çıktısı

- Kanal/hedef/yerleşim/ad grubu bazında medya bütçesi ve günlük/ömür boyu sınır.
- Tahmin edilen erişim (tekil erişim ve gösterim ayrımı), gösterim sıklığı; destek varsa tıklama, CTR, CPC/CPM, dönüşüm/lead ve maliyet aralığı.
- Tahmin kaynağı, hangi hesap/ülke/senaryo, çekilme tarihi, model/veri aralığı ve varsayımlar.
- Düşük/orta/yüksek senaryo veya platformun confidence/forecast aralığı; tam sayı gibi kesinlik izlenimi verme.
- Çapraz kanal toplam erişim yalnızca ortak/uygun deduplikasyon verisi varsa; toplanabilir tekil erişim varsayılmaz.
- “Gerçek sonuç değişebilir; tahmin garanti değildir” açıklaması; henüz API/hesap/veri yoksa değer uydurmayan mesaj.
- Medya bütçesi GrowthTwin ücreti değildir; platform ücreti, vergi, döviz kur varsayımı, üretim kredisi ve hizmet ücreti ayrı kalem.

### Satın alma öncesi ayrıntı

Kullanıcı reklam satın almadan kanal bazında hedefleme, yerleşim, amaç, tahmin, bütçe, GrowthTwin ücreti, doğrudan platform ödemesi, kampanya dönemi, başarı ölçümü, risk/kısıt ve iptal/iade koşullarını açıp inceleyebilmelidir. “Önizle” veya senaryo kaydetmek hesap bağlamaz, para çekmez, kampanya oluşturmaz ve veri paylaşmaz.

## 8. İçerik ve AI kabiliyet planı

### Modality bazında işler

| Modality/araç | Kullanım | Ürün kontrolü | Seçim için gerekli kanıt |
|---|---|---|---|
| Metin | Brief soruları, strateji seçenekleri, başlık/açıklama/CTA, platform varyantı, düzenleme, çeviri/ton uyarlama | Kaynak gerçekleri, marka tonu, iddia/tıbbi/finansal/sözleşmesel sakınca, karakter limiti, şema ve tekrar üretim sürümü | Sentetik Türkiye reklam senaryoları; marka sadakati, doğruluk, yasak iddia, Türkçe kalitesi, structured output, gecikme ve maliyet |
| Görsel | Statik reklam, mevcut varlıkta düzenleme, farklı oran/yerleşime uyarlama, ürün/brand kompozisyonu | Kaynak/marka varlığının kullanım hakkı, insan/ünlü rızası, logo/doğru ürün, görüntü üzerindeki yazı, AI karakter/dijital benzerlik açıklaması | Lisans/veri şartı, bölgesel hizmet, işleme/retention, logo ve metin kalitesi, düzenlenebilirlik, kredi maliyeti |
| Video | Kısa video/storyboard, sahne/senaryo, dikey oran, altyazı/voiceover, mevcut videodan varyant | Kullanılan müzik/ses/görüntü hakkı, yüz/ses rızası, deepfake/dijital replica kontrolü, reklam açıklaması, süre/aspect/kanal politikası | Lisans ve ticari kullanım, gerçek kişi/voice hakları, tutarlılık, ses altyazı, süre/kalite, gecikme ve maliyet |
| Dokümandan içerik | PDF/Doc/PPT/görsel ve mevcut kampanya tarama; ürün bilgisi, FAQ ve onaylı iddia çıkarımı | Kaynak sayfa/alıntı, extraction confidence, prompt injection savunması, PII/secret tespiti, tenant izolasyonu, paylaşım öncesi redaksiyon | Dosya tipleri, OCR, zararlı içerik izolasyonu, silme/retention, dış sağlayıcı aktarımına açık izin |

AI sağlayıcıları adaydır; bu belge yeni bir sağlayıcı seçmez. `AI_PROVIDERS.md`'deki mevcut değerlendirmeler sentetik ve tek/az sayıda örneğe dayalı olup üretim seçimi değildir. Üretim geçidi sağlayıcıdan bağımsız olmalı; model çıktısı onaysız yayın/harcama/limit değiştirememelidir. İçerik/kaynaklar sağlayıcıya gönderilecekse görev, veri sınıfı, lokasyon, saklama/eğitim şartı, sözleşme, hukuki aktarım yolu ve kullanıcı izni önceden doğrulanmalı.

### Kendi içeriğini koruma ve geliştirme

- Yüklenen orijinal her zaman değiştirilemez kaynak sürüm olarak kalır.
- Sistemden üretilen veya düzenlenen her çıktı yeni sürüm olup hangi brief, dosya, model/araç, istem/ayar ve insan düzenlemesinden geldiği izlenir.
- Müşteri içeriğin sahibiyim/kullanım yetkim var beyanını verir; üçüncü taraf logo, görsel, influencer, yüz/ses ve müzik hakları kullanım öncesi çözülür.
- Müşterinin yüklediği dosyayı AI'a gönderme varsayılan olarak kapalı veya görev başına açık bilgilendirmeli onaya bağlanmalı; bu değer ürün ve hukuk incelemesiyle kesinleşecek.
- İçe aktarılan talimatlar güvenilmeyen kaynak kabul edilir; dosyanın içindeki “sistem komutu” çalışma davranışını veya güvenlik sınırlarını değiştiremez.

## 9. Reklam stratejisi, çoklu kreatif ve kazananı büyütme

Strateji katmanı sadece “daha fazla reklam göster” demez; brief ve gözlenen kanıta göre şu playbook'ları öneri olarak sunar: hedef/teklif eşleşmesi; marka/ürün farkı; yeni kitle ve müşteri aşaması; kanal-format-kreatif eşleşmesi; hook/başlık/CTA çeşitleri; yerel hizmet alanı; landing page/lead form sürtünmesi; bütçe ve dönem; tekrar hedefleme yalnızca izin ve platform uygunluğu ile; sıklık/creative fatigue; ölçüm ve deney.

Her öneri: hedefi, varsayımı, destekleyici kanıtı, beklenen mekanizmayı, riskini, maliyet etkisini, test edilebilir metriğini ve geri dönüşünü gösterir. Öneri kaynağı doğrulanamıyorsa veri yerine uzman varsayımı olduğu belirtilir. Sektöre özel kurallar (sağlık, finans, işe alım vb.) genel önerinin üstüne uygulanır.

Deney döngüsü:

1. Müşteri hedefi için bir hipotez ve tek ana değişken tanımla (ör. hook veya CTA). Kanalın yerleşik testi daha fazla/başka değişkene izin veriyorsa farkı açıkla.
2. Kontrol ve test hücresinde diğer önemli koşulları mümkün olduğunca aynı tut; kitle/bütçe/yerleşim karışıklığını göster.
3. Başlamadan bütçe tavanı, harcama hücreleri, süre, asgari veri/örneklem, ana metrik, koruma metrikleri ve durdurma kuralı için kullanıcı onayı al.
4. Platformun kendi deney/istatistik yöntemi, ölçüm ve rapor API'sini kullan. Yeterli veri yoksa test sonuçsuz/kararsız olarak kalır; “kazanan” yaratılmaz.
5. Kazanan iddiası için temel metrik kadar koruma metriklerini de incele (harcama, kalite, lead uygunluğu, şikâyet/iade, açılış sayfası). Fark küçük veya belirsizse varyantları eşit/temkinli bırak.
6. Harcama artışını tanımlı maksimum adım, günlük toplam tavan, kanal tavanı ve kullanıcının verdiği otomasyon izni içinde yap; ilk sürümde her artış için onay iste.
7. Sonuçları ve öğrenmeyi kampanya/marka kütüphanesine aktar; geçmiş sonucu yeni brief için kaynak yaparken tarih ve kanal bağlamını koru.

Bu, genel bir “kreatifi çoğaltıp rastgele yaygınlaştırma” değildir: kontrollü test, kanalın deney kapasitesi, para tavanı ve belirsizlik raporu olmadan otomatik ölçekleme yapılmaz.

## 10. Türkiye mevzuatı ve reklam uyum planı

Bu bölüm mevzuat incelemesi değildir ve hukuki görüş sayılmaz. Canlı veri/yayın öncesi güncel Türk hukukçusu ve gerekiyorsa sektör uzmanı ile yükümlülük matrisi, sözleşme ve kullanıcı akışı incelenmelidir.

### 10.1 İlk taramada saptanan maddeler

- Ticaret Bakanlığı, Ticari Reklam ve Haksız Ticari Uygulamalar Yönetmeliği'ndeki değişikliğin 1 Ağustos 2026'da yürürlüğe girdiğini; hedefli reklam, yapay zekâyla üretilen reklam, dijital kişi benzerliği ve influencer açıklaması konularını kapsadığını belirtiyor. Bakanlık açıklamasına göre gerçek kişinin AI ile üretilmiş dijital kopyasının bir ürünü bizzat deneyimleyip tavsiye ettiği izlenimi veren reklam yasaklanıyor; ayırt edilmesi güç AI karakteri için açıklama gerekiyor; çocuklara yönelik davranışsal profiling temelli hedefli reklam ve temelsiz çevresel iddialar özel kısıta giriyor. Her kreatif/özellik güncel yönetmelik metnine göre hukukça teyit edilmeli. Kaynak: [Ticaret Bakanlığı, 27 Temmuz 2026](https://www.ticaret.gov.tr/haberler/aldaticici-reklam-ve-haksiz-ticari-uygulamalarla-mucadelede-yeni-donem-basliyor).
- KVKK'nın 2024 sonrası 9. madde rejiminde yurtdışına veri aktarımı için standart sözleşmeler uygun güvence yollarından biri; uygun rol, taraf, kapsam ve bildirim yükümlülüğü veri akışına göre incelenmelidir. AI, bulut, analytics, reklam platformu ve müşteri CRM'leri için yurt dışına gidiş varsayılarak harita çıkarılmalı; aktarımın hukuki şartları her sağlayıcıya özel doğrulanmalıdır. Kaynaklar: [KVKK standart sözleşme duyurusu](https://www.kvkk.gov.tr/Icerik/7938/Standart-Sozlesmeler-ve-Baglayici-Sirket-Kurallarina-Iliskin-Dokumanlar-Hakkinda-Kamuoyu-Duyurusu), [KVKK bildirim şartları](https://www.kvkk.gov.tr/Icerik/8170/Yurt-Disina-Kisisel-Veri-Aktariminda-Kullanilacak-Standart-Sozlesmelerde-Dikkat-Edilmesi-Gereken-Hususlara-Iliskin-Kamuoyu-Duyurusu).
- Ticari elektronik iletiler (SMS, e-posta, telefon vb.) reklam mecrasında kullanıcıların gördüğü paid ads ile aynı şey değildir. GrowthTwin veya müşteri adına e-posta/SMS ile lead takip/yeniden pazarlama yapılacaksa İYS onay/ret, ispat, hizmet sağlayıcı ve entegratör yetkisi ayrıca değerlendirilmelidir. Bakanlık kaynağı: [İYS](https://ticaret.gov.tr/ic-ticaret/ticari-elektronik-iletiler/ileti-yonetim-sistemi-iys), [Ticari elektronik ileti genel bilgi](https://ticaret.gov.tr/ic-ticaret/ticari-elektronik-iletiler/genel-bilgiler).
- KVKK veri sorumlusu/veri işleyen rolleri, amaç/hukuki sebep, aydınlatma, veri sahibi hakları, saklama-imha, erişim, güvenlik ihlali ve özel nitelikli kişisel veri konuları iş akışına göre ayrıca haritalanmalı. Bu plan genel bir açık rıza/banner çözümünü yeterli saymıyor.
- Reklam veren, GrowthTwin, platform ve lead alan CRM arasındaki sözleşme/rol/izin; lead formundaki amacın açıklanması; veri kaynağı; erişim ve silme; yeniden kullanım/retargeting sınırı tasarımdan önce belirlenmeli.
- Sağlık, finans/kredi, gıda/takviye, alkol, kumar/bahis, çocuk/genç, siyasi reklam, istihdam ve influencer/endorsement kategorilerinin reklam kısıtları farklı olabilir. İlk MVP'ye hangi sektör/ürünlerin alınacağı açıkça belirlenmeli; özel kategori kampanyası kurala göre durdurulmalı.
- Fikri mülkiyet: müşterinin yüklediği kaynak ve üretilmiş görsel/metin/video üzerinde ticari kullanım, stok/müzik/karakter/font/logo, model lisansı ve üçüncü kişi hakları ayrı kaydedilmeli. Üretici/sağlayıcı şartları kapsam bazında okunmalı.

### 10.2 Uyumun ürün davranışı olması

- İçerik ve landing page iddiaları kaynağa bağlanır; “garantili gelir/sonuç”, sahte referans/testimonial, kanıtsız sağlık iddiası gibi bayraklar açıklar ve yayımlamayı bloklar.
- Yaş/hedef ve sektör sınırlamaları platform ve hukuk kurallarına göre deterministik policy katmanında uygulanır; model kuralları gevşetemez.
- AI karakter/gerçek kişi taklidi, influencer tavsiyesi, sentetik fotoğraf/video/ses, çevre ve indirim iddiaları için kanal/tarih ile sürümlenmiş kurallar kullanılır.
- Veri alım ekranı amaç, kullanılacak materyal, saklama, erişim ve aktarım hakkında anlaşılır bilgi verir; dış AI veya CRM kullanımını varsaymaz.
- Her kontrol kararı kaynak/kural sürümü ve son gözden geçirme tarihiyle audit trail'e yazılır. Politika değiştiğinde aktif taslaklar yeniden kontrol edilir.

## 11. Farklı gelir, müşteri bağlılığı ve başarı vaadi

Değer önerisi “reklamı ücretsiz yap” değil, başlangıç riskini düşürürken kaliteli üretim ve karar desteğini göstermek:

- Yeni hesap için sınırlı, ücretsiz başlangıç kredisi; reklam medya harcaması ve dış platform ücreti dahil değildir.
- Brief'e göre kişiye/markaya uygun örnek üretim; müşteri ürünü ve kaynak belgesinden çıktının izlenebilir olması.
- Kampanya planını satın almadan, bütçe ve kanal bazında ücretsiz inceleme/senaryolaştırma (hesap tahmini erişim hakkı varsa gerçek, yoksa örnek/simülasyon etiketiyle).
- Kampanya bitince yalnız metrik yığını değil, “neyin değiştiği, niçin, veri yeterli mi ve bir sonraki denenebilir şey ne?” açıklaması.
- Marka/varlık arşivi, tekrar kullanılabilir başarılı kreatif, kampanya geçmişi, kullanıcı seçimine bağlı bütçe/başarı tercihleri; yeni kampanyayı hızlandırma.
- İlk müşteriler için ücretsiz kredi dışında pilot kapsamı ve öğrenme karşılığı konusunda net, sınırı belirli teklif. Süresiz/şartı belirsiz ücretsiz hizmet taahhüdü yok.
- Müşteri her zaman dosyasını/raporunu dışarı alabilir, üyeliği/kampanyayı/bağlantıyı kapatabilir ve saklama süresi sonunda silme isteyebilir.

## 12. Veri, güvenlik ve gerçek veriye geçiş kapısı

Gerçek veri ve reklam hesabı için aşağıdaki kontrollerin tamamı kanıtlanmadan geçiş yoktur:

1. Onaylanmış ilk müşteri/kampanya/hizmet sınırı ve user journey.
2. Platformun Türkiye hesap/ülke/ürün uygunluğu ile GrowthTwin SaaS/API izninin, OAuth kapsamının ve onayının yazılı kanıtı.
3. Veri envanteri: müşteri/hesap/lead/kreatif/belge/analitik/veri sahibi; amaç, hukuk rolü, erişen, sistem ve ülke, sağlayıcı/alt işleyen haritası.
4. KVKK/Türkiye reklam/e-ticaret/IP/ürün kategorisi hukuk kontrolü; güncel aydınlatma, sözleşme, izin ve veri sahibi akışları.
5. Her veri sınıfı için saklama, otomatik silme, dışa aktarma, yedek/restore/silme, ihlal ve müşteri hesabını kapatma testi.
6. Tenant/rol izolasyonu, güvenli dosya yükleme/antimalware, prompt injection, PII redaksiyonu, şifreleme, sır/token kasası, OAuth kapsamını daraltma ve token iptali denemeleri.
7. Üretim dış AI sağlayıcısı ve her veri türü için lisans/işleme/lokasyon/eğitim/saklama şartı, aktarım yolu, sözleşme ve model güvenlik değerlendirmesi. Deneme endpoint'i gerçek veriye açılmaz.
8. Bütçe/kanal/zaman/içerik limitlerinin platformda/sunucuda uygulanması; tekrar deneme/idempotency; yayın durdurma ve acil geri alma; insan müdahale/olay bildirimi.
9. Rapor metriklerinin kaynağı, atıf farkı ve hata durumunun doğruluğu; gerçek sonucu/tahmini karıştırmayan ekran.
10. Ücret, reklam harcaması, iade/garanti, vergi/fatura ve destek sürecinin unit economics/hukuk incelemesi.
11. Sentetik yerel E2E, staging E2E, yedek/geri yükleme, deployment rollback, CI merge gate, izleme/uyarı ve olay/incident tatbikatı.
12. Hazırlık kanıtlarının ürün sahibi ve gerekli uzmanlarca gözden geçirilmesi; kullanıcının gerçek veriye geçiş için ayrıca açık kararı.

Bu kapıdan önce mevcut yerel ürün prototipi kullanılabilir, ancak yalnız sentetik içerikle; gerçek reklam yayınlayamaz veya harcama yapamaz.

## 13. Aşamalı yol haritası ve kabul ölçütleri

### Aşama A — Blueprint ve karar defteri (ilk workflow kararı alındı; kalan iş kanıt toplamak)

- Müşteri/ürün kapsamı, hesap türü, ilk kullanıcı görüşmeleri/segment kanıtı.
- Tek başlangıç hizmeti, kampanya amacı, içerik modları (GrowthTwin üretimi/kendi materyali) ve ilk lead hedefi.
- Kanal skor kartını resmi kaynak ve aday hesap koşullarıyla tamamla; Meta/TikTok/Google/X/LinkedIn arasından bir dar uçtan uca senaryo seç.
- Basit/pro deneyim, ana akış çizimi, düşük-fidelity wireframe ve hesaplayıcı fiyat/forecast mantığı.
- Üretim kredi tüketimi için model/araç ve cost benchmark; fiyat/bonus/iade karar defteri.
- Uyum matrisi, veri akış haritası, gerçek-data gate ve belirsizlik kaydı.
- **Kabul:** İlk senaryo/kanal adayı/lead yolu sentetik yerel dilim için ADR-0008 ile belirlendi. Açık kalan API erişimi, gerçek kullanıcı talebi, data/legal, forecast hesabı ve fiyat başlıkları canlıya geçiş öncesi doğrulanır; seçim bunların tamamlandığı anlamına gelmez.

### Aşama B — Sentetik tasarım doğrulama

- Masaüstü/mobil etkileşimli prototip: iki kreatif modu, belge yükleme benzetimi, basit/pro akış, satın alma öncesi hesaplayıcı, ücret kırılımı, kampanya detayı ve birleşik rapor.
- Ürün araştırması için sentetik kullanıcı senaryoları ve görevler; acemi/pro katılımcı ile kullanılabilirlik gözlemi.
- Kredi cüzdanı ve tüketim tahmini simüle edilir; gerçek ödeme veya platform hesabı bağlantısı yok.
- **Kabul:** Yeni kullanıcı brief'ten satın alma öncesi plan/creative/report akışını yardımsız tamamlar; uzman ise önemli denetimleri bulur; yanlış tahmin/gerçek sonuç karışmaz.

### Aşama C — Güvenli yerel temel ve çok formatlı içerik

- Workspace, marka ve varlık geçmişi, dosya alımı/izin/sürüm, veri erişim/silme modeli.
- Tek sağlayıcı kararı vermeden önce metin/görsel/video görevleri ve maliyet/kalite/safety benchmarkları.
- Yerel veya izinli sentetik model üzerinde içerik oluştur, düzenle, formatla; deterministic policy; kullanıcıya açık kaynak ve sürüm.
- **Kabul:** Sentetik dosyadan taslağa izlenebilir akış; orijinal korunur; model dış etkide bulunamaz; tenant tests geçer.

### Aşama D — Fiyat/credits ve hizmet checkout prototipi

- Kredi defteri: tahsis, satın alım, bonus, harcama, iade, düzeltme; idempotency; önceden maliyet gösterimi.
- Üretim türü ve iş miktarı için kredi maliyet tablosu; hediye kredisi kuralları; TRY fiyatı/vergiler/ödeme sağlayıcı kararı.
- Gerçek payment processor olmadan sentetik ödeme/chargeback/iptal/invoice akışı; harcama kalemi ayrımı.
- **Kabul:** 100=$10, 1000+20%=1200/$100 örnek matematiği doğru gösterilir; bonus ve ücret ayrı muhasebeleşir; kullanıcı ücret sürprizi yaşamaz.

### Aşama E — Hesaplayıcı ve medya planı

- İlk kanalın gerçek tahmin API'si alınabiliyorsa adapter; değilse mock veride belirgin `simülasyon` etiketi.
- Kanal/amaç/yerleşim rapor metric dictionary, range/confidence, kur/vergiler ve büyütme senaryoları.
- **Kabul:** kullanıcı satın almadan tüm medya bütçesi ve GrowthTwin maliyetini kanal bazında inceleyebilir; sayı kaynağı/tarih görünür; farklı channel reach doğrudan toplanmaz.

### Aşama F — Tek kanal hesabı ve test kampanyası

- Platform API/partner onayı ve test hesabı; OAuth güvenlik/revoke; API'ye dar erişim; kreatif upload, campaign draft, preview, pause/retry, metric sync.
- İlk pilot yalnızca kullanıcı kontrollü hesabında, uygulamanın tüm bütçe/yayın sınırları ve hukuk/kişisel veri onayıyla.
- **Kabul:** ilk platformda yayınlama ve durdurma hesap sahipliği açık; aynı istek çift harcama/yayın üretmez; hata ve token iptali güvenli; platform raporu anlaşılır.

### Aşama G — Kontrollü gerçek müşteri beta

- Gerçek veriye geçiş readiness listesinin tamamı ve ayrıca owner kararı; dar cohort; süreç/güvenlik olaylarını izleme; başarı/şikayet/tahmin sapması değerlendirme.
- Hedef garantisi, AI otomatik yayın/harcama, kredi tahsilatı gerçek ancak sözleşme/unit economics/hukuk onayı sonrasında değerlendirilir.
- **Kabul:** sınırlı müşteri kendi sınırları içinde işini tamamlar; müşteri verisi/lead yetkili kişiye doğru ulaşır, talep halinde silinir; destek/geri alma/olay prosedürü çalışır.

### Aşama H — Kanal ve optimizasyon genişlemesi

- Kademeli yeni kanal, yaratıcı format ve gerçek A/B/deney; müşteriye kontrollü öneri/otomasyon seviyesi.
- Her yeni kanal için aynı API, privacy, test, policy ve bakım skoru; gerçek kanaldan gerçek metriğe ve rapor kaynağına kadar doğrulama.
- **Kabul:** her yeni hedef, kanal, format ve otomasyon sınırları ayrı kanıtlı ve sürümlü.

## 14. Açık karar defteri

| ID | Sınıf | Konu | Şimdiki kayıt | Kapatmak için gerekli kanıt/karar |
|---|---|---|---|---|
| R-01 | Kullanıcı gereksinimi | Her ölçekte reklamveren, Türkiye başlangıcı, sektör bağımsızlığı | Kabul edilmiş ürün yönü | İlk 1–2 segment ve ilk workflow için kullanıcı kanıtı |
| R-02 | Kullanıcı gereksinimi | GrowthTwin üretimi ve müşteri materyaliyle reklam | Kabul edilmiş ürün yeteneği | Hangi dosyalar/işleme, lisans beyanı, kredi/servis ücreti |
| R-03 | Kullanıcı fiyat çıpası | 100/$10, 1000+$20%=1200/$100 ve ücretsiz ilk kredi | Talep edilmiş paket yönü; nihai satış tarifesi değil | TRY, kur, KDV, provider cost, kredi başına iş, expiry, fraud, ödeme hukuku |
| R-04 | Kullanıcı fiyat fikri | Reklam hedef/bütçesiyle artan ayrı reklam bedeli | Talep edilmiş model yönü | Formül, minimum, platform media spend, ücret, tahsilat/iptal |
| R-05 | Kullanıcı değer fikri | Etkileşim olmazsa ücret iadesi/garanti | İlke yönü açık; sözleşme ve taahhüt kararı açık | Ölçüm/KPI/atıf/süre, işletme koşulları, reserve, hukuk ve pilot verisi |
| R-06 | Öneri | Başlangıç için tek hedef ve destinasyon seç | MVP'yi test edilebilir yapar | Kullanıcı araştırması + resmi API/izin + işletme maliyeti skorlaması |
| R-07 | Açık | Gerçek veri ve hesap açma zamanı | Sistem tamamen hazır olana dek ertelenecek | Bölüm 12 readiness kanıtı ve owner onayı |
| R-08 | Açık | İçerik araçları/provider ve kredi tüketimi | Üretim sağlayıcısı yok | Modality değerlendirme, lisans, privacy, cost, kalite, latency |
| R-09 | Açık | CRM/lead alıcısı ve izin akışı | Kararlaştırılmadı | Lead kullanım amacı, alıcı, channel, consent, data retention ve API |
| R-10 | Öneri | Basit ve profesyonel kip tek motor üzerinde | İkisini progresif açıklamayla sun | Prototip kullanım testi ve uzman kullanıcı değerlendirmesi |
| R-11 | Öneri | Büyütme otomatikliği başlangıçta onaylı ve capped | Hatalı spend riski azaltılır | Aşama G sonrası gerçek test verisi ve owner yetki politikası |

## 15. Araştırma ve kaynak notları

Resmi/primary kaynaklar 2026-09-29 tarihinde incelendi; ilgili platform, API, mevzuat ve fiyatlar değişebilir. Dış kaynaklar GrowthTwin'in erişim veya hukuki uygunluk onayı değildir.

### Türkiye reklam mevzuatı, kişisel veri ve mesajlaşma

- [Ticaret Bakanlığı — Yönetmelik değişikliği ve 1 Ağustos 2026 yürürlüğü](https://www.ticaret.gov.tr/haberler/aldaticici-reklam-ve-haksiz-ticari-uygulamalarla-mucadelede-yeni-donem-basliyor)
- [KVKK — yurtdışı aktarımında standart sözleşme/binding corporate rules](https://www.kvkk.gov.tr/Icerik/7938/Standart-Sozlesmeler-ve-Baglayici-Sirket-Kurallarina-Iliskin-Dokumanlar-Hakkinda-Kamuoyu-Duyurusu)
- [KVKK — standart sözleşme imza ve bildirim konuları](https://www.kvkk.gov.tr/Icerik/8170/Yurt-Disina-Kisisel-Veri-Aktariminda-Kullanilacak-Standart-Sozlesmelerde-Dikkat-Edilmesi-Gereken-Hususlara-Iliskin-Kamuoyu-Duyurusu)
- [Ticaret Bakanlığı — İleti Yönetim Sistemi](https://ticaret.gov.tr/ic-ticaret/ticari-elektronik-iletiler/ileti-yonetim-sistemi-iys)
- [Ticaret Bakanlığı — ticari elektronik ileti genel bilgiler](https://ticaret.gov.tr/ic-ticaret/ticari-elektronik-iletiler/genel-bilgiler)

### Kanal ve tahmin/API erişimi

- [TikTok — Türkiye dâhil self-serve Ads Account oluşturma bölgeleri](https://ads.tiktok.com/resources/help/article/available-countries-and-regions-for-ad-account-creation-in-bc?lang=en)
- [TikTok — hesap ülkesi ve reklam yerleşim/hedef konum eşleşmesi](https://ads.tiktok.com/help/article/placements-available-locations?lang=tr)
- [TikTok — lokasyon hedefleme sınırlamaları](https://ads.tiktok.com/help/article/location-targeting)
- [TikTok API for Business — campaign creation, lead generation ve reporting use cases](https://business-api.tiktok.com/portal)
- [TikTok — API for Business / Marketing API capability overview](https://ads.tiktok.com/resources/help/article/marketing-api?lang=tr)
- [X Ads — self-serve reklamveren uygun ülkeleri (Türkiye listede)](https://help.x.com/en/business-and-advertising/about-eligibility-for-x-ads)
- [X — A/B test özellikleri ve metodolojisi](https://business.x.com/en/help/campaign-measurement-and-analytics/ab-testing)
- [Google Ads API — access levels, application reviews and permissible use](https://developers.google.com/google-ads/api/docs/api-policy/access-levels)
- [Google Ads API — campaign reporting](https://developers.google.com/google-ads/api/docs/reporting/overview)
- [Google Ads API — campaign types, budgets and targeting](https://developers.google.com/google-ads/api/docs/campaigns/overview)
- [LinkedIn — Marketing API şartları ve ön onay/vetting](https://www.linkedin.com/legal/l/marketing-api-terms)
- [LinkedIn — Ads API başvuru inceleme süreci](https://www.linkedin.com/help/linkedin/answer/a524477)
- [LinkedIn — Campaign Manager ad account/campaign/targeting/reporting overview](https://www.linkedin.com/help/linkedin/answer/a420420/campaign-manager-overview?lang=en)
- [Google Ads API — YouTube/Video Partners reach forecasting, allowlist gereği](https://developers.google.com/google-ads/api/docs/reach-forecasting)
- [Google Ads API — ReachPlanService tahmin kapsamı](https://developers.google.com/google-ads/api/docs/reach-forecasting/concepts)
- [Google Ads API — ReachPlanService özel erişimi](https://developers.google.com/google-ads/api/docs/reach-forecasting/authentication)
- [Google Ads — coğrafi hedefleme](https://support.google.com/google-ads/answer/10835274?hl=en)
- [Meta Developers — Marketing API Access Tier ve 2026 app-review koşulu değişikliği](https://developers.meta.com/blog/updates-to-ads-management-standard-access-feature/)
- [Meta for Business — Facebook/Instagram Reels placements and creative testing](https://www.facebook.com/business/ads/facebook-instagram-reels-ads)

### Deney ve kreatif varyantı

- [TikTok — split test oluşturma ve önerilen minimum süre](https://ads.tiktok.com/help/article/create-split-test?lang=en)
- [TikTok — bir testteki değişken/uyumluluk matrisi](https://ads.tiktok.com/help/article/split-testing-variables?lang=en)
- [Google Ads — deney hipotezi, kurulum ve kontrol](https://support.google.com/google-ads/answer/7281575?hl=en)
- [Google Ads — sonuç belirlenemiyorsa deney süresi/veri ihtiyacı](https://support.google.com/google-ads/answer/10682377?hl=en)
- [X — test hücresi, yaratıcı değişkenleri ve Bayesian win chance](https://business.x.com/en/help/campaign-measurement-and-analytics/ab-testing)

