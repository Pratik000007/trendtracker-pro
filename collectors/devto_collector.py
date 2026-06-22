import requests
from datetime import datetime, timedelta
from typing import List, Optional
from .base_collector import BaseCollector, SocialPost

class DevToCollector(BaseCollector):
    def __init__(self):
        super().__init__("devto")
        self.base_url = "https://dev.to/api/articles"
    
    def collect(self, keywords: List[str], hours_back: int = 24) -> List[SocialPost]:
        posts = []
        cutoff = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Search multiple tags that match your keywords
        tags = ['ai', 'saas', 'startup', 'business', 'productivity', 'marketing', 
                'remote-work', 'b2b', 'software', 'tools', 'tech', 'webdev']
        
        for tag in tags:
            try:
                response = requests.get(
                    self.base_url,
                    params={'tag': tag, 'top': 7, 'per_page': 50},
                    timeout=30
                )
                
                if response.status_code != 200:
                    continue
                    
                articles = response.json()
                
                for article in articles:
                    text = f"{article.get('title', '')} {article.get('description', '')}"
                    
                    # FIX: Looser keyword matching - check each word
                    matched = False
                    for kw in keywords:
                        kw_words = kw.lower().split()
                        for word in kw_words:
                            if len(word) > 2 and word in text.lower():
                                matched = True
                                break
                        if matched:
                            break
                    
                    if not matched:
                        continue
                    
                    created = datetime.fromisoformat(article['created_at'].replace('Z', '+00:00'))
                    if created.replace(tzinfo=None) < cutoff:
                        continue
                    
                    engagement = article.get('public_reactions_count', 0) + article.get('comments_count', 0) * 2
                    
                    posts.append(SocialPost(
                        id=str(article['id']),
                        platform="devto",
                        text=article.get('title', ''),
                        author=article['user']['username'],
                        created_at=created.replace(tzinfo=None),
                        engagement_score=engagement,
                        url=article['url'],
                        hashtags=article.get('tag_list', [])
                    ))
            except Exception as e:
                print(f"Dev.to tag {tag} error: {e}")
                continue
        
        return posts
    
    def get_trending_topics(self, location: Optional[str] = None) -> List[dict]:
        trending = []
        try:
            response = requests.get(
                self.base_url,
                params={'top': 1, 'per_page': 10},
                timeout=30
            )
            for article in response.json():
                trending.append({
                    'title': article['title'],
                    'author': article['user']['username'],
                    'reactions': article.get('public_reactions_count', 0),
                    'url': article['url']
                })
        except Exception as e:
            print(f"Dev.to trending error: {e}")
        return trending