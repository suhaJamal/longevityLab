{{
    config(
        materialized="table"
    )
}}

-- Analyze which media outlets distort aging language most
-- This helps advocates target their media engagement efforts

WITH outlet_stats AS (
    SELECT
        media_name,
        COUNT(*) as total_articles,
        
        -- Match statistics
        SUM(CASE WHEN category_match THEN 1 ELSE 0 END) as matches,
        SUM(CASE WHEN NOT category_match THEN 1 ELSE 0 END) as mismatches,
        ROUND(100.0 * SUM(CASE WHEN category_match THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        
        -- Sentiment analysis
        ROUND(AVG(sentiment_score), 3) as avg_sentiment,
        ROUND(AVG(subjectivity), 3) as avg_subjectivity,
        
        -- Category distribution
        SUM(CASE WHEN phrase_category_clean = 'empowering' THEN 1 ELSE 0 END) as empowering_phrases,
        SUM(CASE WHEN phrase_category_clean = 'limiting' THEN 1 ELSE 0 END) as limiting_phrases,
        SUM(CASE WHEN phrase_category_clean = 'neutral' THEN 1 ELSE 0 END) as neutral_phrases,
        
        -- Predicted category distribution (actual sentiment)
        SUM(CASE WHEN predicted_category = 'empowering' THEN 1 ELSE 0 END) as actual_empowering,
        SUM(CASE WHEN predicted_category = 'limiting' THEN 1 ELSE 0 END) as actual_limiting,
        SUM(CASE WHEN predicted_category = 'neutral' THEN 1 ELSE 0 END) as actual_neutral,
        
        -- Sentiment label distribution
        SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END) as positive_articles,
        SUM(CASE WHEN sentiment_label = 'negative' THEN 1 ELSE 0 END) as negative_articles,
        SUM(CASE WHEN sentiment_label = 'neutral' THEN 1 ELSE 0 END) as neutral_sentiment_articles,
        
        -- Coverage metrics
        COUNT(DISTINCT phrase) as unique_phrases,
        COUNT(DISTINCT province_clean) as provinces_covered,
        MIN(publish_date) as earliest_article,
        MAX(publish_date) as latest_article
        
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    GROUP BY media_name
),

mismatch_patterns AS (
    SELECT
        media_name,
        
        -- Top mismatch patterns for each outlet
        SUM(CASE WHEN phrase_category_clean = 'empowering' AND predicted_category = 'neutral' THEN 1 ELSE 0 END) as empowering_to_neutral,
        SUM(CASE WHEN phrase_category_clean = 'empowering' AND predicted_category = 'limiting' THEN 1 ELSE 0 END) as empowering_to_limiting,
        SUM(CASE WHEN phrase_category_clean = 'neutral' AND predicted_category = 'limiting' THEN 1 ELSE 0 END) as neutral_to_limiting,
        SUM(CASE WHEN phrase_category_clean = 'neutral' AND predicted_category = 'empowering' THEN 1 ELSE 0 END) as neutral_to_empowering,
        SUM(CASE WHEN phrase_category_clean = 'limiting' AND predicted_category = 'neutral' THEN 1 ELSE 0 END) as limiting_to_neutral,
        SUM(CASE WHEN phrase_category_clean = 'limiting' AND predicted_category = 'empowering' THEN 1 ELSE 0 END) as limiting_to_empowering
        
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    WHERE NOT category_match
    GROUP BY media_name
),

outlet_rankings AS (
    SELECT
        media_name,
        total_articles,
        matches,
        mismatches,
        accuracy_pct,
        
        -- Rank outlets by accuracy (1 = most accurate)
        ROW_NUMBER() OVER (ORDER BY accuracy_pct DESC, total_articles DESC) as accuracy_rank,
        
        -- Sentiment metrics
        avg_sentiment,
        avg_subjectivity,
        
        -- Language usage patterns
        empowering_phrases,
        limiting_phrases,
        neutral_phrases,
        ROUND(100.0 * limiting_phrases / total_articles, 1) as limiting_phrase_pct,
        ROUND(100.0 * empowering_phrases / total_articles, 1) as empowering_phrase_pct,
        
        -- Actual sentiment (ML predictions)
        actual_empowering,
        actual_limiting,
        actual_neutral,
        ROUND(100.0 * actual_limiting / total_articles, 1) as actual_limiting_pct,
        ROUND(100.0 * actual_empowering / total_articles, 1) as actual_empowering_pct,
        
        -- Sentiment distribution
        positive_articles,
        negative_articles,
        neutral_sentiment_articles,
        ROUND(100.0 * negative_articles / total_articles, 1) as negative_pct,
        
        -- Coverage
        unique_phrases,
        provinces_covered,
        earliest_article,
        latest_article,
        
        -- Calculate distortion score (higher = more distortion)
        -- Based on: mismatch rate + gap between phrase usage and actual sentiment
        ROUND(
            (100.0 - accuracy_pct) + 
            ABS(ROUND(100.0 * limiting_phrases / total_articles, 1) - ROUND(100.0 * actual_limiting / total_articles, 1)),
            1
        ) as distortion_score
        
    FROM outlet_stats
)

SELECT
    r.media_name,
    r.total_articles,
    r.accuracy_rank,
    r.accuracy_pct,
    r.matches,
    r.mismatches,
    r.distortion_score,
    
    -- Sentiment metrics
    r.avg_sentiment,
    r.avg_subjectivity,
    
    -- Language usage (what phrases they use)
    r.empowering_phrases,
    r.limiting_phrases,
    r.neutral_phrases,
    r.limiting_phrase_pct,
    r.empowering_phrase_pct,
    
    -- Actual sentiment (what ML detected)
    r.actual_empowering,
    r.actual_limiting,
    r.actual_neutral,
    r.actual_limiting_pct,
    r.actual_empowering_pct,
    
    -- Sentiment distribution
    r.positive_articles,
    r.negative_articles,
    r.neutral_sentiment_articles,
    r.negative_pct,
    
    -- Mismatch patterns
    m.empowering_to_neutral,
    m.empowering_to_limiting,
    m.neutral_to_limiting,
    m.neutral_to_empowering,
    m.limiting_to_neutral,
    m.limiting_to_empowering,
    
    -- Coverage
    r.unique_phrases,
    r.provinces_covered,
    r.earliest_article,
    r.latest_article,
    
    -- Classification for advocacy targeting
    CASE
        WHEN r.accuracy_pct >= 60 THEN 'Balanced'
        WHEN r.accuracy_pct >= 50 THEN 'Moderate Distortion'
        WHEN r.accuracy_pct >= 40 THEN 'High Distortion'
        ELSE 'Severe Distortion'
    END as outlet_classification,
    
    -- Primary distortion pattern
    CASE
        WHEN m.neutral_to_limiting >= m.empowering_to_neutral AND m.neutral_to_limiting >= m.empowering_to_limiting THEN 'Negative Bias'
        WHEN m.empowering_to_neutral >= m.neutral_to_limiting AND m.empowering_to_neutral >= m.empowering_to_limiting THEN 'Performative Positivity'
        WHEN m.empowering_to_limiting >= m.neutral_to_limiting AND m.empowering_to_limiting >= m.empowering_to_neutral THEN 'Contradictory Framing'
        ELSE 'Mixed Patterns'
    END as primary_distortion_pattern
    
FROM outlet_rankings r
LEFT JOIN mismatch_patterns m ON r.media_name = m.media_name
ORDER BY r.distortion_score DESC, r.total_articles DESC

-- Data quality tests
{{ with_test("not_null", column="media_name", severity="error") }}
{{ with_test("count_greater_than", count=0, severity="error") }}
{{ with_test("not_null", column="accuracy_pct", severity="error") }}
{{ with_test("not_null", column="distortion_score", severity="error") }}