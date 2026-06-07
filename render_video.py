import os, sys, requests, json, subprocess, socket, gc
import urllib3.util.connection as urllib3_cn
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, TextClip, ColorClip, vfx, afx

# 🛡️ Force IPv4 to bypass Hostinger block (agar API calls hostinger se ja rahe hain)
def allowed_gai_family():
    return socket.AF_INET
urllib3_cn.allowed_gai_family = allowed_gai_family

HINDI_FONT_FILE = "Hindi.ttf" 

# --- VARIABLES DEFINED HERE ---
chat_id = os.environ.get('CHAT_ID')
pexels_key = os.environ.get('PEXELS_API_KEY')
scenes_data = json.loads(os.environ.get('SCENES_DATA', '[]'))
title = os.environ.get('TITLE', 'Mind-blowing Earning Secret')
description = os.environ.get('DESCRIPTION', 'Make money online secret tricks.')
thumbnail_prompt = os.environ.get('THUMBNAIL_PROMPT', 'Cinematic beautiful thumbnail')

print(f"Total Scenes to render: {len(scenes_data)}")

# 🌟 LONG FORMAT (Landscape 1920x1080) for Earn-Smart
TARGET_W, TARGET_H = 1920, 1080
viral_colors = ['#FFD400', '#00FFFF', '#FFFFFF', '#39FF14']
headers = {"Authorization": pexels_key}

try:
    whoosh_sfx = AudioFileClip("whoosh.mp3").volumex(0.25)
    pop_sfx = AudioFileClip("pop.mp3").volumex(0.15)        
except:
    whoosh_sfx = pop_sfx = None

rendered_files = [] 
master_audio_clips = []
current_time = 0.0

# ==========================================
# Process Each Scene (100% PERFECT SYNC)
# ==========================================
for i, scene in enumerate(scenes_data):
    keyword = scene.get('keyword', 'finance')
    text_line = scene.get('text', '').strip()
    
    if not text_line: continue
    
    # 1. SCENE-BY-SCENE AUDIO GENERATION (Swara Female Voice for Earn-Smart)
    temp_txt_path = "temp_scene.txt"
    audio_path = f"voice_scene_{i}.mp3"
    
    with open(temp_txt_path, "w", encoding="utf-8") as f:
        f.write(text_line)
        
    try:
        # Generate Voiceover
        subprocess.run([sys.executable, '-m', 'edge_tts', '--voice', 'hi-IN-SwaraNeural', '-f', temp_txt_path, '--write-media', audio_path], check=True)
        raw_scene_audio = AudioFileClip(audio_path).fx(vfx.speedx, 1.1)
        
        # Trim baseline silence
        if raw_scene_audio.duration > 0.5:
            scene_audio = raw_scene_audio.subclip(0.3)
        else:
            scene_audio = raw_scene_audio
        
        scene_duration = scene_audio.duration
        
        master_audio_clips.append(scene_audio.set_start(current_time))
        if whoosh_sfx: master_audio_clips.append(whoosh_sfx.set_start(current_time))
        
    except Exception as e:
        print(f"Audio failed for scene {i}: {e}")
        continue
        
    # 2. VIDEO & TEXT PROCESSING
    try:
        search_query = f"{keyword} finance technology"
        res = requests.get(f"https://api.pexels.com/videos/search?query={search_query}&per_page=1&orientation=landscape", headers=headers, timeout=15).json()
        
        if 'videos' in res and len(res['videos']) > 0:
            video_url = res['videos'][0]['video_files'][0]['link']
        else:
            res = requests.get("https://api.pexels.com/videos/search?query=abstract technology money&per_page=1&orientation=landscape", headers=headers, timeout=15).json()
            video_url = res['videos'][0]['video_files'][0]['link']
        
        vid_path = f"vid_{i}.mp4"
        with open(vid_path, "wb") as f:
            f.write(requests.get(video_url, timeout=30).content)
            
        clip = VideoFileClip(vid_path).subclip(0, scene_duration)
        clip = clip.resize(height=TARGET_H)
        if clip.w < TARGET_W: clip = clip.resize(width=TARGET_W)
        clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=TARGET_W, height=TARGET_H)
        
        zoomed_clip = clip.resize(lambda t: 1.0 + 0.04 * (t / scene_duration)).set_position(('center', 'center'))
        dark_overlay = ColorClip(size=(TARGET_W, TARGET_H), color=(0,0,0)).set_opacity(0.35).set_duration(scene_duration).set_position(('center', 'center'))
        
        words = text_line.split(' ')
        chunk_size = 3 
        chunks = [' '.join(words[j:j + chunk_size]) for j in range(0, len(words), chunk_size)]
        
        word_clips = []
        duration_per_chunk = scene_duration / max(len(chunks), 1)
        
        for w_i, chunk in enumerate(chunks):
            current_color = viral_colors[w_i % len(viral_colors)]
            
            bg_txt = TextClip(chunk, fontsize=100, color='black', font=HINDI_FONT_FILE, stroke_color='black', stroke_width=15, method='caption', size=(1600, None))
            bg_txt = bg_txt.set_position(('center', 'center')).set_duration(duration_per_chunk).set_start(w_i * duration_per_chunk)
            
            main_txt = TextClip(chunk, fontsize=100, color=current_color, font=HINDI_FONT_FILE, stroke_color='black', stroke_width=3, method='caption', size=(1600, None))
            main_txt = main_txt.set_position(('center', 'center')).set_duration(duration_per_chunk).set_start(w_i * duration_per_chunk)
            
            word_clips.extend([bg_txt, main_txt])
        
        final_scene = CompositeVideoClip([zoomed_clip, dark_overlay] + word_clips, size=(TARGET_W, TARGET_H)).set_duration(scene_duration)
        
        # --- RAM/MEMORY FIX: Render Each Scene & Clear Memory ---
        scene_filename = f"scene_rendered_{i}.mp4"
        final_scene.write_videofile(scene_filename, fps=24, codec="libx264", preset="ultrafast", audio=False, logger=None)
        rendered_files.append(scene_filename)
        
        final_scene.close()
        clip.close()
        del final_scene, clip, zoomed_clip, word_clips
        gc.collect()
        # -------------------------------------------------
        
        current_time += scene_duration
        print(f"Scene {i+1} Ready: {keyword}")
    except Exception as e:
        print(f"Error on scene {i}: {e}")

