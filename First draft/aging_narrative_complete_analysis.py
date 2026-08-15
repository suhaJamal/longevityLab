#!/usr/bin/env python3
"""
Aging Narratives Analysis - Media Cloud Study
Analyzes limiting, neutral, and empowering narratives about aging in 2023 media coverage
"""

from datetime import date
import mediacloud.api
import json
import pandas as pd
from collections import defaultdict
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = '...'
YEAR = 2023
START_DATE = date(2023, 1, 1)
END_DATE = date(2023, 12, 31)

# Three narrative categories with search phrases
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

# ============================================================================
# STEP 1: VOLUME ANALYSIS - Calculate Narrative Imbalance Ratios
# ============================================================================

def get_volume_data(mc):
    """Get story counts for all narrative phrases"""
    print("="*80)
    print("STEP 1: VOLUME ANALYSIS")
    print("="*80)
    
    results = {
        'limiting': {},
        'neutral': {},
        'empowering': {}
    }
    
    for category, phrases in NARRATIVES.items():
        print(f"\n{category.upper()} NARRATIVES:")
        print("-"*80)

        category_total = 0
        for i, phrase in enumerate(phrases):
            # Add small delay between requests (except first one)
            if i > 0 or list(NARRATIVES.keys()).index(category) > 0:
                time.sleep(0.3)  # 0.3 second delay

            count_result = mc.story_count(phrase, start_date=START_DATE, end_date=END_DATE)
            count = count_result['relevant']
            results[category][phrase] = count
            category_total += count
            print(f"  '{phrase}': {count:>8,} stories")
        
        results[category]['TOTAL'] = category_total
        print(f"  {'─'*76}")
        print(f"  TOTAL {category}: {category_total:>8,} stories")
    
    return results

def calculate_imbalance_ratios(volume_data):
    """Calculate and display narrative imbalance ratios"""
    print("\n" + "="*80)
    print("NARRATIVE IMBALANCE ANALYSIS")
    print("="*80)
    
    limiting = volume_data['limiting']['TOTAL']
    neutral = volume_data['neutral']['TOTAL']
    empowering = volume_data['empowering']['TOTAL']
    
    print(f"\nLimiting narratives:    {limiting:>10,} stories")
    print(f"Neutral narratives:     {neutral:>10,} stories")
    print(f"Empowering narratives:  {empowering:>10,} stories")
    
    total = limiting + neutral + empowering
    print(f"\n{'─'*80}")
    print(f"TOTAL:                  {total:>10,} stories")
    
    # Calculate percentages
    print(f"\nPercentage Distribution:")
    print(f"  Limiting:    {(limiting/total*100):>6.2f}%")
    print(f"  Neutral:     {(neutral/total*100):>6.2f}%")
    print(f"  Empowering:  {(empowering/total*100):>6.2f}%")
    
    # Calculate imbalance ratios
    print(f"\nImbalance Ratios:")
    if empowering > 0:
        ratio_1 = limiting / empowering
        print(f"  Limiting/Empowering:  {ratio_1:.2f} : 1")
        print(f"    → For every 1 empowering story, there are {ratio_1:.1f} limiting stories")
    
    if neutral > 0:
        ratio_2 = limiting / neutral
        print(f"  Limiting/Neutral:     {ratio_2:.2f} : 1")
        
        ratio_3 = empowering / neutral
        print(f"  Empowering/Neutral:   {ratio_3:.2f} : 1")
    
    return {
        'limiting': limiting,
        'neutral': neutral,
        'empowering': empowering,
        'total': total,
        'imbalance_ratio': limiting / empowering if empowering > 0 else None
    }

# ============================================================================
# STEP 2: TEMPORAL ANALYSIS - Track narrative trends over time
# ============================================================================

def get_temporal_data(mc, phrase, category):
    """Get time series data for a specific phrase"""
    time_results = mc.story_count_over_time(phrase, 
                                           start_date=START_DATE, 
                                           end_date=END_DATE)
    
    # Add metadata
    for entry in time_results:
        entry['phrase'] = phrase
        entry['category'] = category
    
    return time_results

