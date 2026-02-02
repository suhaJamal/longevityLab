-- Executive Summary: Aging Narratives Analysis
-- Comprehensive insights for advocacy strategy and media engagement

WITH overall_metrics AS (
    SELECT 
        COUNT(*) as total_articles,
        COUNT(DISTINCT MEDIA_NAME) as total_outlets,
        COUNT(DISTINCT PHRASE) as total_phrases,
        MIN(PUBLISH_DATE) as data_start_date,
        MAX(PUBLISH_DATE) as data_end_date,
        ROUND(100.0 * SUM(CASE WHEN CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as overall_accuracy_pct,
        ROUND(100.0 * SUM(CASE WHEN NOT CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as overall_mismatch_pct,
        ROUND(AVG(SENTIMENT_SCORE), 3) as avg_sentiment_score
    FROM {{ ref('sentiment_analysis_longevity_data') }}
),

most_distorted_phrases AS (
    SELECT 
        PHRASE,
        PHRASE_CATEGORY_CLEAN as category,
        COUNT(*) as article_count,
        ROUND(100.0 * SUM(CASE WHEN NOT CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as mismatch_pct,
        ROW_NUMBER() OVER (ORDER BY ROUND(100.0 * SUM(CASE WHEN NOT CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) DESC) as rank
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    GROUP BY PHRASE, PHRASE_CATEGORY_CLEAN
    HAVING COUNT(*) >= 100
),

most_accurate_phrases AS (
    SELECT 
        PHRASE,
        PHRASE_CATEGORY_CLEAN as category,
        COUNT(*) as article_count,
        ROUND(100.0 * SUM(CASE WHEN CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        ROW_NUMBER() OVER (ORDER BY ROUND(100.0 * SUM(CASE WHEN CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) DESC) as rank
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    GROUP BY PHRASE, PHRASE_CATEGORY_CLEAN
    HAVING COUNT(*) >= 100
),

priority_outlets AS (
    SELECT 
        MEDIA_NAME,
        COUNT(*) as article_count,
        ROUND(100.0 * SUM(CASE WHEN NOT CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as mismatch_pct,
        CASE 
            WHEN ROUND(100.0 * SUM(CASE WHEN CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) >= 60 THEN 'Balanced'
            WHEN ROUND(100.0 * SUM(CASE WHEN CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) >= 50 THEN 'Moderate'
            WHEN ROUND(100.0 * SUM(CASE WHEN CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) >= 40 THEN 'High Distortion'
            ELSE 'Severe Distortion'
        END as classification,
        ROW_NUMBER() OVER (ORDER BY ROUND(100.0 * SUM(CASE WHEN NOT CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) DESC) as rank
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    GROUP BY MEDIA_NAME
    HAVING COUNT(*) >= 50
),

exemplar_outlets AS (
    SELECT 
        MEDIA_NAME,
        COUNT(*) as article_count,
        ROUND(100.0 * SUM(CASE WHEN CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        ROW_NUMBER() OVER (ORDER BY ROUND(100.0 * SUM(CASE WHEN CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) DESC) as rank
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    GROUP BY MEDIA_NAME
    HAVING COUNT(*) >= 50
),

recent_trend AS (
    SELECT 
        DATE_TRUNC('month', PUBLISH_DATE) as month,
        ROUND(100.0 * SUM(CASE WHEN NOT CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as mismatch_pct,
        ROW_NUMBER() OVER (ORDER BY DATE_TRUNC('month', PUBLISH_DATE) DESC) as recency_rank
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    WHERE PUBLISH_DATE >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY DATE_TRUNC('month', PUBLISH_DATE)
),

trend_direction AS (
    SELECT 
        CASE 
            WHEN (SELECT mismatch_pct FROM recent_trend WHERE recency_rank = 1) < 
                 (SELECT mismatch_pct FROM recent_trend WHERE recency_rank = 6) THEN 'IMPROVING'
            WHEN (SELECT mismatch_pct FROM recent_trend WHERE recency_rank = 1) > 
                 (SELECT mismatch_pct FROM recent_trend WHERE recency_rank = 6) THEN 'WORSENING'
            ELSE 'STABLE'
        END as trend,
        ROUND(
            (SELECT mismatch_pct FROM recent_trend WHERE recency_rank = 1) - 
            (SELECT mismatch_pct FROM recent_trend WHERE recency_rank = 6), 
            1
        ) as change_pct_points
)

-- Final output: Executive Summary
SELECT 
    'EXECUTIVE SUMMARY' as section,
    'Overall Metrics' as subsection,
    om.total_articles,
    om.total_outlets,
    om.total_phrases,
    om.data_start_date,
    om.data_end_date,
    om.overall_accuracy_pct,
    om.overall_mismatch_pct,
    om.avg_sentiment_score,
    td.trend as trend_direction,
    td.change_pct_points,
    NULL as detail_name,
    NULL as detail_value,
    NULL as detail_metric,
    1 as priority_order
FROM overall_metrics om
CROSS JOIN trend_direction td

UNION ALL

SELECT 
    'MOST DISTORTED PHRASES' as section,
    'Top 5 Requiring Attention' as subsection,
    NULL as total_articles,
    NULL as total_outlets,
    NULL as total_phrases,
    NULL as data_start_date,
    NULL as data_end_date,
    NULL as overall_accuracy_pct,
    NULL as overall_mismatch_pct,
    NULL as avg_sentiment_score,
    NULL as trend_direction,
    NULL as change_pct_points,
    PHRASE as detail_name,
    CAST(article_count AS VARCHAR) as detail_value,
    CONCAT(category, ': ', mismatch_pct, '% mismatch') as detail_metric,
    2 as priority_order
FROM most_distorted_phrases
WHERE rank <= 5

UNION ALL

SELECT 
    'MOST ACCURATE PHRASES' as section,
    'Top 5 Positive Examples' as subsection,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    PHRASE as detail_name,
    CAST(article_count AS VARCHAR) as detail_value,
    CONCAT(category, ': ', accuracy_pct, '% accuracy') as detail_metric,
    3 as priority_order
FROM most_accurate_phrases
WHERE rank <= 5

UNION ALL

SELECT 
    'PRIORITY OUTLETS' as section,
    'Top 10 for Advocacy Engagement' as subsection,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    MEDIA_NAME as detail_name,
    CAST(article_count AS VARCHAR) as detail_value,
    CONCAT(classification, ': ', mismatch_pct, '% mismatch') as detail_metric,
    4 as priority_order
FROM priority_outlets
WHERE rank <= 10

UNION ALL

SELECT 
    'EXEMPLAR OUTLETS' as section,
    'Top 5 Best Practices' as subsection,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    MEDIA_NAME as detail_name,
    CAST(article_count AS VARCHAR) as detail_value,
    CONCAT(accuracy_pct, '% accuracy') as detail_metric,
    5 as priority_order
FROM exemplar_outlets
WHERE rank <= 5

ORDER BY priority_order, detail_value DESC