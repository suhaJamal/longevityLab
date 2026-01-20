#!/usr/bin/env python3
"""
Media Cloud API - Quick Connection Test
Tests API connectivity before running the full analysis
"""

import mediacloud.api
from datetime import date

print("="*80)
print("MEDIA CLOUD API CONNECTION TEST")
print("="*80)

# Configuration
API_KEY = '9e047cbfc9e1cd397857c21eb52c78902fc5f181'
print(f"\nAPI Key: {API_KEY[:20]}...")

# Test dates
START = date(2023, 1, 1)
END = date(2023, 12, 31)
print(f"Test period: {START} to {END}")

# Initialize
print("\n1. Initializing API connection...")
try:
    mc = mediacloud.api.SearchApi(API_KEY)
    print("   ✓ API object created")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

# Test 1: story_count
print("\n2. Testing story_count method...")
try:
    result = mc.story_count('aging', start_date=START, end_date=END)
    print(f"   ✓ SUCCESS")
    print(f"     Stories matching 'aging': {result['relevant']:,}")
    print(f"     Total stories in database: {result['total']:,}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

# Test 2: story_count_over_time
print("\n3. Testing story_count_over_time method...")
try:
    time_result = mc.story_count_over_time('aging crisis', 
                                          start_date=START, 
                                          end_date=END)
    print(f"   ✓ SUCCESS")
    print(f"     Returned {len(time_result)} daily data points")
    print(f"     First date: {time_result[0]['date']}")
    print(f"     Last date: {time_result[-1]['date']}")
    print(f"     Sample: {time_result[0]['count']} stories on {time_result[0]['date']}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

# Test 3: story_list
print("\n4. Testing story_list method...")
try:
    story_result = mc.story_list('aging population crisis',
                                start_date=START,
                                end_date=END)
    
    stories = story_result[0]  # First element is the story list
    pagination = story_result[1]  # Second element is pagination info
    
    print(f"   ✓ SUCCESS")
    print(f"     Retrieved {len(stories)} stories")
    print(f"     Pagination token: {pagination[:30]}...")
    
    if stories:
        first_story = stories[0]
        print(f"\n     First story details:")
        print(f"       Title: {first_story.get('title', 'N/A')[:80]}...")
        print(f"       URL: {first_story.get('url', 'N/A')[:80]}...")
        print(f"       Published: {first_story.get('publish_date', 'N/A')}")
        print(f"       Media: {first_story.get('media_name', 'N/A')}")
        print(f"       Available fields: {list(first_story.keys())}")
        
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

# Test 4: Test one phrase from each category
print("\n5. Testing narrative category phrases...")
test_phrases = {
    'limiting': 'aging tsunami',
    'neutral': 'older adults',
    'empowering': 'healthy aging'
}

for category, phrase in test_phrases.items():
    try:
        result = mc.story_count(phrase, start_date=START, end_date=END)
        count = result['relevant']
        print(f"   {category.upper()}: '{phrase}' = {count:,} stories ✓")
    except Exception as e:
        print(f"   {category.upper()}: '{phrase}' FAILED: {e}")

print("\n" + "="*80)
print("CONNECTION TEST COMPLETE")
print("="*80)
print("\n✓ All tests passed!")
print("\nYou're ready to run the full analysis:")
print("  python aging_narrative_complete_analysis.py")
print("\nExpected runtime: 15-30 minutes")
print("="*80)