def analyze_temporal_trends(mc):
    """Analyze temporal trends for all narratives"""
    print("\n" + "="*80)
    print("STEP 2: TEMPORAL TREND ANALYSIS")
    print("="*80)

    all_time_series = []

    for category, phrases in NARRATIVES.items():
        print(f"\nGathering time series for {category.upper()} narratives...")

        for phrase in phrases:
            print(f"  Processing: '{phrase}'")

            # Add small delay to avoid rate limiting
            if len(all_time_series) > 0:
                time.sleep(0.5)  # 0.5 second delay between requests

            time_data = get_temporal_data(mc, phrase, category)
            all_time_series.extend(time_data)
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(all_time_series)
    
    # Aggregate by category and date
    category_daily = df.groupby(['date', 'category']).agg({
        'count': 'sum',
        'total_count': 'first'  # Total is same for all on a given day
    }).reset_index()
    
    category_daily['ratio'] = category_daily['count'] / category_daily['total_count']
    
    print(f"\n✓ Processed {len(df)} data points across {len(df['date'].unique())} days")
    
    # Calculate monthly aggregates
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
    monthly_summary = df.groupby(['month', 'category'])['count'].sum().unstack(fill_value=0)
    
    print(f"\nMonthly Summary:")
    print(monthly_summary)
    
    return df, category_daily, monthly_summary

# ============================================================================
# STEP 3: ARTICLE EXTRACTION - Get sample articles for manual coding
# ============================================================================

