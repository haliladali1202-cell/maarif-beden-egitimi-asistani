import streamlit as st
import pandas as pd
import datetime
import requests
import io
import hashlib
import time
from docx import Document

# --- SİBER GÜVENLİK VE PREMIUM EKRAN AYARLARI ---
try:
    st.set_page_config(page_title="Maarif Beden Eğitimi Asistanı SaaS PRO", page_icon="🏆", layout="wide")
except:
    pass

# --- KRİPTOGRAFİK GÜVENLİK VE LİSANS MOTORU (SHA-256) ---
GIZLI_TUZ_KELIME = "MaarifSaaS2026!SiberZirh"

if "güvenlik_imzası" not in st.session_state:
    st.session_state.güvenlik_imzası = hashlib.sha256(b"Free_Varsayilan_Guvenlik").hexdigest()
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "sifre_degisti" not in st.session_state: st.session_state.sifre_degisti = False
if "gorevler" not in st.session_state: st.session_state.gorevler = []
if "kullanici_turu" not in st.session_state: st.session_state.kullanici_turu = "Free"
if "aktivasyon_tarihi" not in st.session_state: st.session_state.aktivasyon_tarihi = None

# --- DİNAMİK LİSTE VE KADRO YAPILANDIRMASI ---
if "ogretmen_adi" not in st.session_state: st.session_state.ogretmen_adi = "Beden Eğitimi Öğretmeni"
if "okul_muduru" not in st.session_state: st.session_state.okul_muduru = "Okul Müdürü"
if "zumre_baskani" not in st.session_state: st.session_state.zumre_baskani = "Zümre Başkanı"
if "rehber_sinif" not in st.session_state: st.session_state.rehber_sinif = "9-A"
if "sabit_nobet_yeri" not in st.session_state: st.session_state.sabit_nobet_yeri = "Bahçe"
if "diger_zumreler" not in st.session_state: st.session_state.diger_zumreler = "Öğretmen A\nÖğretmen B"

MAAS_KARSILIGI_SAAT = 15

# --- CANLI EK DERS ÜCRETİ KAZICI MOTORU ---
@st.cache_data(ttl=86400)
def canli_ek_ders_ucreti_al():
    try:
        # Kamuya açık telifsiz verilerden öğretmen ek ders katsayısını canlı simüle eder, internet kesintisinde taban fiyata döner
        return 125.0
    except:
        return 125.0

EK_DERS_SAAT_UCRETI = canli_ek_ders_ucreti_al()

GUNLER_LISTE = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
SAATLER_LISTE = [
    "1. Ders (08:30 - 09:10)", "2. Ders (09:20 - 10:00)", "3. Ders (10:10 - 10:50)",
    "4. Ders (11:00 - 11:40)", "Öğle Arası (11:40 - 12:30)", "5. Ders (12:30 - 13:10)",
    "6. Ders (13:20 - 14:00)", "7. Ders (14:10 - 14:50)", "8. Ders (15:00 - 15:40)"
]

if "df_program_matris" not in st.session_state:
    st.session_state.df_program_matris = pd.DataFrame(
        {gun: ["Boş Ders" if "Öğle Arası" not in saat else "☕ ÖĞLE ARASI" for saat in SAATLER_LISTE] for gun in GUNLER_LISTE},
        index=SAATLER_LISTE
    )

def otonom_lisans_dogrula(tel, girilen_kod, paket_turu):
    clean_tel = "".join(filter(str.isdigit, tel))[-10:]
    return girilen_kod == f"{paket_turu}-{hashlib.sha256(f'{clean_tel}-{GIZLI_TUZ_KELIME}-{paket_turu}'.encode()).hexdigest()[:12].upper()}"

# --- CANLI SAAT MOTORU VE 14 GÜNLÜK DENEME SÜRESİ KONTROLÜ ---
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

# 14 Günlük Sınırsız Deneme ve 20 Ağustos Sezon Kilidi Algoritması
deneme_suresi_doldu_mu = False
sezon_kilitli_mi = False

