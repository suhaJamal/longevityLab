#!/usr/bin/env python3
"""
Aging Narratives - Canada Temporal Analysis
Generates aging_narratives_temporal.csv for Canadian media
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
def get_temporal_data(mc, phrase, category, province_name, collection_id):
    """Get daily story counts for a phrase in one province"""
    print(f"  '{phrase}' in {province_name}...")
    
    time.sleep(0.3)  # Avoid rate limiting
    
    time_results = mc.story_count_over_time(
        phrase,
        start_date=START_DATE,
        end_date=END_DATE,
        collection_ids=[collection_id]
    )
    
    # Add metadata to each row
    rows = []
    for entry in time_results:
        rows.append({
            'date': entry['date'],
            'count': entry['count'],
            'phrase': phrase,
            'category': category,
            'province': province_name
        })
    
    return rows

def main():
    """Generate temporal data for all Canadian provinces"""
    print("="*60)
    print("AGING NARRATIVES - CANADA TEMPORAL ANALYSIS")
    print("="*60)
    
    mc = mediacloud.api.SearchApi(API_KEY)
    
    all_rows = []
    
    for province_name, collection_id in PROVINCES.items():
        print(f"\nProcessing {province_name}...")
        
        for category, phrases in NARRATIVES.items():
            for phrase in phrases:
                rows = get_temporal_data(mc, phrase, category, province_name, collection_id)
                all_rows.extend(rows)
    
    # Convert to DataFrame and save
    df = pd.DataFrame(all_rows)
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/aging_narratives_temporal.csv', index=False)
    
    print("\n" + "="*60)
    print(f"Done! Saved {len(df)} rows to data/aging_narratives_temporal.csv")

if __name__ == "__main__":
    main()
