# main.py
import os
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

from collectors.youtube_collector import YouTubeCollector
from collectors.hackernews_collector import HackerNewsCollector
from collectors.devto_collector import DevToCollector
from collectors.github_collector import GitHubCollector
from analysis.trend_analyzer import TrendAnalyzer

import json

load_dotenv()

class TrendTracker:
    def __init__(self):
        self.collectors = {
            'youtube': YouTubeCollector(),
            'hackernews': HackerNewsCollector(),
            'devto': DevToCollector(),
            'github': GitHubCollector()
        }
        self.analyzer = TrendAnalyzer()
    
    def run_analysis(self, business_keywords: List[str], hours_back: int = 24):
        all_posts = []
        
        print(f"🔍 Starting collection for keywords: {business_keywords}")
        
        for name, collector in self.collectors.items():
            print(f"\n📡 Collecting from {name}...")
            try:
                posts = collector.collect(business_keywords, hours_back)
                all_posts.extend(posts)
                print(f"   ✓ Collected {len(posts)} posts from {name}")
            except Exception as e:
                print(f"   ✗ Error with {name}: {e}")
        
        print(f"\n📊 Total posts collected: {len(all_posts)}")
        
        if not all_posts:
            print("No data collected. Check API credentials.")
            return None
        
        print("\n🧠 Analyzing trends...")
        trending_topics = self.analyzer.find_trending_topics(all_posts, min_mentions=2)
        
        platform_trends = {}
        for name, collector in self.collectors.items():
            try:
                platform_trends[name] = collector.get_trending_topics()
            except Exception as e:
                platform_trends[name] = []
        
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'keywords_searched': business_keywords,
            'total_posts_analyzed': len(all_posts),
            'trending_topics': trending_topics,
            'platform_native_trending': platform_trends,
            'summary': {
                'top_rising_topics': [t for t in trending_topics if 'rising' in t['trending_velocity']][:10],
                'most_engaging_topic': max(trending_topics, key=lambda x: x['engagement_score']) if trending_topics else None,
                'sentiment_overview': self._aggregate_sentiment(trending_topics)
            }
        }
        
        return report
    
    def _aggregate_sentiment(self, topics: List[Dict]) -> Dict:
        total_pos = sum(t['sentiment'].get('positive', 0) for t in topics)
        total_neg = sum(t['sentiment'].get('negative', 0) for t in topics)
        total = total_pos + total_neg
        
        if total == 0:
            return {'overall': 'neutral', 'positive_pct': 50}
        
        pos_pct = round(total_pos / total * 100, 1)
        return {
            'overall': 'positive' if pos_pct > 55 else 'negative' if pos_pct < 45 else 'mixed',
            'positive_pct': pos_pct
        }

if __name__ == "__main__":
    tracker = TrendTracker()
    
    keywords = [
        "AI business tools",
        "SaaS pricing",
        "startup funding",
        "remote work",
        "productivity software",
        "B2B marketing"
    ]
    
    report = tracker.run_analysis(keywords, hours_back=24)
    
    with open(f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.json", 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("📈 TRENDING TOPICS SUMMARY")
    print("="*60)
    
    for i, topic in enumerate(report['trending_topics'][:10], 1):
        print(f"\n{i}. {topic['topic'].upper()} {topic['trending_velocity']}")
        print(f"   Mentions: {topic['mention_count']} | Engagement: {topic['engagement_score']}")
        print(f"   Sentiment: {topic['sentiment'].get('positive_pct', 0)}% positive")
        print(f"   Platforms: {', '.join(topic['platforms'])}")