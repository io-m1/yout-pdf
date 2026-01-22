import datetime
import textwrap
import tempfile
import os
from yt_dlp import YoutubeDL
from fpdf import FPDF

def get_video_urls(target_url, max_videos=None):
    print(f"🔍 Crawling: {target_url}...")
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

    print(f"✅ Found {len(videos)} videos.")
    return videos

def get_transcript(video_id, video_url):
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            'skip_download': True,
            'writeautomaticsub': True,
            'writesubtitles': True,
            'subtitleslangs': ['en'],
            'subtitlesformat': 'vtt',
            'quiet': True,
            'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            print(f"⚠️ Download error for subtitles {video_id}: {e}")
            return None

        files = os.listdir(tmpdir)
        subtitle_files = [f for f in files if f.endswith('.vtt')]
        if not subtitle_files:
            print(f"⚠️ No subtitles found for {video_id}")
            return None

        subtitle_path = os.path.join(tmpdir, subtitle_files[0])

        transcript_lines = []
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            content = f.readlines()

        i = 0
        while i < len(content):
            line = content[i].strip()
            i += 1
            if '-->' in line:
                timestamp = line.split('-->')[0].strip()
                # Clean timestamp to HH:MM:SS (remove milliseconds)
                if '.' in timestamp:
                    timestamp = timestamp.split('.')[0]
                # Pad if needed
                parts = timestamp.split(':')
                if len(parts) == 3 and len(parts[0]) == 1:
                    timestamp = '0' + timestamp
                elif len(parts) == 2:
                    timestamp = '00:' + ':'.join(parts)

                text_parts = []
                while i < len(content):
                    next_line = content[i].strip()
                    i += 1
                    if not next_line or '-->' in next_line:
                        break
                    if next_line:
                        text_parts.append(next_line)
                text = ' '.join(text_parts)
                if text:
                    transcript_lines.append(f"[{timestamp}] {text}")

        if transcript_lines:
            return '\n'.join(transcript_lines)
        else:
            return None

def create_pdf(report_data, filename="Full_YouTube_Transcripts.pdf"):
    pdf = FPDF()
    pdf.set_title("Full YouTube Video Transcripts")
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

    pdf.output(filename)
    print(f"📄 Full transcript PDF saved as {filename}")

if __name__ == "__main__":
    print("YouTube Full Transcript to PDF Scraper (yt-dlp version)")
    target_link = input("Enter YouTube channel, playlist, or video URL: ").strip()
    max_videos_input = input("Max videos to process (leave blank for all): ").strip()
    max_videos = int(max_videos_input) if max_videos_input.isdigit() else None

    videos = get_video_urls(target_link, max_videos=max_videos)

    report_data = []
    for video in videos:
        print(f"\nProcessing: {video['title']}")
        transcript = get_transcript(video['video_id'], video['url'])
        if transcript:
            report_data.append({
                'title': video['title'],
                'url': video['url'],
                'transcript': transcript
            })
            print(f"   ✅ Transcript extracted")
        else:
            print("   ⏭️  Skipping (no subtitles available)")

    if report_data:
        create_pdf(report_data)
        print("\n🎉 Done! Check the PDF in this folder.")
    else:
        print("No transcripts were extracted.")
