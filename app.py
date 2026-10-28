import streamlit as st
import pandas as pd
import datetime
import requests
import io
import hashlib
from docx import Document

# --- SİBER GÜVENLİK VE EKRAN AYARLARI ---
try:
    st.set_page_config(page_title="Maarif Beden Eğitimi Asistanı SaaS PRO", layout="wide")
except:
    pass

GIZLI_TUZ_KELIME = "MaarifSaaS2026!SiberZirh"

if "güvenlik_imzası" not in st.session_state:
    st.session_state.güvenlik_imzası = hashlib.sha256(b"Free_Varsayilan_Guvenlik").hexdigest()
if "giris_yapildi" not in st.session_state: st.session_state.giris_yapildi = False
if "sifre_degisti" not in st.session_state: st.session_state.sifre_degisti = False
if "gorevler" not in st.session_state: st.session_state.gorevler = []
if "kullanici_turu" not in st.session_state: st.session_state.kullanici_turu = "Free"

# --- DİNAMİK LİSTE YÖNETİMİ ---
if "ogretmen_adi" not in st.session_state: st.session_state.ogretmen_adi = "M. Kemal ATATÜRK"
if "okul_muduru" not in st.session_state: st.session_state.okul_muduru = "Müdür Bey"
if "zumre_baskani" not in st.session_state: st.session_state.zumre_baskani = "Zümre Başkanı"
if "rehber_sinif" not in st.session_state: st.session_state.rehber_sinif = "9-A"
if "sabit_nobet_yeri" not in st.session_state: st.session_state.sabit_nobet_yeri = "Bahçe"
if "diger_zumreler" not in st.session_state: st.session_state.diger_zumreler = "Öğretmen A\nÖğretmen B"

GUNLER_LISTE = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
SAATLER_LISTE = [f"{i}. Ders" for i in range(1, 9)] + ["Öğle Arası"]

if "df_program_matris" not in st.session_state:
    st.session_state.df_program_matris = pd.DataFrame(
        {gun: ["Boş Ders" if "Öğle Arası" not in saat else "☕ ÖĞLE ARASI" for saat in SAATLER_LISTE] for gun in GUNLER_LISTE},
        index=SAATLER_LISTE
    )

def otonom_lisans_dogrula(tel, girilen_kod, paket_turu):
    clean_tel = "".join(filter(str.isdigit, tel))[-10:]
    return girilen_kod == f"{paket_turu}-{hashlib.sha256(f'{clean_tel}-{GIZLI_TUZ_KELIME}-{paket_turu}'.encode()).hexdigest()[:12].upper()}"

# --- GİRİŞ PANELİ ---
if not st.session_state.giris_yapildi:
    st.title("📱 Maarif Beden Eğitimi Asistanı")
    tel_no = st.text_input("Telefon Numaranız (5xxxxxxxxxx):")
    girilen_sifre = st.text_input("Giriş Şifreniz veya Lisans Kodunuz:", type="password")
    
    if st.button("Sisteme Güvenli Giriş Yap"):
        if girilen_sifre == "Maarif2026" or otonom_lisans_dogrula(tel_no, girilen_sifre, "PRO") or otonom_lisans_dogrula(tel_no, girilen_sifre, "ELITE"):
            st.session_state.giris_yapildi = True
            if "ELITE" in girilen_sifre: st.session_state.kullanici_turu = "Elite"
            st.rerun()
        else:
            st.error("Giriş kodu hatalı!")
    st.stop()

if st.session_state.giris_yapildi and not st.session_state.sifre_degisti:
    st.title("🔒 Şifre Özelleştirme")
    yeni_sifre = st.text_input("Kalıcı Şifrenizi Oluşturun:", type="password")
    if st.button("Şifremi Kaydet"):
        st.session_state.sifre_degisti = True
        st.rerun()
    st.stop()

# --- ANA MENÜ ---
t1, t2, t3, t4 = st.tabs(["📅 Ders Programı", "📝 Tutanak Sihirbazı", "⚙️ Ayarlar", "📆 İş Günü Takvimi"])

with t1:
    st.subheader("📊 Haftalık Ders Programı Matrisi")
    st.write("Aşağıdaki tablonun hücrelerine çift tıklayarak ders ve sınıf bilgilerini elinizle serbestçe yazabilirsiniz:")
    st.session_state.df_program_matris = st.data_editor(st.session_state.df_program_matris, use_container_width=True)
    
    csv_prog = st.session_state.df_program_matris.to_csv().encode('utf-8')
    st.download_button("🖨️ Programı Excel/CSV Olarak İndir", data=csv_prog, file_name="ders_programi.csv")

with t2:
    st.subheader("📝 Düzenlenebilir Tutanak Sihirbazı")
    tutanak_metni = st.text_area("Tutanak Metni Önizlemesi (İndirmeden önce buradan düzenleyebilirsiniz):", value=f"OKUL ADI: {st.session_state.okul_muduru} adına kayıtlı kurum\nÖĞRETMEN: {st.session_state.ogretmen_adi}\nZÜMRE BAŞKANI: {st.session_state.zumre_baskani}\n\nGÜNDEM VE KARARLAR:\n1. Türkiye Yüzyılı Maarif Modeli erdem-değer-eylem planlaması görüşüldü.\n2. Okul nöbet alanı olarak {st.session_state.sabit_nobet_yeri} belirlendi.", height=250)
    
    if st.button("📄 Word (.docx) Olarak Üret"):
        doc = Document()
        for satir in tutanak_metni.split("\n"): doc.add_paragraph(satir)
        bio = io.BytesIO()
        doc.save(bio)
        st.download_button("📥 Word Belgesini İndir", data=bio.getvalue(), file_name="maarif_tutanak.docx")

with t3:
    st.subheader("⚙️ Kadro Yapılandırma Ayarları")
    st.session_state.ogretmen_adi = st.text_input("Adınız Soyadınız:", value=st.session_state.ogretmen_adi)
    st.session_state.okul_muduru = st.text_input("Okul Müdürü:", value=st.session_state.okul_muduru)
    st.session_state.zumre_baskani = st.text_input("Zümre Başkanı:", value=st.session_state.zumre_baskani)
    st.session_state.rehber_sinif = st.text_input("Rehberlik Sınıfınız:", value=st.session_state.rehber_sinif)
    st.session_state.sabit_nobet_yeri = st.text_input("Nöbet Yeriniz:", value=st.session_state.sabit_nobet_yeri)

with t4:
    st.subheader("📆 Genel Resmi İş Günü Takvimi")
    st.table(pd.DataFrame([{"Tarih": "29 Ekim", "Etkinlik": "Cumhuriyet Bayramı Törenleri"}, {"Tarih": "24 Kasım", "Etkinlik": "Öğretmenler Günü Etkinlikleri"}]))
