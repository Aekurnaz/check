import streamlit as st
from google import genai
from PIL import Image
import os

# --- 1. AYARLAR ---
st.set_page_config(page_title="Hızlı Çözücü", layout="wide", page_icon="📸")

# API Anahtarı Kontrolü
# Streamlit Cloud'da 'Secrets' kısmında tanımlı olmalı.
# Lokal çalışıyorsa aşağıya kendi keyini yazabilirsin ama GitHub'a atarken sil.
try:
    if "GOOGLE_API_KEY" in st.secrets:
        API_KEY = st.secrets["GOOGLE_API_KEY"]
    else:
        # Lokal test için buraya key yazabilirsin (Sadece test ederken)
        API_KEY = "BURAYA_KEY_GELECEK"
except:
    st.error("API Key bulunamadı.")
    st.stop()

# --- 2. TASARIM (CSS) ---
st.markdown("""
    <style>
        /* Sayfa kenar boşluklarını sıfırla */
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        header, footer {visibility: hidden;}
        
        /* KAMERA BUTONUNU BÜYÜTME */
        div[data-testid="stCameraInput"] button {
            transform: scale(1.3); /* Butonu büyüt */
            margin-top: 15px;
            background-color: #FF4B4B !important; 
            color: white !important;
            border-radius: 30px !important;
        }

        /* SONUÇ YAZISI */
        .big-answer {
            font-size: 60px !important;
            font-weight: 900;
            text-align: center;
            color: #2ecc71;
            padding: 10px;
            border: 2px solid #2ecc71;
            border-radius: 10px;
            margin-bottom: 15px;
            background-color: #f9f9f9;
        }

        /* YENİ SORU BUTONU */
        div.stButton > button {
            width: 100%;
            height: 100px;
            font-size: 26px !important;
            font-weight: bold;
            background-color: #f0f2f6;
            border: 3px solid #333;
            border-radius: 15px;
            color: #333;
        }
        div.stButton > button:hover {
            border-color: #2ecc71;
            color: #2ecc71;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. İSTEMCİ ---
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.warning("API Key hatası. Lütfen ayarlardan kontrol edin.")
    st.stop()

# --- 4. STATE YÖNETİMİ ---
if 'page' not in st.session_state:
    st.session_state.page = 'camera'
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = ""

def reset_app():
    st.session_state.page = 'camera'

def solve(image_file):
    try:
        img = Image.open(image_file)
        prompt = "Bu görseldeki soruyu çöz. SADECE cevabı (Örn: 'A', '42', 'Edirne') büyük harfle yaz. Asla açıklama yapma. Sadece net sonuç."
        
        with st.spinner('...'):
            response = client.models.generate_content(
                model='gemini-1.5-flash', 
                contents=[prompt, img]
            )
            st.session_state.last_answer = response.text.strip() if response.text else "❓"
            st.session_state.page = 'result'
            st.rerun()
    except Exception as e:
        st.error(f"Hata: {e}")

# --- 5. ARAYÜZ ---

if st.session_state.page == 'camera':
    # Başlık veya uyarı yok, direkt kamera
    pic = st.camera_input("Kamera", label_visibility="collapsed")
    
    if pic:
        solve(pic)

elif st.session_state.page == 'result':
    st.markdown("<br>", unsafe_allow_html=True) # Biraz boşluk
    st.markdown(f'<div class="big-answer">{st.session_state.last_answer}</div>', unsafe_allow_html=True)
    st.button("🔄 Yeni Soru", on_click=reset_app)