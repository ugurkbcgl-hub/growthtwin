# Üretim kimliği ve herkese açık sayfalar: uygulama gereksinimleri

**Durum:** 19 Ekim 2026, Europe/Istanbul; uygulama öncesi gereksinim belgesi.
Kod inceleme temeli: PR #289 / `09f54cc`; erişim bulguları PR #290.
Bu belge yayımlanacak gizlilik metni, sözleşme veya hukuki uygunluk onayı değildir.
Alan adı henüz yok. Satın alma, dağıtım veya Google ayarı değiştirilmedi.

## 1. Uygulama sınırı ve kimlik

GrowthTwin Türkiye'deki farklı reklamverenlere yönelik bir reklam platformudur.
Bugünkü ürün yerel sentetik prototiptir; Google entegrasyonu PAUSED TEST
kaynaklarıyla sınırlıdır. Gelecekteki içerik/yayın/rapor yetenekleri, çalışan
özelliklerden açıkça ayrılmalıdır. Satış veya sonuç garantisi ilan edilmemeli.

Üretime hazırlıkta mevcut test Cloud projesi ve loopback OAuth istemcisi korunur.
Üretim için ayrı Cloud projesi, OAuth istemcisi, veri deposu ve secret namespace
planlanır; bunlar bu işte oluşturulmaz. Test token'ı, kullanıcı listesi, onayı veya
gönderim kaydı üretim yetkisi olarak taşınmaz. Üretim yönlendirmesi, seçilmiş
HTTPS adresi belli olduğunda ayrıca kaydedilir; loopback adresi onun yerine geçmez.

Alan adı seçiminden önce marka/hak uygunluğu, sahiplik hesabı, yenileme maliyeti
ve kontrolün kimde olacağı değerlendirilir. Satın alma ve yeni yinelenen gider
ayrı karardır. Alan sahipliği Search Console ile doğrulanabilir olmalıdır.
Google Branding'deki ad, ürün sayfası ve gerçek işletme ilişkisi tutarlı olmalı;
marka ile sözleşmenin tarafı aynı değilse bu ilişki açıklanmalıdır.

## 2. Sayfa haritası ve içerik kabul ölçütleri

Aşağıdaki yollar öneridir; henüz route olarak mevcut değildir (`/` hariç).
Üretim alanı belirlenmeden sahte tam URL oluşturulmaz veya konsola yazılmaz.

| Yol | İçerik ve kabul ölçütü |
|---|---|
| `/` | Kimin için, bugün hangi hizmetlerin sunulduğu, nelerin henüz hazırlanmakta olduğu; Google hesabına neden ihtiyaç duyulduğu; iletişim/gizlilik/şartlar bağlantıları. Giriş yapmadan okunabilmeli. Sahte müşteri, performans, canlı yayın veya iade garantisi yok. |
| `/iletisim/` | Doğrulanmış işletme/sağlayıcı kimliği ve gerçekten takip edilen destek ile veri-hakkı başvuru kanalı. Yerel iskelette eksik bilgi açıkça belirtilir; uydurma adres/e-posta veya çalışmayan form yok. İlk adımda veri toplayan iletişim formu eklenmez. |
| `/gizlilik/` | Veri sorumlusu/roller, kategoriler, amaçlar, toplama yöntemi ve hukuki dayanak, alıcılar/aktarım, saklama-silme-yedekleme, haklar ve başvuru yolu; Google verisinin erişimi/kullanımı/saklanması/paylaşımı ayrı anlatılır. Bilinmeyenler üretim yayınına engeldir. |
| `/kullanim-kosullari/` | Hizmet kapsamı, hesap/içerik hakları, reklamveren yetkisi, durdurma ve bağlantı kesme ayrımı; medya bütçesi ile hizmet/üretim bedellerinin ayrımı; henüz satılmayan kredi/garanti paketlerini satışa açık göstermeme. Satış öncesi fiyat, vergi, iptal/iade ve tüketici/ticari müşteri hükümleri ayrıca incelenir. |

Tüm sayfalar Türkçe, mobilde okunabilir, klavyeyle erişilebilir ve birbirine
bağlı olmalı. Yerel hazırlık sayfaları görünür biçimde **taslak / üretime hazır
değil** olarak işaretlenir. Taslakları herkese açıp Google'a nihai politika diye
sunmak tamamlanma sayılmaz. Yayın sürümü/tarihi belirli olmalı; gizlilik metni
gerçek akış değiştiğinde güncellenmeli. Politika okumak, pazarlama izni, OAuth
hesap yetkisi ve finansal yayın izni aynı kutuda birleştirilmez.

