{{
    config(
        materialized="table"
    )
}}

-- Track how language distortion changed over time from 2023 → 2025 → 2026
-- Reveals whether media coverage of aging is improving or worsening

WITH yearly_overall AS (
    -- Overall mismatch rate by year
    SELECT
        year,
        COUNT(*) as total_articles,
        SUM(CASE WHEN category_match THEN 1 ELSE 0 END) as matches,
        SUM(CASE WHEN NOT category_match THEN 1 ELSE 0 END) as mismatches,
        ROUND(100.0 * SUM(CASE WHEN category_match THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        ROUND(100.0 * SUM(CASE WHEN NOT category_match THEN 1 ELSE 0 END) / COUNT(*), 1) as mismatch_pct,
        ROUND(AVG(sentiment_score), 3) as avg_sentiment,
        ROUND(AVG(subjectivity), 3) as avg_subjectivity
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    GROUP BY year
),

yearly_by_phrase AS (
    -- Track specific phrases over time
    SELECT
        year,
        phrase,
        phrase_category_clean,
        COUNT(*) as total_articles,
        SUM(CASE WHEN category_match THEN 1 ELSE 0 END) as matches,
        ROUND(100.0 * SUM(CASE WHEN category_match THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        ROUND(AVG(sentiment_score), 3) as avg_sentiment
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    GROUP BY year, phrase, phrase_category_clean
),

yearly_by_province AS (
    -- Provincial accuracy trends
    SELECT
        year,
        province_clean,
        COUNT(*) as total_articles,
        SUM(CASE WHEN category_match THEN 1 ELSE 0 END) as matches,
        ROUND(100.0 * SUM(CASE WHEN category_match THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        ROUND(AVG(sentiment_score), 3) as avg_sentiment
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    GROUP BY year, province_clean
),

yearly_by_category AS (
    -- Track phrase categories over time
    SELECT
        year,
        phrase_category_clean,
        COUNT(*) as total_articles,
        SUM(CASE WHEN category_match THEN 1 ELSE 0 END) as matches,
        ROUND(100.0 * SUM(CASE WHEN category_match THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        ROUND(AVG(sentiment_score), 3) as avg_sentiment,
        
        -- Predicted category distribution
        SUM(CASE WHEN predicted_category = 'empowering' THEN 1 ELSE 0 END) as actual_empowering,
        SUM(CASE WHEN predicted_category = 'limiting' THEN 1 ELSE 0 END) as actual_limiting,
        SUM(CASE WHEN predicted_category = 'neutral' THEN 1 ELSE 0 END) as actual_neutral
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    GROUP BY year, phrase_category_clean
),

yearly_by_outlet AS (
    -- Media outlet trends over time
    SELECT
        year,
        media_name,
        COUNT(*) as total_articles,
        SUM(CASE WHEN category_match THEN 1 ELSE 0 END) as matches,
        ROUND(100.0 * SUM(CASE WHEN category_match THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        ROUND(AVG(sentiment_score), 3) as avg_sentiment
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    GROUP BY year, media_name
),

monthly_trends AS (
    -- Monthly granularity for temporal patterns
    SELECT
        year,
        month,
        COUNT(*) as total_articles,
        SUM(CASE WHEN category_match THEN 1 ELSE 0 END) as matches,
        ROUND(100.0 * SUM(CASE WHEN category_match THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        ROUND(AVG(sentiment_score), 3) as avg_sentiment
    FROM {{ ref('sentiment_analysis_longevity_data') }}
    GROUP BY year, month
),

phrase_trends AS (
    -- Calculate year-over-year change for key phrases
    SELECT
        phrase,
        phrase_category_clean,
        
        -- 2023 metrics
        MAX(CASE WHEN year = 2023 THEN total_articles ELSE 0 END) as articles_2023,
        MAX(CASE WHEN year = 2023 THEN accuracy_pct ELSE NULL END) as accuracy_2023,
        MAX(CASE WHEN year = 2023 THEN avg_sentiment ELSE NULL END) as sentiment_2023,
        
        -- 2025 metrics
        MAX(CASE WHEN year = 2025 THEN total_articles ELSE 0 END) as articles_2025,
        MAX(CASE WHEN year = 2025 THEN accuracy_pct ELSE NULL END) as accuracy_2025,
        MAX(CASE WHEN year = 2025 THEN avg_sentiment ELSE NULL END) as sentiment_2025,
        
        -- 2026 metrics
        MAX(CASE WHEN year = 2026 THEN total_articles ELSE 0 END) as articles_2026,
        MAX(CASE WHEN year = 2026 THEN accuracy_pct ELSE NULL END) as accuracy_2026,
        MAX(CASE WHEN year = 2026 THEN avg_sentiment ELSE NULL END) as sentiment_2026,
        
        -- Calculate changes
        MAX(CASE WHEN year = 2026 THEN accuracy_pct ELSE NULL END) - 
        MAX(CASE WHEN year = 2023 THEN accuracy_pct ELSE NULL END) as accuracy_change_2023_to_2026,
        
        MAX(CASE WHEN year = 2026 THEN avg_sentiment ELSE NULL END) - 
        MAX(CASE WHEN year = 2023 THEN avg_sentiment ELSE NULL END) as sentiment_change_2023_to_2026
        
    FROM yearly_by_phrase
    GROUP BY phrase, phrase_category_clean
),

province_trends AS (
    -- Calculate year-over-year change by province
    SELECT
        province_clean,
        
        -- 2023 metrics
        MAX(CASE WHEN year = 2023 THEN total_articles ELSE 0 END) as articles_2023,
        MAX(CASE WHEN year = 2023 THEN accuracy_pct ELSE NULL END) as accuracy_2023,
        
        -- 2025 metrics
        MAX(CASE WHEN year = 2025 THEN total_articles ELSE 0 END) as articles_2025,
        MAX(CASE WHEN year = 2025 THEN accuracy_pct ELSE NULL END) as accuracy_2025,
        
        -- 2026 metrics
        MAX(CASE WHEN year = 2026 THEN total_articles ELSE 0 END) as articles_2026,
        MAX(CASE WHEN year = 2026 THEN accuracy_pct ELSE NULL END) as accuracy_2026,
        
        -- Calculate change
        MAX(CASE WHEN year = 2026 THEN accuracy_pct ELSE NULL END) - 
        MAX(CASE WHEN year = 2023 THEN accuracy_pct ELSE NULL END) as accuracy_change_2023_to_2026
        
    FROM yearly_by_province
    GROUP BY province_clean
),

outlet_trends AS (
    -- Track outlet improvement/decline over time
    SELECT
        media_name,
        
        -- 2023 metrics
        MAX(CASE WHEN year = 2023 THEN total_articles ELSE 0 END) as articles_2023,
        MAX(CASE WHEN year = 2023 THEN accuracy_pct ELSE NULL END) as accuracy_2023,
        
        -- 2025 metrics
        MAX(CASE WHEN year = 2025 THEN total_articles ELSE 0 END) as articles_2025,
        MAX(CASE WHEN year = 2025 THEN accuracy_pct ELSE NULL END) as accuracy_2025,
        
        -- 2026 metrics
        MAX(CASE WHEN year = 2026 THEN total_articles ELSE 0 END) as articles_2026,
        MAX(CASE WHEN year = 2026 THEN accuracy_pct ELSE NULL END) as accuracy_2026,
        
        -- Calculate change
        MAX(CASE WHEN year = 2026 THEN accuracy_pct ELSE NULL END) - 
        MAX(CASE WHEN year = 2023 THEN accuracy_pct ELSE NULL END) as accuracy_change_2023_to_2026,
        
        -- Determine trend
        CASE
            WHEN MAX(CASE WHEN year = 2026 THEN accuracy_pct ELSE NULL END) - 
                 MAX(CASE WHEN year = 2023 THEN accuracy_pct ELSE NULL END) > 10 THEN 'Significantly Improving'
            WHEN MAX(CASE WHEN year = 2026 THEN accuracy_pct ELSE NULL END) - 
                 MAX(CASE WHEN year = 2023 THEN accuracy_pct ELSE NULL END) > 5 THEN 'Improving'
            WHEN MAX(CASE WHEN year = 2026 THEN accuracy_pct ELSE NULL END) - 
                 MAX(CASE WHEN year = 2023 THEN accuracy_pct ELSE NULL END) >= -5 THEN 'Stable'
            WHEN MAX(CASE WHEN year = 2026 THEN accuracy_pct ELSE NULL END) - 
                 MAX(CASE WHEN year = 2023 THEN accuracy_pct ELSE NULL END) >= -10 THEN 'Declining'
            ELSE 'Significantly Declining'
        END as trend_direction
        
    FROM yearly_by_outlet
    GROUP BY media_name
    HAVING MAX(CASE WHEN year = 2023 THEN total_articles ELSE 0 END) > 0
       AND MAX(CASE WHEN year = 2026 THEN total_articles ELSE 0 END) > 0
)

-- Final output: Comprehensive temporal analysis
SELECT
    'overall' as analysis_type,
    CAST(year AS VARCHAR) as dimension_value,
    NULL as sub_dimension,
    total_articles,
    matches,
    mismatches,
    accuracy_pct,
    mismatch_pct,
    avg_sentiment,
    avg_subjectivity,
    NULL as accuracy_2023,
    NULL as accuracy_2025,
    NULL as accuracy_2026,
    NULL as accuracy_change,
    NULL as trend_direction,
    
    -- Calculate year-over-year change
    accuracy_pct - LAG(accuracy_pct) OVER (ORDER BY year) as yoy_accuracy_change,
    avg_sentiment - LAG(avg_sentiment) OVER (ORDER BY year) as yoy_sentiment_change
    
FROM yearly_overall

UNION ALL

SELECT
    'phrase' as analysis_type,
    phrase as dimension_value,
    phrase_category_clean as sub_dimension,
    articles_2023 + articles_2025 + articles_2026 as total_articles,
    NULL as matches,
    NULL as mismatches,
    accuracy_2026 as accuracy_pct,
    NULL as mismatch_pct,
    sentiment_2026 as avg_sentiment,
    NULL as avg_subjectivity,
    accuracy_2023,
    accuracy_2025,
    accuracy_2026,
    accuracy_change_2023_to_2026 as accuracy_change,
    CASE
        WHEN accuracy_change_2023_to_2026 > 10 THEN 'Significantly Improving'
        WHEN accuracy_change_2023_to_2026 > 5 THEN 'Improving'
        WHEN accuracy_change_2023_to_2026 >= -5 THEN 'Stable'
        WHEN accuracy_change_2023_to_2026 >= -10 THEN 'Declining'
        ELSE 'Significantly Declining'
    END as trend_direction,
    NULL as yoy_accuracy_change,
    NULL as yoy_sentiment_change
FROM phrase_trends
WHERE articles_2023 + articles_2025 + articles_2026 >= 10  -- Minimum sample size

UNION ALL

SELECT
    'province' as analysis_type,
    province_clean as dimension_value,
    NULL as sub_dimension,
    articles_2023 + articles_2025 + articles_2026 as total_articles,
    NULL as matches,
    NULL as mismatches,
    accuracy_2026 as accuracy_pct,
    NULL as mismatch_pct,
    NULL as avg_sentiment,
    NULL as avg_subjectivity,
    accuracy_2023,
    accuracy_2025,
    accuracy_2026,
    accuracy_change_2023_to_2026 as accuracy_change,
    CASE
        WHEN accuracy_change_2023_to_2026 > 10 THEN 'Significantly Improving'
        WHEN accuracy_change_2023_to_2026 > 5 THEN 'Improving'
        WHEN accuracy_change_2023_to_2026 >= -5 THEN 'Stable'
        WHEN accuracy_change_2023_to_2026 >= -10 THEN 'Declining'
        ELSE 'Significantly Declining'
    END as trend_direction,
    NULL as yoy_accuracy_change,
    NULL as yoy_sentiment_change
FROM province_trends

UNION ALL

SELECT
    'outlet' as analysis_type,
    media_name as dimension_value,
    NULL as sub_dimension,
    articles_2023 + articles_2025 + articles_2026 as total_articles,
    NULL as matches,
    NULL as mismatches,
    accuracy_2026 as accuracy_pct,
    NULL as mismatch_pct,
    NULL as avg_sentiment,
    NULL as avg_subjectivity,
    accuracy_2023,
    accuracy_2025,
    accuracy_2026,
    accuracy_change_2023_to_2026 as accuracy_change,
    trend_direction,
    NULL as yoy_accuracy_change,
    NULL as yoy_sentiment_change
FROM outlet_trends
WHERE articles_2023 + articles_2025 + articles_2026 >= 10  -- Minimum sample size

UNION ALL

SELECT
    'category' as analysis_type,
    CAST(year AS VARCHAR) as dimension_value,
    phrase_category_clean as sub_dimension,
    total_articles,
    matches,
    NULL as mismatches,
    accuracy_pct,
    NULL as mismatch_pct,
    avg_sentiment,
    NULL as avg_subjectivity,
    NULL as accuracy_2023,
    NULL as accuracy_2025,
    NULL as accuracy_2026,
    NULL as accuracy_change,
    NULL as trend_direction,
    accuracy_pct - LAG(accuracy_pct) OVER (PARTITION BY phrase_category_clean ORDER BY year) as yoy_accuracy_change,
    avg_sentiment - LAG(avg_sentiment) OVER (PARTITION BY phrase_category_clean ORDER BY year) as yoy_sentiment_change
FROM yearly_by_category

UNION ALL

SELECT
    'monthly' as analysis_type,
    CAST(year AS VARCHAR) || '-' || LPAD(CAST(month AS VARCHAR), 2, '0') as dimension_value,
    NULL as sub_dimension,
    total_articles,
    matches,
    NULL as mismatches,
    accuracy_pct,
    NULL as mismatch_pct,
    avg_sentiment,
    NULL as avg_subjectivity,
    NULL as accuracy_2023,
    NULL as accuracy_2025,
    NULL as accuracy_2026,
    NULL as accuracy_change,
    NULL as trend_direction,
    NULL as yoy_accuracy_change,
    NULL as yoy_sentiment_change
FROM monthly_trends
ORDER BY analysis_type, dimension_value

-- Data quality tests
{{ with_test("not_null", column="analysis_type", severity="error") }}
{{ with_test("not_null", column="dimension_value", severity="error") }}
{{ with_test("count_greater_than", count=0, severity="error") }}