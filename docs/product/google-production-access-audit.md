# Google gerçek hesap erişimi: salt okunur denetim

**Tarih:** 2026-10-19, Europe/Istanbul. **Kod temeli:** `09f54cc` / PR #289.
Denetim, mevcut test Cloud projesinin oturum açık konsolunda yapıldı.
Anahtar, parola, token veya özel hesap kimliği kaydedilmedi.

## Konsolda doğrulanan durum

| Alan | Gözlem | Anlamı |
|---|---|---|
| Google Ads API | Enabled; Current access level **Test** | Yalnız test hesapları; ekranda günlük 15.000 test işlemi yazıyor. Gerçek hesaba API erişimi hazır değil. |
| Sonraki erişim | **Explorer** ve Apply for access düğmesi | Başvuru gönderilmedi. Google başvurudan sonra otomatik yükseltme yapabileceğini belirtiyor; düğme yalnız bir taslak form açıyormuş gibi tıklanmamalı. |
| OAuth audience | **External / Testing**, 1 test kullanıcısı / 100 sınır | Bu, müşterilere açık üretim yayını değil. Kullanıcının kişisel e-postası burada kaydedilmedi. |
| OAuth Publish app | **Disabled**; Branding tamamlanmalı uyarısı | Yayına geçme işlemi yapılmadı. |
| Branding | Uygulama adı ve destek/geliştirici irtibatı var. Home page, privacy policy, terms bağlantıları boş; yetkili alan adı listesi boş. | Kontrolümüzdeki gerçek adresler, doğru işletme/uygulama kimliği ve alan sahipliği hazırlığı eksik. Alanlar uydurularak doldurulmamalı. |
| Verification Center | Testing nedeniyle doğrulama gerekmiyor mesajı | Üretim onayı veya kapsam incelemesinin tamamlandığı anlamına gelmez. |
| Data Access | Non-sensitive / sensitive / restricted tablolarının üçü de boş | Konsolda beyan edilen kapsam listesi boş. Çalışan yerel adwords yetkisinin iptal olduğu anlamına gelmez; runtime kapsamı ile yayın öncesi kapsam beyanı ayrı değerlendirilmeli. |
| Alan adı | Proje sahibi bu çalışmada henüz alan adı olmadığını bildirdi | Satın alma yapılmadı. Yerel geliştirme sürer; üretim marka sayfaları için adres seçimi açık. |

## Ayrı tutulacak üç izin

1. **Cloud API erişimi:** Explorer, Google Ads API'nin gerçek hesaplara istek
   gönderebilmesini sağlayabilir. Hesap yetkisi, doğru OAuth ve ürünün gerçek
   yayın/harcama kontrolleri ayrıca gerekir.
2. **OAuth uygulama yayını/doğrulaması:** Marka, kontrolümüzdeki alanlar, herkese
   açık ürün tanıtımı/gizlilik/şartlar, gerçek kullanılan kapsamlar ve ilgili
   doğrulama gereksinimleri değerlendirilir. Test projesini değiştirmenin yerine
   geliştirme/üretim ayrımı ayrıca tasarlanmalıdır.
3. **Reklamveren ve finansal yayın izni:** Gerçek hesap/marka/hedef, toplam ve
   hesap tavanı, tarih ve içerik sürümüne bağlı izin; politika/gizlilik/kurtarma
   kapıları. İlk ikisinin geçmesi bu kapıları otomatik açmaz.

## Önerilen sıra ve sonraki somut işlem

Test projesini mevcut Test/Testing durumunda koru. Üretime geçiş planında test ve
üretim projesi/kimlik bilgisi ayrımını netleştir; yalnız görünür olduğu için mevcut
projenin Explorer düğmesine basma. Üretim erişimi için hangi projenin kullanılacağı
ve gerçekten ihtiyaç doğduğu belirlendiğinde Explorer başvurusu hazırlanabilir.
Tarayıcı güvenlik kuralı erişimi genişleten son işlemde eylem anında açık onay
ister. API yükseltmesi, OAuth publish/kapsam ekleme ve gerçek reklamveren/harcama
izni ayrı işlemler olarak değerlendirilir.

Sayfa, veri akışı ve eksik sahip kararları
[uygulama gereksinimlerinde](public-identity-page-requirements.md) kaydedildi.
Tek sonraki yerel iş: veri toplamayan, açıkça taslak olarak işaretli iletişim,
gizlilik ve şartlar hazırlık sayfaları ile footer bağlantıları. Alan adı henüz
yok; satın alma/yayın veya gerçek bilgi uydurma yok. Yerel iskelet, Google
doğrulamasına veya hukuki onaya hazır sayılmaz. Çalışan şifreli TEST grant'ini
veya ledgeri bu hazırlık için değiştirme.

## Güncel resmi kaynaklar

- [Ads erişim seviyeleri](https://developers.google.com/google-ads/api/docs/api-policy/access-levels): Test yalnız test hesapları; Explorer üretim için günlük 2.880 işlem, test için 15.000. Başvuru otomatik yükseltebilir. Explorer planlama ve hesap/faturalama yönetiminin listelenen işlevlerini desteklemez; tahmin/anahtar kelime araçları için ayrıca erişim gerekir.
- [OAuth audience](https://support.google.com/cloud/answer/15549945): Testing kullanıcı sınırı ve adwords gibi kapsamlarla test yetkisinin/refresh token'ın yedi günlük ömrü. Mevcut grant'in kesin bitiş tarihi bu denetimde hesaplanmadı; yalnız genel kural kaydedildi.
- [Marka doğrulaması](https://developers.google.com/identity/verification/authentication-verification): uygulama kimliği, alan sahipliği ve herkese açık ana sayfa/gizlilik bağlantıları.
- [OAuth politikası](https://developers.google.com/identity/protocols/oauth2/policies): kullanılmasına izinli alanlar, doğru uygulama bilgileri ve kullanıcı verisi/izin kuralları.

Kaynaklar 19 Ekim'de kontrol edildi. Eski sayfa özetlerindeki developer-token
ifadeleriyle güncel Cloud projesi erişim modeli karıştırılmamalı. Bu denetim
yazılım değişikliği, üretim hesabı denemesi, erişim yükseltme veya yayın yapmadı.
