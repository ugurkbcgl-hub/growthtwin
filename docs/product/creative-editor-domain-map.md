# İlk görsel editör: mevcut yapı ve uygulama sınırı

23 Ekim 2026. Y01 kaynak incelemesi; [uygulama planı](yaparo-delivery-plan.md)
ve ADR-0040 kapsamındadır. Bu harita yeni tabloların oluşturulduğu anlamına gelmez.

| Alan | Bugünkü kaynak ve davranış | Sonraki ürün ihtiyacı |
|---|---|---|
| Sahiplik | `workspaces/models.py`: `Workspace.owner`, ad ve oluşturulma zamanı | Marka, varlık ve sahne aynı çalışma alanına bağlanmalı; kimlik istemciden güvenilir kabul edilmemeli |
| Marka | `campaigns/models.py`: taslak üzerindeki `brand_name` metni | Y04: yeniden kullanılabilir renk, logo, font, teklif ve kanıt; eski taslağı otomatik değiştirmeyen marka sürümü |
| Metin | `content/creative.py`: başlık/gövde/çağrı; kampanyada `creative_versions`, tercih edilen anahtar/sürüm | Grafik metin katmanı mevcut metinden kopya alabilir; eski metin sürümü ve kaynak bağı korunmalı |
| Varlık | `assets/contracts.py`: saf izin, karantina, tarama ve silme durumları; dosya deposu yok | Y05: ayrı orijinal dosya, hak/kaynak, tarama, türev ve tenant erişimi; sözleşme varlığı gerçek tarama kanıtı değil |
| Tasarım | Kalıcı grafik sahne modeli yok | Y06: Yaparo şema sürümü, varlık referansları ve düzenlenebilir katmanlar; editör kütüphanesi JSON'u tek kayıt kaynağı olmayacak |
| İndirme | `campaigns/views.py`: tercih edilen metin sürümünün `.txt` indirmesi | PNG çıktısı yeni türevdir; metin indirmesini veya sahneyi ikame etmez |
| Arayüz | Kampanya listesi/oluştur/detay/yolculuk/düzenle/rapor ve metin geçmişi | Y07: kampanyadan editöre tek yol, açık kayıt durumu, kayıp düzenleme önleme |
| Google | Taslağa bağlı onay ve gönderim kayıtları, bütçe ve durum geçmişi | Editör denemesi bu kayıtları değiştirmez; sonraki gerçek yayın yeni içerik sürümüne bağlı onay gerektirir |

Kaynak yolları `apps/web/growthtwin/modules/` altındadır. Python paket adını
marka değişimi nedeniyle yeniden adlandırmıyoruz.

## Denemenin tek kullanıcı görevi

İki kurmaca örnekten birini seç → görsel/logo ve Türkçe metin katmanlarını
düzenle → kaydet → yeniden aç → aynı düzenlenebilir tasarımı PNG olarak indir.
Hizmet ve ürün örnekleri yalnız yazılımla üretilen sentetik bitmap kullanır.
Gerçek marka, müşteri dosyası, dış görsel URL'si veya reklam ağı kullanılmaz.

İlk deneme bağımsız, yalnız yerelde açılan bir ekrandır. Tarayıcıdaki geçici
kayıt ürünün tenant yalıtımlı veritabanı veya yedekleme sistemi değildir.
Bu nedenle başarılı deneme, Y04–Y07 kalıcı entegrasyonunun tamamlandığını göstermez.

## Karşılaştırma ve ilerleme ölçütleri

- Aynı Türkçe karakterler, metin ve görsel dönüşümleri kayıttan sonra korunmalı.
- İndirilen dosya gerçekten PNG olmalı; yeniden açılan sahne düzenlenebilmeli.
- Dış ağ isteği olmadan görev tamamlanmalı; paketler önceden yerel kurulmuş olmalı.
- Bozuk/sınırı aşan sahne reddedilmeli; JSON içindeki dış URL veya kod yürütülmemeli.
- Sabit sürüm, lisans, bağımlılık denetimi ve gerçek kurulum sonucu ayrı kaydedilmeli.
- Hazır editörün başarısız kurulumu işlevsel karşılaştırma başarısı sayılmamalı.
- Üretime geçmeden kalıcı orijinal/varlık/sahne/çıktı ayrımı, font taşınabilirliği,
  kullanıcı erişimi, gerçek dosya güvenliği ve yükseltme/geri dönüş ayrıca tamamlanmalı.
