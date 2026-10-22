# İzole scoped Google TEST denemesi: hazırlık kaydı

**Doğrulama:** 22 Ekim 2026, 17:02 Europe/Istanbul (+03:00).
**Kod tabanı:** `0c87014` / birleştirilmiş PR #312.
**Durum:** Ayrı yerel sentetik DB hazır; OAuth başlatmaya hazır değil.

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
