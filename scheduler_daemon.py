import os
import json
import random
import requests
import time
import threading
import schedule

CONFIG_PATH = os.path.expanduser("~/.fb_ai_automator_config.json")
HISTORY_PATH = os.path.expanduser("~/.fb_ai_automator_history.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "page_id": "1237613292776083",
        "access_token": "",
        "ai_model": "Multi-Model-Ensemble",
        "posts_per_day": 6
    }

def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def save_history(history):
    with open(HISTORY_PATH, 'w') as f:
        json.dump(history, f, indent=4)

def ai_generate_content():
    # Multi-model AI workflow simulation for automated generation
    titles = [
        "🔥 Unstoppable Anime Peak Moments! Watch till the end! ⚡",
        "✨ The greatest plot twist in anime history! Rate 1-10! 💫",
        "💔 Pure emotional mastery... Have you seen this masterpiece? 🥺",
        "⚡ Epic battle choreography that gave millions chills! 🚀",
        "🎯 Absolute perfection! Share this with your anime bestie! 🔥"
    ]
    hashtags = "#AnimeReels #Viral #TrendingNow #OtakuWorld #AnimeEdits #FYP #ExplorePage"
    title = random.choice(titles)
    caption = f"{title}\n\n{hashtags}"
    return caption

def automated_post_job():
    cfg = load_config()
    page_id = cfg.get("page_id")
    token = cfg.get("access_token")
    
    if not token or not page_id:
        print("[AI-AUTOMATOR-CRON] Missing Page ID or Access Token. Skipping automated post cycle.")
        return

    # Select sample or scouted video URL
    sample_videos = [
        "https://www.w3schools.com/html/mov_bbb.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    ]
    video_url = random.choice(sample_videos)
    caption = ai_generate_content()

    url = f"https://graph-video.facebook.com/v19.0/{page_id}/videos"
    payload = {
        "file_url": video_url,
        "description": caption,
        "published": "true",
        "access_token": token
    }

    print(f"[AI-AUTOMATOR-CRON] Publishing automated 1/6 post to Facebook Page {page_id}...")
    try:
        res = requests.post(url, data=payload, timeout=45)
        res_data = res.json()
        history = load_history()
        history.append({
            "timestamp": time.time(),
            "response": res_data
        })
        save_history(history[-100:])
        print(f"[AI-AUTOMATOR-CRON] Post response: {res_data}")
    except Exception as e:
        print(f"[AI-AUTOMATOR-CRON] Error posting video: {e}")

def run_scheduler():
    # Schedule 6 posts per day evenly spaced (e.g. every 4 hours)
    schedule.every(4).hours.do(automated_post_job)
    print("Background 6-posts-per-day AI scheduler started successfully.")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    t = threading.Thread(target=run_scheduler, daemon=True)
    t.start()
    print("AI Automator Background Daemon running...")
