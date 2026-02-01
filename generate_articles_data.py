#!/usr/bin/env python3
"""
Aging Narratives - Canada Articles Data
Generates aging_narratives_articles.csv with article text for ML classification
Saves progress every BATCH_SIZE articles to prevent data loss
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
START_DATE = date(2025, 1, 1)
END_DATE = date(2026, 1, 30)
BATCH_SIZE = 200  # Save every 200 articles
OUTPUT_FILE = 'newData/aging_narratives_articles.csv'

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

def load_existing_data():
    """Load existing data if available, returns DataFrame and set of scraped URLs"""
    if os.path.exists(OUTPUT_FILE):
        try:
            df = pd.read_csv(OUTPUT_FILE)
            scraped_urls = set(df['url'].tolist())
            print(f"Loaded {len(df)} existing articles from {OUTPUT_FILE}")
            print(f"Will skip {len(scraped_urls)} already scraped URLs")
            return df.to_dict('records'), scraped_urls
        except Exception as e:
            print(f"Error loading existing data: {e}")
    return [], set()

def save_data(rows):
    """Save current data to CSV"""
    os.makedirs('newData', exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"  [SAVED] {len(rows)} articles to {OUTPUT_FILE}")

def main():
    """Generate articles data for all Canadian provinces"""
    print("="*60)
    print("AGING NARRATIVES - CANADA ARTICLES DATA")
    print(f"Batch size: {BATCH_SIZE} (saves every {BATCH_SIZE} articles)")
    print("="*60)

    mc = mediacloud.api.SearchApi(API_KEY)

    # Load existing data to resume from where we left off
    all_rows, scraped_urls = load_existing_data()
    articles_since_last_save = 0

    for province_name, collection_id in PROVINCES.items():
        print(f"\nProcessing {province_name}...")

        for category, phrases in NARRATIVES.items():
            for phrase in phrases:
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

                    for story in stories:
                        url = story.get('url', '')

                        # Skip if already scraped
                        if url in scraped_urls:
                            print(f"    Skipping (already scraped): {url[:50]}...")
                            continue

                        print(f"    Scraping: {url[:50]}...")

                        row = {
                            'url': url,
                            'title': story.get('title', ''),
                            'publish_date': story.get('publish_date', ''),
                            'media_name': story.get('media_name', ''),
                            'phrase': phrase,
                            'phrase_category': category,
                            'province': province_name,
                            'article_text': scrape_article_text(url)
                        }

                        all_rows.append(row)
                        scraped_urls.add(url)
                        articles_since_last_save += 1

                        # Save every BATCH_SIZE articles
                        if articles_since_last_save >= BATCH_SIZE:
                            save_data(all_rows)
                            articles_since_last_save = 0

                        time.sleep(0.3)  # Be polite to servers

                except Exception as e:
                    print(f"    Error: {e}")
                    # Save on error to preserve progress
                    if all_rows:
                        save_data(all_rows)
                        articles_since_last_save = 0

    # Final save
    save_data(all_rows)

    print("\n" + "="*60)
    print(f"Done! Saved {len(all_rows)} articles to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
