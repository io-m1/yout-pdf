import datetime
import re
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from langdetect import detect
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='auto', target='en')

def get_video_urls(target_url, max_videos=None):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'ignoreerrors': True,
        'skip_download': True
    }
    if max_videos:
        ydl_opts['playlistend'] = max_videos
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(target_url, download=False)
        except Exception as e:
            return None, f"yt-dlp failed: {e}"
    if info is None:
        return None, "yt-dlp returned no data. Invalid or unsupported YouTube URL."
    videos = []
    if isinstance(info, dict) and 'entries' in info and info['entries']:
        for entry in info['entries']:
            if not entry or not entry.get('id'):
                continue
            vid = entry['id']
            videos.append({
                'video_id': vid,
                'title': entry.get('title', 'Untitled'),
                'url': f"https://www.youtube.com/watch?v={vid}",
                'thumbnail': f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg"
            })
    elif isinstance(info, dict) and info.get('id'):
        vid = info['id']
        videos.append({
            'video_id': vid,
            'title': info.get('title', 'Untitled'),
            'url': info.get('webpage_url') or info.get('original_url'),
            'thumbnail': f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg"
        })
    else:
        return None, "No videos could be extracted from this URL."
    return videos, None

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def get_transcript(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return None
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
        lines = [f"[{str(datetime.timedelta(seconds=int(e['start']))).zfill(8)}] {e['text'].strip()}" for e in data]
        raw_text = "\n".join(lines)

        lang = detect(raw_text[:200]) if raw_text.strip() else 'en'
        if lang != 'en':
            try:
                raw_text = translator.translate(raw_text)
            except:
                pass

        if raw_text.strip() and 'openai_key' in st.session_state and st.session_state.openai_key:
            from openai import OpenAI
            client = OpenAI(api_key=st.session_state.openai_key)
            prompt = f"Clean and improve this translated transcript to make it natural English, fix errors, fill gaps:\n{raw_text}"
            try:
                resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                raw_text = resp.choices[0].message.content
            except:
                pass

        return raw_text
    except:
        return None
