# İzole scoped Google TEST denemesi: hazırlık kaydı

**Doğrulama:** 22 Ekim 2026, 17:02 Europe/Istanbul (+03:00).
**Kod tabanı:** `0c87014` / birleştirilmiş PR #312.
**İlk hazırlık durumu (17:02):** Ayrı yerel sentetik DB hazırdı; henüz OAuth başlatılmamıştı. Güncel takip aşağıdadır.

## Bu adımda yapılanlar

Git dışındaki hazırlama yardımcısı, Django başlatılmadan önce yalnız yeni geçici
SQLite yolunu seçti. Migrasyonlar sadece bu yeni DB'ye uygulandı. Ayrı sentetik
kullanıcı ve workspace, rastgele büyük pozitif sayısal PK'lerle oluşturuldu;
connector/generation UUID'leri yenidir ve connector **quarantined** durumundadır.
Kullanıcının kullanılabilir parolası yok; tarayıcı oturumu veya giriş atlatma
mekanizması oluşturulmadı. Aday deneme ve Google kampanya ledger sayıları sıfır.

Bu kimlik çifti için eski tip grant yolunun mevcut olmadığı yalnız dosya varlık
kontrolüyle görüldü. Yeni DB'nin otomatik 1/1 PK'leri kullanılmadı: legacy dosya
yolu kullanıcı adından değil owner/workspace sayılarından türetiliyor.
Korunan eski DB, grant ve ledger okunmadı/değiştirilmedi. Hazırlama sürecinde
credential okuma/yazma, client yükleme ve token transport fonksiyonları doğrudan
reddeden işlevlerle kapatıldı; helper bu işlevleri kullanmadan tamamlandı.

Normal kaynak ayarlarındaki scoped endpoint/candidate bayrakları False kaldı;
hazırlama sürecinde local OAuth ve TEST kampanya bayrakları da False idi.
Sunucu çalıştırılmadı, port bağlanmadı, PKCE/state veya OAuth rezervasyonu
oluşturulmadı. Bu işlem ürün test turu veya başarılı OAuth testi değildir.

Bağımsız kaynak ve yeni DB metadata incelemesi de owner/workspace bağını, tek
karantina generation'ını ve sıfır aday/ledger/session kaydını doğruladı. Manifestin
ilk sıfır I/O alanları ölçüm sayacı değildi; kayıt bu sınırı belirtecek biçimde
düzeltildi. Deny yamaları genel ağ/subprocess engeli değildir ve django.setup
sonrasında kurulur. İncelenen akışta dış çağrı yoktur; bu, ölçülmüş egress veya
gelecekteki runtime için bir ağ güvenliği kanıtı değildir. Runtime aynı DB/kimlik
ve kapalı ayarları yeniden kurmadan devam edemez.

## Yerel devam kaydı

- DB: `%TEMP%\gwt-scoped-preparation-_jafwrsl\synthetic.sqlite3`
- Kimlik ve kalan koşul metadatası: aynı dizinde `preparation.json`.
- Git dışı hazırlama yardımcısı: `%TEMP%\growthtwin_prepare_closed_scoped.py`.
- Manifest token/parola/client secret içermez. Sayısal PK/UUID'ler ve tam yerel
  yol bu özel manifestte kalır; gerçek credential içeriği Git'e eklenmez.
- Helper yeniden çalıştırılırsa YENİ ortam oluşturur; devam/onarım aracı değildir.
  Yeni bir ortam yaratarak belirsiz denemeyi veya eski geçmişi atlamak yasaktır.
  `%TEMP%` kalıcı saklama garantisi vermez; dosya yoksa hazırmış gibi davranma.

## OAuth öncesi tamamlanacak koşullar

1. **Güncel TEST kanıtı:** UI adı ve Cloud Test erişimi yeterli değildir. Sabit
   `customer.id/test_account/manager` sorgusuyla doğru non-manager TEST child
   doğrulanmalı. Mevcut `verification.verify(binding)` önce eski DPAPI grant/client
   okur ve token yeniler; DB değiştirmese de credential/provider işlemidir.
   Bu hazırlık adımında çağrılmadı. Böyle bir sorgu ayrıca izole yeni adayın aynı
   hesaba eriştiğini kanıtlamaz; aday kendi sınırında da doğrulanmalıdır.
2. **Kesin client/target/owner/workspace bağı:** Yeni DB yeni OAuth client değildir.
   Backend hâlâ sabit mevcut TEST client dosyasını kullanır. Dosya açılmadığından
   gerçek client bağı doğrulanmadı. Ayrı client gerektiğinde eski dosyayı ezme;
   ayrı yapılandırma tasarımı gerekir. Hedefler tahmin edilerek doldurulmamalı.
