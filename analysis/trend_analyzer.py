# analysis/trend_analyzer.py
from collections import Counter, defaultdict
from typing import List, Dict, Tuple
import re
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from transformers import pipeline

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng')

class TrendAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.custom_stop = {'http', 'https', 'www', 'com', 'rt', 'amp', 'co'}
        self.stop_words.update(self.custom_stop)
        
        # Sentiment analysis
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            truncation=True
        )
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """Extract meaningful keywords using POS tagging."""
        # Clean text
        text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text.lower())
        tokens = word_tokenize(text)
        tokens = [t for t in tokens if t.isalpha() and len(t) > 2]
        
        # POS tagging - keep nouns and adjectives
        tagged = pos_tag(tokens)
        keywords = [word for word, tag in tagged 
                   if tag.startswith(('NN', 'JJ')) and word not in self.stop_words]
        
        return Counter(keywords).most_common(top_n)
    
    def analyze_sentiment(self, texts: List[str]) -> Dict:
        """Batch sentiment analysis."""
        results = {'positive': 0, 'negative': 0, 'neutral': 0, 'details': []}
        
        # Process in batches of 32
        for i in range(0, len(texts), 32):
            batch = texts[i:i+32]
            try:
                sentiments = self.sentiment_analyzer(batch)
                for s in sentiments:
                    label = s['label'].lower()
                    if label == 'positive':
                        results['positive'] += 1
                    else:
                        results['negative'] += 1
                    results['details'].append({
                        'label': label,
                        'score': round(s['score'], 3)
                    })
            except Exception as e:
                print(f"Sentiment batch error: {e}")
        
        total = sum([results['positive'], results['negative']])
        if total > 0:
            results['positive_pct'] = round(results['positive'] / total * 100, 1)
            results['negative_pct'] = round(results['negative'] / total * 100, 1)
        
        return results
    
    def find_trending_topics(self, posts: List, min_mentions: int = 3) -> List[Dict]:
        """Aggregate posts into trending topics."""
        # Collect all keywords weighted by engagement
        keyword_scores = defaultdict(float)
        keyword_posts = defaultdict(list)
        
        for post in posts:
            keywords = self.extract_keywords(post.text, top_n=5)
            for word, count in keywords:
                keyword_scores[word] += count * (1 + post.engagement_score / 100)
                keyword_posts[word].append(post)
        
        # Filter and sort
        trending = []
        for word, score in sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True):
            if len(keyword_posts[word]) >= min_mentions:
                posts_for_topic = keyword_posts[word]
                sentiments = self.analyze_sentiment([p.text for p in posts_for_topic[:50]])
                
                trending.append({
                    'topic': word,
                    'mention_count': len(posts_for_topic),
                    'engagement_score': round(score, 2),
                    'sentiment': sentiments,
                    'platforms': list(set(p.platform for p in posts_for_topic)),
                    'sample_posts': [
                        {'text': p.text[:150], 'url': p.url, 'platform': p.platform}
                        for p in sorted(posts_for_topic, key=lambda x: x.engagement_score, reverse=True)[:3]
                    ],
                    'trending_velocity': self._calculate_velocity(posts_for_topic)
                })
        
        return trending[:50]  # Top 50 topics
    
    def _calculate_velocity(self, posts: List) -> str:
        """Determine if topic is rising, steady, or falling."""
        if len(posts) < 2:
            return "insufficient_data"
        
        # FIX: Normalize all datetimes to offset-naive UTC
        def normalize_dt(dt):
            if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                return dt.replace(tzinfo=None)
            return dt
        
        posts_sorted = sorted(posts, key=lambda p: normalize_dt(p.created_at))
        first_half = posts_sorted[:len(posts)//2]
        second_half = posts_sorted[len(posts)//2:]
        
        first_engagement = sum(p.engagement_score for p in first_half) / max(len(first_half), 1)
        second_engagement = sum(p.engagement_score for p in second_half) / max(len(second_half), 1)
        
        if second_engagement > first_engagement * 1.5:
            return "🔥 rising_fast"
        elif second_engagement > first_engagement * 1.1:
            return "📈 rising"
        elif second_engagement < first_engagement * 0.7:
            return "📉 falling"
        else:
            return "➡️ steady"