"""Static preparation pages; no account, session, provider or storage operations."""

from django.shortcuts import render
from django.views.decorators.http import require_safe

PAGES = {
    "contact": {
        "title": "İletişim",
        "intro": "Destek ve başvuru yollarını tek yerde bulabilmen için hazırlanıyor.",
        "sections": (
            (
                "İşletme ve destek bilgileri hazırlanıyor",
                "GrowthTwin'in doğrulanmış hizmet sağlayıcı bilgileri ve takip edilen "
                "destek adresi henüz yayımlanmadı. Bu sayfada şu an başvuru alınmıyor.",
            ),
            (
                "Kişisel bilgi gönderme",
                "Bu hazırlık sayfasında iletişim formu yok. Parola, API anahtarı, "
                "kimlik belgesi veya müşteri bilgisi paylaşma.",
            ),
            (
                "Yayından önce tamamlanacaklar",
                "Hizmet sağlayıcının kimliği, iletişim bilgileri ve kişisel verilerle "
                "ilgili başvuruların nasıl iletileceği doğrulanarak eklenecek.",
            ),
        ),
    },
    "privacy": {
        "title": "Gizlilik hazırlığı",
        "intro": "Hangi bilgilerin neden kullanılacağını anlaşılır biçimde açıklamak "
        "için hazırlanıyor. Bu sayfa nihai gizlilik veya aydınlatma metni değildir.",
        "sections": (
            (
                "Bugünkü prototip",
                "Yerel kampanya akışı sentetik örnekler içindir. Oturum, çalışma "
                "alanı, örnek kampanya metinleri ve plan kayıtları kullanılabilir. "
                "Gerçek reklamveren, müşteri veya hasta verisi girme.",
            ),
            (
                "Google bağlantısı ayrı bir izindir",
                "Sınırlı yerel test akışı, hesap sahibinin yetkilendirmesiyle Google'a "
                "örnek kampanya metinleri ve plan bilgileri gönderebilir. Yetki "
                "bilgileri korumalı yerel depoda; test onayı ve gönderim kayıtları "
                "uygulamanın veritabanında tutulur. Bu, gerçek reklam yayını izni değildir.",
            ),
            (
                "Durdurma, bağlantıyı kesme ve silme",
                "Bunlar ayrı işlemlerdir. Bağlantıyı kesmek reklamı durdurmak veya "
                "tüm kayıtları silmek anlamına gelmez. Saklama süreleri, silme ve "
                "yedeklerden temizleme süreçleri üretim için henüz tamamlanmadı.",
            ),
            (
                "Nihai metin için eksik bilgiler",
                "Veri sorumlusunun kimliği, işleme amaçları ve hukuki dayanaklar, "
                "veri alıcıları ve aktarım koşulları, çerez ve kayıt bilgileri, saklama "
                "süreleri ve hak başvurusu kanalı gerçek hizmete göre netleştirilecek. "
                "Üretim yayını öncesinde yetkin inceleme gerekiyor.",
            ),
        ),
    },
    "terms": {
        "title": "Kullanım koşulları hazırlığı",
        "intro": "Hizmetin kapsamını ve kontrolün sende olduğu noktaları açıklamak "
        "için hazırlanıyor. Bu sayfa nihai hizmet sözleşmesi değildir.",
        "sections": (
            (
                "Şu an neyi deneyebilirsin?",
                "GrowthTwin'in yerel prototipinde sabit sentetik kampanya örneklerini "
                "inceleyebilirsin. Gerçek müşteri kullanımı, ödeme ve canlı reklam "
                "yayını bu hazırlık sayfalarıyla açılmaz.",
            ),
            (
                "Hesap, içerik ve yayın izni",
                "Gelecekte kullanılacak reklam hesabı ve içerik için gerekli haklar "
                "doğrulanmalı; hesap bağlantısı, içerik, zamanlama ve harcama sınırları "
                "ayrı yetkilendirilmelidir. Test için verilen onay üretime taşınmaz.",
            ),
            (
                "Üretim bedeli ile reklam bütçesi farklıdır",
                "İçerik üretim kredileri, GrowthTwin hizmet bedeli ve reklam "
                "platformuna ayrılan medya bütçesi ayrı kalemler olarak planlanıyor. "
                "Nihai fiyat, vergi, iptal ve iade koşulları henüz belirlenmedi. "
                "Bu sayfadan paket satın alınamaz; sonuç veya ücret iadesi garantisi verilmez.",
            ),
            (
                "Kontrol ve başvuru yolları",
                "Kampanyayı durdurma, hesap bağlantısını kesme ve veri silme "
                "birbirinden farklıdır. Nihai hizmet kapsamı, tarafların sorumlulukları "
                "ve destek/başvuru yolları doğrulanıp incelendikten sonra yayımlanacak.",
            ),
        ),
    },
}


@require_safe
def information_page(request, page_key):
    """Render only a route-selected static page without accessing user data."""
    return render(request, "site/information.html", {"page": PAGES[page_key]})
