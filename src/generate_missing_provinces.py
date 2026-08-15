#!/usr/bin/env python3
"""
Fetch articles for missing provinces only
"""

from datetime import date
import mediacloud.api
import pandas as pd
import time
import os
import random
from bs4 import BeautifulSoup

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    print("Cloudscraper not available - install with: pip install cloudscraper")

print("Script loaded...")

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = '...'
START_DATE = date(2023, 1, 1)
END_DATE = date(2023, 12, 31)

NARRATIVES = {
    'limiting': [
        'aging crisis', 'aging population crisis', 'elderly burden',
        'aging tsunami', 'silver tsunami', 'demographic time bomb'
    ],
    'neutral': [
        'aging population', 'older adults', 'senior citizens',
        'elderly population', 'population aging'
    ],
    'empowering': [
        'active aging', 'successful aging', 'healthy aging',
        'aging well', 'productive aging', 'elder wisdom'
    ]
}

# Only missing provinces
MISSING_PROVINCES = {
    'Alberta': 38379399,
    'Quebec': 38379395,
    'Saskatchewan': 38379406,
    'Manitoba': 38379405,
    'Nova Scotia': 38379416,
    'New Brunswick': 38379411,
    'PEI': 38379414
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
]

def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/'
    }

def scrape_article_text(url):
    """Scrape using cloudscraper for bot bypass"""
    if not CLOUDSCRAPER_AVAILABLE:
        return ""
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, headers=get_headers(), timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text().strip() for p in paragraphs])
            return text[:5000] if text else ""
    except Exception as e:
        print(f"    Error: {e}")
    return ""


def get_articles(mc, phrase, category, province_name, collection_id):
    """Fetch articles for a phrase in one province"""
    print(f"  '{phrase}' in {province_name}...")
    
    time.sleep(0.5)
    
    try:
        story_result = mc.story_list(
            phrase,
            start_date=START_DATE,
            end_date=END_DATE,
            collection_ids=[collection_id]
        )
        
        stories = story_result[0]
        print(f"    Found {len(stories)} articles")
        
        rows = []
        for i, story in enumerate(stories, 1):
            url = story.get('url', '')
            print(f"    [{i}/{len(stories)}] Scraping: {url[:50]}...")
            text = scrape_article_text(url)
            
            # Only keep if text is 500+ chars
            if len(text) >= 500:
                rows.append({
                    'url': url,
                    'title': story.get('title', ''),
                    'publish_date': story.get('publish_date', ''),
                    'media_name': story.get('media_name', ''),
                    'phrase': phrase,
                    'phrase_category': category,
                    'province': province_name,
                    'article_text': text
                })
            
            time.sleep(0.3)
        
        return rows
    except Exception as e:
        print(f"    Error: {e}")
        return []
    
def main():
    """Generate articles data for missing provinces"""
    print("="*60)
    print("FETCHING ARTICLES FOR MISSING PROVINCES")
    print("="*60)
    
    mc = mediacloud.api.SearchApi(API_KEY)
    
    all_rows = []
    
    for province_name, collection_id in MISSING_PROVINCES.items():
        print(f"\nProcessing {province_name}...")
        
        for category, phrases in NARRATIVES.items():
            for phrase in phrases:
                rows = get_articles(mc, phrase, category, province_name, collection_id)
                all_rows.extend(rows)

                # Save after each phrase
                df = pd.DataFrame(all_rows)
                os.makedirs('../data', exist_ok=True)
                df.to_csv('../data/aging_narratives_articles_missing_provinces.csv', index=False)
                print(f"    Saved progress: {len(df)} articles total")
    
    print("\n" + "="*60)
    print(f"Done! Saved {len(all_rows)} articles to data/aging_narratives_articles_missing_provinces.csv")

if __name__ == "__main__":
    main()

