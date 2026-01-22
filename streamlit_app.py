import streamlit as st
import datetime
import textwrap
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from fpdf import FPDF
import io

# === Custom Glassmorphism + Neon UI ===
st.set_page_config(page_title="io-m1 AI Transcript Portal", layout="centered")

custom_css = """
<style>
    /* Dark futuristic background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #e0e0ff;
    }

    /* Glassmorphism main container */
    .main-glass {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
        padding: 2rem;
        margin: 2rem auto;
        max-width: 900px;
    }

    /* Neon glowing title */
    h1 {
        font-size: 3rem !important;
        background: linear-gradient(90deg, #00ffea, #ff00ff, #00ffea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        text-shadow: 0 0 20px rgba(0, 255, 234, 0.8);
        margin-bottom: 0.5rem;
    }

    /* Neon subtitle */
    .neon-subtitle {
        text-align: center;
        font-size: 1.3rem;
        color: #bb86fc;
        text-shadow: 0 0 15px rgba(187, 134, 252, 0.6);
        margin-bottom: 2rem;
    }

    /* Input fields with glass + neon glow */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 234, 0.4);
        border-radius: 12px;
        color: #ffffff;
        padding: 12px;
        box-shadow: 0 0 15px rgba(0, 255, 234, 0.3);
    }

    /* Button with neon pulse */
    .stButton > button {
        background: linear-gradient(45deg, #00ffea, #ff00ff);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 30px;
        font-weight: bold;
        box-shadow: 0 0 20px rgba(0, 255, 234, 0.6);
        transition: all 0.3s;
    }
    .stButton > button:hover {
        box-shadow: 0 0 30px rgba(0, 255, 234, 0.9);
        transform: scale(1.05);
    }

    /* Progress & status messages */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00ffea, #ff00ff);
    }

    /* Caption */
    .custom-caption {
        text-align: center;
        margin-top: 3rem;
        color: #88ffff;
        font-size: 1rem;
        text-shadow: 0 0 10px rgba(136, 255, 255, 0.5);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Wrap content in glass container
st.markdown('<div class="main-glass">', unsafe_allow_html=True)

st.markdown("<h1>io-m1 AI</h1>", unsafe_allow_html=True)
st.markdown('<p class="neon-subtitle">Augmented Intelligence • YouTube Transcript to PDF Portal</p>', unsafe_allow_html=True)
st.markdown("Enter any YouTube channel, playlist, or video URL → Get a full-timestamped transcript PDF instantly.")

target_link = st.text_input("YouTube URL", placeholder="e.g., https://www.youtube.com/@examplechannel/videos")
max_videos_input = st.text_input("Max videos to process (optional)", placeholder="Leave blank for all videos")
generate = st.button("Generate PDF")

if generate and target_link:
    with st.spinner("Crawling videos and extracting transcripts... (may take 5–30 mins for large channels)"):
        def get_video_urls(target_url, max_videos=None):
            ydl_opts = {
                'extract_flat': True,
                'quiet': True,
                'ignoreerrors': True,
            }
            if max_videos:
                ydl_opts['playlistend'] = max_videos

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=False)

            videos = []
            if 'entries' in info:
                for entry in info['entries']:
                    if entry and entry.get('id'):
                        videos.append({
                            'video_id': entry['id'],
                            'title': entry.get('title', 'Untitled Video'),
                            'url': f"https://www.youtube.com/watch?v={entry['id']}"
                        })
            else:
                videos.append({
                    'video_id': info.get('id'),
                    'title': info.get('title', 'Untitled Video'),
                    'url': info.get('webpage_url') or info.get('original_url')
                })
            st.write(f"**Found {len(videos)} videos**")
            return videos

        def get_transcript(video_id):
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                try:
                    transcript = transcript_list.find_transcript(['en'])
                except NoTranscriptFound:
                    try:
                        transcript = transcript_list.find_generated_transcript(['en'])
                    except NoTranscriptFound:
                        transcript = next(iter(transcript_list))
                data = transcript.fetch()

                lines = []
                for entry in data:
                    start = entry['start']
                    timestamp = str(datetime.timedelta(seconds=int(start)))
                    if len(timestamp) < 8:
                        timestamp = timestamp.zfill(8)
                    text = entry['text'].strip()
                    lines.append(f"[{timestamp}] {text}")
                return "\n".join(lines)

            except (TranscriptsDisabled, VideoUnavailable, NoTranscriptFound):
                return None
            except Exception as e:
                st.error(f"Error for {video_id}: {e}")
                return None

        max_videos = int(max_videos_input) if max_videos_input.isdigit() and max_videos_input else None
        videos = get_video_urls(target_link, max_videos=max_videos)

        report_data = []
        progress_bar = st.progress(0)
        for idx, video in enumerate(videos):
            st.write(f"**Processing:** {video['title']}")
            transcript = get_transcript(video['video_id'])
            if transcript:
                report_data.append({
                    'title': video['title'],
                    'url': video['url'],
                    'transcript': transcript
                })
                st.success("✓ Transcript extracted")
            else:
                st.warning("⚠ Skipped (no captions available)")
            progress_bar.progress((idx + 1) / len(videos))

        if report_data:
            pdf_buffer = io.BytesIO()
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            for item in report_data:
                pdf.add_page()
                pdf.set_font("Helvetica", 'B', 16)
                wrapped_title = "\n".join(textwrap.wrap(item['title'], width=80))
                pdf.multi_cell(0, 10, txt=wrapped_title, align='C')
                pdf.ln(5)
                pdf.set_font("Helvetica", '', 10)
                pdf.cell(0, 8, txt=f"Source: {item['url']}", ln=True)
                pdf.ln(10)
                pdf.set_font("Helvetica", '', 11)
                pdf.multi_cell(0, 6, txt=item['transcript'])
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)

            st.success("🎉 PDF ready!")
            st.download_button(
                label="📥 Download Full Transcripts PDF",
                data=pdf_buffer,
                file_name="YouTube_Transcripts.pdf",
                mime="application/pdf"
            )
        else:
            st.error("No transcripts were extracted.")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p class="custom-caption">Powered by io-m1 AI • Augmented Intelligence</p>', unsafe_allow_html=True)
