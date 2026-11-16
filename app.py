import os
import json
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

CONFIG_PATH = os.path.expanduser("~/.fb_automator_config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "page_id": "",
        "access_token": "",
        "ai_model": "gemini-flash",
        "auto_caption": "🔥 Check out this amazing viral video! Don't forget to like and share. #Viral #Reels #Trending"
    }

def save_config(cfg):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(cfg, f, indent=4)
        return True
    except:
        return False

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
    cfg['ai_model'] = data.get('ai_model', cfg['ai_model'])
    cfg['auto_caption'] = data.get('auto_caption', cfg['auto_caption'])
    if save_config(cfg):
        return jsonify({"status": "success", "message": "Configuration saved successfully!"})
    return jsonify({"status": "error", "message": "Failed to save configuration."}), 500

@app.route('/api/generate-ai-caption', methods=['POST'])
def api_generate_ai_caption():
    data = request.json or {}
    prompt = data.get('prompt', 'Create an engaging viral Facebook Reel caption with hashtags.')
    # AI caption generator simulation / integration
    ai_captions = [
        f"🔥 {prompt} — You won't believe what happens next! Double tap if you love this! #Viral #Trending #Reels #Explore",
        f"✨ Absolute masterclass! {prompt} Share this with your friends right now! 🚀 #Epic #MustWatch #TrendingNow",
        f"⚡ Pure chills! {prompt} Drop your thoughts in the comments below! 👇 #Aesthetic #ViralReels #Creator"
    ]
    import random
    selected = random.choice(ai_captions)
    return jsonify({"status": "success", "caption": selected})

@app.route('/api/post-video', methods=['POST'])
def api_post_video():
    data = request.json or {}
    cfg = load_config()
    page_id = cfg.get('page_id')
    token = cfg.get('access_token')
    video_url = data.get('video_url', '')
    caption = data.get('caption', cfg.get('auto_caption'))

    if not page_id or not token:
        return jsonify({"status": "error", "message": "Page ID or Access Token is missing in config!"}), 400

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
            return jsonify({"status": "success", "post_id": res_data["id"], "message": "Video posted successfully to Facebook via AI Automator!"})
        else:
            return jsonify({"status": "error", "message": res_data.get("error", {}).get("message", "Facebook API Error")}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
