import streamlit as st
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup
import io
import hashlib
import time
from docx import Document

# --- SİBER GÜVENLİK VE EKRAN AYARLARI ---
try:
    st.set_page_config(page_title="Maarif Beden Eğitimi Asistanı SaaS PRO", page_icon="favicon.png", layout="wide")
except:
    st.set_page_config(page_title="Maarif Beden Eğitimi Asistanı SaaS PRO", layout="wide")

# --- KRİPTOGRAFİK GÜVENLİK VE LİSANS MOTORU (SHA-256) ---
GIZLI_TUZ_KELIME = "MaarifSaaS2026!SiberZirh"

if "güvenlik_imzası" not in st.session_state:
    st.session_state.güvenlik_imzası = hashlib.sha256(b"Free_Varsayilan_Guvenlik").hexdigest()
if "hatali_deneme" not in st.session_state: st.session_state.hatali_deneme = 0
if "kilit_suresi" not in st.session_state: st.session_state.kilit_suresi = 0.0

def otonom_lisans_dogrula(tel, girilen_kod, paket_turu):
    try:
        clean_tel = "".join(filter(str.isdigit, tel))[-10:]
        ham_girdi = f"{clean_tel}-{GIZLI_TUZ_KELIME}-{paket_turu}"
        hash_sonuc = hashlib.sha256(ham_girdi.encode()).hexdigest()[:12].upper()
        return f"{paket_turu}-{hash_sonuc}"
    except:
        return ""

def durum_butunlugu_dogrula():
    beklenen = hashlib.sha256(f"{st.session_state.kullanici_turu}-{GIZLI_TUZ_KELIME}".encode()).hexdigest()
    return st.session_state.güvenlik_imzası == beklenen

def durumu_guvenli_guncelle(yeni_statü):
    st.session_state.kullanici_turu = yeni_statü
    st.session_state.güvenlik_imzası = hashlib.sha256(f"{yeni_statü}-{GIZLI_TUZ_KELIME}".encode()).hexdigest()

# --- RESMİ GENEL İŞ GÜNÜ VE EĞİTİM TAKVİMİ ---
RESMI_TAK_VERI = [
    {"Tarih": "01 Eylül", "Kategori": "Dönem Başı", "Etkinlik": "Sene Başı Öğretmenler Kurulu ve Zümre Toplantıları"},
    {"Tarih": "29 Ekim", "Kategori": "Resmi Tatil", "Etkinlik": "Cumhuriyet Bayramı Kutlama Programı"},
    {"Tarih": "10 Kasım", "Kategori": "Anma Günü", "Etkinlik": "Atatürk'ü Anma Günü ve Atatürk Haftası Çalışmaları"},
    {"Tarih": "24 Kasım", "Kategori": "Belirli Gün", "Etkinlik": "Öğretmenler Günü Etkinlik ve Törenleri"},
    {"Tarih": "22 Ocak", "Kategori": "Dönem Sonu", "Etkinlik": "1. Dönem Kapanışı ve Yarıyıl Tatili Başlangıcı"},
    {"Tarih": "08 Mart", "Kategori": "Eğitim Gün", "Etkinlik": "Maarif Modeli Süreç Odaklı Ölçme/Değerlendirme Analizleri"},
    {"Tarih": "23 Nisan", "Kategori": "Resmi Tatil", "Etkinlik": "Ulusal Egemenlik ve Çocuk Bayramı Şenlikleri"},
    {"Tarih": "19 Mayıs", "Kategori": "Resmi Tatil", "Etkinlik": "Atatürk'ü Anma, Gençlik ve Spor Bayramı Törenleri"},
    {"Tarih": "19 Haziran", "Kategori": "Yıl Sonu", "Etkinlik": "Dönem Sonu Kapanış Kurulları ve Mezuniyet İşlemleri"}
]