if os.path.exists("temp_scene.txt"): os.remove("temp_scene.txt")

# ==========================================
# DISK CONCATENATION (No RAM usage)
# ==========================================
print("Merging scenes without RAM using ffmpeg...")
with open("concat_list.txt", "w") as f:
    for file in rendered_files:
        f.write(f"file '{file}'\n")

subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'concat_list.txt', '-c', 'copy', 'merged_scenes.mp4'])
final_video = VideoFileClip("merged_scenes.mp4")

# PROGRESS BAR
progress_bar = ColorClip(size=(TARGET_W, 15), color=(255, 0, 0))
progress_bar = progress_bar.set_position(lambda t: (-TARGET_W + int(TARGET_W * (t / max(final_video.duration, 1))), 'bottom'))
progress_bar = progress_bar.set_duration(final_video.duration)

final_video = CompositeVideoClip([final_video, progress_bar])

try:
    bgm = AudioFileClip("bgm.mp3").volumex(0.10)
    if bgm.duration < final_video.duration: bgm = afx.audio_loop(bgm, duration=final_video.duration)
    else: bgm = bgm.subclip(0, final_video.duration)
    master_audio_clips.append(bgm)
except: pass

final_audio = CompositeAudioClip(master_audio_clips)
final_video = final_video.set_audio(final_audio)

print("Rendering Final COMPRESSED LONG Video...")
final_video.write_videofile("final_video.mp4", fps=24, codec="libx264", audio_codec="aac", threads=2, bitrate="2000k", preset="ultrafast")

# ==========================================
# UPLOAD SYSTEM
# ==========================================
print("Starting Core Indestructible Upload System...")
video_link = "Upload Failed"

endpoints = [
    ("File.io", "https://file.io", "file", lambda r: r.json()['link']),
    ("0x0.st", "https://0x0.st", "file", lambda r: r.text.strip()),
    ("Uguu.se", "https://uguu.se/upload.php", "files[]", lambda r: r.json()['files'][0]['url']),
    ("Catbox.moe", "https://catbox.moe/user/api.php", "reqtype", lambda r: r.text.strip())
]

for name, url, field, get_link in endpoints:
    if video_link != "Upload Failed" and video_link.startswith("http"): break
    try:
        print(f"Trying upload to {name}...")
        files = {field: open("final_video.mp4", 'rb')}
        data = {'reqtype': 'fileupload'} if "catbox" in url else {}
        res = requests.post(url, files=files, data=data, timeout=300)
        
        if res.status_code == 200:
            link = get_link(res)
            if "http" in link: 
                video_link = link
                print(f"✅ Upload Success: {video_link}")
    except Exception as e: 
        print(f"❌ {name} failed: {e}")

# ==========================================
# TELEGRAM BRIDGE (Triggering n8n IF Router)
# ==========================================
BOT_TOKEN = "7707041789:AAFB0DUbGlypExkUjxm0qpJC60Cj5HFLd-E" 

# Safe pipe separated structure for n8n extraction
message_text = f"READY_TO_UPLOAD|{video_link}|{title}|{thumbnail_prompt}|{description}"

try:
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message_text}
    response = requests.post(telegram_url, json=payload)
    print(f"✅ Webhook bypassed! Sent video details directly to Telegram! Status: {response.status_code}")
except Exception as e:
    print(f"❌ Failed to send Telegram alert: {e}")
