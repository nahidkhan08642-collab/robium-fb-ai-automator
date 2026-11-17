import os
import json
import random
import requests
import time
import threading
import schedule
import redis
from flask import Flask, render_template, request, jsonify
from local_ai_ensemble import SpecializedLocalAIEnsemble

app = Flask(__name__)
ai_ensemble = SpecializedLocalAIEnsemble()

# Redis configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://red-dbtu9ap42hec73b1dgc0:6379")
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    print(f"[{ai_ensemble.get_publisher_agent()}] Connected successfully to Redis database!")
except Exception as e:
    print(f"[{ai_ensemble.get_recovery_agent()}] Warning: Redis unavailable, using local JSON fallback: {e}")
    redis_client = None

CONFIG_PATH = os.path.expanduser("~/.fb_ai_automator_config.json")
HISTORY_PATH = os.path.expanduser("~/.fb_ai_automator_history.json")
TOKENS_JSON_PATH = os.path.expanduser("~/permanent_page_tokens.json")

def load_default_pages():
    if os.path.exists(TOKENS_JSON_PATH):
        try:
            with open(TOKENS_JSON_PATH, "r") as f:
                data = json.load(f)
                pages = []
                for pid, info in data.items():
                    pages.append({
                        "name": info.get("name", "Anime Page"),
                        "page_id": pid,
                        "access_token": info.get("permanent_token", "")
                    })
                return pages
        except:
            pass
    return [
        {"name": "Anime world lover", "page_id": "1240263435841497", "access_token": "EAAfml573upUBSt96RoQhyZCR4d7nvO1DZBlwTIzud8pQpkif6qfv8ngFrwyfELD2iZBVmnhFtWZBnwTx044oHeG5btq5cgQYZAr9jDfoBoWJrtfPO8rjfAZABPfkNvo5Qb6cmTckGYcBWc3HdALCiY9hcQBmVRaCZBBje9kQZAbCbOidH8ZBMNUpJsyxlKste2wny3SAVDVV5"},
        {"name": "anime world", "page_id": "963922040147989", "access_token": "EAAtOZBWbGMWkBSg4XuNlJs2lS5R4TysTO91QKHr2NceRZB2C35XqDRPDYysu4SmCZCcFo4LpaZBsomuiCarvhXYYVsGVAQF5jwXuZAXZCz1MDCHKfvH61G6OvQAFbYFCXw9pZAl4mM6nNJNyYaIkAwe1Q7LYP7rZCtfot5wHyxK7ysYhUJi9HM0mLCUA0VzP2ZAZCvXl6gAhYg"},
        {"name": "Quarrelsome cover", "page_id": "110244978515347", "access_token": "EAAtOZBWbGMWkBSjcevJgliGvbdoBGGrOp7LQR08ZCklnJOaF6rQTI2qJlvFyrLahsXD91viNhZC49ysMFQWUBXmZBwFB9NZAUi4YbQjgRxh7TY3NKog7BNsfdBZBeKu8lwkNpGcoWLaHVY5SBzrNEV8NYHHESvGs9TwEZBbG0mDJGiyZCYYfI3wGy2df820uUz1EQGw3Ib4ZD"},
        {"name": "anime lover", "page_id": "1046094275254219", "access_token": "EAAYgiB7ZAQ4MBSoH2EljZCaHi2Be08xhy4hgsPqALySTInJj6eZCf2CgVzZBZA5l2tXD6inkusa01jAC6VfaYxO4XPiWkwzmZBl8L2g90GhpwiFstBO0Qe2hqhn81hZAuIYKxcThP3MHjBSINhDCgZASoIqtfkhJcFRCZCln6IZC8px8umJCbQl3pDBWgVAwVNr8POllZA1Y7xM"},
        {"name": "Rifat Islam", "page_id": "1089498234242779", "access_token": "EAAYgiB7ZAQ4MBSg1wvDSDkGUY09O0GOaBBF5wP3wJkdKBBggGtmrSHk2vmSDpnERfO1OWNPl50lGQQBNy1dBOZAZCpm9AzZBemVZCbgy7aYLxzdn6AJOKINnBA1m8gGS8k6i7K262doGsuVCYk2quofAf0Esn6fhi5GJbnZAWDRGZC98t7BBZAYgC9NUxrpnkKYB5sGL6rHZB"}
    ]

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
        "pages": load_default_pages(),
        "posts_per_day": 6,
        "schedule_mode": "usa_prime_time_6_daily"
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