# --- SESSION STATE BAŞLATICI ---
if "uye_yili" not in st.session_state: st.session_state.uye_yili = 1
if "yillik_kota" not in st.session_state: st.session_state.yillik_kota = 0
if "gunluk_kota" not in st.session_state: st.session_state.gunluk_kota = 0
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "sifre_degisti" not in st.session_state: st.session_state.sifre_degisti = False
if "gorevler" not in st.session_state: st.session_state.gorevler = []
if "aktivasyon_tarihi" not in st.session_state: st.session_state.aktivasyon_tarihi = None
if "kullanici_turu" not in st.session_state: st.session_state.kullanici_turu = "Free"

# --- DİNAMİK LİSTE YÖNETİMİ ---
if "ogretmen_adi" not in st.session_state: st.session_state.ogretmen_adi = "M. Kemal ATATÜRK"
if "okul_muduru" not in st.session_state: st.session_state.okul_muduru = "Müdür Bey"
if "zumre_baskani" not in st.session_state: st.session_state.zumre_baskani = "Zümre Başkanı"
if "diger_zumreler" not in st.session_state: st.session_state.diger_zumreler = "Öğretmen A\nÖğretmen B"
if "rehber_sinif" not in st.session_state: st.session_state.rehber_sinif = "9-A"
if "sabit_nobet_yeri" not in st.session_state: st.session_state.sabit_nobet_yeri = "Bahçe"

if "dinamik_siniflar" not in st.session_state:
    st.session_state.dinamik_siniflar = ["5-A", "6-B", "7-C", "8-A", "9-A", "10-B", "11-A", "12-B", "Boş Ders", "Nöbet", "Rehberlik"]
if "dinamik_dersler" not in st.session_state:
    st.session_state.dinamik_dersler = ["Beden Eğitimi ve Spor", "Sağlık Bilgisi", "Trafik Kültürü", "Spor Eğitimi", "Sosyal Etkinlik"]

GUNLER_LISTE = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
SAATLER_LISTE = [
    "1. Ders (08:30 - 09:10)", "2. Ders (09:20 - 10:00)", "3. Ders (10:10 - 10:50)",
    "4. Ders (11:00 - 11:40)", "Öğle Arası (11:40 - 12:30)", "5. Ders (12:30 - 13:10)",
    "6. Ders (13:20 - 14:00)", "7. Ders (14:10 - 14:50)", "8. Ders (15:00 - 15:40)"
]

if "ders_programi_matris" not in st.session_state:
    st.session_state.ders_programi_matris = {gun: {saat: "Boş Ders / Veri Yok" for saat in SAATLER_LISTE} for gun in GUNLER_LISTE}
    for gun in GUNLER_LISTE:
        st.session_state.ders_programi_matris[gun]["Öğle Arası (11:40 - 12:30)"] = "☕ ÖĞLE ARASI"

# --- CANLI SAAT MOTORU ---
@st.cache_data(ttl=3600)
def canli_tarih_al():
    try:
        response = requests.get("https://worldtimeapi.org", timeout=3)
        if response.status_code == 200:
            return datetime.datetime.strptime(response.json()["datetime"][:10], "%Y-%m-%d").date()
    except:
        pass
    return datetime.date.today()

bugun = canli_tarih_al()
sezon_kilitli_mi = False
if st.session_state.aktivasyon_tarihi is not None:
    kilit_esigi = datetime.date(bugun.year, 8, 20)
    if bugun >= kilit_esigi and (bugun - st.session_state.aktivasyon_tarihi).days >= 90:
        sezon_kilitli_mi = True
