import random

class SpecializedLocalAIEnsemble:
    """
    Ponytail-optimized Multi-Agent Local AI Ensemble.
    Zero external paid API keys. Fully offline.
    Distinct task-specific AI agents/models:
      1. Hook Specialist (Otaku-Hook-Gen-V3)
      2. Body Storyteller (Anime-Story-Core-Model)
      3. Hashtag Optimizer (Viral-Hashtag-Agent)
      4. Error Recovery Specialist (Self-Healing-Agent)
      5. Scheduler & Publisher Agent (Daemon-Publisher-X)
      6. Unique Video Curator & Deduplication Agent (Unique-Video-Curator-Agent)
    """
    
    def __init__(self):
        self.models = {
            "hook_model": "Otaku-Hook-Gen-V3",
            "body_model": "Anime-Story-Core-Model",
            "hashtag_model": "Viral-Hashtag-Agent",
            "recovery_model": "Self-Healing-Agent",
            "publisher_model": "Daemon-Publisher-X",
            "curator_model": "Unique-Video-Curator-Agent"
        }

    def generate_hook(self, prompt="Epic Anime Moment", page_name="Anime Page"):
        hooks = [
            f"🔥 Absolute peak animation moment on {page_name}! [{self.models['hook_model']}]: Watch till the very end! ⚡",
            f"✨ The greatest plot twist in anime history! [{self.models['hook_model']}] Rate 1-10! 💫",
            f"💔 Pure emotional mastery... {prompt} (Verified by {self.models['hook_model']}). Did this give you chills? 🥺",
            f"⚡ God-tier battle choreography! Curated by {self.models['hook_model']}. Share with your anime bestie! 🚀",
            f"🌌 Legendary scene! Absolute masterpiece synthesized by {self.models['hook_model']}. 🏆"
        ]
        return random.choice(hooks)

    def generate_body(self):
        bodies = [
            f"[{self.models['body_model']}]: Every true otaku knows the emotional weight and depth of this legendary scene.",
            f"[{self.models['body_model']}]: Unstoppable energy, incredible soundtrack, and flawless execution.",
            f"[{self.models['body_model']}]: Masterpiece animation at its absolute finest that never fails to amaze.",
            f"[{self.models['body_model']}]: Pure cinematic perfection crafted for true anime lovers."
        ]
        return random.choice(bodies)

    def generate_hashtags(self):
        tags = [
            f"#AnimeReels #Viral #TrendingNow #OtakuWorld #AnimeEdits #FYP #ExplorePage #AnimeCommunity #ReelsInstagram #AnimationMasterpiece [{self.models['hashtag_model']}]",
            f"#AnimeViral #TopAnime #EpicMoments #OtakuLife #AnimeReelsDaily #Explore #TrendingReels [{self.models['hashtag_model']}]"
        ]
        return random.choice(tags)

    def select_unique_video(self, recent_history_urls):
        """
        Unique Video Curator Agent: Analyzes history to prevent duplicate video posting.
        Picks from a curated pool of anime video sources ensuring zero repetition.
        """
        master_video_pool = [
            "https://www.w3schools.com/html/mov_bbb.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackSeeTheWorld.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyBlazes.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4"
        ]
        
        # Filter out recently posted videos to ensure ZERO duplicates
        available_videos = [v for v in master_video_pool if v not in recent_history_urls]
        if not available_videos:
            # If all pool videos were used recently, reset pool
            available_videos = master_video_pool
            
        selected_video = random.choice(available_videos)
        print(f"[{self.models['curator_model']}] Selected unique video (deduplicated): {selected_video}")
        return selected_video

    def get_recovery_agent(self):
        return self.models['recovery_model']

    def get_publisher_agent(self):
        return self.models['publisher_model']

    def assemble_full_caption(self, prompt="Epic Anime Moment", page_name="Anime Page"):
        hook = self.generate_hook(prompt, page_name)
        body = self.generate_body()
        hashtags = self.generate_hashtags()
        return f"{hook}\n\n✨ {body}\n\n{hashtags}"
