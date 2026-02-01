#!/usr/bin/env python3
"""
Aging Narratives - Canada Volume Analysis
Generates aging_narratives_volume.json for Canadian media
"""

from datetime import date
import mediacloud.api
import json
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = '9e047cbfc9e1cd397857c21eb52c78902fc5f181'
START_DATE = date(2025, 1, 1)
END_DATE = date(2026, 1, 30)

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
    'Quebec': 38379395

}
'''
    'Saskatchewan': 38379406,
    'Manitoba': 38379405,
    'Nova Scotia': 38379416,
    'New Brunswick': 38379411,
    'PEI': 38379414

'''


def get_province_volume(mc, province_name, collection_id):
    """Get story counts for all narrative phrases in one province"""
    print(f"\nProcessing {province_name}...")
    
    results = {
        'limiting': {},
        'neutral': {},
        'empowering': {}
    }
    
    for category, phrases in NARRATIVES.items():
        for phrase in phrases:
            time.sleep(0.3)  # Avoid rate limiting
            count_result = mc.story_count(
                phrase,
                start_date=START_DATE,
                end_date=END_DATE,
                collection_ids=[collection_id]
            )
            count = count_result['relevant']
            results[category][phrase] = count
            print(f"  '{phrase}': {count}")
    
    return results

def main():
    """Generate volume data for all Canadian provinces"""
    print("="*60)
    print("AGING NARRATIVES - CANADA VOLUME ANALYSIS")
    print("="*60)
    
    mc = mediacloud.api.SearchApi(API_KEY)
    
    # Collect data for each province
    volume_by_province = {}
    for province_name, collection_id in PROVINCES.items():
        volume_by_province[province_name] = get_province_volume(mc, province_name, collection_id)
    
    # Build final output
    output = {
        'year': 2023,
        'country': 'Canada',
        'narratives': NARRATIVES,
        'provinces': list(PROVINCES.keys()),
        'volume_by_province': volume_by_province
    }
    
    # Save to JSON
    with open('newData/aging_narratives_volume.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "="*60)
    print("Done! Saved to aging_narratives_volume.json")

if __name__ == "__main__":
    main()