## 3. Koddan doğrulanan veri akışları ve açıklama açıkları

Bu envanter bugünkü sentetik yerel kodu kapsar; üretim veri/alıcı envanteri değildir.

| Veri / kanıt | Bugünkü akış | Üretimden önce çözülmesi gereken |
|---|---|---|
| Hesap, oturum ve çalışma alanı | Django auth/session; `modules/workspaces/models.py` sahibine bağlı çalışma alanını tutar. Genel kayıt kapalıdır. | Üretim kimlik alanları, roller, hukuki dayanak, oturum ve hesap silme süreleri; destek başvurusu doğrulaması. |
| Anonim sentetik taslak | `site/models.py` oturuma bağlı örnek brief/yaratıcı sürümleri saklar. Süresi dolan oturumlar için `clearsessions` vardır. | Scheduler best-effort davranışı kesin silme süresi değildir; yedekleri de kapsayan süre ve yürütüm kanıtı gerekir. |
| Çalışma alanı kampanyası | `modules/campaigns/models.py` brief, yaratıcı geçmişi, seçimi, bütçe ve plan tarihlerini tutar. | Gerçek veri için kategori/amaç/alıcı/süre ve dışa aktarma-silme tasarımı; mevcut örnek kayıtları gerçek müşteri verisine çevirmeme. |
| Google bağlantısı | `connections/backend.py` sabit Google token/revoke uçlarına gider; kullanıcı/çalışma alanına bağlı grant yerel Windows DPAPI ile korunur. | Üretim vault, tenant erişimi, log/izleme, token yenileme/iptal ve ihlal süreci; Windows yerel güvenliğini üretim altyapısı saymama. |
| Google kampanya işlemi | Onaylı metin/plan, TEST hedef hesabına `draft_dispatch.py` üzerinden gider. Google kaynak kimliği/durum ve kalıcı onay/gönderim snapshot'ı yerel DB'de tutulur. | Google'a gönderilen gerçek alanlar ve işleme amaçları; üretim hizmet/alıcı koşulları. Snapshot metin de içerir; yalnız anonim olay metadata'sı sayılmaz. |
| Kalıcı onay/gönderim | `GoogleDraftApproval` / `GoogleDraftDispatch` PROTECT ilişkileri ve tekrar göndermeme kaydı korunur. | Silme talebi; kampanyayı durdurma, token iptali, yerel kayıt temizliği ve yedek dönüşünde tekrar gönderimi önleme ayrı tasarlanmalı. Süresiz saklama veya anında tüm veri silme sözü verilmez. |
| Ziyaret/operasyon bilgisi | Django oturumu ve callback log filtresi kodda var. Üretim proxy/hosting logları bu incelemeyle doğrulanmadı. | Çerez/log envanteri, IP/istek kayıtları, erişim ve süreler; incelemeden “hiç çerez/log yok” denmez. |
| AI, ödeme, dosya ve lead | Bu Google TEST akışı bunları devreye almaz. İlk kanal kararı ham lead'i GrowthTwin'de tutmamaktır. | Gelecekte sağlayıcı seçilirse gerçek veri alıcısı/ülke/saklama ve hukuki inceleme gerekir. API token'ı AI girdisi olamaz. Reklamveren sitesindeki lead ve ölçüm sorumlulukları ayrıca açıklanır. |

Bağlantıyı kesmek Google'daki reklamı durdurmak, kampanyayı durdurmak veriyi silmek
değildir. Her eylem kullanıcıya gerçek etkisiyle anlatılmalı. Belirsiz işlemde
ledger silinerek tekrar oluşturma yolu açılmamalı. Bu çalışma mevcut DB/grant'e
okuma veya yazma yapmadı; tablo koduna göre envanter çıkardı.

## 4. Eksik kararlar ve sorumlular

