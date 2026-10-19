# İlk gerçek Google Search yayını: hazırlık denetimi

**Tarih:** 2026-10-19, Europe/Istanbul. **İncelenen kod:** `bfc7397`
(PR #287) ve bu belgenin toplam bütçe doğrulaması. Bu denetim gerçek hesap,
reklamveren verisi, yayın, harcama veya yeni altyapı yetkisi vermez.

## Hedef ve güncel kanıt

Türkiye'de farklı sektörlere hizmet veren, kullanıcının talebini alıp onaylı
sınırlar içinde reklam üretimi/yayını/raporlamasını yürüten ürün hedefi değişmedi.
İlk teknik kanal Google Search. Mevcut akış yalnız sentetik örnek ve TEST hesabı.

PR #287'nin yerel akışı, seçili sürümden onaylı paketi PAUSED gönderdi ve geri
okuyup durdurdu. Zorunlu CI `39237793375` ve main CI `39238090433` başarılı.
Bu, gerçek yayın başarısı veya gerçek harcama sınırı kanıtı değildir.

## Gerçek yayına kalanlar — öncelik sırası

| Öncelik / kapı | Doğrulanmış olan | Eksik kanıt ve tamamlanma koşulu |
|---|---|---|
| 1. Toplam bütçe | Günlük örnek tutar açıkça toplam tavan sayılmıyor. Google v25 TEST hesabı bu çalışmada CUSTOM_PERIOD / totalAmountMicros isteğini validateOnly ile kabul etti. | Toplam bütçeli yeni PAUSED TEST kaynağı oluşturulup period, total ve tarihler geri okunmalı. Gerçek kullanımda kampanya ve hesap toplamı, mevcut başka harcamalar ve eşzamanlı işlemler ayrıca sınırlandırılmalı. Otomatik günlük bütçe alternatifi yok. |
| 2. API ve reklamveren hesabı | Yerel şifreli OAuth ve yalnız belirlenmiş TEST çocuk hesabı kontrolü var. | Üretime uygun Cloud API erişimi, gerekli OAuth/harici uygulama incelemesi, gerçek hesabın sahipliği/izinleri, ülke/para birimi/saat dilimi/faturalama uygunluğu ayrı doğrulanmalı. TEST onayı bu kapıyı açmaz. Bu denetim özel hesabın erişim seviyesini yeniden sorgulamadı. |
| 3. Reklamveren yetkisi | Sentetik sürüme bağlı TEST onayı ve gönderim kaydı var. | Gerçek hesap, içerik sürümü, gerçek hedef adres, kampanya/hesap tavanı, zamanlama ve geri alma koşullarına bağlı finansal yayın izni kaydedilmeli; eski test onayı taşınmamalı. |
| 4. Hedef ve politika | Kaynak URL korunuyor; example.com yalnız görünen TEST değişikliği. | Gerçek HTTPS hedefi, hak sahipliği, erişilebilirlik/yönlendirmeler, teklif/iddia kanıtları ve kampanyaya özgü Türkiye/platform uygunluğu doğrulanmalı. Örnek adresi gerçek site gibi kullanma; genel amaçlı sunucu URL isteği eklemeden SSRF sınırını tasarla. |
| 5. Gizlilik ve veri yaşam döngüsü | Geliştirme sentetik. 29 Eylül araştırması ürün kapılarını listeliyor. | Gerçek girdiler, alıcılar, KVKK/transfer, saklama/silme/yedekler, erişim ve yetkili hukuki değerlendirme tamamlanmalı. Dated araştırma güncel hukuki onay sayılmaz. İlk akışta ham lead saklamama kararı korunur. |
| 6. Üretim işletimi ve kurtarma | CI/PostgreSQL, yerel test akışı, tarihli profil staging E2E ve aynı kodlu rollback kanıtları var. | Yapılandırılmış/Heroku DB tam geri yüklemesi, kod/şema değişiminden kurtarma ve güncel kampanya akışının dağıtım revision'ında E2E'si açık. Windows DPAPI/loopback/tek süreç tasarımı üretim vault/tenant/concurrency/izleme çözümü değildir. |
| 7. Rapor ve dönüşüm | Rapor ekranı ve gözlem/metrik sözleşmeleri mevcut. | Gerçek kaynak, dönem tamlığı, tazelik, harcama ve dönüşüm ölçümünün reklamveren hedefiyle eşleşmesi doğrulanmalı. TEST'te gösterim/gelir/lead sonucu kanıtlanamaz. |
| 8. Ticari hizmet | Kredi fiyat çıpaları ve medya/ücret ayrımı belgeli. | Ödeme/kredi muhasebesi, TRY/vergi, hizmet ücreti ve iade/garanti şartları ürünleştirilmedi. Ücretsiz kontrollü pilot kararı bile platform ücretini veya hukuki kapıları kaldırmaz. |

## Bu çalışmada uygulanan küçük adım

Onaylı sürümden ayrı, bellekte kalan toplam bütçe adayı hazırlanır. Orijinal
medya tutarı minor unit'ten micros'a tam çevrilir; günlük amountMicros kaldırılır,
period=CUSTOM_PERIOD ve totalAmountMicros kullanılır; bütçe paylaşılmaz.
Tarihler, saat dilimi, metinler ve görünen TEST URL/konum kuralları korunur.

Yerel sahibin CSRF ve on dakikalık imzalı sürüm/hedef kontrolünden sonra yalnız
doğrulanmış TEST hesabına validateOnly=true gider. Kaynak/hedef çağrı öncesi ve
sonrası kontrol edilir. Ağ veya şema sorunu anlaşılır başarısızlık olur; günlük
bütçeye düşülmez. Ledger/approval değiştirilmez; oluşturma veya ENABLED yoktur.
Tarayıcıda 5.000 TRY örnek istek kabul edildi; bu tutar harcanmadı ve mevcut
günlük bütçeli kaynağa toplam sınır uygulanmadı. 79 hedefli test başarılı.

## Tek sonraki geliştirme

Yeni bir sentetik taslak için toplam bütçeli PAUSED TEST gönderim profili hazırla;
onay ekranına kesin toplam/period/tarihleri bağla, kalıcı işlem rezervasyonu ile
oluştur ve geri okumada CUSTOM_PERIOD/totalAmountMicros/tarihleri doğrula.
Mevcut günlük bütçeli ledger veya kaynağın türünü dönüştürme/sıfırlama. Google
bütçe türünün oluşturulduktan sonra değiştirilemediğini belirtiyor. Eski
günlük kayıtların kontrol/durdurma yolu korunmalı. Canlı yayın hâlâ ayrı kapıdır.

## Resmi kaynaklar — 19 Ekim'de kontrol edildi

- [Bütçe oluşturma](https://developers.google.com/google-ads/api/docs/campaigns/budgets/create-budgets): CUSTOM_PERIOD, total_amount_micros, paylaşılmayan bütçe ve Search başlangıç/bitiş tarih-saat gereksinimi.
- [Bütçe türleri](https://developers.google.com/google-ads/api/docs/campaigns/budgets/overview): günlük ortalama ve kampanya toplamının ayrımı.
- [API quick start](https://developers.google.com/google-ads/api/docs/get-started/make-first-call): Cloud projesi erişimi; TEST erişiminin gerçek hesaba yetmediği. Sayfa özetindeki eski token ifadeleri yerine gövde ve hesap özelindeki güncel kanıt kullanılmalı.
- [Üretim erişim seviyeleri](https://developers.google.com/google-ads/api/docs/productionize/access-levels): Cloud erişim incelemesi ve gerekli işlev kapsamı.

Hesaba özgü üretim onayı, güncel hukuk görüşü veya sonuç garantisi bu kaynaklardan çıkarılmaz.
