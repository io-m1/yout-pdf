import streamlit as st

def apply_css():
    custom_css = """
<style>
    .stApp {background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0ff;}
    .main-glass {background: rgba(255, 255, 255, 0.08); border-radius: 20px; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.15); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37); padding: 2rem; margin: 2rem auto; max-width: 1100px;}
    h1 {font-size: 3rem !important; background: linear-gradient(90deg, #00ffea, #ff00ff, #00ffea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-shadow: 0 0 20px rgba(0, 255, 234, 0.8);}
    .neon-subtitle {text-align: center; font-size: 1.3rem; color: #bb86fc; text-shadow: 0 0 15px rgba(187, 134, 252, 0.6); margin-bottom: 2rem;}
    .stTextInput > div > div > input {background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(0, 255, 234, 0.4); border-radius: 12px; color: #ffffff; padding: 12px; box-shadow: 0 0 15px rgba(0, 255, 234, 0.3);}
    .stButton > button {background: linear-gradient(45deg, #00ffea, #ff00ff); color: white; border: none; border-radius: 12px; padding: 12px 30px; font-weight: bold; box-shadow: 0 0 20px rgba(0, 255, 234, 0.6);}
    .stButton > button:hover {box-shadow: 0 0 30px rgba(0, 255, 234, 0.9); transform: scale(1.05);}
    .custom-caption {text-align: center; margin-top: 3rem; color: #88ffff; font-size: 1rem; text-shadow: 0 0 10px rgba(136, 255, 255, 0.5);}
</style>
"""
    st.markdown(custom_css, unsafe_allow_html=True)
    st.markdown('<div class="main-glass">', unsafe_allow_html=True)

def render_header():
    st.markdown("<h1>io-m1 AI</h1>", unsafe_allow_html=True)
    st.markdown('<p class="neon-subtitle">Augmented Intelligence • Multi-Model Red Team Analysis</p>', unsafe_allow_html=True)

def render_footer():
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<p class="custom-caption">Powered by io-m1 AI • Multi-Model Augmented Intelligence</p>', unsafe_allow_html=True)