3. **Tarayıcı ve süreç:** Kullanılabilir test girişi, özgün session/CSRF,
   DEBUG False, exact loopback8002, forwarded header yokluğu ve tek süreç/reload
   kapalı çalışma doğrulanmalı. Başlamış handshake yeniden başlatma sonrası
   sürdürülemez; otomatik yeniden gönderim yoktur. Yeni aday dosya yolu exact
   attempt UUID'sine bağlıdır; gelecekteki yol henüz doğrulanmış sayılmaz.
4. **Log ve hata kontrolleri:** Callback query/referrer/body/exceptions kaydı
   oluşmamalı; Django filtresine ek olarak gerçek çalıştırıcı/access/error yolları
   incelenmeli. Bu adım sunucu başlatmadığından log güvenliği doğrulanmadı.
5. **Belirsizlik ve geri dönüş:** EXCHANGING/UNCERTAIN veya olası dosya/SQL ayrışması
   durdurur. Otomatik retry/revoke/unlink/adoption yok. RESERVED-only retirement
   izni belirsiz aday temizliği izni değildir. Eski grant ve stop/reconcile yolu
   korunmalı; kapatılan bayraklar yeni dosyayı etkinleştirmez veya temizlemez.
6. **Denemenin açık kapsamı:** Önkoşullar ve ADR-0031/0036 rollout sınırları
   karşılanmadan bayrak açma/OAuth başlatma. İzinli bir aday kaydı dahi inactive
   kalır; aktif grant, refresh consumer, gerçek reklam hesabı/yayın/harcama,
   üretim vault veya müşteri hazır oluşu anlamına gelmez.

## Kabul ölçütü ve sonuç

Yeni DB'nin tek veri kaynağı olması, unusable-password sentetik owner/workspace,
quarantined connector, sıfır aday/ledger, kapalı bayraklar ve yeni kimliğe ait
legacy yolunun yokluğu hazırlama sırasındaki kontrollerle doğrulandı.
Yerel otomatik uygulama testleri çalıştırılmadı; uygulama kodu değişmedi.
PR #312 required CI39768028595 ve main CI39768447961 başarılıydı:
586 PostgreSQL testi ve11 tarayıcı E2E. Bunlar bu yeni ortamın OAuth kanıtı değildir.

**Sonraki tek iş:** Eski grant'i koruyan güncel TEST hedef doğrulamasının kesin
kapsamını ve izole runtime/client bağını tamamla; sonuçlar olmadan OAuth başlatma.


## Hedef ve kapalı runtime doğrulaması — 22 Ekim, 17:49

- PR #313 merge `b310e7d`; required CI39792541560 ve main CI39795773585
  başarılı:586 PostgreSQL testi +11 tarayıcı E2E. Uygulama kodu değiştirilmedi.
- Ayrı sınırlandırılmış preflight, eski helper'ı çalıştırmadan yalnız hedef
  sabitlerini AST'den ve owner/workspace metadata'sını mode=ro/query_only ile
  okudu. Django veri kaynağı memory idi. **Bir** refresh_token isteği ardından
  **bir** sabit Ads kimlik sorgusu, mevcut client ile doğru non-manager TEST
  child'ı doğruladı. Saklı client kimliği kayıtlı TEST istemcisiyle eşleşti.
- Bu işlem credential okuma ve gerçek provider erişimidir; önceki hazırlıktan
  ayrı tutulur. Credential yazısı yok. Şifreli client/grant dosyalarının önce/sonra
  hash'leri ve korunan DB boyut/mtime'sı aynıydı. DB hash'i veya uzak grant'in
  gelecekte geçerliliği doğrulanmadı. Kanıt yalnız eski grant'e aittir.
- Aynı yeni DB/kimlikle loopback8002'de tek süreç/reload'suz/proxy'siz kapalı
  WSGI çalıştı. Python TCP connect ve credential fonksiyonları reddedildi;
  request log metodu boş, stderr/error çıktıları atıldı. Bu genel sistem veya
  tarayıcı/proxy log güvencesi değildir.
- Gerçek Django parola+CSRF girişi ve logout sentetik kullanıcıyla başarılıydı.
  Açık parola yalnız tarayıcı kontrol belleğinde; DB'ye PBKDF2 özeti yazıldı.
  Kapalı overview ve callback'in iki yazımında404, no-store/private,
  callback no-referrer ve Location yokluğu görüldü; gerçek code kullanılmadı.
