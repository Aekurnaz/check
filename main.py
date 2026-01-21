import streamlit as st
from google import genai
from PIL import Image
import os

# --- 1. AYARLAR ---
# layout="wide" yaparak telefonda kenar boşluklarını kaldırdık (Geniş Açı Hissi)
st.set_page_config(page_title="Hızlı Çözücü", layout="wide", page_icon="⚡")

# API Anahtarı Kontrolü
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.warning("⚠️ API Anahtarı 'Secrets' ayarında bulunamadı. Yerel test için koda eklemelisiniz.")
    st.stop()

# --- 2. CSS İLE MOBİL ODAKLI TASARIM ---
st.markdown("""
    <style>
        /* Sayfanın üstündeki boşlukları tamamen yok et */
        .block-container {
            padding-top: 0rem; 
            padding-bottom: 0rem; 
            padding-left: 0.5rem; 
            padding-right: 0.5rem;
        }
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Cevap Metni Tasarımı */
        .big-answer {
            font-size: 60px !important;
            font-weight: 900;
            text-align: center;
            color: #2ecc71;
            margin-top: 20px;
            margin-bottom: 20px;
            word-wrap: break-word;
        }
        
        /* Kamera Widget'ını Özelleştirme */
        /* Kameranın etrafındaki çerçeveyi kaldırıp full ekran hissi verelim */
        .stCameraInput {
            width: 100% !important;
        }
        
        /* Buton Tasarımı - Mobil parmak dostu */
        .stButton button {
            width: 100%;
            height: 100px;
            font-size: 24px;
            font-weight: bold;
            background-color: #f0f2f6;
            border: 2px solid #ccc;
            border-radius: 15px;
            color: #333;
        }
        .stButton button:hover {
            border-color: #2ecc71;
            color: #2ecc71;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. İSTEMCİ KURULUMU ---
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")
    st.stop()

# --- 4. OTURUM YÖNETİMİ ---
if 'page' not in st.session_state:
    st.session_state.page = 'camera'
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = ""

def reset_app():
    st.session_state.page = 'camera'

def solve(image_file):
    try:
        img = Image.open(image_file)
        # Geniş açı fotoğraflarda netlik için Gemini'ye uyarı
        prompt = """
        GÖREV: Bu görseldeki soruyu çöz.
        KURALLAR:
        1. Çıktı SADECE net cevap olsun (Örn: "A", "42", "Ankara").
        2. Asla açıklama yapma.
        3. Merhaba veya giriş cümlesi kurma.
        4. Sadece sonucu BÜYÜK harflerle yaz.
        """
        
        with st.spinner('Analiz ediliyor...'):
            response = client.models.generate_content(
                model='gemini-flash-latest', 
                contents=[prompt, img]
            )
            
            if response.text:
                st.session_state.last_answer = response.text.strip()
            else:
                st.session_state.last_answer = "❓"
            
            st.session_state.page = 'result'
            st.rerun()
            
    except Exception as e:
        st.error(f"Hata: {e}")

# --- 5. ARAYÜZ AKIŞI ---

if st.session_state.page == 'camera':
    # Telefonda burası tam ekran görünür
    # Not: Kamera açılınca kullanıcı "Select Device" diyerek Arka Kamerayı seçmelidir.
    st.markdown("### 📸 Soruyu Çek")
    pic = st.camera_input("Kamera", label_visibility="collapsed")
    
    if pic:
        solve(pic)

elif st.session_state.page == 'result':
    st.markdown("### 💡 Cevap")
    st.markdown("---")
    # Cevabı ekrana bas
    st.markdown(f'<div class="big-answer">{st.session_state.last_answer}</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Geri Dön Butonu
    st.button("🔄 Yeni Soru", on_click=reset_app)