import requests
from datetime import datetime, timedelta
from typing import List, Optional
from .base_collector import BaseCollector, SocialPost

class HackerNewsCollector(BaseCollector):
    def __init__(self):
        super().__init__("hackernews")
        self.base_url = "https://hacker-news.firebaseio.com/v0"
    
    def collect(self, keywords: List[str], hours_back: int = 24) -> List[SocialPost]:
        posts = []
        cutoff = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Expand keywords to match HN content better
        hn_keywords = ['AI', 'SaaS', 'startup', 'funding', 'remote', 'productivity', 
                       'marketing', 'business', 'tool', 'software', 'app', 'platform']
        
        response = requests.get(f"{self.base_url}/topstories.json", timeout=30)
        story_ids = response.json()[:150]  # Check more stories
        
        for story_id in story_ids:
            try:
                story = requests.get(f"{self.base_url}/item/{story_id}.json", timeout=10).json()
                if not story or 'title' not in story:
                    continue
                
                title = story.get('title', '').lower()
                text = story.get('text', '').lower() if story.get('text') else ''
                combined = f"{title} {text}"
                
                # Check if ANY keyword matches (partial match)
                matched = False
                for kw in keywords:
                    kw_clean = kw.lower().replace('business ', '').replace(' tools', '').replace(' software', '').replace(' pricing', '')
                    if kw_clean in combined or kw.lower() in combined:
                        matched = True
                        break
                
                # Also check HN-specific keywords
                if not matched:
                    for kw in hn_keywords:
                        if kw.lower() in combined:
                            matched = True
                            break
                
                if not matched:
                    continue
                
                created = datetime.utcfromtimestamp(story.get('time', 0))
                if created < cutoff:
                    continue
                
                engagement = story.get('score', 0) + story.get('descendants', 0) * 2
                
                posts.append(SocialPost(
                    id=str(story_id),
                    platform="hackernews",
                    text=story.get('title', ''),
                    author=story.get('by', 'unknown'),
                    created_at=created,
                    engagement_score=engagement,
                    url=story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                    hashtags=[]
                ))
            except Exception as e:
                continue
        
        return posts
    
    def get_trending_topics(self, location: Optional[str] = None) -> List[dict]:
        trending = []
        try:
            response = requests.get(f"{self.base_url}/topstories.json", timeout=30)
            top_ids = response.json()[:25]
            
            for story_id in top_ids:
                story = requests.get(f"{self.base_url}/item/{story_id}.json", timeout=10).json()
                if story:
                    trending.append({
                        'title': story.get('title', ''),
                        'score': story.get('score', 0),
                        'comments': story.get('descendants', 0),
                        'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                    })
        except Exception as e:
            print(f"Hacker News trending error: {e}")
        return trending