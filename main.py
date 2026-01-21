import streamlit as st
from google import genai
from PIL import Image
import os

# --- 1. AYARLAR ---
st.set_page_config(page_title="Hızlı Çözücü", layout="wide", page_icon="📸")

# API Anahtarı
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.warning("⚠️ API Key bulunamadı. Lütfen Secrets ayarlarını kontrol edin.")
    st.stop()

# --- 2. TASARIM (CSS HACKLERİ) ---
st.markdown("""
    <style>
        /* Sayfa kenar boşluklarını sıfırla */
        .block-container {
            padding-top: 1rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        header, footer {visibility: hidden;}
        
        /* 1. HACK: KAMERA BUTONUNU BÜYÜTME */
        /* Streamlit'in içindeki kamera butonunu hedef alıp %50 büyütüyoruz */
        div[data-testid="stCameraInput"] button {
            transform: scale(1.5); /* Butonu 1.5 kat büyüt */
            margin-top: 20px;      /* Biraz boşluk bırak */
            background-color: #FF4B4B !important; /* Rengi Kırmızı yap */
            color: white !important;
            border-radius: 50px !important; /* Yuvarlak hatlı olsun */
        }

        /* Sonuç Metni */
        .big-answer {
            font-size: 50px !important;
            font-weight: 900;
            text-align: center;
            color: #2ecc71;
            padding: 20px;
            border: 2px solid #2ecc71;
            border-radius: 15px;
            margin-bottom: 20px;
        }

        /* 'Yeni Soru' Butonu */
        .stButton button {
            width: 100%;
            height: 120px;
            font-size: 28px !important;
            font-weight: bold;
            background-color: #f0f2f6;
            border: 3px solid #333;
            border-radius: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. İSTEMCİ ---
client = genai.Client(api_key=API_KEY)

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
        prompt = "Bu görseldeki soruyu çöz. SADECE cevabı (Örn: 'A', '42') büyük harfle yaz. Açıklama yapma."
        
        with st.spinner('Analiz ediliyor...'):
            response = client.models.generate_content(
                model='gemini-flash-latest', 
                contents=[prompt, img]
            )
            st.session_state.last_answer = response.text.strip() if response.text else "❓"
            st.session_state.page = 'result'
            st.rerun()
    except Exception as e:
        st.error(f"Hata: {e}")

# --- 5. ARAYÜZ ---

if st.session_state.page == 'camera':
    st.markdown("<h3 style='text-align: center;'>📸 Soruyu Çek</h3>", unsafe_allow_html=True)
    
    # UYARI MESAJI
    st.info("💡 Telefonunuzda kamera açılınca, kamera görüntüsünün altındaki listeden 'Back Camera' (Arka Kamera) seçeneğini seçmelisiniz. (Tarayıcı buna otomatik izin vermez.)")
    
    pic = st.camera_input("Kamera", label_visibility="collapsed")
    
    if pic:
        solve(pic)

elif st.session_state.page == 'result':
    st.markdown("<h3 style='text-align: center;'>💡 Cevap</h3>", unsafe_allow_html=True)
    st.markdown(f'<div class="big-answer">{st.session_state.last_answer}</div>', unsafe_allow_html=True)
    st.button("🔄 Yeni Soru", on_click=reset_app)