# Görsel editör denemesi: doğrulanmış sonuçlar

23 Ekim 2026, Europe/Istanbul. Y01–Y03; [kaynak haritası](creative-editor-domain-map.md).

## Çalışan teslim

`experiments/creative-editor` bağımsız yerel denemesi iki kurmaca örnek sunar:
seramik ürünü ve ev bakım hizmeti. Metin, renk, logo/görsel konumu, boyut ve
döndürme düzenlenebilir. Taslak aynı tarayıcıda kaydedilip açılır; 800×800 PNG
indirilir. Arayüz Türkçedir. Yalnız sabit sentetik bitmapler koddan üretilir.

Sahne Yaparo şema v1'dir; Fabric JSON içe aktarma yoktur. Dört sabit katman,
bilinen varlık kimlikleri, kesin alan/tür ve uzunluk/sayı sınırları doğrulanır.
Bozuk kayıt korunur ve temiz örnek uyarıyla gösterilir. Kullanıcının kaydetmediği
değişiklikler örnek değiştirirken veya sıfırlarken onay alınmadan atılmaz.

Sunucu yalnız 127.0.0.1'e bağlanır, tam Host/port kontrolü yapar ve beş belirli
statik dosya sunar. Depo dizini, kaynak Python veya keyfi node_modules dosyaları
sunulmaz. CSP dış bağlantıları kapatır. Django, hesap, veritabanı, AI, ödeme,
Google yetkisi veya canlı reklamla bağlantı kurulmadı.

## Aynı makinede ölçülen teknik sonuçlar

| Ölçüt | Fabric denemesi | react-design-editor incelemesi |
|---|---|---|
| Sabit kaynak | npm `fabric@7.4.0`, lockfile v3/integrity | `v0.2.1`, commit `b1a09dd700dbba95c6770ed91043d1228afaeea4` |
| Lisans | MIT; paket LICENSE doğrulandı | MIT; kaynak LICENSE doğrulandı; bağımlılıklar farklı lisanslar taşır |
| Kurulum | Node24.11.1/npm11.6.2; `npm ci --ignore-scripts --omit=optional`, 1 bağımlılık eklendi | `npm install --ignore-scripts` ve lockfile override; upstream legacy peer çözümüyle 899 paket, yaklaşık 4 dakika |
| Bağımlılık taraması | Kurulu/optional hariç ağaçta npm audit: 0 bulgu | Production taraması: 4 etkilenen paket (1 critical, 3 moderate); tam ağaç: 5 (2 critical, 3 moderate) |
| Derleme | Browser dağıtımı doğrudan yerelden kullanılır; build aracı gerekmedi | Vite JS bundle üretimi geçti (3,16 saniye); `build:lib` TypeScript bildirim aşaması TS2883 ile başarısız |
| Tarayıcıya sunulan JS | Fabric minified dosya 299.013 byte, uygulama kodu ayrıca | ES library 4.135,55 kB ham / 1.040,44 kB gzip; React ayrıca. Bunlar eşit özellik/bundle karşılaştırması değildir |
| Türkçe düzenle/kaydet/aç/PNG | Beş odaklı test geçti; gerçek PNG decode800×800, dış istek0 | Aynı görev tarayıcıda çalıştırılmadı; başarılı sayılmaz |

Tarama sayıları etkilenen paket sayısıdır; her bulgunun Yaparo'da sömürülebilir
olduğunu kanıtlamaz. Sıfır bulgu da güvenlik garantisi değildir. Optional
canvas/jsdom Fabric denemesine kurulmadı; lockfile'da bulunmaları bunların çalışan
browser bağımlılığı olduğu anlamına gelmez.

Hazır adayda dompurify3.4.8, monaco-editor0.56.0, echarts4.9.0 ve zrender4.3.2
tarama kapsamındaydı; dev ağacında gh-pages2.2.0 eklenir. Örnek advisory:
[DOMPurify](https://github.com/advisories/GHSA-cg2g-xh64-v4q7),
[ECharts](https://github.com/advisories/GHSA-fgmj-fm8m-jvvx),
[zrender](https://github.com/advisories/GHSA-fhv8-fx5f-7fxf).
Hazır adayın tam build hatası bu Windows ortamındaki TypeScript inferred-type
yoluyla ilişkilidir; bütün işletim sistemlerinde başarısız olduğu iddia edilmez.

Yayımlanan hazır paket Canvas/handler sunar; demo araç çubukları ayrıca uyarlanır.
Serbest HTML/CSS/JS Element nesneleri ve uzak kaynak destekleri Yaparo'nun sınırlı
sahne adaptöründen geçirilmeden açılamaz. Demo font ağ bağımlılıkları da kaldırılmalı.
Bu nedenle hazır adayın büyük özellik listesi doğrudan entegrasyon kazancı sayılmadı.

## Doğrulama ve sınırlar

- `python test_editor.py`: 5 test geçti (yerel son koşu 3,613 saniye); bu süre
  gerçek kullanıcı görevi süresi veya üretim performans ölçümü değildir.
- Türkçe karakterler, x/y/scale/angle ve logo konumu kaydet/aç işleminde korundu.
- PNG başlığı, boyutları ve tarayıcıda gerçek decode doğrulandı.
- Ürün/hizmet kayıtları ayrıdır; 390px görünümde yatay taşma yoktur.
- Dış URL, beklenmeyen alan, yanlış renk türü, aşırı boyut/metin ve bozuk JSON
  reddedildi. Bozuk yerel kayıt sessizce üzerine yazılmadı.
- Sunucunun dosya allowlist'i, Host reddi ve CSP kontrol edildi.
- JavaScript sözdizimi, Python Ruff biçim/lint ve yeniden `npm ci` geçti.
- Masaüstü ve mobil ekran görüntüleri incelendi. Bağımsız kaynak incelemesinin
  renk türü bulgusu düzeltildi; regresyon testi eklendi; kalan blocker bildirilmedi.
- İlk CI koşusunda çalışma dizinine bağlı import sıralaması farkı bulundu;
  lint adımı yereldeki gibi depo kökünden çalışacak şekilde hizalandı. Yerel
  tekrarda CSP ile çakışan string-eval beklemesi de görüldü; güvenlik başlığı
  değiştirilmeden locator beklemesine geçildi. Ardından beş test yeniden geçti.
- CI aynı kilitli kurulumu, audit'i ve odaklı tarayıcı testini artık çalıştırır;
  güncel CI sonucu PR üzerinden ayrıca doğrulanmalıdır.

## Karar ve bir sonraki kabul

Fabric bu yerel dilimin çalışan adayıdır; üretim veya tüm editör özellikleri için
nihai seçim ilan edilmedi. Hazır adayın güvenlik/derleme sorunları çözülmeden
ürüne alınması uygun değil. **Y01 tamam, Y02–Y03 karşılaştırmalı kabul açık.**
Hazır adayda aynı görevin başarısı, gerçek yükseltme/geri dönüş denemesi ve bakım
maliyeti henüz ölçülmedi; teknik inceleme bunların yerine geçmez.

Deneme kalıcı marka/tenant varlık deposu, undo/crop/katman sırası, farklı oranlar,
paket import/export veya kampanya entegrasyonu sunmaz. Sistem Arial kullanır;
font indirme/dağıtma yoktur ve platformlar arasında piksel eşitliği vaat edilmez.
Y04–Y07 ve Y06 font/şema/taşınabilirlik kapıları devam eder. Yerel storage silinirse
taslak kaybolur; gerçek müşteri verisi girilmemelidir.