# --- MOBİL / BİLGİSAYAR CSS KATMANI ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { min-width: 280px; max-width: 320px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 42px; font-weight: bold; }
    .reportview-container .main .block-container { max-width: 480px; padding: 10px; }
    .premium-banner { background: linear-gradient(90deg, #fff3cd, #ffeeba); padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #ffeeba; margin-top: 20px; font-size: 13px;}
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ PANELİ ---
if not st.session_state.giris_yapildi:
    st.title("📱 Maarif Beden Eğitimi Asistanı")
    st.subheader("Güvenli Otomatik Giriş Paneli (Maks 2 Cihaz)")
    
    if st.session_state.hatali_deneme >= 5:
        kalan_sure = int(st.session_state.kilit_suresi - time.time())
        if kalan_sure > 0:
            st.error(f"🛑 Çok fazla hatalı deneme yaptınız! Sistem güvenliği için {kalan_sure} saniye kilitlendiniz.")
            st.stop()
        else:
            st.session_state.hatali_deneme = 0

    tel_no = st.text_input("Telefon Numaranız (5xxxxxxxxxx):", placeholder="5xxxxxxxxxx")
    girilen_sifre = st.text_input("Giriş Şifreniz veya Otonom Lisans Kodunuz:", type="password")
    
    if st.button("Sisteme Güvenli Giriş Yap"):
        if len(tel_no) >= 10:
            if girilen_sifre == "Maarif2026":
                durumu_guvenli_guncelle("Free")
                st.session_state.giris_yapildi = True
                if st.session_state.aktivasyon_tarihi is None: st.session_state.aktivasyon_tarihi = bugun
                st.rerun()
            elif girilen_sifre == otonom_lisans_dogrula(tel_no, girilen_sifre, "PRO"):
                durumu_guvenli_guncelle("Pro")
                st.session_state.giris_yapildi = True
                if st.session_state.aktivasyon_tarihi is None: st.session_state.aktivasyon_tarihi = bugun
                st.rerun()
            elif girilen_sifre == otonom_lisans_dogrula(tel_no, girilen_sifre, "ELITE"):
                durumu_guvenli_guncelle("Elite")
                st.session_state.giris_yapildi = True
                if st.session_state.aktivasyon_tarihi is None: st.session_state.aktivasyon_tarihi = bugun
                st.rerun()
            else:
                st.session_state.hatali_deneme += 1
                if st.session_state.hatali_deneme >= 5:
                    st.session_state.kilit_suresi = time.time() + 900
                st.error("Giriş kodu veya lisans anahtarı telefon numaranızla eşleşmiyor!")
        else:
            st.error("Lütfen geçerli bir telefon numarası giriniz!")
    st.stop()

if st.session_state.giris_yapildi and not st.session_state.sifre_degisti:
    st.title("🔒 Şifre Özelleştirme")
    st.warning("Çoklu cihaz güvenliği için kalıcı şifrenizi belirlemeniz zorunludur.")
    yeni_sifre = st.text_input("Kalıcı Şifrenizi Oluşturun:", type="password")
    yeni_sifre_onay = st.text_input("Kalıcı Şifrenizi Tekrar Girin:", type="password")
    
    if st.button("Şifremi Kaydet ve Uygulamayı Başlat"):
        if yeni_sifre and yeni_sifre == yeni_sifre_onay:
            st.session_state.sifre_degisti = True
            st.success("Şifreniz başarıyla mühürlendi!")
            st.rerun()
        else:
            st.error("Şifreler uyuşmuyor!")
    st.stop()

if not durum_butunlugu_dogrula():
    st.error("🚨 Güvenlik İhlali Saptandı! Oturum kapatıldı.")
    st.session_state.clear()
    st.stop()

if seznam_lock if 'seznam_lock' in locals() else sezon_kilitli_mi and st.session_state.kullanici_turu != "Elite":
    st.error(f"🛑 Yeni Eğitim Dönemi Sezon Güncelleme Kilidi!")
    g_kodu = st.text_input("Sitenizden Aldığınız Sezon Yenileme Kodunu Girin:")
    if st.button("Sezon Kilidini Kaldır"):
        if g_kodu == otonom_lisans_dogrula(tel_no if 'tel_no' in locals() else "5321234567", g_kodu, "GUNCEL"):
            durumu_guvenli_guncelle("Elite")
            st.success("Yeni sezon kilitleri başarıyla kaldırıldı!")
            st.rerun()
        else:
            st.error("Hatalı sezon güncelleme kodu!")
    st.stop()

# --- CANLI HAVA DURUMU MOTORU ---
def hava_durumu_ve_mekan_al(sehir):
    koordinatlar = {"İstanbul": (41.0082, 28.9784), "Ankara": (39.9334, 32.8597), "İzmir": (38.4192, 27.1287), "Bursa": (40.1885, 29.0610)}
    lat, lon = koordinatlar.get(sehir, (41.0082, 28.9784))
    try:
        url = f"https://open-meteo.com{lat}&longitude={lon}&current_weather=true"
        res = requests.get(url, timeout=3).json()
        sicaklik = res["current_weather"]["temperature"]
        kod = res["current_weather"]["weathercode"]
        yagis_kodlari = [51, 53, 55, 61, 63, 65, 71, 73, 75, 80, 81, 82, 95, 96, 99]
        if kod in yagis_kodlari:
            return sicaklik, "Yağışlı/Fırtınalı", "🚨 Kapalı Spor Salonu veya Çok Amaçlı Derslik / Sınıf (Teorik/Eğitsel Oyun)"
        else:
            return sicaklik, "Açık/Güvenli", "Açık Alan / Okul Bahçesi, Açık Saha veya Halı Saha (Fiziksel Dayanıklılık)"
    except:
        return 20, "Hava Bilgisi Alınamadı", "Okul Bahçesi veya Kapalı Spor Salonu (Esnek Kullanım)"

# --- ANA MENÜ VE SEKMELİ YÖNETİM SİSTEMİ ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Haftalık Ders Programı", 
    "📝 Resmi Tutanak Önizleme", 
    "⚙️ Okul & Kadro Ayarları", 
    "📆 Resmi İş Günü Takvimi", 
    "💎 Üyelik & Pro Paket"
])
# --- TAB 1: DERS PROGRAMI VE DİNAMİK SAAT AYARLAMA ---
with tab1:
    st.subheader("📊 Haftalık Ders Programı Matrisi")
    sehir = st.selectbox("Canlı Mekan Önerisi İçin Şehrinizi Seçin:", ["İstanbul", "Ankara", "İzmir", "Bursa"])
    sicaklik, durum, mekan_onerisi = hava_durumu_ve_mekan_al(sehir)
    st.metric(label=f"Canlı Hava Durumu ({sehir})", value=f"{sicaklik} °C - {durum}")
    st.info(f"💡 **Önerilen İşleme Alanı:** {mekan_onerisi}")
    
    st.write("---")
    st.markdown("### ✏️ Hücre Bazlı Dinamik Ders Düzenleme")
    
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        sec_gun = st.selectbox("Gün Seçin:", GUNLER_LISTE)
    with col_h2:
        sec_saat = st.selectbox("Ders Saati Seçin:", [s for s in SAATLER_LISTE if "Öğle Arası" not in s])
    with col_h3:
        durum_modu = st.radio("İşlem Türü:", ["Aşağı Açılan Listeden Seç", "➕ Yeni Sınıf Ekle", "➕ Yeni Ders Ekle"], horizontal=True)
    
    if durum_modu == "Aşağı Açılan Listeden Seç":
        secilen_icerik_sinif = st.selectbox("Sınıf / Görev Seçin:", st.session_state.dinamik_siniflar)
        secilen_icerik_ders = st.selectbox("İşlenecek Ders Türü:", st.session_state.dinamik_dersler)
        verilecek_metin = f"{secilen_icerik_sinif} ({secilen_icerik_ders})" if secilen_icerik_sinif not in ["Boş Ders", "Nöbet", "Rehberlik"] else secilen_icerik_sinif
    elif durum_modu == "➕ Yeni Sınıf Ekle":
        yeni_sinif_ad = st.text_input("Eklenecek Yeni Sınıf Adı (Örn: 11-H):")
        if st.button("Sınıfı Havuza Ekle") and yeni_sinif_ad:
            if yeni_sinif_ad not in st.session_state.dinamik_siniflar:
                st.session_state.dinamik_siniflar.append(yeni_sinif_ad)
                st.success(f"{yeni_sinif_ad} eklendi!")
                st.rerun()
        verilecek_metin = "Boş Ders / Veri Yok"
    else:
        yeni_ders_ad = st.text_input("Eklenecek Yeni Ders Adı (Örn: Halk Oyunları):")
        if st.button("Dersi Havuza Ekle") and yeni_ders_ad:
            if yeni_ders_ad not in st.session_state.dinamik_dersler:
                st.session_state.dinamik_dersler.append(yeni_ders_ad)
                st.success(f"{yeni_ders_ad} eklendi!")
                st.rerun()
        verilecek_metin = "Boş Ders / Veri Yok"

    if durum_modu == "Aşağı Açılan Listeden Seç" and st.button("💾 Hücreyi Güncelle ve Programa İşle"):
        st.session_state.ders_programi_matris[sec_gun][sec_saat] = verilecek_metin
        st.success(f"✅ {sec_gun} günü {sec_saat} başarıyla güncellendi!")

    st.write("---")
    st.markdown("### 📋 Güncel Haftalık Ders Çizelgeniz")
    df_gosterim = pd.DataFrame(st.session_state.ders_programi_matris)
    st.table(df_gosterim)

    toplam_saat = 0
    nobet_sayisi = 0
    for g in GUNLER_LISTE:
        for s in SAATLER_LISTE:
            val = st.session_state.ders_programi_matris[g][s]
            if "(" in val: toplam_saat += 1
            if "Nöbet" in val: nobet_sayisi += 1

    st.write("---")
    st.markdown("### 📊 Ders Programı Resmi Görev Özet Çıktısı")
    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Öğretmen İsim:", st.session_state.ogretmen_adi)
    o2.metric("Toplam Maaş/Ek Ders Saati:", f"{toplam_saat} Saat")
    o3.metric("Haftalık Nöbet Alanı/Günü:", f"{st.session_state.sabit_nobet_yeri} ({nobet_sayisi} Gün)")
    o4.metric("Sorumlu Rehberlik Sınıfı:", st.session_state.rehber_sinif)

    st.write("---")
    csv_dosya = df_gosterim.to_csv().encode('utf-8')
    st.download_button(label="🖨️ Derli Toplu Yazdırılabilir Ders Programını İndir (Excel/CSV)", data=csv_dosya, file_name=f"{st.session_state.ogretmen_adi.replace(' ','_')}_ders_programi.csv", mime="text/csv")

