# collectors/youtube_collector.py
from googleapiclient.discovery import build
import os
from datetime import datetime, timedelta
from typing import List, Optional
from .base_collector import BaseCollector, SocialPost

class YouTubeCollector(BaseCollector):
    def __init__(self):
        super().__init__("youtube")
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
    
    def collect(self, keywords: List[str], hours_back: int = 24) -> List[SocialPost]:
        posts = []
        published_after = (datetime.utcnow() - timedelta(hours=hours_back)).isoformat("T") + "Z"
        
        for keyword in keywords:
            try:
                response = self.youtube.search().list(
                    q=keyword,
                    part='snippet',
                    type='video',
                    order='viewCount',
                    publishedAfter=published_after,
                    maxResults=50
                ).execute()
                
                video_ids = [item['id']['videoId'] for item in response.get('items', [])]
                
                if not video_ids:
                    continue
                
                # Get statistics
                stats_response = self.youtube.videos().list(
                    part='statistics,snippet',
                    id=','.join(video_ids)
                ).execute()
                
                for item in stats_response.get('items', []):
                    stats = item['statistics']
                    snippet = item['snippet']
                    
                    engagement = (
                        int(stats.get('viewCount', 0)) * 0.1 +
                        int(stats.get('likeCount', 0)) * 1 +
                        int(stats.get('commentCount', 0)) * 2
                    )
                    
                    # FIX: Make datetime offset-naive
                    published_at = snippet['publishedAt'].replace('Z', '+00:00')
                    created = datetime.fromisoformat(published_at).replace(tzinfo=None)
                    
                    posts.append(SocialPost(
                        id=item['id'],
                        platform="youtube",
                        text=f"{snippet['title']}. {snippet.get('description', '')[:300]}",
                        author=snippet['channelTitle'],
                        created_at=created,
                        engagement_score=engagement,
                        url=f"https://youtube.com/watch?v={item['id']}",
                        hashtags=[]
                    ))
                    
            except Exception as e:
                print(f"YouTube collection error: {e}")
        
        return posts
    
    def get_trending_topics(self, location: Optional[str] = None) -> List[dict]:
        """Get YouTube trending videos."""
        region = location or 'US'
        try:
            response = self.youtube.videos().list(
                part='snippet,statistics',
                chart='mostPopular',
                regionCode=region,
                maxResults=25
            ).execute()
            
            return [{
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'views': item['statistics'].get('viewCount', 0),
                'url': f"https://youtube.com/watch?v={item['id']}"
            } for item in response.get('items', [])]
            
        except Exception as e:
            print(f"YouTube trending error: {e}")
            return []