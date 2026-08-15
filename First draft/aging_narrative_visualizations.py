#!/usr/bin/env python3
"""
Aging Narratives - Visualization and Analysis
Creates visualizations from the data collected by the main analysis script
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================================================
# LOAD DATA
# ============================================================================

def load_data():
    """Load all analysis data files"""
    print("Loading data files...")
    
    # Volume data
    with open('aging_narratives_volume.json', 'r') as f:
        volume_data = json.load(f)
    
    # Temporal data
    temporal_df = pd.read_csv('aging_narratives_temporal.csv')
    temporal_df['date'] = pd.to_datetime(temporal_df['date'])
    
    # Coded sample (after manual coding is done)
    try:
        coded_df = pd.read_csv('aging_narratives_coding_sample.csv')
        has_coded_data = True
    except FileNotFoundError:
        print("  Note: Coded sample not found (complete manual coding first)")
        coded_df = None
        has_coded_data = False
    
    return volume_data, temporal_df, coded_df, has_coded_data

# ============================================================================
# VISUALIZATION 1: NARRATIVE VOLUME DISTRIBUTION
# ============================================================================

def plot_narrative_distribution(volume_data):
    """Create pie chart of narrative distribution"""
    print("\nCreating narrative distribution visualization...")
    
    counts = volume_data['imbalance_summary']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Pie chart
    labels = ['Limiting', 'Neutral', 'Empowering']
    sizes = [counts['limiting'], counts['neutral'], counts['empowering']]
    colors = ['#ff6b6b', '#95a5a6', '#51cf66']
    explode = (0.05, 0, 0)
    
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
    ax1.set_title('Distribution of Aging Narratives in 2023 Media\n(Total Stories: {:,})'.format(
        counts['total']), fontsize=14, fontweight='bold')
    
    # Bar chart
    ax2.bar(labels, sizes, color=colors, edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('Number of Stories', fontsize=12)
    ax2.set_title('Story Count by Narrative Type', fontsize=14, fontweight='bold')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    # Add value labels on bars
    for i, v in enumerate(sizes):
        ax2.text(i, v + max(sizes)*0.02, f'{v:,}', ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('viz_narrative_distribution.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: viz_narrative_distribution.png")
    plt.close()

# ============================================================================
# VISUALIZATION 2: TEMPORAL TRENDS
# ============================================================================

def plot_temporal_trends(temporal_df):
    """Create time series visualization of narrative trends"""
    print("\nCreating temporal trend visualization...")
    
    # Aggregate by date and category
    daily_counts = temporal_df.groupby(['date', 'category'])['count'].sum().reset_index()
    
    # Pivot for easier plotting
    daily_pivot = daily_counts.pivot(index='date', columns='category', values='count')
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Line plot - absolute counts
    colors = {'limiting': '#ff6b6b', 'neutral': '#95a5a6', 'empowering': '#51cf66'}
    for category in ['limiting', 'neutral', 'empowering']:
        if category in daily_pivot.columns:
            ax1.plot(daily_pivot.index, daily_pivot[category], 
                    label=category.capitalize(), color=colors[category], 
                    linewidth=2, alpha=0.8)
    
    ax1.set_ylabel('Daily Story Count', fontsize=12)
    ax1.set_title('Aging Narratives Over Time - 2023', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Calculate rolling averages
    window = 7
    daily_pivot_smooth = daily_pivot.rolling(window=window, center=True).mean()
    
    for category in ['limiting', 'neutral', 'empowering']:
        if category in daily_pivot_smooth.columns:
            ax2.plot(daily_pivot_smooth.index, daily_pivot_smooth[category],
                    label=f'{category.capitalize()} ({window}-day avg)', 
                    color=colors[category], linewidth=2.5)
    
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Story Count (7-day rolling avg)', fontsize=12)
    ax2.set_title('Smoothed Trends', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('viz_temporal_trends.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: viz_temporal_trends.png")
    plt.close()

# ============================================================================
# VISUALIZATION 3: MONTHLY HEATMAP
# ============================================================================

def plot_monthly_heatmap(temporal_df):
    """Create heatmap of narrative intensity by month"""
    print("\nCreating monthly heatmap...")
    
    temporal_df['month'] = temporal_df['date'].dt.to_period('M')
    monthly = temporal_df.groupby(['month', 'category'])['count'].sum().reset_index()
    monthly_pivot = monthly.pivot(index='category', columns='month', values='count')
    
    plt.figure(figsize=(14, 6))
    sns.heatmap(monthly_pivot, annot=True, fmt=',.0f', cmap='YlOrRd', 
                cbar_kws={'label': 'Story Count'}, linewidths=0.5)
    plt.title('Monthly Distribution of Aging Narratives - 2023', 
              fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Narrative Category', fontsize=12)
    plt.tight_layout()
    plt.savefig('viz_monthly_heatmap.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: viz_monthly_heatmap.png")
    plt.close()

# ============================================================================
# VISUALIZATION 4: PHRASE COMPARISON
# ============================================================================

def plot_phrase_comparison(volume_data):
    """Create bar chart comparing individual phrases"""
    print("\nCreating phrase comparison visualization...")
    
    # Prepare data
    all_phrases = []
    for category, phrases in volume_data['volume_counts'].items():
        for phrase, count in phrases.items():
            if phrase != 'TOTAL':
                all_phrases.append({
                    'phrase': phrase,
                    'category': category,
                    'count': count
                })
    
    df = pd.DataFrame(all_phrases)
    df = df.sort_values('count', ascending=True)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 10))
    
    colors = {'limiting': '#ff6b6b', 'neutral': '#95a5a6', 'empowering': '#51cf66'}
    phrase_colors = [colors[cat] for cat in df['category']]
    
    bars = ax.barh(df['phrase'], df['count'], color=phrase_colors, edgecolor='black')
    
    ax.set_xlabel('Number of Stories (2023)', fontsize=12)
    ax.set_title('Story Count by Search Phrase', fontsize=14, fontweight='bold', pad=20)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    # Add value labels
    for i, (phrase, count) in enumerate(zip(df['phrase'], df['count'])):
        ax.text(count + max(df['count'])*0.02, i, f'{count:,}', 
               va='center', fontsize=9)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=colors['limiting'], label='Limiting'),
                      Patch(facecolor=colors['neutral'], label='Neutral'),
                      Patch(facecolor=colors['empowering'], label='Empowering')]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('viz_phrase_comparison.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: viz_phrase_comparison.png")
    plt.close()

# ============================================================================
# VISUALIZATION 5: IMBALANCE RATIO
# ============================================================================

def plot_imbalance_ratio(volume_data):
    """Visualize the narrative imbalance ratio"""
    print("\nCreating imbalance ratio visualization...")
    
    counts = volume_data['imbalance_summary']
    ratio = counts.get('imbalance_ratio', 0)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['Empowering', 'Limiting']
    values = [1, ratio]
    colors = ['#51cf66', '#ff6b6b']
    
    bars = ax.bar(categories, values, color=colors, edgecolor='black', linewidth=2)
    
    ax.set_ylabel('Relative Frequency', fontsize=12)
    ax.set_title(f'Narrative Imbalance Ratio: {ratio:.1f} : 1\n' + 
                 f'For every 1 empowering story, there are {ratio:.1f} limiting stories',
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels
    for i, v in enumerate(values):
        ax.text(i, v + max(values)*0.02, f'{v:.1f}', 
               ha='center', fontsize=12, fontweight='bold')
    
    # Add visual emphasis
    ax.axhline(y=1, color='gray', linestyle='--', alpha=0.5, label='Parity')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('viz_imbalance_ratio.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: viz_imbalance_ratio.png")
    plt.close()

# ============================================================================
# VISUALIZATION 6: CODED DATA ANALYSIS (if available)
# ============================================================================

def plot_coded_analysis(coded_df):
    """Create visualizations from manually coded data"""
    print("\nCreating coded data visualizations...")
    
    if coded_df is None:
        print("  ⚠ Skipping - complete manual coding first")
        return
    
    # Check if coding columns are filled
    if coded_df['coded_narrative'].isna().all():
        print("  ⚠ Skipping - no coded data found (fill in the CSV first)")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Voice representation
    if 'voice_representation' in coded_df.columns:
        voice_counts = coded_df['voice_representation'].value_counts()
        axes[0, 0].bar(range(len(voice_counts)), voice_counts.values, 
                      color='steelblue', edgecolor='black')
        axes[0, 0].set_xticks(range(len(voice_counts)))
        axes[0, 0].set_xticklabels(voice_counts.index, rotation=45, ha='right')
        axes[0, 0].set_title('Voice Representation in Articles', fontweight='bold')
        axes[0, 0].set_ylabel('Count')
    
    # 2. Ageism presence
    if 'ageism_present' in coded_df.columns:
        ageism_counts = coded_df['ageism_present'].value_counts()
        colors_ageism = ['#ff6b6b' if x == 'yes' else '#51cf66' 
                        for x in ageism_counts.index]
        axes[0, 1].bar(range(len(ageism_counts)), ageism_counts.values,
                      color=colors_ageism, edgecolor='black')
        axes[0, 1].set_xticks(range(len(ageism_counts)))
        axes[0, 1].set_xticklabels(ageism_counts.index, rotation=45, ha='right')
        axes[0, 1].set_title('Ageism Detected', fontweight='bold')
        axes[0, 1].set_ylabel('Count')
    
    # 3. Coded vs. original category
    if 'coded_narrative' in coded_df.columns:
        comparison = pd.crosstab(coded_df['category'], coded_df['coded_narrative'])
        comparison.plot(kind='bar', stacked=True, ax=axes[1, 0], 
                       color=['#ff6b6b', '#95a5a6', '#51cf66'])
        axes[1, 0].set_title('Original vs. Coded Narrative Category', fontweight='bold')
        axes[1, 0].set_xlabel('Original Category')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].legend(title='Coded Category')
        axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 4. Distribution by outlet
    if 'media_name' in coded_df.columns:
        top_outlets = coded_df['media_name'].value_counts().head(10)
        axes[1, 1].barh(range(len(top_outlets)), top_outlets.values,
                       color='coral', edgecolor='black')
        axes[1, 1].set_yticks(range(len(top_outlets)))
        axes[1, 1].set_yticklabels(top_outlets.index)
        axes[1, 1].set_title('Top Media Outlets in Sample', fontweight='bold')
        axes[1, 1].set_xlabel('Count')
    
    plt.tight_layout()
    plt.savefig('viz_coded_analysis.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: viz_coded_analysis.png")
    plt.close()

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

def generate_summary_stats(volume_data, temporal_df, coded_df):
    """Generate comprehensive summary statistics"""
    print("\nGenerating summary statistics...")
    
    with open('analysis_summary_stats.txt', 'w') as f:
        f.write("="*80 + "\n")
        f.write("AGING NARRATIVES ANALYSIS - DETAILED STATISTICS\n")
        f.write("="*80 + "\n\n")
        
        # Volume statistics
        counts = volume_data['imbalance_summary']
        f.write("VOLUME STATISTICS:\n")
        f.write("-"*80 + "\n")
        f.write(f"Total stories analyzed: {counts['total']:,}\n")
        f.write(f"  Limiting:    {counts['limiting']:,} ({counts['limiting']/counts['total']*100:.1f}%)\n")
        f.write(f"  Neutral:     {counts['neutral']:,} ({counts['neutral']/counts['total']*100:.1f}%)\n")
        f.write(f"  Empowering:  {counts['empowering']:,} ({counts['empowering']/counts['total']*100:.1f}%)\n\n")
        
        if counts.get('imbalance_ratio'):
            f.write(f"Narrative Imbalance Ratio: {counts['imbalance_ratio']:.2f} : 1\n")
            f.write(f"  Interpretation: For every empowering story, {counts['imbalance_ratio']:.1f} limiting stories\n\n")
        
        # Temporal statistics
        f.write("TEMPORAL PATTERNS:\n")
        f.write("-"*80 + "\n")
        temporal_df['month'] = pd.to_datetime(temporal_df['date']).dt.to_period('M')
        monthly = temporal_df.groupby(['month', 'category'])['count'].sum().reset_index()
        
        for category in ['limiting', 'neutral', 'empowering']:
            cat_data = monthly[monthly['category'] == category]
            if not cat_data.empty:
                peak_month = cat_data.loc[cat_data['count'].idxmax()]
                f.write(f"  {category.capitalize()}:\n")
                f.write(f"    Peak month: {peak_month['month']} ({peak_month['count']:,} stories)\n")
                f.write(f"    Average per month: {cat_data['count'].mean():.0f} stories\n")
        
        # Coded data statistics (if available)
        if coded_df is not None and not coded_df['coded_narrative'].isna().all():
            f.write("\nCODED SAMPLE ANALYSIS:\n")
            f.write("-"*80 + "\n")
            f.write(f"Sample size: {len(coded_df)}\n")
            
            if 'voice_representation' in coded_df.columns:
                voice_dist = coded_df['voice_representation'].value_counts()
                f.write(f"\nVoice Representation:\n")
                for voice, count in voice_dist.items():
                    f.write(f"  {voice}: {count} ({count/len(coded_df)*100:.1f}%)\n")
            
            if 'ageism_present' in coded_df.columns:
                ageism_rate = (coded_df['ageism_present'] == 'yes').sum() / len(coded_df)
                f.write(f"\nAgeism Detection Rate: {ageism_rate*100:.1f}%\n")
    
    print("  ✓ Saved: analysis_summary_stats.txt")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all visualizations and statistics"""
    print("="*80)
    print("AGING NARRATIVES - VISUALIZATION & ANALYSIS")
    print("="*80)
    
    try:
        # Load data
        volume_data, temporal_df, coded_df, has_coded = load_data()
        
        # Generate visualizations
        plot_narrative_distribution(volume_data)
        plot_temporal_trends(temporal_df)
        plot_monthly_heatmap(temporal_df)
        plot_phrase_comparison(volume_data)
        plot_imbalance_ratio(volume_data)
        
        if has_coded:
            plot_coded_analysis(coded_df)
        
        # Generate summary statistics
        generate_summary_stats(volume_data, temporal_df, coded_df)
        
        print("\n" + "="*80)
        print("VISUALIZATION COMPLETE!")
        print("="*80)
        print("\nGenerated files:")
        print("  • viz_narrative_distribution.png")
        print("  • viz_temporal_trends.png")
        print("  • viz_monthly_heatmap.png")
        print("  • viz_phrase_comparison.png")
        print("  • viz_imbalance_ratio.png")
        if has_coded:
            print("  • viz_coded_analysis.png")
        print("  • analysis_summary_stats.txt")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