- Kapalı süreç durduruldu; dış interrupt finally'yi çalıştırmadığı için exact
  yeni DB'de ayrıca kontrol/temizlik yapıldı: session0, attempt0, kullanıcı
  parolası tekrar unusable. Zorla kapatmada cleanup varsayılmamalı.

## Tek gerçek aday denemesi: onay ve sınır

Kullanıcı eylem anında tek TEST yetkilendirmesine açık onay verdi. Aynı Google
istemcisinin yeni consent/token üretiminin eski uzak token'ı etkileyebileceği
bildirildi; yerel dosya koruması uzak grant garantisi olarak sunulmadı.

Git dışı `%TEMP%\growthtwin_one_candidate_runtime.py` kaynak incelemesi iki
hata buldu ve düzeltme sonrası onaylandı: parola değişimi prerequisite/proof
kontrollerinden sonra cleanup kapsamında; ≤1 saatlik hedef kanıtı başlangıçta,
start ve exchange öncesinde yeniden kontrol ediliyor. Cleanup adımları bağımsız;
zorla durdurma sonrası exact-DB kontrolü ayrıca gerekir.

Yalnız bu süreçte scoped/local OAuth bayrakları açıldı. Normal kaynak ayarları
False kaldı. WSGI yol izin listesi legacy/retire/kampanya işlemlerini engeller;
tek start POST, tek exact authorization_code exchange ve receipt/envelope/path
bağlı tek inactive aday yazısı sınırı var. Refresh/revoke/Ads sorgusu/adoption
bu çalıştırıcıda yok. Tek süreç/PKCE/CSRF ve owner/workspace denetimleri korunur.
Mevcut kanıt yeni adayın hesap erişimini doğrulamaz.

17:42'de uygulama üzerinden **bir** start gönderildi; kayıt RESERVED.
Google seçilen kullanıcı için geçiş anahtarı istedi; alternatif yöntem sonunda
“Geçiş anahtarı bulunamadı” gösterdi. Yeni credential oluşturulmadı ve kullanıcıya
kendi doğrulaması için devir yapıldı. 17:45 itibarıyla token exchange/aday yazısı
henüz doğrulanmış değildi; başarılı OAuth iddiası yok. Beş dakikalık handshake
17:47:23 Europe/Istanbul'da bitti; süresi geçen deneme yeniden başlatılmaz.

EXCHANGING/UNCERTAIN veya dosya–SQL ayrışması olursa aynı DB/receipt/dosyayı koru;
otomatik retry, yeni kimlikle atlama, revoke, unlink veya adoption yoktur.
RESERVED kaydı da kendiliğinden silinmez. Yetkilendirme bitse bile inactive aday
normal runtime tarafından tüketilmez; hesap doğrulaması/üretim/yayın kapıları açık.


### Son durum — 17:49

Google geçiş anahtarı sorunu çözülmeden handshake süresi doldu. Exact yeni DB'de
tek kayıt hâlâ RESERVED; EXCHANGING sınırına hiç geçilmedi. Türetilen exact aday
dosya yolunda dosya yok. Bu akışın exchange öncesinde commit zorunluluğu, token
isteği gönderilmediğiyle tutarlıdır; kapanış raporunun başlangıç sayaçları tek
başına ölçüm kanıtı olarak kullanılmadı. Başarılı OAuth/aday yok.

Tek denemelik süreç durduruldu,8002 dinleyicisi kalmadı. Interrupt sonrasında
finally yine garanti edilmediğinden exact yeni DB'de sentetik parola unusable,
session0 ve korunan tek RESERVED kayıt ayrıca doğrulandı. Receipt/generation
silinmedi, döndürülmedi veya yeniden denenmedi; revoke/unlink/adoption yok.
Google sekmesi kullanıcıya kimlik doğrulama sorunu için bırakıldı; süresi dolmuş
bu akışı tamamlamak artık geçerli bir callback/yenileme izni sağlamaz.

Sonraki tek iş kullanıcıya ait Google geçiş anahtarı doğrulamasının çözülmesidir.
Ardından aynı DB'deki expired RESERVED için ayrı gözden geçirilen retirement ve
onaylı yeni deneme kapsamı belirlenmeli. Var olan helper başlangıçta attempt0
beklediği için bu DB'de yeniden çalıştırılamaz; koşulu kaldırarak aşma veya başka
DB/kimlikle geçmişi atlama. Eski TEST hedef kanıtını güncel kabul etmeden önce
zaman/client/target bağını yeniden doğrula.