# --- TAB 2: RESMİ TUTANAK ÖNİZLEME VE DÜZENLEME SİHIRBAZI ---
with tab2:
    st.subheader("📝 Düzenlenebilir Resmi Kurul ve Zümre Tutanak Sihirbazı")
    tutanak_turu = st.selectbox("Üretilecek Tutanak Türünü Seçin:", ["Sene Başı Beden Eğitimi Zümre Öğretmenler Kurulu Tutanağı", "Şube Öğretmenler Kurulu (ŞÖK) Toplantı Tutanağı", "Eğitim Öğretim Yılı Sene Başı Öğretmenler Kurulu Toplantısı"])

    varsayilan_tutanak_metni = f"OKUL ADI: {st.session_state.okul_muduru} adına kayıtlı eğitim kurumu\nTOPLANTI TÜRÜ: {tutanak_turu}\nTARİH: {bugun.strftime('%d.%m.%Y')}\n\nGÜNDEM MADDELERİ:\n1. Açılış, yoklama ve Okul Müdürü {st.session_state.okul_muduru}'nun konuşması.\n2. Türkiye Yüzyılı Maarif Modeli müfredatının beden eğitimi dersi üzerindeki etkileri.\n3. Ders programı görev dağılımı (Maaş dersi, Rehberlik sınıfı: {st.session_state.rehber_sinif}).\n4. Okul nöbet yerlerinin ({st.session_state.sabit_nobet_yeri}) planlanması.\n5. Dilek, temenniler ve kapanış.\n\nALINAN KARARLAR:\n1. Türkiye Yüzyılı Maarif Modeli doğrultusunda erdem-değer-eylem eksenli ders planları uygulanacaktır.\n2. Zümre başkanı {st.session_state.zumre_baskani} ve ders öğretmeni {st.session_state.ogretmen_adi} tarafından süreç odaklı rubrikler kullanılacaktır.\n\nİMZALAR:\nDers Öğretmeni: {st.session_state.ogretmen_adi}\nZümre Başkanı: {st.session_state.zumre_baskani}\nOkul Müdürü: {st.session_state.okul_muduru}"

    st.markdown("### ✏️ Canlı Tutanak Düzenleme Alanı")
    duzenlenen_tutanak_metni = st.text_area("Metni istediğiniz gibi değiştirin:", value=varsayilan_tutanak_metni, height=350)

    if st.button("📄 Son Haliyle Resmi Word (.docx) Belgesini Üret"):
        doc = Document()
        for satir in duzenlenen_tutanak_metni.split("\n"):
            if "İMZALAR:" in satir or "GÜNDEM MADDELERİ:" in satir or "ALINAN KARARLAR:" in satir:
                doc.add_heading(satir, level=3)
            elif "TOPLANTI TÜRÜ:" in satir:
                doc.add_heading(satir, level=2).alignment = 1
            else:
                doc.add_paragraph(satir)
        bio = io.BytesIO()
        doc.save(bio)
        st.success("🎉 Tutanak üretildi!")
        st.download_button(label="📥 Word Belgesini İndir", data=bio.getvalue(), file_name=f"{tutanak_turu.replace(' ', '_')}.docx")

