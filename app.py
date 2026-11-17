import os
import json
import random
import requests
import time
import threading
import schedule
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

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

def save_config(cfg):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(cfg, f, indent=4)
        return True
    except:
        return False

def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def save_history(history):
    try:
        with open(HISTORY_PATH, 'w') as f:
            json.dump(history, f, indent=4)
    except:
        pass

def ai_generate_content(prompt="Epic Anime Battle"):
    titles = [
        f"🔥 {prompt} — Unstoppable Peak Moments! Watch till the end! ⚡",
        f"✨ The greatest plot twist! {prompt} Rate 1-10! 💫",
        f"💔 Pure emotional mastery... {prompt} Have you seen this? 🥺",
        f"⚡ Epic choreography! {prompt} Share with your bestie! 🚀"
    ]
    hashtags = "#AnimeReels #Viral #TrendingNow #OtakuWorld #AnimeEdits #FYP #ExplorePage"
    title = random.choice(titles)
    return f"{title}\n\n{hashtags}"

def automated_post_job():
    cfg = load_config()
    page_id = cfg.get("page_id")
    token = cfg.get("access_token")
    
    if not token or not page_id:
        print("[DAEMON] Missing Page ID or Access Token. Skipping automated post.")
        return

    sample_videos = [
        "https://www.w3schools.com/html/mov_bbb.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    ]
    video_url = random.choice(sample_videos)
    caption = ai_generate_content("Viral Anime Highlight")

    url = f"https://graph-video.facebook.com/v19.0/{page_id}/videos"
    payload = {
        "file_url": video_url,
        "description": caption,
        "published": "true",
        "access_token": token
    }

    print(f"[DAEMON] Publishing automated 24/7 post to Facebook Page {page_id}...")
    try:
        res = requests.post(url, data=payload, timeout=45)
        res_data = res.json()
        history = load_history()
        history.append({
            "timestamp": time.time(),
            "response": res_data
        })
        save_history(history[-100:])
        print(f"[DAEMON] Post response: {res_data}")
    except Exception as e:
        print(f"[DAEMON] Error posting video: {e}")

def run_scheduler():
    # Schedule automated posts 6 times a day (every 4 hours)
    schedule.every(4).hours.do(automated_post_job)
    print("24/7 Background AI Scheduler Daemon started.")
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start background daemon thread when Flask app boots up on Render
threading.Thread(target=run_scheduler, daemon=True).start()

@app.route('/')
def index():
    cfg = load_config()
    return render_template('index.html', config=cfg)

@app.route('/api/save-config', methods=['POST'])
def api_save_config():
    data = request.json or {}
    cfg = load_config()
    cfg['page_id'] = data.get('page_id', cfg['page_id'])
    cfg['access_token'] = data.get('access_token', cfg['access_token'])
    if save_config(cfg):
        return jsonify({"status": "success", "message": "Configuration saved successfully!"})
    return jsonify({"status": "error", "message": "Failed to save configuration."}), 500

@app.route('/api/generate-ai-caption', methods=['POST'])
def api_generate_ai_caption():
    data = request.json or {}
    prompt = data.get('prompt', 'Viral Anime Moment')
    caption = ai_generate_content(prompt)
    return jsonify({"status": "success", "caption": caption})

@app.route('/api/post-video', methods=['POST'])
def api_post_video():
    data = request.json or {}
    cfg = load_config()
    page_id = cfg.get('page_id')
    token = cfg.get('access_token')
    video_url = data.get('video_url', '')
    caption = data.get('caption', ai_generate_content())

    if not page_id or not token:
        return jsonify({"status": "error", "message": "Page ID or Access Token is missing!"}), 400

    url = f"https://graph-video.facebook.com/v19.0/{page_id}/videos"
    payload = {
        "description": caption,
        "published": "true",
        "access_token": token
    }
    if video_url:
        payload["file_url"] = video_url

    try:
        res = requests.post(url, data=payload, timeout=45)
        res_data = res.json()
        if "id" in res_data:
            return jsonify({"status": "success", "post_id": res_data["id"], "message": "Video published successfully!"})
        else:
            return jsonify({"status": "error", "message": res_data.get("error", {}).get("message", "API Error")}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
