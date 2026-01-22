import streamlit as st

def apply_css():
    is_dark = st.session_state.get('theme', 'dark') == 'dark'
    bg = '#0f0f1a' if is_dark else '#f8f9fa'
    text = '#e0e0ff' if is_dark else '#1a1a2e'
    accent = '#00ff9d' if is_dark else '#00c853'
    card_bg = '#1e2330' if is_dark else '#ffffff'
    border = '#30363d' if is_dark else '#e0e0e0'
    css = f"""
    <style>
        .stApp {{background:{bg};color:{text};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;}}
        section[data-testid="stSidebar"] {{background:{'transparent'};border-right:1px solid {border};width:280px !important;min-width:280px !important;}}
        .stSidebar .stButton > button {{background:transparent;border:none;color:{text};width:100%;text-align:left;padding:12px 20px;border-radius:8px;}}
        .stSidebar .stButton > button:hover {{background:rgba(0,255,157,0.08);}}
        .header {{background:linear-gradient(90deg,{accent},#00c853);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2.4rem;font-weight:700;text-align:center;margin:1rem 0 0.5rem;}}
        .orb-container {{position:relative;width:160px;height:160px;margin:2rem auto;}}
        .orb {{position:absolute;inset:0;border-radius:50%;background:radial-gradient(circle at 35% 35%,{accent}33,transparent 65%);box-shadow:0 0 80px {accent}55,0 0 160px {accent}33;animation:pulse 7s infinite ease-in-out,rotate 24s infinite linear;}}
        @keyframes pulse {{0%,100% {{transform:scale(1);opacity:0.75;}}50% {{transform:scale(1.12);opacity:1;}}}}
        @keyframes rotate {{0% {{transform:rotate(0deg);}}100% {{transform:rotate(360deg);}}}}
        .welcome {{text-align:center;font-size:1.9rem;margin:0.5rem 0 1.5rem;color:{accent};}}
        .card {{background:{card_bg};border:1px solid {border};border-radius:12px;padding:1.2rem;margin:1rem 0;box-shadow:0 4px 12px rgba(0,0,0,0.25);}}
        .mode-toggle {{position:fixed;top:1rem;right:1rem;z-index:9999;}}
        @media (max-width:768px) {{.header {{font-size:1.9rem;}}.welcome {{font-size:1.6rem;}}.orb-container {{width:140px;height:140px;}}.main-content {{padding:1rem 0.8rem;}}}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.markdown('<div class="orb-container"><div class="orb"></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="mode-toggle">' + st.radio("", ["Dark","Light"], horizontal=True, key="theme_radio", label_visibility="collapsed") + '</div>', unsafe_allow_html=True)
    if st.session_state.theme_radio == "Light":
        st.session_state.theme = 'light'
    else:
        st.session_state.theme = 'dark'

def render_header():
    st.markdown('<div class="header">io-m1 AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome">Welcome to io-m1 AI</div>', unsafe_allow_html=True)

def render_footer():
    st.markdown('<p style="text-align:center;color:#8b949e;margin-top:2rem;">Powered by io-m1 AI • Augmented Intelligence</p>', unsafe_allow_html=True)
