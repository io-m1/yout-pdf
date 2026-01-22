import streamlit as st
import datetime
import textwrap
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from fpdf import FPDF
import io

# === Glassmorphism + Neon UI (Same Stunning Design) ===
st.set_page_config(page_title="io-m1 AI Hub", layout="centered")

custom_css = """
<style>
    .stApp {background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0ff;}
    .main-glass {background: rgba(255, 255, 255, 0.08); border-radius: 20px; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.15); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37); padding: 2rem; margin: 2rem auto; max-width: 1000px;}
    h1 {font-size: 3rem !important; background: linear-gradient(90deg, #00ffea, #ff00ff, #00ffea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-shadow: 0 0 20px rgba(0, 255, 234, 0.8); margin-bottom: 0.5rem;}
    .neon-subtitle {text-align: center; font-size: 1.3rem; color: #bb86fc; text-shadow: 0 0 15px rgba(187, 134, 252, 0.6); margin-bottom: 2rem;}
    .stTextInput > div > div > input {background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(0, 255, 234, 0.4); border-radius: 12px; color: #ffffff; padding: 12px; box-shadow: 0 0 15px rgba(0, 255, 234, 0.3);}
    .stButton > button {background: linear-gradient(45deg, #00ffea, #ff00ff); color: white; border: none; border-radius: 12px; padding: 12px 30px; font-weight: bold; box-shadow: 0 0 20px rgba(0, 255, 234, 0.6);}
    .stButton > button:hover {box-shadow: 0 0 30px rgba(0, 255, 234, 0.9); transform: scale(1.05);}
    .stProgress > div > div {background: linear-gradient(90deg, #00ffea, #ff00ff);}
    .custom-caption {text-align: center; margin-top: 3rem; color: #88ffff; font-size: 1rem; text-shadow: 0 0 10px rgba(136, 255, 255, 0.5);}
    .thumbnail-gallery {display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center;}
    .thumb-card {text-align: center; max-width: 300px;}
    .thumb-img {border-radius: 12px; box-shadow: 0 0 20px rgba(0, 255, 234, 0.5);}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.markdown('<div class="main-glass">', unsafe_allow_html=True)

st.markdown("<h1>io-m1 AI</h1>", unsafe_allow_html=True)
st.markdown('<p class="neon-subtitle">Augmented Intelligence • Transcript Extraction + Red Team Knowledge Query</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📥 Extract Transcripts", "🧠 Query Knowledge"])

with tab1:
    st.markdown("Enter any YouTube URL → Extract full transcripts + snapshots + PDF")
    target_link = st.text_input("YouTube URL", placeholder="e.g., https://www.youtube.com/@examplechannel/videos")
    max_videos_input = st.text_input("Max videos (optional)", placeholder="Leave blank for all")
    generate = st.button("🚀 Extract & Analyze")

    if generate and target_link:
        with st.spinner("Processing..."):
            def get_video_urls(target_url, max_videos=None):
                ydl_opts = {'extract_flat': True, 'quiet': True, 'ignoreerrors': True}
                if max_videos: ydl_opts['playlistend'] = max_videos
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(target_url, download=False)
                videos = []
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry and entry.get('id'):
                            videos.append({'video_id': entry['id'], 'title': entry.get('title', 'Untitled'), 'url': f"https://www.youtube.com/watch?v={entry['id']}", 'thumbnail': f"https://img.youtube.com/vi/{entry['id']}/maxresdefault.jpg"})
                else:
                    videos.append({'video_id': info.get('id'), 'title': info.get('title', 'Untitled'), 'url': info.get('webpage_url') or info.get('original_url'), 'thumbnail': f"https://img.youtube.com/vi/{info.get('id')}/maxresdefault.jpg"})
                st.write(f"**Found {len(videos)} videos**")
                return videos

            def get_transcript(video_id):
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    try: transcript = transcript_list.find_transcript(['en'])
                    except NoTranscriptFound:
                        try: transcript = transcript_list.find_generated_transcript(['en'])
                        except NoTranscriptFound: transcript = next(iter(transcript_list))
                    data = transcript.fetch()
                    lines = [f"[{str(datetime.timedelta(seconds=int(e['start']))).zfill(8)}] {e['text'].strip()}" for e in data]
                    return "\n".join(lines)
                except: return None

            max_videos = int(max_videos_input) if max_videos_input.isdigit() and max_videos_input else None
            videos = get_video_urls(target_link, max_videos=max_videos)
            report_data = []
            full_text = ""
            progress = st.progress(0)
            for i, v in enumerate(videos):
                st.write(f"**{v['title']}**")
                trans = get_transcript(v['video_id'])
                if trans:
                    report_data.append({**v, 'transcript': trans})
                    full_text += f"\n\n--- {v['title']} ---\n{trans}"
                    st.success("✓ Extracted")
                else:
                    st.warning("⚠ No captions")
                progress.progress((i+1)/len(videos))

            if report_data:
                # PDF
                buf = io.BytesIO()
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                for item in report_data:
                    pdf.add_page()
                    pdf.set_font("Helvetica", 'B', 16)
                    pdf.multi_cell(0, 10, item['title'], align='C')
                    pdf.ln(5)
                    pdf.set_font("Helvetica", '', 10)
                    pdf.cell(0, 8, f"Source: {item['url']}", ln=True)
                    pdf.ln(10)
                    pdf.set_font("Helvetica", '', 11)
                    pdf.multi_cell(0, 6, item['transcript'])
                pdf.output(buf)
                buf.seek(0)
                st.download_button("📥 Download PDF", buf, "Transcripts.pdf", "application/pdf")

                # Thumbnails Gallery
                st.markdown("### 📸 Video Snapshots")
                cols = st.columns(3)
                for i, item in enumerate(report_data):
                    with cols[i % 3]:
                        st.image(item['thumbnail'], caption=item['title'], use_column_width=True)

                # Store for Query tab
                st.session_state.full_text = full_text
                st.session_state.report_data = report_data
                st.success("Ready for deep query!")

with tab2:
    if 'full_text' not in st.session_state:
        st.info("First extract transcripts in the left tab.")
    else:
        st.markdown("### 🧠 Red Team Analyst Query")
        st.markdown("Ask anything—the AI will critically analyze, teach profoundly, and red-team ideas using **only** the extracted knowledge.")
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        query = st.chat_input("Your question (e.g., 'Red-team this liquidity strategy')")
        if query:
            st.session_state.messages.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)
            
            # Simple but powerful "AI" response using context (no external LLM needed—pure red-team prompt)
            context = st.session_state.full_text[:20000]  # Truncate for speed; full in real LLM
            prompt = f"""
You are io-m1 AI Red Team Analyst—super intelligent, profound teacher.
Use ONLY the following transcripts. Critically analyze ('red-team'): find flaws, alternatives, risks.
Teach deeply with examples. Be honest, detailed, insightful.

Transcripts:
{context}

Question: {query}
"""
            # Here: Simulate profound response (in production, replace with OpenAI/Grok API call)
            response = f"**Red Team Analysis:**\n\nBased on the extracted concepts (liquidity, imbalances, structure)... [Profound critical breakdown would go here].\n\nKey risks: ...\nAlternative view: ...\nDeep insight: ..."
            # TODO: Replace above with real LLM call if you add API key input
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<p class="custom-caption">Powered by io-m1 AI • Augmented Intelligence</p>', unsafe_allow_html=True)
