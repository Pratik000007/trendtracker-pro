import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
from .base_collector import BaseCollector, SocialPost

class GitHubCollector(BaseCollector):
    def __init__(self):
        super().__init__("github")
    
    def collect(self, keywords: List[str], hours_back: int = 24) -> List[SocialPost]:
        posts = []
        
        # Map keywords to GitHub languages/topics
        keyword_to_lang = {
            'ai': ['python', 'javascript', 'typescript'],
            'business': ['python', 'javascript'],
            'saas': ['javascript', 'typescript', 'python'],
            'startup': ['javascript', 'python'],
            'productivity': ['javascript', 'typescript'],
            'marketing': ['javascript', 'python'],
            'remote': ['javascript', 'typescript'],
            'software': ['python', 'javascript', 'go', 'rust']
        }
        
        # Get unique languages to search
        languages = set()
        for kw in keywords:
            kw_lower = kw.lower().replace(' tools', '').replace(' software', '').replace(' pricing', '').replace(' business', '')
            if kw_lower in keyword_to_lang:
                languages.update(keyword_to_lang[kw_lower])
        
        if not languages:
            languages = ['python', 'javascript', 'typescript']
        
        for lang in languages:
            try:
                url = f"https://github.com/trending/{lang}?since=daily"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                repos = soup.find_all('article', class_='Box-row')
                
                for repo in repos[:15]:
                    try:
                        link = repo.find('h2', class_='h3').find('a')
                        name = link.text.strip().replace('\n', '').replace(' ', '')
                        repo_url = f"https://github.com{link['href']}"
                        
                        desc = repo.find('p', class_='col-9')
                        description = desc.text.strip() if desc else ''
                        
                        text = f"{name} {description}".lower()
                        
                        # FIX: Looser keyword matching - check each word
                        matched = False
                        for kw in keywords:
                            kw_words = kw.lower().split()
                            for word in kw_words:
                                if len(word) > 2 and word in text:
                                    matched = True
                                    break
                            if matched:
                                break
                        
                        if not matched:
                            continue
                        
                        stars_text = repo.find('a', href=lambda x: x and 'stargazers' in x)
                        stars = 0
                        if stars_text:
                            try:
                                stars = int(stars_text.text.strip().replace(',', ''))
                            except:
                                pass
                        
                        posts.append(SocialPost(
                            id=name.replace('/', '-'),
                            platform="github",
                            text=f"{name}: {description}",
                            author=name.split('/')[0],
                            created_at=datetime.utcnow(),
                            engagement_score=stars,
                            url=repo_url,
                            hashtags=[lang]
                        ))
                    except Exception:
                        continue
            except Exception as e:
                print(f"GitHub error: {e}")
        
        return posts
    
    def get_trending_topics(self, location: Optional[str] = None) -> List[dict]:
        trending = []
        try:
            url = "https://github.com/trending?since=daily"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            repos = soup.find_all('article', class_='Box-row')[:10]
            for repo in repos:
                try:
                    link = repo.find('h2', class_='h3').find('a')
                    name = link.text.strip().replace('\n', '').replace(' ', '')
                    desc = repo.find('p', class_='col-9')
                    
                    trending.append({
                        'name': name,
                        'description': desc.text.strip() if desc else '',
                        'url': f"https://github.com{link['href']}"
                    })
                except Exception:
                    continue
        except Exception as e:
            print(f"GitHub trending error: {e}")
        return trending