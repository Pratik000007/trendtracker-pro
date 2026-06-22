# collectors/twitter_collector.py
import tweepy
import os
from datetime import datetime, timedelta
from typing import List, Optional
from .base_collector import BaseCollector, SocialPost

class TwitterCollector(BaseCollector):
    def __init__(self):
        super().__init__("twitter")
        # Use ONLY Bearer Token for read-only access
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            wait_on_rate_limit=True
        )
    
    def collect(self, keywords: List[str], hours_back: int = 24) -> List[SocialPost]:
        posts = []
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        query = f"({' OR '.join(keywords)}) -is:retweet lang:en"
        
        try:
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                tweet_fields=['created_at', 'public_metrics', 'entities', 'author_id'],
                expansions=['author_id'],
                user_fields=['username'],
                max_results=100,
                start_time=start_time.isoformat() + "Z"
            ).flatten(limit=1000)
            
            for tweet in tweets:
                metrics = tweet.public_metrics or {}
                engagement = (
                    metrics.get('like_count', 0) * 1 +
                    metrics.get('retweet_count', 0) * 2 +
                    metrics.get('reply_count', 0) * 1.5 +
                    metrics.get('quote_count', 0) * 2
                )
                
                hashtags = []
                if tweet.entities and 'hashtags' in tweet.entities:
                    hashtags = [h['tag'] for h in tweet.entities['hashtags']]
                
                posts.append(SocialPost(
                    id=str(tweet.id),
                    platform="twitter",
                    text=tweet.text,
                    author=str(tweet.author_id),
                    created_at=tweet.created_at,
                    engagement_score=engagement,
                    url=f"https://twitter.com/i/web/status/{tweet.id}",
                    hashtags=hashtags
                ))
                
        except Exception as e:
            print(f"Twitter collection error: {e}")
        
        return posts