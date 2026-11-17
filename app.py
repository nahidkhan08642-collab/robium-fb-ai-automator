import os
import json
import random
import requests
import time
import threading
import schedule
import redis
from flask import Flask, render_template, request, jsonify
from local_ai_ensemble import LocalAIEnsemble

app = Flask(__name__)
ai_engine = LocalAIEnsemble()

# Redis configuration from user
REDIS_URL = os.environ.get("REDIS_URL", "redis://red-dbtu9ap42hec73b1dgc0:6379")
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    print("[REDIS] Connected successfully to Redis database!")
except Exception as e:
    print(f"[REDIS] Warning: Could not connect to Redis: {e}")
    redis_client = None

CONFIG_PATH = os.path.expanduser("~/.fb_ai_automator_config.json")
HISTORY_PATH = os.path.expanduser("~/.fb_ai_automator_history.json")

def load_config():
    if redis_client:
        try:
            cfg_data = redis_client.get("fb_automator_config")
            if cfg_data:
                return json.loads(cfg_data)
        except:
            pass
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "pages": [
            {"name": "Anime Page 1", "page_id": "1237613292776083", "access_token": ""},
            {"name": "Anime Page 2", "page_id": "", "access_token": ""},
            {"name": "Anime Page 3", "page_id": "", "access_token": ""},
            {"name": "Anime Page 4", "page_id": "", "access_token": ""},
            {"name": "Anime Page 5", "page_id": "", "access_token": ""}
        ],
        "ai_model": "Local-Multi-Model-Ensemble",
        "posts_per_day": 6
    }

def save_config(cfg):
    try:
        if redis_client:
            redis_client.set("fb_automator_config", json.dumps(cfg))
        with open(CONFIG_PATH, 'w') as f:
            json.dump(cfg, f, indent=4)
        return True
    except:
        return False

def load_history():
    if redis_client:
        try:
            hist_data = redis_client.get("fb_automator_history")
            if hist_data:
                return json.loads(hist_data)
        except:
            pass
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def save_history(history):
    try:
        if redis_client:
            redis_client.set("fb_automator_history", json.dumps(history))
        with open(HISTORY_PATH, 'w') as f:
            json.dump(history, f, indent=4)
    except:
        pass

def automated_post_job():
    cfg = load_config()
    pages = cfg.get("pages", [])
    
    sample_videos = [
        "https://www.w3schools.com/html/mov_bbb.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackSeeTheWorld.mp4"
    ]

    for idx, page in enumerate(pages):
        page_id = page.get("page_id")
        token = page.get("access_token")
        page_name = page.get("name", f"Anime Page {idx+1}")

        if not token or not page_id:
            print(f"[DAEMON] Skipping {page_name} ({page_id}): Missing Access Token.")
            continue

        time.sleep(random.randint(10, 25))
        video_url = random.choice(sample_videos)
        caption = ai_engine.generate_caption("Viral Anime Highlight", page_name)

        url = f"https://graph-video.facebook.com/v19.0/{page_id}/videos"
        payload = {
            "file_url": video_url,
            "description": caption,
            "published": "true",
            "access_token": token
        }

        print(f"[DAEMON] Publishing automated 24/7 post to {page_name} (ID: {page_id})...")
        success = False
        res_data = {}
        for attempt in range(3):
            try:
                res = requests.post(url, data=payload, timeout=60)
                res_data = res.json()
                if "id" in res_data:
                    success = True
                    break
                else:
                    time.sleep(2 ** attempt)
            except Exception as e:
                print(f"[DAEMON] Error posting to {page_name}: {e}")
                time.sleep(2 ** attempt)

        history = load_history()
        history.append({
            "timestamp": time.time(),
            "page_name": page_name,
            "page_id": page_id,
            "success": success,
            "response": res_data
        })
        save_history(history[-200:])
        print(f"[DAEMON] {page_name} post result -> Success: {success}, Response: {res_data}")

def run_scheduler():
    schedule.every(4).hours.do(automated_post_job)
    print("24/7 Multi-Page Local AI Ensemble Scheduler Daemon started.")
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=run_scheduler, daemon=True).start()

@app.route('/')
def index():
    cfg = load_config()
    return render_template('index.html', config=cfg)

@app.route('/api/save-config', methods=['POST'])
def api_save_config():
    data = request.json or {}
    cfg = load_config()
    if 'pages' in data:
        cfg['pages'] = data['pages']
    if save_config(cfg):
        return jsonify({"status": "success", "message": "All 5 Anime Pages configuration saved successfully!"})
    return jsonify({"status": "error", "message": "Failed to save configuration."}), 500

@app.route('/api/generate-ai-caption', methods=['POST'])
def api_generate_ai_caption():
    data = request.json or {}
    prompt = data.get('prompt', 'Viral Anime Moment')
    page_name = data.get('page_name', 'Anime Page')
    caption = ai_engine.generate_caption(prompt, page_name)
    return jsonify({"status": "success", "caption": caption})

@app.route('/api/post-video', methods=['POST'])
def api_post_video():
    data = request.json or {}
    cfg = load_config()
    pages = cfg.get('pages', [])
    page_index = data.get('page_index', 0)
    video_url = data.get('video_url', '')
    caption = data.get('caption', ai_engine.generate_caption())

    if not pages or page_index >= len(pages):
        return jsonify({"status": "error", "message": "Invalid page index or configuration!"}), 400

    target_page = pages[page_index]
    page_id = target_page.get('page_id')
    token = target_page.get('access_token')
    page_name = target_page.get('name', f'Page {page_index+1}')

    if not page_id or not token:
        return jsonify({"status": "error", "message": f"Page ID or Access Token missing for {page_name}!"}), 400

    url = f"https://graph-video.facebook.com/v19.0/{page_id}/videos"
    payload = {
        "description": caption,
        "published": "true",
        "access_token": token
    }
    if video_url:
        payload["file_url"] = video_url

    try:
        res = requests.post(url, data=payload, timeout=60)
        res_data = res.json()
        if "id" in res_data:
            return jsonify({"status": "success", "post_id": res_data["id"], "message": f"Video published successfully to {page_name}!"})
        else:
            return jsonify({"status": "error", "message": res_data.get("error", {}).get("message", "API Error")}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
