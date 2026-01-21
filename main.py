import streamlit as st
from google import genai
from PIL import Image
import os

# --- 1. AYARLAR VE GÜVENLİK ---
st.set_page_config(page_title="Hızlı Soru Çözücü", layout="centered", page_icon="⚡")

# Streamlit Cloud'un "Secrets" kısmından anahtarı çekiyoruz
# Eğer yerel bilgisayarda test ediyorsan secrets.toml dosyası gerekir veya hata verir.
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit ayarlarından 'Secrets' kısmına ekleyin.")
    st.stop()

# Tasarım İyileştirmeleri (CSS)
st.markdown("""
    <style>
        .block-container {padding-top: 1rem; padding-bottom: 0rem;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        .big-answer {
            font-size: 80px !important;
            font-weight: 900;
            text-align: center;
            color: #2ecc71;
            margin: 20px 0;
        }
        
        /* Yeniden Başlat Butonu */
        .stButton button {
            width: 100%;
            height: 150px;
            font-size: 24px;
            background-color: #f8f9fa;
            border: 2px dashed #333;
            color: #333;
            border-radius: 12px;
        }
        .stButton button:hover {
            border-color: #2ecc71;
            color: #2ecc71;
            background-color: #e8f5e9;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. İSTEMCİ BAŞLATMA ---
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Sunucu Hatası: {e}")
    st.stop()

# --- 3. SAYFA YÖNETİMİ ---
if 'page' not in st.session_state:
    st.session_state.page = 'camera'
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = ""

def reset_app():
    st.session_state.page = 'camera'

def solve(image_file):
    try:
        img = Image.open(image_file)
        # Çok net ve kısa cevap isteyen prompt
        prompt = "Bu görseldeki soruyu çöz. Çıktı olarak SADECE doğru cevabı (Örn: 'A', '42', 'Edirne') yaz. Asla açıklama yapma. Sadece sonucu büyük harfle ver."
        
        with st.spinner('Zeka çalışıyor...'):
            response = client.models.generate_content(
                model='gemini-flash-latest', 
                contents=[prompt, img]
            )
            
            st.session_state.last_answer = response.text.strip() if response.text else "Bulunamadı"
            st.session_state.page = 'result'
            st.rerun()
            
    except Exception as e:
        st.error(f"Hata: {e}")

# --- 4. ARAYÜZ AKIŞI ---

if st.session_state.page == 'camera':
    st.title("📸 Soruyu Göster")
    pic = st.camera_input("Foto", label_visibility="collapsed")
    if pic:
        solve(pic)

elif st.session_state.page == 'result':
    st.title("💡 Sonuç")
    st.markdown(f'<div class="big-answer">{st.session_state.last_answer}</div>', unsafe_allow_html=True)
    st.button("🔄 Yeni Soru Çek", on_click=reset_app)