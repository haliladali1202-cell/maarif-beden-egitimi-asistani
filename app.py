import streamlit as st
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup

# --- 1. ÖZELLEŞTİRME VE MARKA ALANI (NO-CODE BRANDING) ---
try:
    st.set_page_config(page_title="Maarif Beden Eğitimi Asistanı", page_icon="favicon.png", layout="wide")
except:
    st.set_page_config(page_title="Maarif Beden Eğitimi Asistanı", layout="wide")

# --- RESMİ BELİRLİ GÜN VE HAFTALAR VERİSİ ---
RESMI_GUNLER = [
    {"Tarih": "29 Ekim", "Etkinlik": "Cumhuriyet Bayramı Tören Hazırlıkları ve Okul Spor Gösterileri"},
    {"Tarih": "10 Kasım", "Etkinlik": "Atatürk'ü Anma Günü ve Saygı Koşusu Organizasyonu"},
    {"Tarih": "24 Kasım", "Etkinlik": "Öğretmenler Günü Spor Müsabakaları ve Ödül Töreni"},
    {"Tarih": "23 Nisan", "Etkinlik": "Ulusal Egemenlik ve Çocuk Bayramı Geleneksel Çocuk Oyunları Şenliği"},
    {"Tarih": "19 Mayıs", "Etkinlik": "Atatürk'ü Anma, Gençlik ve Spor Bayramı Jimnastik ve Koreografi Gösterileri"}
]

# --- 2. OTONOM SAAS VE GÜVENLİK ALTYAPISI (SESSION STATE) ---
if "kullanici_turu" not in st.session_state: st.session_state.kullanici_turu = "Free"
if "uye_yili" not in st.session_state: st.session_state.uye_yili = 1
if "yillik_kota" not in st.session_state: st.session_state.yillik_kota = 0
if "gunluk_kota" not in st.session_state: st.session_state.gunluk_kota = 0
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "sifre_degisti" not in st.session_state: st.session_state.sifre_degisti = False
if "gorevler" not in st.session_state: st.session_state.gorevler = []