def extract_sample_articles(mc, sample_size=100):
    """Extract sample articles from each narrative category for manual coding"""
    print("\n" + "="*80)
    print("STEP 3: EXTRACTING SAMPLE ARTICLES FOR MANUAL CODING")
    print("="*80)

    all_articles = []

    for category, phrases in NARRATIVES.items():
        print(f"\n{category.upper()} NARRATIVES:")
        print("-"*80)

        category_articles = []

        # Get articles from each phrase (will return up to 1000 per phrase)
        for phrase in phrases:
            print(f"  Extracting: '{phrase}'")

            # Add retry logic with exponential backoff for rate limiting
            max_retries = 3
            retry_delay = 2  # Start with 2 seconds

            for attempt in range(max_retries):
                try:
                    # Add delay between requests to avoid rate limiting
                    if len(all_articles) > 0:  # Skip delay on first request
                        time.sleep(1.5)  # 1.5 second delay between requests

                    story_result = mc.story_list(phrase,
                                                start_date=START_DATE,
                                                end_date=END_DATE)

                    stories = story_result[0]  # stories are in first element of tuple

                    # Add metadata
                    for story in stories:
                        story['search_phrase'] = phrase
                        story['narrative_category'] = category
                        category_articles.append(story)

                    print(f"    Retrieved: {len(stories):,} articles")
                    break  # Success, exit retry loop

                except json.JSONDecodeError as e:
                    if attempt < max_retries - 1:
                        print(f"    ⚠ Rate limit hit, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        print(f"    ❌ Failed after {max_retries} attempts: {e}")
                        print(f"    Skipping phrase '{phrase}' and continuing...")
                except Exception as e:
                    print(f"    ❌ Unexpected error: {e}")
                    print(f"    Skipping phrase '{phrase}' and continuing...")
                    break

        all_articles.extend(category_articles)
        print(f"  TOTAL for {category}: {len(category_articles):,} articles")
    
    print(f"\n{'='*80}")
    print(f"TOTAL ARTICLES RETRIEVED: {len(all_articles):,}")
    
    # Sample for manual coding (stratified by category)
    sample_articles = {}
    per_category = sample_size // 3
    
    for category in ['limiting', 'neutral', 'empowering']:
        cat_articles = [a for a in all_articles if a['narrative_category'] == category]
        
        # Random sample if more than needed
        if len(cat_articles) > per_category:
            import random
            sample_articles[category] = random.sample(cat_articles, per_category)
        else:
            sample_articles[category] = cat_articles
    
    total_sample = sum(len(v) for v in sample_articles.values())
    print(f"\nSampled {total_sample} articles for manual coding:")
    for cat, articles in sample_articles.items():
        print(f"  {cat}: {len(articles)} articles")
    
    return all_articles, sample_articles

# ============================================================================
# STEP 4: EXPORT RESULTS
# ============================================================================

def export_results(volume_data, imbalance_summary, temporal_df, all_articles, sample_articles):
    """Export all results to files for further analysis"""
    print("\n" + "="*80)
    print("STEP 4: EXPORTING RESULTS")
    print("="*80)
    
    # 1. Volume data as JSON
    volume_export = {
        'year': YEAR,
        'narratives': NARRATIVES,
        'volume_counts': volume_data,
        'imbalance_summary': imbalance_summary
    }
    
    with open('aging_narratives_volume.json', 'w') as f:
        json.dump(volume_export, f, indent=2)
    print("\n✓ Saved: aging_narratives_volume.json")
    
    # 2. Temporal data as CSV
    temporal_df.to_csv('aging_narratives_temporal.csv', index=False)
    print("✓ Saved: aging_narratives_temporal.csv")
    
    # 3. All articles as JSON
    with open('aging_narratives_all_articles.json', 'w') as f:
        json.dump(all_articles, f, indent=2, default=str)
    print("✓ Saved: aging_narratives_all_articles.json")
    
    # 4. Sample articles for coding as CSV (easier to work with)
    sample_flat = []
    for category, articles in sample_articles.items():
        for article in articles:
            sample_flat.append({
                'category': category,
                'phrase': article['search_phrase'],
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'publish_date': article.get('publish_date', ''),
                'media_name': article.get('media_name', ''),
                'media_url': article.get('media_url', ''),
                # Add coding columns
                'coded_narrative': '',
                'ageism_present': '',
                'voice_representation': '',
                'notes': ''
            })
    
    sample_df = pd.DataFrame(sample_flat)
    sample_df.to_csv('aging_narratives_coding_sample.csv', index=False)
    print("✓ Saved: aging_narratives_coding_sample.csv (ready for manual coding)")
    
    # 5. Summary report
    with open('aging_narratives_summary.txt', 'w') as f:
        f.write("="*80 + "\n")
        f.write("AGING NARRATIVES ANALYSIS - SUMMARY REPORT\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Analysis Period: {START_DATE} to {END_DATE}\n\n")
        
        f.write("VOLUME ANALYSIS:\n")
        f.write("-"*80 + "\n")
        f.write(f"Limiting narratives:    {imbalance_summary['limiting']:>10,} stories\n")
        f.write(f"Neutral narratives:     {imbalance_summary['neutral']:>10,} stories\n")
        f.write(f"Empowering narratives:  {imbalance_summary['empowering']:>10,} stories\n")
        f.write(f"TOTAL:                  {imbalance_summary['total']:>10,} stories\n\n")
        
        if imbalance_summary['imbalance_ratio']:
            f.write(f"Narrative Imbalance Ratio: {imbalance_summary['imbalance_ratio']:.2f} : 1\n")
            f.write(f"(For every 1 empowering story, there are {imbalance_summary['imbalance_ratio']:.1f} limiting stories)\n\n")
        
        f.write("ARTICLES COLLECTED:\n")
        f.write("-"*80 + "\n")
        f.write(f"Total articles retrieved:  {len(all_articles):>10,}\n")
        f.write(f"Sample for manual coding:  {sum(len(v) for v in sample_articles.values()):>10,}\n")
    
    print("✓ Saved: aging_narratives_summary.txt")
    
    print("\n" + "="*80)
    print("EXPORT COMPLETE!")
    print("="*80)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run complete aging narratives analysis"""
    print("\n" + "="*80)
    print("AGING NARRATIVES ANALYSIS - MEDIA CLOUD 2023")
    print("="*80)
    print(f"Analysis period: {START_DATE} to {END_DATE}")
    print(f"API Key: {API_KEY[:20]}...")
    print("\n")
    
    # Initialize API
    mc = mediacloud.api.SearchApi(API_KEY)
    
    try:
        # Step 1: Volume analysis
        volume_data = get_volume_data(mc)
        imbalance_summary = calculate_imbalance_ratios(volume_data)
        
        # Step 2: Temporal analysis
        temporal_df, category_daily, monthly_summary = analyze_temporal_trends(mc)
        
        # Step 3: Extract articles
        all_articles, sample_articles = extract_sample_articles(mc, sample_size=90)
        
        # Step 4: Export results
        export_results(volume_data, imbalance_summary, temporal_df, all_articles, sample_articles)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
        print("\nNext Steps:")
        print("1. Open 'aging_narratives_coding_sample.csv' to begin manual narrative coding")
        print("2. Review 'aging_narratives_summary.txt' for key findings")
        print("3. Analyze 'aging_narratives_temporal.csv' for trend visualization")
        print("4. Reference 'aging_narratives_volume.json' for detailed statistics")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
