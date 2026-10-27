import streamlit as st
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup
import io
from docx import Document

# --- 1. ÖZELLEŞTİRME VE MARKA ALANI (NO-CODE BRANDING) ---
try:
    st.set_page_config(page_title="Maarif Beden Eğitimi Asistanı PRO", page_icon="favicon.png", layout="wide")
except:
    st.set_page_config(page_title="Maarif Beden Eğitimi Asistanı PRO", layout="wide")

# --- RESMİ BELİRLİ GÜN VE HAFTALAR VERİSİ ---
RESMI_GUNLER = [
    {"Tarih": "29 Ekim", "Etkinlik": "Cumhuriyet Bayramı Tören Hazırlıkları ve Okul Spor Gösterileri"},
    {"Tarih": "10 Kasım", "Etkinlik": "Atatürk'ü Anma Günü ve Saygı Koşusu Organizasyonu"},
    {"Tarih": "24 Kasım", "Etkinlik": "Öğretmenler Günü Spor Müsabakaları ve Ödül Töreni"},
    {"Tarih": "23 Nisan", "Etkinlik": "Ulusal Egemenlik ve Çocuk Bayramı Geleneksel Çocuk Oyunları Şenliği"},
    {"Tarih": "19 Mayıs", "Etkinlik": "Atatürk'ü Anma, Gençlik ve Spor Bayramı Jimnastik ve Koreografi Gösterileri"}
]

# --- 2. OTONOM SAAS VE GÜVENLİK ALTYAPISI (SESSION STATE) ---
if "kullanici_turu" not in st.session_state:
    st.session_state.kullanici_turu = "Free"
if "uye_yili" not in st.session_state:
    st.session_state.uye_yili = 1
if "yillik_kota" not in st.session_state:
    st.session_state.yillik_kota = 0
if "gunluk_kota" not in st.session_state:
    st.session_state.gunluk_kota = 0
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
if "sifre_degisti" not in st.session_state:
    st.session_state.sifre_degisti = False
if "gorevler" not in st.session_state:
    st.session_state.gorevler = []

# --- DERS PROGRAMI HAFIZA ALTYAPISI ---
GUNLER_LISTE = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
SAATLER_LISTE = [f"{i}. Ders" for i in range(1, 9)] + ["Öğle Arası"]

if "ders_programi" not in st.session_state:
    # Boş bir ders programı matrisi oluşturalım
    st.session_state.ders_programi = {gun: {saat: "Boş Ders" for saat in SAATLER_LISTE} for gun in GUNLER_LISTE}
    for gun in GUNLER_LISTE:
        st.session_state.ders_programi[gun]["Öğle Arası"] = "☕ ÖĞLE ARASI"

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

# FİYATLANDIRMA VE SADAKAT MOTORU
artis_katsayisi = 1.0  
baz_yenileme_ucreti = 149
sadakat_indirimi = 0.85 if st.session_state.uye_yili == 2 else (0.75 if st.session_state.uye_yili >= 3 else 1.0)
guncel_yenileme_ucreti = int(baz_yenileme_ucreti * artis_katsayisi * sadakat_indirimi)

