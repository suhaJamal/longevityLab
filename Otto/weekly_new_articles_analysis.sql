-- Weekly New Articles Analysis
-- Analyzes only this week's new articles from Media Cloud and compares to historical baseline

WITH this_week_articles AS (
    SELECT *
    FROM {{ ref('sentiment_analysis_mediacloud_data') }}
),

historical_baseline AS (
    SELECT
        COUNT(*) as total_articles,
        ROUND(100.0 * SUM(CASE WHEN CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        ROUND(100.0 * SUM(CASE WHEN NOT CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as mismatch_pct,
        ROUND(AVG(SENTIMENT_SCORE), 3) as avg_sentiment
    FROM {{ ref('sentiment_analysis_longevity_data') }}
),

this_week_summary AS (
    SELECT
        COUNT(*) as new_articles_count,
        COUNT(DISTINCT URL) as unique_urls,
        ROUND(100.0 * SUM(CASE WHEN CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        ROUND(100.0 * SUM(CASE WHEN NOT CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as mismatch_pct,
        ROUND(AVG(SENTIMENT_SCORE), 3) as avg_sentiment,
        MIN(PUBLISH_DATE) as earliest_article,
        MAX(PUBLISH_DATE) as latest_article
    FROM this_week_articles
),

phrase_breakdown AS (
    SELECT
        PHRASE,
        PHRASE_CATEGORY,
        COUNT(*) as article_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct_of_total
    FROM this_week_articles
    GROUP BY PHRASE, PHRASE_CATEGORY
    ORDER BY article_count DESC
    LIMIT 10
),

outlet_breakdown AS (
    SELECT
        MEDIA_NAME,
        COUNT(*) as article_count,
        ROUND(100.0 * SUM(CASE WHEN NOT CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as mismatch_pct,
        ROUND(AVG(SENTIMENT_SCORE), 3) as avg_sentiment
    FROM this_week_articles
    GROUP BY MEDIA_NAME
    ORDER BY article_count DESC
    LIMIT 10
),

province_breakdown AS (
    SELECT
        PROVINCE,
        COUNT(*) as article_count,
        ROUND(100.0 * SUM(CASE WHEN NOT CATEGORY_MATCH THEN 1 ELSE 0 END) / COUNT(*), 1) as mismatch_pct
    FROM this_week_articles
    GROUP BY PROVINCE
    ORDER BY article_count DESC
),

trend_analysis AS (
    SELECT
        'Overall Trend' as metric,
        CASE
            WHEN tw.mismatch_pct > hb.mismatch_pct + 5 THEN 'WORSENING (Alert!)'
            WHEN tw.mismatch_pct > hb.mismatch_pct THEN 'Slightly Worsening'
            WHEN tw.mismatch_pct < hb.mismatch_pct - 5 THEN 'IMPROVING'
            WHEN tw.mismatch_pct < hb.mismatch_pct THEN 'Slightly Improving'
            ELSE 'Stable'
        END as trend_status,
        hb.mismatch_pct as historical_mismatch_pct,
        tw.mismatch_pct as this_week_mismatch_pct,
        ROUND(tw.mismatch_pct - hb.mismatch_pct, 1) as change_pct_points,
        CASE
            WHEN tw.mismatch_pct > 50 THEN 'YES - Immediate attention needed'
            ELSE 'No'
        END as alert_required
    FROM this_week_summary tw
    CROSS JOIN historical_baseline hb
)

-- Final output: Weekly summary metrics
SELECT
    'Weekly Summary' as analysis_type,
    CURRENT_DATE as analysis_date,
    tw.new_articles_count,
    tw.unique_urls,
    tw.accuracy_pct as this_week_accuracy_pct,
    tw.mismatch_pct as this_week_mismatch_pct,
    hb.mismatch_pct as historical_mismatch_pct,
    ROUND(tw.mismatch_pct - hb.mismatch_pct, 1) as mismatch_change_pct_points,
    ta.trend_status,
    ta.alert_required,
    tw.avg_sentiment as this_week_avg_sentiment,
    hb.avg_sentiment as historical_avg_sentiment,
    tw.earliest_article,
    tw.latest_article,
    NULL as detail_name,
    NULL as detail_value,
    NULL as detail_metric
FROM this_week_summary tw
CROSS JOIN historical_baseline hb
CROSS JOIN trend_analysis ta

UNION ALL

-- Phrase breakdown details
SELECT
    'Top Phrases This Week' as analysis_type,
    CURRENT_DATE as analysis_date,
    NULL as new_articles_count,
    NULL as unique_urls,
    NULL as this_week_accuracy_pct,
    NULL as this_week_mismatch_pct,
    NULL as historical_mismatch_pct,
    NULL as mismatch_change_pct_points,
    NULL as trend_status,
    NULL as alert_required,
    NULL as this_week_avg_sentiment,
    NULL as historical_avg_sentiment,
    NULL as earliest_article,
    NULL as latest_article,
    PHRASE as detail_name,
    CAST(article_count AS VARCHAR) as detail_value,
    PHRASE_CATEGORY || ' (' || pct_of_total || '%)' as detail_metric
FROM phrase_breakdown

UNION ALL

-- Outlet breakdown details
SELECT
    'Top Outlets This Week' as analysis_type,
    CURRENT_DATE as analysis_date,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    MEDIA_NAME as detail_name,
    CAST(article_count AS VARCHAR) as detail_value,
    'Mismatch: ' || mismatch_pct || '%, Sentiment: ' || avg_sentiment as detail_metric
FROM outlet_breakdown

UNION ALL

-- Province breakdown details
SELECT
    'Province Breakdown' as analysis_type,
    CURRENT_DATE as analysis_date,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    PROVINCE as detail_name,
    CAST(article_count AS VARCHAR) as detail_value,
    'Mismatch: ' || mismatch_pct || '%' as detail_metric
FROM province_breakdown

ORDER BY analysis_type, detail_value DESC