from ibis import ir
from typing import Dict, Any
import pandas as pd

from ascend.application.context import ComponentExecutionContext
from ascend.common.events import log
from ascend.resources import ref, test, transform

@transform(
    inputs=[
        ref("cleaned_longevity_data"),
    ],
    input_data_format="pandas",  # Use pandas for ML processing
    tests=[
        test("not_null", column="predicted_category"),
        test("not_null", column="sentiment_score"),
        test("count_greater_than", count=0),
    ]
)
def sentiment_analysis_longevity_data(
    cleaned_longevity_data: pd.DataFrame,
    context: ComponentExecutionContext
) -> pd.DataFrame:
    """
    Apply ML sentiment analysis to article text and compare with phrase categories.
    
    This reveals how media language about aging aligns with actual article sentiment.
    
    Args:
        cleaned_longevity_data: Cleaned article data
        context: Component execution context
        
    Returns:
        Data with sentiment analysis and category predictions
    """
    import numpy as np
    import re
    
    log(f"Starting sentiment analysis on {len(cleaned_longevity_data)} articles")
    
    # Define sentiment lexicons
    positive_words = {
        'success', 'successful', 'thrive', 'thriving', 'wisdom', 'wise', 'experience', 'experienced',
        'active', 'healthy', 'vibrant', 'engaged', 'independent', 'opportunity', 'opportunities',
        'growth', 'positive', 'good', 'better', 'best', 'excellent', 'great', 'wonderful',
        'happy', 'joy', 'celebrate', 'achievement', 'accomplish', 'benefit', 'benefits',
        'improve', 'improvement', 'enhance', 'strong', 'strength', 'capable', 'empower',
        'empowering', 'empowered', 'dignity', 'respect', 'valued', 'valuable', 'contribute',
        'contribution', 'productive', 'fulfilling', 'meaningful', 'purpose', 'purposeful'
    }
    
    negative_words = {
        'crisis', 'burden', 'burdensome', 'decline', 'declining', 'problem', 'problems',
        'challenge', 'challenging', 'struggle', 'struggling', 'vulnerable', 'frail', 'fragile',
        'dependent', 'dependency', 'costly', 'expensive', 'strain', 'stress', 'difficult',
        'difficulty', 'poor', 'worse', 'worst', 'bad', 'negative', 'concern', 'concerning',
        'worried', 'worry', 'fear', 'fearful', 'risk', 'risky', 'danger', 'dangerous',
        'threat', 'threatening', 'loss', 'lose', 'losing', 'fail', 'failure', 'failing',
        'inadequate', 'insufficient', 'lack', 'lacking', 'unable', 'incapable', 'weak',
        'weakness', 'isolated', 'isolation', 'lonely', 'loneliness', 'neglect', 'neglected'
    }
    
    # Step 1: Apply ML Sentiment Analysis
    def analyze_sentiment(text: str) -> Dict[str, Any]:
        """Analyze sentiment of article text using lexicon-based approach."""
        try:
            if pd.isna(text) or len(str(text).strip()) == 0:
                return {
                    'sentiment_score': 0.0,
                    'sentiment_label': 'neutral',
                    'subjectivity': 0.0
                }
            
            # Tokenize and clean text
            text_lower = str(text).lower()
            words = re.findall(r'\b\w+\b', text_lower)
            
            # Count positive and negative words
            pos_count = sum(1 for word in words if word in positive_words)
            neg_count = sum(1 for word in words if word in negative_words)
            total_words = len(words)
            
            # Calculate sentiment score (-1 to +1)
            if total_words > 0:
                # Normalize by text length
                pos_ratio = pos_count / total_words
                neg_ratio = neg_count / total_words
                
                # Calculate polarity
                if pos_count + neg_count > 0:
                    polarity = (pos_count - neg_count) / (pos_count + neg_count)
                else:
                    polarity = 0.0
                
                # Calculate subjectivity (how opinionated vs factual)
                subjectivity = min((pos_count + neg_count) / total_words * 10, 1.0)
            else:
                polarity = 0.0
                subjectivity = 0.0
            
            # Classify sentiment
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'sentiment_score': round(polarity, 3),
                'sentiment_label': label,
                'subjectivity': round(subjectivity, 3)
            }
        except Exception as e:
            log(f"Error analyzing sentiment: {str(e)}")
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'subjectivity': 0.0
            }
    
    log("Analyzing sentiment for all articles...")
    sentiment_results = cleaned_longevity_data['article_text'].apply(analyze_sentiment)
    
    # Extract sentiment components
    data = cleaned_longevity_data.copy()
    data['sentiment_score'] = sentiment_results.apply(lambda x: x['sentiment_score'])
    data['sentiment_label'] = sentiment_results.apply(lambda x: x['sentiment_label'])
    data['subjectivity'] = sentiment_results.apply(lambda x: x['subjectivity'])
    
    log(f"Sentiment distribution: {data['sentiment_label'].value_counts().to_dict()}")
    
    # Step 2: Create predicted_category based on ML analysis
    def predict_category(sentiment_score: float, sentiment_label: str, text: str) -> str:
        """
        Predict category based on sentiment analysis and content.
        
        Logic:
        - Positive sentiment + empowering language → empowering
        - Negative sentiment + crisis language → limiting
        - Balanced/factual tone → neutral
        """
        text_lower = str(text).lower()
        
        # Check for empowering keywords
        empowering_keywords = [
            'success', 'thrive', 'wisdom', 'experience', 'active', 'healthy',
            'vibrant', 'engaged', 'independent', 'opportunity', 'growth'
        ]
        
        # Check for limiting keywords
        limiting_keywords = [
            'crisis', 'burden', 'decline', 'problem', 'challenge', 'struggle',
            'vulnerable', 'frail', 'dependent', 'costly', 'strain'
        ]
        
        empowering_count = sum(1 for kw in empowering_keywords if kw in text_lower)
        limiting_count = sum(1 for kw in limiting_keywords if kw in text_lower)
        
        # Decision logic
        if sentiment_score > 0.15 and empowering_count > limiting_count:
            return 'empowering'
        elif sentiment_score < -0.15 and limiting_count > empowering_count:
            return 'limiting'
        elif sentiment_label == 'positive' and empowering_count >= 2:
            return 'empowering'
        elif sentiment_label == 'negative' and limiting_count >= 2:
            return 'limiting'
        else:
            return 'neutral'
    
    data['predicted_category'] = data.apply(
        lambda row: predict_category(
            row['sentiment_score'],
            row['sentiment_label'],
            row['article_text']
        ),
        axis=1
    )
    
    log(f"Predicted category distribution: {data['predicted_category'].value_counts().to_dict()}")
    
    # Step 3: Compare phrase_category vs predicted_category
    data['category_match'] = (
        data['phrase_category_clean'] == data['predicted_category']
    )
    
    match_rate = (data['category_match'].sum() / len(data)) * 100
    log(f"Category match rate: {match_rate:.1f}%")
    
    # Step 4: Generate Insights
    log("=" * 80)
    log("SENTIMENT ANALYSIS INSIGHTS")
    log("=" * 80)
    
    # Overall match statistics
    total_articles = len(data)
    matches = data['category_match'].sum()
    mismatches = total_articles - matches
    
    log(f"Total articles analyzed: {total_articles}")
    log(f"Matches (phrase aligns with sentiment): {matches} ({match_rate:.1f}%)")
    log(f"Mismatches (phrase doesn't match sentiment): {mismatches} ({100-match_rate:.1f}%)")
    log("")
    
    # Mismatch analysis by phrase
    log("PHRASE ACCURACY ANALYSIS:")
    log("-" * 80)
    
    phrase_analysis = data.groupby('phrase').agg({
        'category_match': ['count', 'sum', 'mean'],
        'sentiment_score': 'mean',
        'predicted_category': lambda x: x.value_counts().to_dict()
    }).round(3)
    
    for phrase in data['phrase'].unique()[:10]:  # Top 10 phrases
        phrase_data = data[data['phrase'] == phrase]
        total = len(phrase_data)
        matched = phrase_data['category_match'].sum()
        match_pct = (matched / total * 100) if total > 0 else 0
        avg_sentiment = phrase_data['sentiment_score'].mean()
        
        log(f"Phrase: '{phrase}'")
        log(f"  Total articles: {total}")
        log(f"  Match rate: {match_pct:.1f}%")
        log(f"  Avg sentiment: {avg_sentiment:.3f}")
        log(f"  Predicted categories: {phrase_data['predicted_category'].value_counts().to_dict()}")
        log("")
    
    # Province-level insights
    log("INSIGHTS BY PROVINCE:")
    log("-" * 80)
    
    for province in data['province_clean'].unique():
        prov_data = data[data['province_clean'] == province]
        total = len(prov_data)
        matched = prov_data['category_match'].sum()
        match_pct = (matched / total * 100) if total > 0 else 0
        avg_sentiment = prov_data['sentiment_score'].mean()
        
        log(f"{province}:")
        log(f"  Articles: {total}")
        log(f"  Match rate: {match_pct:.1f}%")
        log(f"  Avg sentiment: {avg_sentiment:.3f}")
        log(f"  Sentiment distribution: {prov_data['sentiment_label'].value_counts().to_dict()}")
        log("")
    
    # Top mismatches
    log("TOP MISMATCHES (Phrase vs Actual Sentiment):")
    log("-" * 80)
    
    mismatches_df = data[~data['category_match']].copy()
    if len(mismatches_df) > 0:
        mismatch_summary = mismatches_df.groupby(
            ['phrase_category_clean', 'predicted_category']
        ).size().reset_index(name='count').sort_values('count', ascending=False)
        
        for _, row in mismatch_summary.head(10).iterrows():
            log(f"  {row['phrase_category_clean']} → {row['predicted_category']}: {row['count']} articles")
    
    log("=" * 80)
    
    # Select final columns
    output_columns = [
        'url',
        'title',
        'publish_date',
        'year',
        'month',
        'media_name',
        'phrase',
        'phrase_category_clean',
        'predicted_category',
        'sentiment_score',
        'sentiment_label',
        'subjectivity',
        'category_match',
        'province_clean',
        'article_text',
        'text_valid',
        'ingestion_date',
        'row_hash'
    ]
    
    return data[output_columns]