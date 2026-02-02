import pandas as pd
import re
from datetime import datetime

from ascend.application.context import ComponentExecutionContext
from ascend.common.events import log
from ascend.resources import transform, test, ref

@transform(
    inputs=[
        ref("cleaned_mediacloud_data"),
    ],
    input_data_format="pandas",
    tests=[
        test("not_null", column="PREDICTED_CATEGORY"),
        test("not_null", column="SENTIMENT_SCORE"),
        test("not_null", column="CATEGORY_MATCH"),
        test("count_greater_than", count=0, severity="warn"),
    ],
    on_schema_change="sync_all_columns",
)
def sentiment_analysis_mediacloud_data(
    cleaned_mediacloud_data: pd.DataFrame,
    context: ComponentExecutionContext
) -> pd.DataFrame:
    """
    Apply sentiment analysis to Media Cloud articles using lexicon-based approach.
    
    Args:
        cleaned_mediacloud_data (pd.DataFrame): Cleaned Media Cloud articles
        context (ComponentExecutionContext): The execution context
    
    Returns:
        pd.DataFrame: Articles with sentiment analysis columns
    """
    log(f"Analyzing sentiment for {len(cleaned_mediacloud_data)} articles")
    
    df = cleaned_mediacloud_data.copy()
    
    # Lexicon-based sentiment dictionaries
    positive_words = {
        'success', 'thrive', 'wisdom', 'active', 'healthy', 'productive', 'vibrant',
        'engaged', 'empowered', 'independent', 'capable', 'experienced', 'skilled',
        'valuable', 'contributing', 'respected', 'dignity', 'fulfilling', 'opportunity',
        'growth', 'learning', 'achievement', 'accomplished', 'mentor', 'leader',
        'innovative', 'creative', 'resilient', 'strong', 'confident', 'positive',
        'optimistic', 'hopeful', 'energetic', 'passionate', 'dedicated', 'committed',
        'enthusiastic', 'motivated', 'inspired', 'empowering', 'uplifting', 'encouraging',
        'supportive', 'caring', 'compassionate', 'kind', 'generous', 'helpful', 'friendly'
    }
    
    negative_words = {
        'crisis', 'burden', 'decline', 'frail', 'dependent', 'vulnerable', 'weak',
        'failing', 'deteriorating', 'struggling', 'suffering', 'problem', 'challenge',
        'difficulty', 'obstacle', 'barrier', 'limitation', 'constraint', 'restriction',
        'deficit', 'shortage', 'lack', 'inadequate', 'insufficient', 'poor', 'bad',
        'negative', 'harmful', 'damaging', 'detrimental', 'adverse', 'unfavorable',
        'unfortunate', 'tragic', 'sad', 'depressing', 'gloomy', 'bleak', 'dire',
        'severe', 'serious', 'critical', 'urgent', 'alarming', 'concerning', 'worrying',
        'threatening', 'dangerous', 'risky', 'hazardous', 'perilous', 'precarious',
        'unstable', 'insecure', 'uncertain', 'unpredictable', 'chaotic', 'disruptive',
        'tsunami', 'bomb', 'explosion', 'collapse', 'catastrophe', 'disaster'
    }
    
    # Phrase-specific keywords
    limiting_phrases = {'crisis', 'burden', 'tsunami', 'bomb', 'decline', 'problem'}
    empowering_phrases = {'active', 'successful', 'healthy', 'well', 'productive', 'wisdom'}
    
    def analyze_sentiment(text, phrase):
        """Analyze sentiment of article text"""
        if pd.isna(text) or text == "":
            return 0.0, 'neutral', 0.0, 0, 0, 0
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Count positive and negative words
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        # Count phrase-specific keywords
        limiting_count = sum(1 for word in words if word in limiting_phrases)
        empowering_count = sum(1 for word in words if word in empowering_phrases)
        
        # Calculate polarity score (-1 to +1)
        total_sentiment_words = pos_count + neg_count
        if total_sentiment_words == 0:
            polarity = 0.0
        else:
            polarity = (pos_count - neg_count) / total_sentiment_words
        
        # Determine sentiment label
        if polarity > 0.15:
            label = 'positive'
        elif polarity < -0.15:
            label = 'negative'
        else:
            label = 'neutral'
        
        # Calculate subjectivity (0 to 1)
        total_words = len(words)
        subjectivity = total_sentiment_words / total_words if total_words > 0 else 0.0
        
        return polarity, label, subjectivity, limiting_count, empowering_count, total_sentiment_words
    
    # Apply sentiment analysis
    results = df.apply(
        lambda row: analyze_sentiment(row['ARTICLE_TEXT'], row['PHRASE']),
        axis=1
    )
    
    df['SENTIMENT_SCORE'] = results.apply(lambda x: x[0])
    df['SENTIMENT_LABEL'] = results.apply(lambda x: x[1])
    df['SUBJECTIVITY'] = results.apply(lambda x: x[2])
    df['LIMITING_KEYWORD_COUNT'] = results.apply(lambda x: x[3])
    df['EMPOWERING_KEYWORD_COUNT'] = results.apply(lambda x: x[4])
    
    # Predict category based on sentiment and keywords
    def predict_category(row):
        sentiment_score = row['SENTIMENT_SCORE']
        limiting_count = row['LIMITING_KEYWORD_COUNT']
        empowering_count = row['EMPOWERING_KEYWORD_COUNT']
        
        # Strong empowering signals
        if sentiment_score > 0.15 and empowering_count > limiting_count:
            return 'empowering'
        # Strong limiting signals
        elif sentiment_score < -0.15 and limiting_count > empowering_count:
            return 'limiting'
        # Mixed or neutral
        elif abs(sentiment_score) <= 0.15:
            return 'neutral'
        # Default based on sentiment
        elif sentiment_score > 0:
            return 'empowering'
        else:
            return 'limiting'
    
    df['PREDICTED_CATEGORY'] = df.apply(predict_category, axis=1)
    
    # Check if predicted category matches phrase category
    df['CATEGORY_MATCH'] = df['PREDICTED_CATEGORY'] == df['PHRASE_CATEGORY']
    
    # Add metadata
    df['ANALYSIS_TIMESTAMP'] = datetime.now()
    
    # Log summary statistics
    match_rate = (df['CATEGORY_MATCH'].sum() / len(df)) * 100
    log(f"Sentiment analysis complete: {match_rate:.1f}% match rate")
    log(f"Predicted categories: {df['PREDICTED_CATEGORY'].value_counts().to_dict()}")
    log(f"Average sentiment score: {df['SENTIMENT_SCORE'].mean():.3f}")
    
    return df