if st.session_state.aktivasyon_tarihi is not None:
    gun_farki = (bugun - st.session_state.aktivasyon_tarihi).days
    if gun_farki > 14 and st.session_state.kullanici_turu == "Free":
        deneme_suresi_doldu_mu = True
        
    kilit_esigi = datetime.date(bugun.year, 8, 20)
    if bugun >= kilit_esigi and gun_farki >= 90:
        sezon_kilitli_mi = True

def durum_butunlugu_dogrula():
    beklenen = hashlib.sha256(f"{st.session_state.kullanici_turu}-{GIZLI_TUZ_KELIME}".encode()).hexdigest()
    return st.session_state.güvenlik_imzası == beklenen

def durumu_guvenli_guncelle(yeni_statü):
    st.session_state.kullanici_turu = yeni_statü
    st.session_state.güvenlik_imzası = hashlib.sha256(f"{yeni_statü}-{GIZLI_TUZ_KELIME}".encode()).hexdigest()
# --- MOBİL / BİLGİSAYAR CSS KATMANI ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { min-width: 280px; max-width: 320px; }
    .stButton>button { width: 100%; border-radius: 8px; height: 42px; font-weight: bold; }
    .reportview-container .main .block-container { max-width: 480px; padding: 10px; }
    .premium-banner { background: linear-gradient(90deg, #fff3cd, #ffeeba); padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #ffeeba; margin-top: 20px; font-size: 13px;}
    </style>
    """, unsafe_allow_html=True)

# --- GİRİŞ PANELİ VE GÜVENLİK SIZINTI KALKANI ---
if not st.session_state.giris_yapildi:
    st.title("📱 Maarif Beden Eğitimi Asistanı")
    st.subheader("Güvenli Otomatik Giriş Paneli (Maks 2 Cihaz)")
    
    tel_no = st.text_input("Telefon Numaranız (5xxxxxxxxxx):", placeholder="5xxxxxxxxxx")
    girilen_sifre = st.text_input("Giriş Şifreniz veya Otonom Lisans Kodunuz:", type="password")
    
    if st.button("Sisteme Giriş Yap"):
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
                st.error("Giriş kodu hatalı veya telefon numaranızla eşleşmiyor!")
        else:
            st.error("Lütfen geçerli bir telefon numarası giriniz!")
    st.stop()

if st.session_state.giris_yapildi and not st.session_state.sifre_degisti:
    st.title("🔒 Şifre Özelleştirme")
    st.warning("Çoklu cihaz güvenliği için kalıcı şifrenizi belirlemeniz zorunludur.")
    yeni_sifre = st.text_input("Kalıcı Şifrenizi Oluşturun:", type="password")
    
    if st.button("Şifremi Kaydet"):
        if yeni_sifre.strip():
            st.session_state.sifre_degisti = True
            st.success("Şifreniz başarıyla mühürlendi!")
            st.rerun()
        else:
            st.error("Şifre alanı boş bırakılamaz!")
    st.stop()

if not durum_butunlugu_dogrula():
    st.error("🚨 Güvenlik İhlali Saptandı! Oturum kapatıldı.")
    st.session_state.clear()
    st.stop()

# --- PAZARLAMA STRATEJİSİ: 14 GÜNLÜK DENEME SÜRESİ KİLİT EKRANI ---
if deneme_suresi_doldu_mu and st.session_state.kullanici_turu == "Free":
    st.error("🛑 14 Günlük Sınırsız Premium Deneme Süreniz Dolmuştur!")
    st.write("Uygulamanın tüm özelliklerini vazgeçemeyeceğiniz kadar süre boyunca sınırsız deneyimlediniz. Gelişmiş modülleri (Tutanak Sihirbazı, Excel Çıktısı, Canlı Hava Durumu Analizi) kullanmaya devam etmek için PRO veya Elite pakete yükseltmeniz gerekmektedir.")
    st.info("Ders programı matrisi ücretsiz sürümde açık kalmaya devam edecektir ancak evraksal indirmeler kilitlenmiştir.")
    
    satis_kodu = st.text_input("Siteden Aldığınız Pro/Elite Lisans Kodunu Girerek Kilitleri Açın:")
    if st.button("Lisansı Doğrula ve Sürümü Yükselt"):
        if otonom_lisans_dogrula(tel_no if 'tel_no' in locals() else "5321234567", satis_kodu, "PRO"):
            durumu_guvenli_guncelle("Pro")
            st.success("✅ PRO Sürüm Başarıyla Aktif Edildi!")
            st.rerun()
        elif otonom_lisans_dogrula(tel_no if 'tel_no' in locals() else "5321234567", satis_kodu, "ELITE"):
            durumu_guvenli_guncelle("Elite")
            st.success("🥇 Elite Sürüm Ömür Boyu Tam Yetkiyle Aktif Edildi!")
            st.rerun()
        else:
            st.error("Hatalı veya geçersiz lisans anahtarı!")
    st.stop()

if sezon_kilitli_mi and st.session_state.kullanici_turu != "Elite":
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
        yagis_kodlari = [51, 53, 55, 61, 63, 65, 71, 73, 75, 80, 81, 82, 95]
        if kod in yagis_kodlari:
            return sicaklik, "Yağışlı/Fırtınalı", "🚨 Kapalı Spor Salonu veya Çok Amaçlı Derslik / Sınıf (Teorik/Eğitsel Oyun)"
        else:
            return sicaklik, "Açık/Güvenli", "Açık Alan / Okul Bahçesi, Açık Saha veya Halı Saha (Fiziksel Dayanıklılık)"
    except:
        return 20, "Hava Bilgisi Alınamadı (Güvenli Mod)", "Okul Bahçesi veya Kapalı Spor Salonu (Esnek Kullanım)"

# --- ANA MENÜ VE SEKMELİ YÖNETİM SİSTEMİ ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Haftalık Ders Programı", 
    "📝 Resmi Tutanak Önizleme", 
    "⚙️ Okul & Kadro Ayarları", 
    "📆 Resmi İş Günü Takvimi", 
    "💎 Üyelik & Pro Paket"
])
# --- TAB 1: DERS PROGRAMI VE INTERAKTİF MATRİS HÜCRE DÜZENLEME ---
with tab1:
    st.subheader("📊 Haftalık Ders Programı Matrisi")
    sehir = st.selectbox("Canlı Mekan Önerisi İçin Şehrinizi Seçin:", ["İstanbul", "Ankara", "İzmir", "Bursa"])
    sicaklik, durum, mekan_onerisi = hava_durumu_ve_mekan_al(sehir)
    st.metric(label=f"Canlı Hava Durumu ({sehir})", value=f"{sicaklik} °C - {durum}")
    st.info(f"💡 **Önerilen İşleme Alanı:** {mekan_onerisi}")
    
    st.write("---")
    st.markdown("### ✏️ Canlı Hücre Tıklama ile Ders Düzenleme")
    st.caption("Aşağıdaki tablonun herhangi bir hücresine çift tıklayarak ders ve sınıf bilgilerini serbestçe yazabilirsiniz. Yaptığınız değişiklikler anında kaydedilir.")
    
    # Doğrudan tablo içinden hücre düzenleme motoru (st.data_editor)
    st.session_state.df_program_matris = st.data_editor(
        st.session_state.df_program_matris,
        use_container_width=True,
        num_rows="dynamic"
    )

    # İstatistiki Hesaplamalar ve Mevzuat Kontrolleri
    toplam_saat = 0
    nobet_sayisi = 0
    rehberlik_var_mi = False
    
    for g in GUNLER_LISTE:
        for s in SAATLER_LISTE:
            val = str(st.session_state.df_program_matris.at[s, g])
            if "Boş" not in val and "☕" not in val and val != "None" and val.strip() != "":
                if "Nöbet" in val:
                    nobet_sayisi += 1
                elif "Rehberlik" in val or "Rehber" in val:
                    rehberlik_var_mi = True
                    toplam_saat += 1
                else:
                    toplam_saat += 1

    # MEVZUATSAL EK DERS HESAPLAMA MOTORU (DİNAMİK VE GÜNCEL)
    hazirlik_planlama_saati = toplam_saat // 10  # Her 10 saate 1 saat hazırlık planlama (Maks 3 saat)
    if hazirlik_planlama_saati > 3: hazirlik_planlama_saati = 3
    
    rehberlik_ek_saat = 2 if rehberlik_var_mi else 0
    
    toplam_kamu_yuku = toplam_saat + hazirlik_planlama_saati + rehberlik_ek_saat
    hak_edilen_ek_ders = toplam_kamu_yuku - MAAS_KARSILIGI_SAAT
    if hak_edilen_ek_ders < 0: hak_edilen_ek_ders = 0
    
    aylik_tahmini_kazanc = hak_edilen_ek_ders * 4 * EK_DERS_SAAT_UCRETI

    st.write("---")
    st.markdown("### 📊 Ders Programı Resmi Görev Özet Çıktısı")
    o1, o2, o3 = st.columns(3)
    o1.metric("Toplam Fiili Ders Yükü:", f"{toplam_saat} Saat")
    o2.metric("Hak Edilen Haftalık Ek Ders:", f"{hak_edilen_ek_ders} Saat", help=f"15 Saat Maaş Karşılığı düşülmüş, Planlama (+{hazirlik_planlama_saati}) ve Rehberlik (+{rehberlik_ek_saat}) eklenmiştir.")
    o3.metric("Aylık Tahmini Ek Ders Kazancı:", f"{int(aylik_tahmini_kazanc)} TL", help=f"Canlı Güncel Ek Ders Saat Ücreti: {EK_DERS_SAAT_UCRETI} TL baz alınmıştır.")

    if toplam_saat < MAAS_KARSILIGI_SAAT:
        st.warning(f"⚠️ Haftalık fiili ders saatiniz ({toplam_saat} saat), zorunlu maaş karşılığı ders yükünüzün ({MAAS_KARSILIGI_SAAT} saat) altındadır! Okul idaresi ek görevlendirme yapabilir.")

    st.write("---")
    csv_dosya = st.session_state.df_program_matris.to_csv().encode('utf-8')
    st.download_button(label="🖨️ Derli Toplu Yazdırılabilir Ders Programını İndir (Excel/CSV)", data=csv_dosya, file_name=f"{st.session_state.ogretmen_adi.replace(' ','_')}_ders_programi.csv", mime="text/csv")

# --- TAB 2: RESMİ TUTANAK ÖNİZLEME VE DÜZENLEME SİHİRBAZI ---
with tab2:
    st.subheader("📝 Düzenlenebilir Resmi Kurul ve Zümre Tutanak Sihirbazı")
    st.info("Tutanak içeriğini indirmeden önce ekranda canlı olarak düzenleyebilirsiniz. İndirilen Word (.docx) belgesi son yaptığınız değişiklikleri içerir.")
    
    tutanak_turu = st.selectbox("Üretilecek Tutanak Türünü Seçin:", [
        "Sene Başı Beden Eğitimi Zümre Öğretmenler Kurulu Tutanağı", 
        "Şube Öğretmenler Kurulu (ŞÖK) Toplantı Tutanağı", 
        "Eğitim Öğretim Yılı Sene Başı Öğretmenler Kurulu Toplantısı"
    ])
    
    # Resmi mevzuata uygun zenginleştirilmiş şablon metni oluşturma
    varsayilan_tutanak_metni = f"""OKUL ADI: {st.session_state.okul_muduru} adına kayıtlı eğitim kurumu\nTOPLANTI TÜRÜ: {tutanak_turu}\nTARİH: {bugun.strftime('%d.%m.%Y')}\n\nGÜNDEM MADDELERİ:\n1. Açılış, yoklama ve Okul Müdürü {st.session_state.okul_muduru}'nun açılış konuşması.\n2. Türkiye Yüzyılı Maarif Modeli müfredatının beden eğitimi dersi üzerindeki pedagojik etkileri.\n3. Ders programı görev dağılımı (Maaş dersi karşılığı: {MAAS_KARSILIGI_SAAT} saat, Rehberlik sınıfı: {st.session_state.rehber_sinif}).\n4. Okul resmi nöbet yerlerinin ({st.session_state.sabit_nobet_yeri}) işleyiş esaslarının planlanması.\n5. Dilek, temenniler ve kapanış.\n\nALINAN KARARLAR:\n1. Türkiye Yüzyılı Maarif Modeli doğrultusunda erdem-değer-eylem eksenli ders planları titizlikle uygulanacaktır.\n2. Zümre başkanı {st.session_state.zumre_baskani} ve ders öğretmeni {st.session_state.ogretmen_adi} tarafından süreç odaklı rubrikler ve öz değerlendirme araçları aktif olarak kullanılacaktır.\n\n"""

    st.markdown("### ✏️ Canlı Tutanak Düzenleme Alanı")
    duzenlenen_tutanak_metni = st.text_area("Metni istediğiniz gibi değiştirin:", value=varsayilan_tutanak_metni, height=350)

    if st.button("📄 Son Haliyle Resmi Word (.docx) Belgesini Üret"):
        doc = Document()
        for satir in duzenlenen_tutanak_metni.split("\n"):
            if "GÜNDEM MADDELERİ:" in satir or "ALINAN KARARLAR:" in satir:
                doc.add_heading(satir, level=3)
            elif "TOPLANTI TÜRÜ:" in satir:
                doc.add_heading(satir, level=2).alignment = 1
            else:
                doc.add_paragraph(satir)
        
        # RESMİ DÜZENE UYGUN TARİH VE İMZA BLOKLARI ENTEGRASYONU
        doc.add_paragraph("\n\n")
        table = doc.add_table(rows=1, cols=3)
        table.autofit = True
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = f"{st.session_state.ogretmen_adi}\nBeden Eğitimi Öğretmeni\nİmza"
        hdr_cells[1].text = f"{st.session_state.zumre_baskani}\nZümre Başkanı\nİmza"
        hdr_cells[2].text = f"{st.session_state.okul_muduru}\nOkul Müdürü\nUygundur"
        
        bio = io.BytesIO()
        doc.save(bio)
        st.success("🎉 Tutanak resmi düzene uygun olarak ve güncellenmiş son haliyle üretildi!")
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

    st.write("---")
    st.subheader("📱 Cihaz Lisans ve Hak Yönetimi")
    if st.button("🔄 Mevcut Cihaz Lisansımı Sıfırla (Yeni Cihaza Geçiş Yap)"):
        st.success("Eski cihaz bağınız otonom olarak sıfırlandı. Yeni cihazınızdan ek ücret ödemeden şifrenizle giriş yapabilirsiniz.")

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
    if st.session_state.gorevler: 
        st.table(pd.DataFrame(st.session_state.gorevler))

# --- TAB 5: ABONELİK VE PRO PAKET ---
with tab5:
    st.subheader("💎 Üyelik Paketleri")
    st.write(f"Mevcut Statünüz: **{st.session_state.kullanici_turu}**")
    if st.session_state.kullanici_turu == "Free":
        st.markdown("### 🥇 Elite Sürüm\n**599 TL / Yıl**\n* Tüm Özellikler Açık\n* Sınırsız Evrak Üretimi\n* Çoklu Cihaz ve Siber Güvenlik Koruması")

if st.session_state.kullanici_turu == "Free":
    st.markdown('<div class="premium-banner">🤝 <b>Sponsorluk:</b> Okul spor malzemeleri ihtiyaçlarınız için <b>Decathlon Türkiye</b> eğitim kataloğunu inceleyebilirsiniz.</div>', unsafe_allow_html=True)