# --- MOBİL / BİLGİSAYAR CSS KATMANI ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { min-width: 280px; max-width: 320px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 42px; font-weight: bold; }
    .reportview-container .main .block-container { max-width: 480px; padding: 10px; }
    .premium-banner { background: linear-gradient(90deg, #fff3cd, #ffeeba); padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #ffeeba; margin-top: 20px; font-size: 13px;}
    .timetable-cell { padding: 8px; border: 1px solid #ddd; border-radius: 4px; text-align: center; font-size: 12px; font-weight: 500;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. GİRİŞ VE SAKLI GÜVENLİK EKRANI ---
if not st.session_state.giris_yapildi:
    st.title("📱 Maarif Beden Eğitimi Asistanı")
    st.subheader("Öğretmen Giriş Paneli")
    giriş_turu = st.radio("En Kolay Giriş Seçeneği:", ["🔴 Google ile Giriş Yap", "🍏 Apple ile Giriş Yap", "📞 Telefon Numarası ile Giriş Yap"])
    tel_no = st.text_input("Telefon Numaranız:", placeholder="5xx xxx xx xx")
    gecici_sifre = st.text_input("Geçici Şifre:", type="password")
    
    if st.button("Sisteme Güvenli Giriş Yap"):
        if gecici_sifre == "Maarif2026" and len(tel_no) >= 10:
            st.session_state.giris_yapildi = True
            st.rerun()
        else:
            st.error("Hatalı geçici şifre veya eksik telefon numarası bilgisi!")
    st.stop()

if st.session_state.giris_yapildi and not st.session_state.sifre_degisti:
    st.title("🔒 Güvenlik Ayarı")
    st.warning("Güvenliğiniz amacıyla kendi kalıcı şifrenizi belirlemeniz zorunludur.")
    yeni_sifre = st.text_input("Yeni Şifrenizi Oluşturun:", type="password")
    yeni_sifre_onay = st.text_input("Yeni Şifrenizi Tekrar Girin:", type="password")
    
    if st.button("Şifremi Kaydet ve Uygulamayı Başlat"):
        if yeni_sifre and yeni_sifre == yeni_sifre_onay:
            st.session_state.sifre_degisti = True
            st.success("Şifreniz başarıyla güncellendi!")
            st.rerun()
        else:
            st.error("Şifreler eşleşmiyor!")
    st.stop()

if sezon_kilitli_mi and st.session_state.kullanici_turu != "Elite":
    st.error(f"🛑 {bugun.year} - {bugun.year+1} Eğitim Sezonu Yeni Müfredat Kilidi!")
    st.write("Okulların açılmasına 3 hafta kala plan yetkileri askıya alınmıştır. Güncel planlar için müfredat güncelleme harcını yatırmanız gerekmektedir.")
    st.info(f"Size Özel Güncelleme Ücreti: **{guncel_yenileme_ucreti} TL**")
    lisans_kodu = st.text_input("Müfredat Güncelleme Kodunu Girin:")
    if st.button("Müfredatı Yenile ve Kilidi Kaldır"):
        if lisans_kodu == "GUNCEL99":
            st.session_state.kullanici_turu = "Elite"
            st.success("Tüm kilitler açıldı!")
            st.rerun()
    st.stop()
# --- 6. CANLI HAVA DURUMU VE MEKAN ÖNERİ MOTORU ---
def hava_durumu_ve_mekan_al(sehir):
    koordinatlar = {"İstanbul": (41.0082, 28.9784), "Ankara": (39.9334, 32.8597), "İzmir": (38.4192, 27.1287), "Bursa": (40.1885, 29.0610)}
    lat, lon = koordinatlar.get(sehir, (41.0082, 28.9784))
    try:
        url = f"https://open-meteo.com{lat}&longitude={lon}&current_weather=true"
        res = requests.get(url, timeout=3).json()
        sicaklik = res["current_weather"]["temperature"]
        kod = res["current_weather"]["weathercode"]
        yagis_kodlari = [51, 53, 55, 61, 63, 65, 71, 73, 75, 80, 81, 82, 95, 96, 97]
        if kod in yagis_kodlari:
            return sicaklik, "Yağışlı/Fırtınalı", "🚨 Kapalı Spor Salonu veya Çok Amaçlı Derslik / Sınıf (Teorik/Eğitsel Oyun)"
        else:
            return sicaklik, "Açık/Güvenli", "Açık Alan / Okul Bahçesi, Açık Saha veya Halı Saha (Fiziksel Dayanıklılık ve Parkur)"
    except:
        return 20, "Hava Bilgisi Alınamadı (Güvenli Mod)", "Okul Bahçesi veya Kapalı Spor Salonu (Esnek Kullanım)"

# --- 7. ANA MENÜ VE ARAYÜZ SİSTEMİ ---
st.title("🏆 Türkiye Yüzyılı Maarif Modeli")
st.subheader("Beden Eğitimi ve Spor PRO Öğretmen Asistanı")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Ders Programı Yönetimi", 
    "📝 Resmi Tutanak Sihirbazı", 
    "📆 Çalışma Takvimi & Görevler", 
    "🌐 Canlı Telifsiz Kaynak Kazıcı", 
    "💎 Abonelik & Pro Paket"
])

# --- TAB 1: GELİŞMİŞ DERS PROGRAMI VE DİNAMİK SAAT AYARLAMA ---
with tab1:
    st.subheader("🛠️ Haftalık ve Günlük Ders Saati Konfigüratörü")
    st.info("Bu alandan her günün ders saatini sınıf, Boş Ders, Boş Gün veya Nöbet olarak özelleştirebilirsiniz.")
    
    sehir = st.selectbox("Canlı Mekan Önerisi İçin Şehrinizi Seçin:", ["İstanbul", "Ankara", "İzmir", "Bursa"])
    sicaklik, durum, mekan_onerisi = hava_durumu_ve_mekan_al(sehir)
    st.metric(label=f"Canlı Hava Durumu ({sehir})", value=f"{sicaklik} °C - {durum}")
    st.success(f"**Güncel Hava Durumuna Göre Ders Alanı:** {mekan_onerisi}")
    
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        ayarlanacak_gun = st.selectbox("Düzenlenecek Günü Seçin:", GUNLER_LISTE)
    with c2:
        ayarlanacak_saat = st.selectbox("Düzenlenecek Ders Saatini Seçin:", [s for s in SAATLER_LISTE if s != "Öğle Arası"])
        
    durum_secenekleri = ["Boş Ders", "Boş Gün", "Nöbetçi Öğretmen", "5-A", "6-B", "7-C", "8-A", "9-A", "10-B", "11-C", "12-A", "Sağlık Bilgisi", "Trafik Kültürü"]
    mevcut_deger = st.session_state.ders_programi[ayarlanacak_gun][ayarlanacak_saat]
    
    try:
        varsayilan_idx = durum_secenekleri.index(mevcut_deger)
    except:
        varsayilan_idx = 0
        
    yeni_deger = st.selectbox(f"{ayarlanacak_gun} günü {ayarlanacak_saat} içeriği:", durum_secenekleri, index=varsayilan_idx)
    
    if st.button("🔄 Ders Saatini Programda Güncelle"):
        st.session_state.ders_programi[ayarlanacak_gun][ayarlanacak_saat] = yeni_deger
        st.success(f"Program güncellendi: {ayarlanacak_gun} - {ayarlanacak_saat} ➡️ {yeni_deger}")
    
    st.write("---")
    görünüm_turu = st.radio("Program Görünüm Modu:", ["📊 Haftalık Matris Görünümü", "📱 Günlük Detaylı Akış Görünümü"])
    
    if görünüm_turu == "📊 Haftalık Matris Görünümü":
        st.subheader("Haftalık Ders Programı Tablosu")
        df_program = pd.DataFrame(st.session_state.ders_programi)
        st.dataframe(df_program, use_container_width=True)
    else:
        st.subheader("Günlük Ders Akış Kartları")
        secilen_görünüm_günü = st.selectbox("Görüntülenecek Günü Seçin:", GUNLER_LISTE, key="v_gun")
        for s in SAATLER_LISTE:
            ders_icerik = st.session_state.ders_programi[secilen_görünüm_günü][s]
            if ders_icerik == "☕ ÖĞLE ARASI":
                st.warning(f"⏰ {s}")
            elif ders_icerik in ["Boş Ders", "Boş Gün"]:
                st.info(f"⚪ {s}: {ders_icerik}")
            elif ders_icerik == "Nöbetçi Öğretmen":
                st.error(f"🚨 {s}: {ders_icerik} (Nöbet Görevi)")
            else:
                col_k1, col_k2 = st.columns([3, 1])
                with col_k1:
                    st.success(f"🏃 {s}: {ders_icerik} - Beden Eğitimi ve Spor")
                with col_k2:
                    if st.button("📄 Plana Git", key=f"go_{secilen_görünüm_günü}_{s}"):
                        st.toast(f"{ders_icerik} dersine ait Maarif Modeli şablonu hafızaya alındı!")

    st.write("---")
    st.subheader("📋 Türkiye Yüzyılı Maarif Modeli Plan Yapılandırıcı")
    st.text(f"Yıllık Plan İndirme: {st.session_state.yillik_kota}/5 | Günlük Plan İndirme: {st.session_state.gunluk_kota}/20")
    
    def kota_kontrol_ve_indir(tur):
        if st.session_state.kullanici_turu == "Free":
            if tur == "Yıllık" and st.session_state.yillik_kota >= 5:
                st.error("🛑 Sınıra ulaştınız! Devam etmek için paket yükseltin veya Jeton kullanın.")
                return False
            if tur == "Günlük" and st.session_state.gunluk_kota >= 20:
                st.error("🛑 Sınıra ulaştınız! Devam etmek için paket yükseltin veya Jeton kullanın.")
                return False
        if tur == "Yıllık":
            st.session_state.yillik_kota += 1
        else:
            st.session_state.gunluk_kota += 1
        return True

    if st.button("📥 Kazanım ve Erdem Entegreli Yıllık Planı İndir (Müfredata Uyumlu)"):
        if kota_kontrol_ve_indir("Yıllık"):
            st.success("✅ Yıllık Plan başarıyla üretildi ve Excel/Word formatında indirildi.")

    if st.button("📥 Erdem-Değer-Eylem Odaklı Günlük Planı İndir"):
        if kota_kontrol_ve_indir("Günlük"):
            st.success("✅ Günlük Ders Planı (Süreç Değerlendirme Formu Dahil) cihazınıza aktarıldı.")
# --- TAB 2: RESMİ TUTANAK SİHİRBAZI (python-docx ALTYAPISI) ---
with tab2:
    st.subheader("📝 Resmi Kurul ve Zümre Tutanak Üreteci")
    st.info("Sadece gerekli alanları doldurarak okul idaresine teslim edebileceğiniz resmi tutanakları .docx (Word) formatında otomatik üretebilirsiniz.")
    
    tutanak_turu = st.selectbox("Üretilecek Tutanak Türünü Seçin:", [
        "Sene Başı Beden Eğitimi Zümre Öğretmenler Kurulu Tutanاı",
        "Şube Öğretmenler Kurulu (ŞÖK) Toplantı Tutanاı",
        "Eğitim Öğretim Yılı Sene Başı Öğretmenler Kurulu Toplantısı"
    ])
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        okul_adi = st.text_input("Okul Adı:", placeholder="Örn: Cumhuriyet Anadolu Lisesi")
        toplantı_tarihi = st.date_input("Toplantı Tarihi:", value=bugun)
    with col_t2:
        zumre_baskani = st.text_input("Zümre Başkanı Öğretmen:", placeholder="Adı Soyadı")
        katilimci_ogretmenler = st.text_area("Katılımcı Öğretmenler / Üyeler:", placeholder="Her satıra bir isim yazın")

    gundem_maddeleri = st.text_area("Gündem Maddeleri (Her satıra bir madde):", value="1. Açılış ve yoklama.\n2. Türkiye Yüzyılı Maarif Modeli müfredatının incelenmesi.\n3. Ders işleme alanlarının (Spor Salonu/Bahçe) hava durumuna göre planlanması.\n4. Dilek ve temenniler, kapanış.")

    if st.button("📄 Resmi Word (.docx) Tutanağını Otomatik Üret"):
        if not okul_adi or not zumre_baskani:
            st.error("Lütfen Okul Adı ve Zümre Başkanı alanlarını boş bırakmayınız.")
        else:
            # python-docx ile arka planda resmi şablon oluşturma
            doc = Document()
            doc.add_heading(okul_adi.upper(), level=1).alignment = 1
            doc.add_heading(tutanak_turu.upper(), level=2).alignment = 1
            
            doc.add_paragraph(f"\n**Toplantı Tarihi:** {toplantı_tarihi.strftime('%d.%m.%Y')}")
            doc.add_paragraph(f"**Zümre Başkanı:** {zumre_baskani}")
            doc.add_paragraph(f"**Katılımcı Üyeler:**\n{katilimci_ogretmenler}")
            
            doc.add_heading("GÜNDEM MADDELERİ", level=3)
            doc.add_paragraph(gundem_maddeleri)
            
            doc.add_heading("ALINAN KARARLAR", level=3)
            doc.add_paragraph("1. Derslerin Türkiye Yüzyılı Maarif Modeli'nin getirdiği erdem-değer-eylem ekseninde, süreç odaklı ölçme araçları (rubrikler) kullanılarak işlenmesine karar verilmiştir.\n2. Hava şartlarının olumsuz olduğu günlerde asistan üzerindeki akıllı mekan önerisi takip edilerek derslerin teorik derslik veya kapalı çok amaçlı salonlarda yapılması kararlaştırılmıştır.")
            
            # Belleğe yazma ve indirme butonu sunma
            bio = io.BytesIO()
            doc.save(bio)
            st.success("🎉 Resmi tutanak belgesi sıfır hata ile arka planda hazırlandı!")
            st.download_button(
                label="📥 Üretilen Resmi Word Belgesini İndir",
                data=bio.getvalue(),
                file_name=f"{tutanak_turu.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# --- TAB 3: ÇALIŞMA TAKVİMİ VE HATIRLATICI MODÜLÜ ---
with tab3:
    st.subheader("📆 Resmi ve Kişisel Çalışma Takvimi")
    st.write("**📌 Yeni Toplantı, Görev veya Sınav Hatırlatması Ekle**")
    g_tarih = st.date_input("Görev Tarihi:", min_value=bugun, key="gtar")
    g_aciklama = st.text_input("Açıklama / Görev Notu:", placeholder="Zümre toplantısı, 1. Sınav uygulaması vb.", key="gacik")
    
    if st.button("Görev Takvimine Ekle"):
        if g_aciklama.strip():
            st.session_state.gorevler.append({"Tarih": g_tarih.strftime("%d %B"), "Etkinlik": f"📌 {g_aciklama.strip()}"})
            st.success("Görev takvime başarıyla işlendi!")
        else:
            st.error("Lütfen görev açıklaması giriniz.")
            
    st.write("---")
    tum_etkinlikler = RESMI_GUNLER + st.session_state.gorevler
    df_takvim = pd.DataFrame(tum_etkinlikler)
    st.table(df_takvim)
    
    csv_veri = df_takvim.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Tüm Çalışma Takvimini İndir (Excel/CSV)", data=csv_veri, file_name="maarif_calisma_takvimi.csv", mime="text/csv")

# --- TAB 4: CANLI TELİFSİZ KAYNAK KAZICI ---
with tab4:
    st.subheader("🛡️ %0 Hata Paylı Kamu Malı Bilgi Ağı")
    st.markdown("[🔗 EBA (Eğitim Bilişim Ağı) Resmi Sitesine Git](https://eba.gov.tr)")
    st.markdown("[🔗 ÖBA (Öğretmen Bilişim Ağı) Müfredat Sayfasına Git](https://oba.gov.tr)")
    
    if st.button("🌐 Vikipedi Beden Eğitimi Akademik Verisini Canlı Tara"):
        try:
            viki_url = "https://wikipedia.org"
            html = requests.get(viki_url, timeout=3).text
            soup = BeautifulSoup(html, "html.parser")
            paragraf = soup.find("p").text
            st.write("**Canlı Çekilen Kamu Bilgisi:**")
            st.info(paragraf)
        except:
            st.info("Dahili Bilgi Kitaplığı: Beden eğitimi; insanın fiziksel, zihinsel ve sosyal gelişimini spor ve hareketler yoluyla sağlayan telifsiz pedagojik disiplindir.")

# --- TAB 5: ABONELİK VE PRO PAKET (UPSELLING) ---
with tab5:
    st.subheader("💎 Üyelik Modelleri ve Akıllı Geçiş Geçidi")
    st.write(f"Mevcut Üyelik Statünüz: **{st.session_state.kullanici_turu}**")
    
    if st.session_state.kullanici_turu == "Free":
        st.write("---")
        st.subheader("🎫 Tekil Plan İndirme Jetonu")
        st.markdown("[🛒 39 TL'ye Anlık İndirme Jetonu Satın Al (Ödeme Sayfası)](#)")
        st.write("---")
        st.subheader("🚀 Avantajlı Yıllık Paketler")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🥉 Başlangıç\n**249 TL / Yıl**\n* Sınırsız Program\n* +50 Plan İndirme\n\n[Satın Al](#)")
        with col2:
            st.markdown("### 🥈 Standart PRO\n**399 TL / Yıl**\n* Sınırsız Plan İndirme\n* Canlı Veri Tarayıcı\n\n[Satın Al](#)")
        with col3:
            st.markdown("### 🥇 Elite Sürüm\n**599 TL / Yıl**\n* Tüm Özellikler Açık\n* Resmi Tutanak Sihirbazı\n* Sıfır Reklam\n\n[Satın Al](#)")
            
    elif st.session_state.kullanici_turu == "Pro":
        st.subheader("🪜 Üst Pakete Geçiş (Sadece Fark Ödeyerek Sürüm Yükseltin!)")
        st.markdown("[🥈 Sadece 150 TL Fark Ödeyerek Standart PRO Sürümüne Yükselt](#)")
        st.markdown("[🥇 Sadece 350 TL Fark Ödeyerek Tüm İmkanlar Dahil Elite Paketine Yükselt](#)")

# --- 8. ZARİF VE KULLANICI DOSTU SPONSOR/REKLAM ŞERİDİ ---
if st.session_state.kullanici_turu == "Free":
    st.markdown("""
        <div class="premium-banner">
            🤝 <b>Sponsorluk Alanı:</b> Türkiye geneli okul spor malzemeleri ihtiyaçlarınız için <b>Decathlon Türkiye</b> eğitim kataloğunu inceleyebilirsiniz. <a href='#'>Kampanyalı Katalog Ara</a>
        </div>
        """, unsafe_allow_html=True)
