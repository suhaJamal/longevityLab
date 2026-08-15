#!/usr/bin/env python3
"""
Simple test script - Extract articles for ONE phrase only
"""

from datetime import date
import mediacloud.api
import json
import pandas as pd
import time

# Configuration
API_KEY = '...'
START_DATE = date(2023, 1, 1)
END_DATE = date(2023, 12, 31)

# Test with just ONE phrase
TEST_PHRASE = 'aging crisis'

# CANADA FILTER:
# To filter by Canada, you need a collection ID
# Run find_canada_collection.py first to get the ID
# Then set: CANADA_COLLECTION_ID = [12345]  # Replace with actual ID
# Leave as None to search ALL media globally
CANADA_COLLECTION_ID = None  # Set to [collection_id] for Canada only

print("="*80)
print(f"TESTING WITH SINGLE PHRASE: '{TEST_PHRASE}'")
print("="*80)
print(f"Period: {START_DATE} to {END_DATE}")
if CANADA_COLLECTION_ID:
    print(f"Filter: Canada collection {CANADA_COLLECTION_ID}")
else:
    print(f"Filter: ALL MEDIA GLOBALLY (no country filter)")
print()

# Initialize API
mc = mediacloud.api.SearchApi(API_KEY)

# Step 1: Get the count
print("Step 1: Getting story count...")
if CANADA_COLLECTION_ID:
    count_result = mc.story_count(TEST_PHRASE,
                                 start_date=START_DATE,
                                 end_date=END_DATE,
                                 collection_ids=CANADA_COLLECTION_ID)
else:
    count_result = mc.story_count(TEST_PHRASE,
                                 start_date=START_DATE,
                                 end_date=END_DATE)
count = count_result['relevant']
print(f"  Found {count:,} stories with '{TEST_PHRASE}'\n")

# Wait a bit before next request
time.sleep(2)

# Step 2: Extract sample articles
print("Step 2: Extracting sample articles...")
try:
    if CANADA_COLLECTION_ID:
        story_result = mc.story_list(TEST_PHRASE,
                                    start_date=START_DATE,
                                    end_date=END_DATE,
                                    collection_ids=CANADA_COLLECTION_ID)
    else:
        story_result = mc.story_list(TEST_PHRASE,
                                    start_date=START_DATE,
                                    end_date=END_DATE)

    stories = story_result[0]
    print(f"  Retrieved {len(stories):,} articles\n")

    # Show first 3 articles as examples
    print("="*80)
    print("SAMPLE ARTICLES (first 3):")
    print("="*80)

    for i, story in enumerate(stories[:3], 1):
        print(f"\n{i}. {story.get('title', 'No title')}")
        print(f"   URL: {story.get('url', 'No URL')}")
        print(f"   Media: {story.get('media_name', 'Unknown')}")
        print(f"   Date: {story.get('publish_date', 'Unknown')}")

    # Save to CSV
    print("\n" + "="*80)
    print("Saving articles to CSV...")

    articles_data = []
    for story in stories:
        articles_data.append({
            'title': story.get('title', ''),
            'url': story.get('url', ''),
            'media_name': story.get('media_name', ''),
            'publish_date': story.get('publish_date', ''),
            'phrase': TEST_PHRASE
        })

    df = pd.DataFrame(articles_data)
    df.to_csv('test_articles_1.csv', index=False)
    print(f"✓ Saved {len(stories)} articles to 'test_articles.csv'")

    print("\n" + "="*80)
    print("SUCCESS! You can now open 'test_articles.csv' to see the results.")
    print("="*80)

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()