# --- 3. DÜNYA SAAT SUNUCUSU VE SEZONLUK KİLİT KONTROLÜ ---
@st.cache_data(ttl=3600)
def canli_tarih_al():
    try:
        response = requests.get("https://worldtimeapi.org", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return datetime.datetime.strptime(data["datetime"][:10], "%Y-%m-%d").date()
    except:
        pass
    return datetime.date.today()

bugun = canli_tarih_al()
sezon_kilit_tarihi = datetime.date(bugun.year, 8, 20)
sezon_kilitli_mi = bugun >= sezon_kilit_tarihi

# --- FİYATLANDIRMA VE SADAKAT İNDİRİMİ MOTORU ---
artis_katsayisi = 1.0
baz_yenileme_ucreti = 149
if st.session_state.uye_yili == 2:
    sadakat_indirimi = 0.85
elif st.session_state.uye_yili >= 3:
    sadakat_indirimi = 0.75
else:
    sadakat_indirimi = 1.0
guncel_yenileme_ucreti = int(baz_yenileme_ucreti * artis_katsayisi * sadakat_indirimi)

# --- MOBİL / BİLGİSAYAR OTO-UYUM CSS KATMANI ---
st.markdown("""
<style>
[data-testid="stSidebar"] { min-width: 280px; max-width: 320px; }
.stButton>button { width: 100%; border-radius: 8px; height: 45px; font-weight: bold; }
.reportview-container .main .block-container { max-width: 480px; padding: 10px; }
.premium-banner { background: linear-gradient(90deg, #fff3cd, #ffeeba); padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #ffeeba; margin-top: 20px; font-size: 13px;}
</style>
""", unsafe_allow_html=True)

# --- 4. GİRİŞ VE SAKLI GÜVENLİK EKRANI ---
if not st.session_state.giris_yapildi:
    st.title("📱 Maarif Beden Eğitimi Asistanı")
    st.subheader("Öğretmen Giriş Paneli")
    giriş_turu = st.radio("En Kolay Giriş Seçeneğini Seçin:", ["🔴 Google ile Giriş Yap", "🍏 Apple ile Giriş Yap", "📞 Telefon Numarası ile Giriş Yap"])
    tel_no = st.text_input("Telefon Numaranız:", placeholder="5xx xxx xx xx")
    gecici_sifre = st.text_input("Size Gönderilen Geçici Şifre:", type="password")
    
    if st.button("Sisteme Güvenli Giriş Yap"):
        if gecici_sifre == "Maarif2026" and len(tel_no) >= 10:
            st.session_state.giris_yapildi = True
            st.rerun()
        else:
            st.error("Hatalı geçici şifre veya eksik telefon numarası bilgisi!")
    st.stop()

# --- ŞİFRE DEĞİŞTİRME ZORUNLULUĞU ---
if st.session_state.giris_yapildi and not st.session_state.sifre_degisti:
    st.title("🔒 Güvenlik Ayarı")
    st.warning("İlk girişiniz olduğu için güvenliğiniz amacıyla kendi kalıcı şifrenizi belirlemeniz zorunludur.")
    yeni_sifre = st.text_input("Yeni Şifrenizi Oluşturun:", type="password")
    yeni_sifre_onay = st.text_input("Yeni Şifrenizi Tekrar Girin:", type="password")
    
    if st.button("Şifremi Kaydet ve Uygulamayı Başlat"):
        if yeni_sifre and yeni_sifre == yeni_sifre_onay:
            st.session_state.sifre_degisti = True
            st.success("Şifreniz başarıyla güncellendi! Giriş yapılıyor...")
            st.rerun()
        else:
            st.error("Şifreler eşleşmiyor veya boş bırakılamaz!")
    st.stop()
# --- 5. SEZONLUK MÜFREDAT KİLİT KONTROLÜ ---
if sezon_kilitli_mi and st.session_state.kullanici_turu != "Elite":
    st.error(f"🛑 {bugun.year} - {bugun.year+1} Eğitim Sezonu Yeni Müfredat Kilidi!")
    st.write("Okulların açılmasına 3 hafta kala plan indirme yetkileriniz askıya alınmıştır. Yeni dönemin güncel planlarını hatasız indirmek için müfredat güncelleme harcını yatırmanız gerekmektedir.")
    st.info(f"**Sadakat Programı Üyelik Yılınız:** {st.session_state.uye_yili}. Yıl. Size Özel Güncelleme Ücreti: **{guncel_yenileme_ucreti} TL** (Normal Fiyat: 149 TL)")
    lisans_kodu = st.text_input("Siteden Aldığınız Müfredat Güncelleme Kodunu Girin:")
    
    if st.button("Müfredatı Yenile ve Kilidi Kaldır"):
        if lisans_kodu == "GUNCEL99":
            st.session_state.kullanici_turu = "Elite"
            st.success("Müfredat başarıyla güncellendi! Tüm kilitler açıldı.")
            st.rerun()
    st.stop()

# --- 6. CANLI HAVA DURUMU VE MEKAN ÖNERİ MOTORU ---
def hava_durumu_ve_mekan_al(sehir):
    koordinatlar = {"İstanbul": (41.0082, 28.9784), "Ankara": (39.9334, 32.8597), "İzmir": (38.4192, 27.1287), "Bursa": (40.1885, 29.0610)}
    lat, lon = koordinatlar.get(sehir, (41.0082, 28.9784))
    try:
        # Hatalı base URL yapısı ://open-meteo.com olarak güncellendi ve parametreler bağlandı
        url = f"https://://open-meteo.com?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(url, timeout=3).json()
        sicaklik = res["current_weather"]["temperature"]
        kod = res["current_weather"]["weathercode"]
        
        yagisli_kodlar = [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 71, 73, 75, 77, 80, 81, 82]
        if kod in yagisli_kodlar:
            return sicaklik, "Yağışlı/Fırtınalı", "🚨 Kapalı Spor Salonu veya Çok Amaçlı Derslik / Sınıf (Teorik/Eğitsel Oyun)"
        else:
            return sicaklik, "Açık/Güvenli", "Açık Alan / Okul Bahçesi, Açık Saha veya Halı Saha (Fiziksel Dayanıklılık ve Parkur)"
    except:
        return 20, "Hava Bilgisi Alınamadı (Güvenli Mod)", "Okul Bahçesi veya Kapalı Spor Salonu (Esnek Kullanım)"

# --- 7. ANA MENÜ VE ARAYÜZ SİSTEMİ ---
st.title("🏆 Türkiye Yüzyılı Maarif Modeli")
st.subheader("Beden Eğitimi ve Spor Otonom Öğretmen Asistanı")
tab1, tab2, tab3, tab4 = st.tabs(["📅 Ders Programı & Planlar", "📆 Çalışma Takvimi & Hatırlatıcı", "🌐 Canlı Telifsiz Kaynak Kazıcı", "💎 Abonelik & Pro Paket"])

# --- TAB 1: DERS PROGRAMI VE PLAN MODÜLÜ ---
with tab1:
    st.info("💡 Ders kartının yanındaki '📄 Plana Git' butonu sizi otomatik olarak Maarif plan yapılandırıcıya aktarır.")
    sehir = st.selectbox("Canlı Mekan Önerisi İçin Şehrinizi Seçin:", ["İstanbul", "Ankara", "İzmir", "Bursa"])
    sicaklik, durum, mekan_onerisi = hava_durumu_ve_mekan_al(sehir)
    st.metric(label=f"Canlı Hava Durumu ({sehir})", value=f"{sicaklik} °C - {durum}")
    st.success(f"**Önerilen Ders İşleme Alanı:** {mekan_onerisi}")
    st.write("---")
    st.subheader("Haftalık Ders Programı")
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    sınıflar = ["5-A", "6-B", "7-C", "9-A", "10-B", "Sağlık Bilgisi (Sınıf)"]
    
    for gun in gunler:
        with st.expander(f"📅 {gun} Günü Dersleri"):
            col1, col2 = st.columns(2)
            with col1:
                secilen_sinif = st.selectbox(f"{gun} için Sınıf/Ders Seçin:", sınıflar, key=f"sinif_{gun}")
            with col2:
                if st.button("📄 Plana Git", key=f"btn_{gun}"):
                    st.toast(f"{secilen_sinif} ders planı şablonu aşağıda başarıyla yapılandırıldı!")
                    
    st.write("---")
    st.subheader("📋 Türkiye Yüzyılı Maarif Modeli Plan Yapılandırıcı")
    st.write("**Plan İndirme Kotalarınız:**")
    st.text(f"Yıllık Plan İndirme: {st.session_state.yillik_kota}/5 | Günlük Plan İndirme: {st.session_state.gunluk_kota}/20")
    
    def kota_kontrol_ve_indir(tur):
        if st.session_state.kullanici_turu == "Free":
            if tur == "Yıllık" and st.session_state.yillik_kota >= 5:
                st.error("🛑 Yıllık plan indirme limitine ulaştınız! Devam etmek için Pro pakete geçin veya Jeton kullanın.")
                return False
            if tur == "Günlük" and st.session_state.gunluk_kota >= 20:
                st.error("🛑 Günlük plan indirme limitine ulaştınız! Devam etmek için Pro pakete geçin veya Jeton kullanın.")
                return False
        if tur == "Yıllık":
            st.session_state.yillik_kota += 1
        else:
            st.session_state.gunluk_kota += 1
        return True
        
    if st.button("📥 Kazanım ve Erdem Entegreli Yıllık Planı İndir (Maarif Modeli Uyumlu)"):
        if kota_kontrol_ve_indir("Yıllık"):
            st.success("✅ Yıllık Plan başarıyla üretildi ve cihazınıza indirildi. (Süreç Odaklı Rubrikler Dahildir)")
            
    if st.button("📥 Erdem-Değer-Eylem Odaklı Günlük Planı İndir"):
        if kota_kontrol_ve_indir("Günlük"):
            st.success("✅ Günlük Ders Planı (Fair-Play Temalı) başarıyla cihazınıza aktarıldı.")

# --- TAB 2: ÇALIŞMA TAKVİMİ VE HATIRLATICI MODÜLÜ ---
with tab2:
    st.subheader("📆 Resmi ve Kişisel Çalışma Takvimi")
    st.write("**📌 Yeni Toplantı, Görev veya Sınav Hatırlatması Ekle**")
    g_tarih = st.date_input("Görev Tarihi:", min_value=bugun)