def weekly_storage_cleanup_and_ai_audit():
    """
    Weekly Storage Cleanup & AI Model Health Audit Agent:
    Runs every Friday at 12:30 AM.
    1. Purges old storage logs.
    2. Runs comprehensive health audit across all 60 AI models (10 per task) with self-healing failovers.
    """
    print("[STORAGE-CLEANUP & AI-AUDIT] Running Friday 12:30 AM maintenance task...")
    
    # 1. Storage cleanup
    history = load_history()
    if len(history) > 50:
        trimmed = history[-50:]
        save_history(trimmed)
        print(f"[STORAGE-CLEANUP] Cleaned old history logs. Retained latest {len(trimmed)} records.")
    else:
        print("[STORAGE-CLEANUP] Storage is already clean.")
        
    # 2. AI Model Health Audit & Self-Healing
    ai_ensemble.audit_all_ai_models()
    print("[STORAGE-CLEANUP & AI-AUDIT] Friday maintenance completed successfully.")

def automated_post_job():
    publisher = ai_ensemble.get_publisher_agent()
    recovery = ai_ensemble.get_recovery_agent()
    cfg = load_config()
    pages = cfg.get("pages", [])
    
    history = load_history()
    recent_video_urls = [h.get("video_url") for h in history[-30:] if h.get("video_url")]

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
            print(f"[{publisher}] Skipping {page_name}: Missing Access Token.")
            continue

        # Run Growth & Engagement Analytics Optimizer backed by 10 redundant AI models
        growth_analysis = ai_ensemble.analyze_and_optimize_growth(page_name, history[-10:])
        print(f"[{growth_analysis['model_used']}] Reach & Engagement growth strategy optimized for {page_name}.")

        time.sleep(random.randint(10, 20))
        video_url = ai_ensemble.select_unique_video(recent_video_urls, sample_videos)
        recent_video_urls.append(video_url)

        caption = ai_ensemble.assemble_full_caption("USA Prime-Time Viral Anime Highlight", page_name)

        url = f"https://graph-video.facebook.com/v19.0/{page_id}/videos"
        payload = {
            "file_url": video_url,
            "description": caption,
            "published": "true",
            "access_token": token
        }

        print(f"[{publisher}] Publishing scheduled prime-time post to {page_name} (ID: {page_id})...")
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
                    print(f"[{recovery}] Attempt {attempt+1} failed for {page_name}: {res_data}")
                    time.sleep(2 ** attempt)
            except Exception as e:
                print(f"[{recovery}] Exception on attempt {attempt+1} for {page_name}: {e}")
                time.sleep(2 ** attempt)

        history = load_history()
        history.append({
            "timestamp": time.time(),
            "page_name": page_name,
            "page_id": page_id,
            "video_url": video_url,
            "success": success,
            "response": res_data
        })
        save_history(history[-200:])
        print(f"[{publisher}] {page_name} post result -> Success: {success}")

def run_scheduler():
    schedule.every(4).hours.do(automated_post_job)
    schedule.every().friday.at("00:30").do(weekly_storage_cleanup_and_ai_audit)
    print(f"[{ai_ensemble.get_publisher_agent()}] 24/7 Scheduler & Friday AI Audit Daemon started with 60 specialized AI models (10 per task).")
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
        return jsonify({"status": "success", "message": "All 5 Permanent Anime Pages & 10-Model AI Redundancy configuration saved successfully!"})
    return jsonify({"status": "error", "message": "Failed to save configuration."}), 500

@app.route('/api/generate-ai-caption', methods=['POST'])
def api_generate_ai_caption():
    data = request.json or {}
    prompt = data.get('prompt', 'Viral Anime Moment')
    page_name = data.get('page_name', 'Anime Page')
    caption = ai_ensemble.assemble_full_caption(prompt, page_name)
    return jsonify({"status": "success", "caption": caption})

@app.route('/api/post-video', methods=['POST'])
def api_post_video():
    data = request.json or {}
    cfg = load_config()
    pages = cfg.get('pages', [])
    page_index = data.get('page_index', 0)
    video_url = data.get('video_url', '')
    caption = data.get('caption', ai_ensemble.assemble_full_caption())

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