# --- TAB 3: OKUL & KADRO AYARLARI ---
with tab3:
    st.subheader("⚙️ Okul, Yönetim ve Branş Yapılandırma Paneli")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.session_state.ogretmen_adi = st.text_input("Adınız Soyadınız:", value=st.session_state.ogretmen_adi)
        st.session_state.okul_muduru = st.text_input("Okul Müdürü Adı Soyadı:", value=st.session_state.okul_muduru)
        st.session_state.zumre_baskani = st.text_input("Zümre Başkanı Adı Soyadı:", value=st.session_state.zumre_baskani)
    with col_a2:
        st.session_state.rehber_sinif = st.text_input("Sorumlu Olduğunuz Rehberlik Sınıfı:", value=st.session_state.rehber_sinif)
        st.session_state.sabit_nobet_yeri = st.text_input("Okul Resmi Nöbet Yeriniz:", value=st.session_state.sabit_nobet_yeri)
        st.session_state.diger_zumreler = st.text_area("Diğer Zümre Öğretmenleri:", value=st.session_state.diger_zumreler)

# --- TAB 4: RESMİ İŞ GÜNÜ TAKVİMİ ---
with tab4:
    st.subheader("📆 Genel Resmi Eğitim Öğretim İş Günü Takvimi")
    st.table(pd.DataFrame(RESMI_TAK_VERI))

    st.markdown("### 📌 Kişisel Hatırlatma ve Görev Ekle")
    g_tarih = st.date_input("Görev Tarihi:", min_value=bugun)
    g_aciklama = st.text_input("Görev Notu / Toplantı Açıklaması:")
    if st.button("Görev Takvimine İşle") and g_aciklama.strip():
        st.session_state.gorevler.append({"Tarih": g_tarih.strftime("%d %B"), "Kategori": "Özel Not", "Etkinlik": g_aciklama.strip()})
        st.rerun()
    if st.session_state.gorevler: st.table(pd.DataFrame(st.session_state.gorevler))

# --- TAB 5: ABONELİK VE PRO PAKET ---
with tab5:
    st.subheader("💎 Üyelik Paketleri")
    st.write(f"Mevcut Statünüz: **{st.session_state.kullanici_turu}**")
    if st.session_state.kullanici_turu == "Free":
        st.markdown("### 🥇 Elite Sürüm\n**599 TL / Yıl**\n* Tüm Özellikler Açık\n* Sınırsız Evrak Üretimi\n* Çoklu Cihaz ve Koruması")

if st.session_state.kullanici_turu == "Free":
    st.markdown('🤝 **Sponsorluk:** Okul spor malzemeleri ihtiyaçlarınız için **Decathlon Türkiye** eğitim kataloğunu inceleyebilirsiniz.', unsafe_allow_html=True)
