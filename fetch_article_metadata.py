#!/usr/bin/env python3
"""
Fetch all article metadata (URLs, titles, etc.) from MediaCloud API
Saves to CSV WITHOUT scraping - just metadata
This is fast and won't lose data if scraping fails later
Includes retry logic for rate limiting
"""

from datetime import date
import mediacloud.api
import pandas as pd
import time
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = '...'
START_DATE = date(2025, 1, 1)
END_DATE = date(2026, 1, 30)
OUTPUT_FILE = 'newData/article_metadata.csv'

# Rate limiting settings
REQUEST_DELAY = 2  # Seconds between requests
MAX_RETRIES = 5    # Max retry attempts per query
RETRY_DELAY = 10   # Initial retry delay (doubles each retry)

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

def load_existing_metadata():
    """Load existing metadata if available"""
    if os.path.exists(OUTPUT_FILE):
        try:
            df = pd.read_csv(OUTPUT_FILE)
            print(f"Loaded {len(df)} existing records from {OUTPUT_FILE}")
            return df.to_dict('records'), set(df['url'].tolist())
        except Exception as e:
            print(f"Error loading existing data: {e}")
    return [], set()

def save_metadata(rows):
    """Save metadata to CSV"""
    os.makedirs('newData', exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"  [SAVED] {len(rows)} records to {OUTPUT_FILE}")

def fetch_with_retry(mc, phrase, start_date, end_date, collection_ids):
    """Fetch stories with retry logic for rate limiting"""
    retry_delay = RETRY_DELAY

    for attempt in range(MAX_RETRIES):
        try:
            story_result = mc.story_list(
                phrase,
                start_date=start_date,
                end_date=end_date,
                collection_ids=collection_ids
            )
            return story_result[0]
        except Exception as e:
            error_str = str(e)
            if "Expecting value" in error_str or "JSONDecodeError" in error_str:
                # Rate limited - wait and retry
                if attempt < MAX_RETRIES - 1:
                    print(f"    Rate limited. Waiting {retry_delay}s before retry {attempt + 2}/{MAX_RETRIES}...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"    Failed after {MAX_RETRIES} attempts")
                    return None
            else:
                # Other error
                print(f"    Error: {e}")
                return None
    return None

def main():
    """Fetch all article metadata from MediaCloud"""
    print("="*60)
    print("FETCHING ARTICLE METADATA FROM MEDIACLOUD")
    print("(No scraping - just URLs and metadata)")
    print(f"Delay between requests: {REQUEST_DELAY}s")
    print(f"Max retries on rate limit: {MAX_RETRIES}")
    print("="*60)

    mc = mediacloud.api.SearchApi(API_KEY)

    # Load existing data to avoid duplicates
    all_rows, existing_urls = load_existing_metadata()
    new_count = 0
    failed_queries = []

    for province_name, collection_id in PROVINCES.items():
        print(f"\nProcessing {province_name}...")

        for category, phrases in NARRATIVES.items():
            for phrase in phrases:
                print(f"  '{phrase}' in {province_name}...")

                # Check if we already have data for this phrase/province
                # (allows resuming)

                time.sleep(REQUEST_DELAY)  # Delay between requests

                stories = fetch_with_retry(mc, phrase, START_DATE, END_DATE, [collection_id])

                if stories is None:
                    failed_queries.append(f"{phrase} in {province_name}")
                    # Save progress on failure
                    if all_rows:
                        save_metadata(all_rows)
                    continue

                print(f"    Found {len(stories)} articles")

                for story in stories:
                    url = story.get('url', '')

                    # Skip duplicates
                    if url in existing_urls:
                        continue

                    row = {
                        'url': url,
                        'title': story.get('title', ''),
                        'publish_date': story.get('publish_date', ''),
                        'media_name': story.get('media_name', ''),
                        'media_url': story.get('media_url', ''),
                        'phrase': phrase,
                        'phrase_category': category,
                        'province': province_name,
                    }

                    all_rows.append(row)
                    existing_urls.add(url)
                    new_count += 1

    # Final save
    save_metadata(all_rows)

    print("\n" + "="*60)
    print(f"Done! Total: {len(all_rows)} articles")
    print(f"New articles added: {new_count}")
    print(f"Saved to: {OUTPUT_FILE}")

    if failed_queries:
        print(f"\nFailed queries ({len(failed_queries)}):")
        for q in failed_queries:
            print(f"  - {q}")
        print("\nRun the script again to retry failed queries.")

    print("\nNext step: Run scrape_missing_articles.py to scrape the text")

if __name__ == "__main__":
    main()
