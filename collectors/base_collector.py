# collectors/base_collector.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import hashlib

@dataclass
class SocialPost:
    id: str
    platform: str
    text: str
    author: str
    created_at: datetime
    engagement_score: float  # likes + shares + comments weighted
    url: Optional[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    
    def __post_init__(self):
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []
    
    @property
    def unique_key(self):
        return hashlib.md5(f"{self.platform}:{self.id}".encode()).hexdigest()

class BaseCollector(ABC):
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
    
    @abstractmethod
    def collect(self, keywords: List[str], hours_back: int = 24) -> List[SocialPost]:
        """Collect posts matching keywords from the last N hours."""
        pass
    
    @abstractmethod
    def get_trending_topics(self, location: Optional[str] = None) -> List[dict]:
        """Get platform-native trending topics."""
        pass