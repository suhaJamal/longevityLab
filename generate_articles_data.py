#!/usr/bin/env python3
"""
Aging Narratives - Canada Articles Data
Generates aging_narratives_articles.csv with article text for ML classification
"""

from datetime import date
import mediacloud.api
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = '9e047cbfc9e1cd397857c21eb52c78902fc5f181'
START_DATE = date(2023, 1, 1)
END_DATE = date(2023, 12, 31)

# Narrative phrases to search
NARRATIVES = {
    'limiting': [
        'aging crisis',
        'aging population crisis',
        'elderly burden',
        'aging tsunami',
        'silver tsunami',
        'demographic time bomb'
    ],
    'neutral': [
        'aging population',
        'older adults',
        'senior citizens',
        'elderly population',
        'population aging'
    ],
    'empowering': [
        'active aging',
        'successful aging',
        'healthy aging',
        'aging well',
        'productive aging',
        'elder wisdom'
    ]
}

# Canadian province collection IDs
PROVINCES = {
    'Ontario': 38379397,
    'British Columbia': 38379407,
    'Alberta': 38379399,
    'Quebec': 38379395,
    'Saskatchewan': 38379406,
    'Manitoba': 38379405,
    'Nova Scotia': 38379416,
    'New Brunswick': 38379411,
    'PEI': 38379414
}

def scrape_article_text(url):
    """Scrape article text from URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Get text from paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs])
        
        return text[:5000]  # Limit to 5000 chars
    except Exception as e:
        print(f"    Error scraping {url}: {e}")
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
        for story in stories:
            url = story.get('url', '')
            print(f"    Scraping: {url[:50]}...")
            
            rows.append({
                'url': url,
                'title': story.get('title', ''),
                'publish_date': story.get('publish_date', ''),
                'media_name': story.get('media_name', ''),
                'phrase': phrase,
                'phrase_category': category,
                'province': province_name,
                'article_text': scrape_article_text(url)
            })
            
            time.sleep(0.3)  # Be polite to servers
        
        return rows
    except Exception as e:
        print(f"    Error: {e}")
        return []

def main():
    """Generate articles data for all Canadian provinces"""
    print("="*60)
    print("AGING NARRATIVES - CANADA ARTICLES DATA")
    print("="*60)
    
    mc = mediacloud.api.SearchApi(API_KEY)
    
    all_rows = []
    
    for province_name, collection_id in PROVINCES.items():
        print(f"\nProcessing {province_name}...")
        
        for category, phrases in NARRATIVES.items():
            for phrase in phrases:
                rows = get_articles(mc, phrase, category, province_name, collection_id)
                all_rows.extend(rows)
    
    # Convert to DataFrame and save
    df = pd.DataFrame(all_rows)
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/aging_narratives_articles.csv', index=False)
    
    print("\n" + "="*60)
    print(f"Done! Saved {len(df)} articles to data/aging_narratives_articles.csv")

if __name__ == "__main__":
    main()