| Karar | Durum / sorumlu | Tamamlanma kanıtı |
|---|---|---|
| Alan adı ve sahipliği | Yok; proje sahibi, teknik koordinatör seçenekleri hazırlayabilir | Seçim + maliyet onayı + kontrol ve yenileme hesabı; daha sonra DNS/HTTPS/alan sahipliği kanıtı |
| Gerçek sağlayıcı/veri sorumlusu kimliği | Doğrulanmadı; proje sahibi ve yetkin hukuk incelemesi | Gerçek ticari/iletişim bilgileri, hizmet ve veri rolü. Özel belge/kimlik numaraları public Git'e konmaz. |
| Destek ve veri-hakkı kanalı | Üretim için doğrulanmadı; proje sahibi | Takip edilen adres, erişim yetkisi ve başvuru işleyişi; mevcut kişisel konsol e-postasını kendiliğinden yayımlamama |
| Alıcılar, ülkeler ve hukuki dayanaklar | Üretim için açık; teknik envanter + hukuk incelemesi | Hosting/DB, Google, seçilecek AI ve diğer alıcıların gerçek sözleşme/akış değerlendirmesi |
| Saklama, silme, yedek ve ledger | Süreler açık; mühendislik + hukuk incelemesi | Kategori bazında süre/tetikleyici, silme işi ve yedekten dönüşte yeniden silme/tekrar gönderimi önleme kanıtı |
| Ticari kapsam ve iade | Kredi/medya/hizmet ayrımı hedefi var; nihai koşullar açık | Sunulan hizmet, TRY/vergi, iptal/iade ve varsa ölçülebilir garanti için maliyet/hukuk onayı |

Bu bilgiler henüz yerel sayfa iskeletine başlamak için gerekli değildir; nihai
metin ve üretim yayını bunlara bağlıdır. Kullanıcıdan parola veya gizli belgeyi
sohbete göndermesi istenmez. Eksik işletme bilgileri tahminle tamamlanmaz.

## 5. Küçük uygulama sırası

1. Yerel `/iletisim/`, `/gizlilik/`, `/kullanim-kosullari/` hazırlık iskeletleri ve
   footer bağlantıları; sabit metin, belirgin taslak uyarısı, form/veri toplama yok.
   Yeni dış istek, bağımlılık, model, kayıt veya Google ayarı yok.
2. Sadece bu sayfalar için route/şablon ve masaüstü/mobil görünüm doğrulaması;
   giriş gerektirmeden erişim, doğru durum uyarısı ve bağlantılar kontrol edilir.
   Bu belge hazırlığında uygulama testi çalıştırılmadı.
3. Sahip bilgileri, gerçek üretim veri envanteri ve yetkin inceleme tamamlanınca
   nihai metinler; sonra ayrı onaylı alan/HTTPS/yayın ve Google marka/kapsam süreci.
   API erişimi, OAuth yayını ve reklamverenin finansal izni ayrı kapılar kalır.

**Bir sonraki iş:** 1. adımdaki yerel, veri toplamayan hazırlık sayfaları.
Bu belge o sayfaların veya üretim hazırlığının tamamlandığı anlamına gelmez.

## Kaynaklar ve kapsamları — 19 Ekim 2026 kontrolü

- [Google marka doğrulaması](https://developers.google.com/identity/protocols/oauth2/production-readiness/brand-verification): erişilebilir ana sayfa, aynı alandaki gizlilik bağlantısı, alan sahipliği ve ayrı test/üretim projesi önerisi. Terms bağlantısı burada ürün gereksinimidir; her uygulama için bu belgede zorunlu olduğu iddia edilmez.
- [Google OAuth politikaları](https://developers.google.com/identity/protocols/oauth2/policies): kimlik, izin ve ortam hazırlığı.
- [Google API kullanıcı verisi politikası](https://developers.google.com/terms/api-services-user-data-policy): doğru ve erişilebilir veri açıklamaları, gerekli en dar izinler; sonradan farklı kullanımda önceden bilgilendirme ve uygun yeni izin. Gerçek sağlayıcı envanteri bununla tamamlanmış sayılmaz.
- [KVKK aydınlatma yükümlülüğü](https://www.kvkk.gov.tr/Icerik/2033/Aydinlatma-Yukumlulugu-): kimlik, amaç, alıcı, yöntem/hukuki sebep ve haklar hakkında bilgilendirme; rıza olup olmamasından bağımsız yükümlülük. Somut role/dayanağa burada hukuki karar verilmez.
- [Türkiye hazırlık haritası](turkiye-advertising-privacy-readiness.md) ve [canlı yayın kapıları](google-search-live-readiness.md): önceki araştırma ve açık ürün/işletim kararları; eski araştırma tarihi yeni hukuki onay değildir.
