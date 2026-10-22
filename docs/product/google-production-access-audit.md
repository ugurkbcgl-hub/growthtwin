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
Veri toplamayan, açıkça taslak olarak işaretli iletişim, gizlilik ve şartlar
hazırlık sayfaları ile footer bağlantıları yerelde uygulandı. Alan adı henüz
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


## Scoped TEST hazırlığı — 22 Ekim 2026

Saat 14:04 Europe/Istanbul (+03:00), kod tabanı `8fd13b5` / PR #311.
Bu bölüm önceki tarihli gözlemleri günceller; üretim erişimi başvurusu değildir.

- Cloud konsolunda Ads API **Enabled**, erişim seviyesi **Test**; OAuth
  **External / Testing**, bir test kullanıcısı olarak yeniden görüldü. Branding
  ana sayfa/gizlilik/şartlar ve yetkili alanlar boş; uygulama yayımlanmadı.
- Kullanıcının işlem anındaki açık onayıyla yalnız **GrowthTwin Web Test**
  istemcisine `http://127.0.0.1:8002/connections/google/scoped/callback/` eklendi.
  Kaydetme sonrasında istemci yeniden açıldı ve hem bu adres hem eski
  `http://127.0.0.1:8002/connections/google/callback/` okundu. Başka alan,
  kapsam, erişim seviyesi veya kimlik bilgisi değiştirilmedi.
- Ads arayüzündeki mevcut yönetici/alt hesap kimlikleri, korunmuş yerel yardımcının
  kaynak kodundaki hedef sabitleriyle eşleşiyor. Bu, çalışan sürecin güncel
  yapılandırmasının veya owner/workspace bağının doğrulandığı anlamına gelmez.
- Alt hesap arayüzünde üç kampanya ve yayın yapılmadığı/nesnelerin duraklatıldığı
  veya kaldırıldığı uyarısı görüldü. Görüntülenen 16–22 Ekim aralığında tıklama,
  gösterim ve maliyet sıfırdı; tüm zamanlara ilişkin sonuç çıkarılmadı.
- Güncel `customer.test_account=True` API sorgusuyla **yeniden doğrulanmadı**.
  API erişim seviyesinin Test olması veya hesap adı bu kanıtın yerine geçmez.
  Grant yenileme, OAuth başlatma, kampanya işlemi veya ledger SQL okuması yapılmadı.
- Yerel yardımcı yalnız AST/kaynak incelemesiyle değerlendirildi: üst düzey DB ve
  kullanıcı değiştiren işlemleri var, salt okunur denetim için çalıştırılmadı.
  Şifreli kayıt açılmadı; eski grant/DB/ledger, Heroku ve normal kapalı bayraklar
  korundu. Ekran kanıtı gizli alanlar hariç kırpılarak Git dışında tutuldu.

**Sonraki tek iş:** eski grant/ledgeri koruyan ayrı sentetik workspace/owner ve
istemci bağlamıyla izole aday denemesinin hazırlığını tamamla; güncel TEST hedefi,
yetki kapsamı, aynı süreç PKCE, callback/proxy/hata logları ve belirsiz sonuç
uzlaştırma koşullarını doğrulamadan bayrakları açma veya OAuth başlatma.
Dönüş adresinin kaydı, başarılı OAuth/aktif grant/üretim hazırlığı kanıtı değildir.
Bu belge diliminde yerel test çalıştırılmadı; kod değişmedi. PR #311 son-head CI
39765174203 ve main CI39765596754 başarılı: 586 PostgreSQL testi +11 tarayıcı E2E.
