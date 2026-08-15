# Longevity Narratives Analysis Project

## Overview

This project analyzes Canadian media coverage of aging and longevity narratives from 2023-2026, providing advocacy intelligence to identify harmful limiting narratives and amplify empowering stories about aging.

**Dataset:** 11,929 highly relevant longevity articles from Canadian media outlets  
**Time Period:** 2023-2026  
**Data Source:** Snowflake (`PUBLIC.CLEAN_LONGEVITY_TABLE`)  
**Processing Engine:** DuckDB (Ascend Data Plane)

## Project Structure

```
├── flows/longevityLab/              # Main analysis pipeline
│   ├── longevityLab.yaml            # Flow configuration (DuckDB data plane)
│   └── components/
│       ├── read_longevity_all_data.yaml              # Reads CLEAN_LONGEVITY_TABLE from Snowflake
│       ├── sentiment_analysis_longevity_data.py      # Otto's keyword-based sentiment analysis
│       ├── cleaned_longevity_data.py                 # Data cleaning and normalization
│       ├── executive_summary.sql                     # High-level metrics and KPIs
│       ├── outlet_accuracy_analysis.sql              # Media outlet performance analysis
│       ├── temporal_distortion_trends.sql            # Year-over-year narrative trends
│       ├── read_mediacloud_weekly_new.py             # Weekly MediaCloud data ingestion
│       ├── sentiment_analysis_mediacloud_data.py     # MediaCloud sentiment analysis
│       ├── cleaned_mediacloud_data.py                # MediaCloud data cleaning
│       ├── weekly_new_articles_analysis.sql          # Weekly article analysis
│       └── write_new_articles_to_snowflake.yaml      # Write results back to Snowflake
│
├── connections/
│   ├── snowflake_aging_narratives.yaml   # Source database connection
│   └── data_plane_duckdb.yaml            # Processing engine connection
│
├── automations/
│   ├── weekly_mediacloud_update.yaml     # Scheduled weekly data refresh
│   └── weekly_pipeline_summary.yaml      # Automated reporting
│
└── profiles/
    ├── workspace_template.yaml           # Development environment config
    └── deployment_template.yaml          # Production environment config
```

## Data Schema

### CLEAN_LONGEVITY_TABLE (Source)

| Column | Type | Description |
|--------|------|-------------|
| `URL` | VARCHAR | Article URL |
| `TITLE` | VARCHAR | Article headline |
| `PUBLISH_DATE` | DATE | Publication date |
| `YEAR` | INTEGER | Publication year (2023-2026) |
| `MONTH` | INTEGER | Publication month |
| `MEDIA_NAME` | VARCHAR | Media outlet (e.g., cbc.ca, globalnews.ca) |
| `PHRASE` | VARCHAR | Search phrase that matched article |
| `PHRASE_CATEGORY_CLEAN` | VARCHAR | Category of search phrase |
| `PROVINCE_CLEAN` | VARCHAR | Geographic focus (Ontario, BC, Alberta, Quebec, Other) |
| `ARTICLE_TEXT` | TEXT | Full article content |
| `INGESTION_DATE` | DATE | Date added to database |
| `AI_LABEL` | VARCHAR | Ground truth sentiment (limiting/neutral/empowering) |
| `CONFIDENCE` | DOUBLE | AI confidence score (0.0-1.0) |
| `TOPIC` | VARCHAR | Topic category (Healthcare_Medical, Social_Community, etc.) |

### Sentiment Analysis Output

All source columns plus:

| Column | Type | Description |
|--------|------|-------------|
| `otto_label` | VARCHAR | Otto's sentiment classification (limiting/neutral/empowering) |
| `otto_confidence` | DOUBLE | Otto's confidence score (0.3-1.0) |

## Data Pipelines

The longevityLab flow contains two distinct data pipelines that work together to provide comprehensive media analysis.

### 1. Main Longevity Analysis Pipeline

**Purpose:** Analyze the complete historical dataset of 11,929 curated articles for advocacy intelligence.

**Data Flow:**
```
Snowflake (CLEAN_LONGEVITY_TABLE)
    ↓
read_longevity_all_data.yaml
    ↓
sentiment_analysis_longevity_data.py
    ├─ Adds otto_label (limiting/neutral/empowering)
    └─ Adds otto_confidence (0.3-1.0)
    ↓
cleaned_longevity_data.py
    └─ Normalizes column names, handles nulls
    ↓
SQL Analysis Components (parallel processing)
    ├─ executive_summary.sql → Overall KPIs and distribution
    ├─ outlet_accuracy_analysis.sql → Media outlet performance
    └─ temporal_distortion_trends.sql → Year-over-year trends
    ↓
Advocacy Intelligence Dashboard
```

**Key Features:**
- **Full dataset processing:** All 11,929 articles analyzed
- **Otto's sentiment analysis:** Keyword-based classification with confidence scoring
- **Ground truth comparison:** AI_LABEL vs. otto_label (57% agreement)
- **Multi-dimensional analysis:** Harm assessment, opportunity identification, outlet targeting, geographic patterns, temporal trends
- **Output:** Interactive HTML dashboard with 8 analysis sections

**Use Cases:**
- Strategic advocacy planning
- Media outlet engagement prioritization
- Geographic targeting (Ontario, BC, Alberta, Quebec)
- Temporal trend analysis (2023-2026)
- Topic opportunity identification

### 2. Weekly MediaCloud Update Pipeline

**Purpose:** Continuously monitor new articles from MediaCloud API to track emerging narratives and maintain up-to-date coverage.

**Data Flow:**
```
MediaCloud API (Weekly)
    ↓
read_mediacloud_weekly_new.py
    ├─ Fetches new articles published in the last 7 days
    ├─ Filters by longevity-related keywords
    └─ Deduplicates against existing data
    ↓
sentiment_analysis_mediacloud_data.py
    ├─ Applies Otto's sentiment classifier
    └─ Adds otto_label and otto_confidence
    ↓
cleaned_mediacloud_data.py
    └─ Normalizes and validates new articles
    ↓
weekly_new_articles_analysis.sql
    ├─ Compares to historical baselines
    ├─ Identifies narrative shifts
    └─ Flags anomalies (spikes in limiting coverage)
    ↓
write_new_articles_to_snowflake.yaml
    └─ Appends validated articles to CLEAN_LONGEVITY_TABLE
```

**Key Features:**
- **Automated weekly execution:** Runs every Monday via `weekly_mediacloud_update.yaml` automation
- **Incremental processing:** Only fetches and processes new articles
- **Quality control:** Deduplication, validation, and normalization before storage
- **Trend monitoring:** Compares weekly metrics to historical patterns
- **Alert system:** Flags significant narrative shifts (e.g., sudden spike in limiting coverage)

**Use Cases:**
- Real-time narrative monitoring
- Early warning system for harmful narrative spikes
- Weekly advocacy briefings
- Rapid response to emerging media trends
- Continuous dataset enrichment

### Pipeline Integration

**How They Work Together:**

1. **Historical Foundation:** The main pipeline analyzes the complete 11,929-article dataset to establish baselines and identify patterns.

2. **Continuous Monitoring:** The MediaCloud pipeline adds new articles weekly, maintaining current coverage.

3. **Unified Storage:** Both pipelines write to the same Snowflake table (`CLEAN_LONGEVITY_TABLE`), creating a continuously growing dataset.

4. **Comparative Analysis:** Weekly analysis compares new articles against historical baselines to detect:
   - Narrative shifts (e.g., increase in limiting coverage)
   - Emerging topics or themes
   - New media outlets entering the conversation
   - Geographic expansion of coverage

5. **Feedback Loop:** Insights from weekly monitoring inform strategic adjustments to advocacy campaigns.

**Example Workflow:**
```
Monday:
  → MediaCloud pipeline runs automatically
  → Fetches 50-200 new articles from the past week
  → Processes and appends to CLEAN_LONGEVITY_TABLE

Tuesday-Thursday:
  → Analysts review weekly_new_articles_analysis results
  → Identify any concerning trends (e.g., 2026 spike to 25.8% limiting)

Friday:
  → Weekly pipeline summary automation runs
  → Generates email report with key findings
  → Flags any articles requiring immediate response

Monthly:
  → Re-run main analysis pipeline with updated dataset
  → Refresh advocacy intelligence dashboard
  → Update strategic priorities based on cumulative trends
```

**Data Quality Assurance:**
- **Deduplication:** Both pipelines check for duplicate URLs before processing
- **Schema validation:** Ensures consistent column structure across sources
- **Confidence thresholds:** Low-confidence classifications flagged for manual review
- **Anomaly detection:** Statistical outliers investigated before inclusion

## Sentiment Classification

### Three-Category Framework

1. **LIMITING (18.4%)** - Crisis/burden framing
   - Keywords: "crisis", "burden", "strain", "overwhelmed", "time bomb"
   - Phrases: "aging crisis", "healthcare burden", "silver tsunami"
   - Focus: Decline, dependency, cost, problems

2. **NEUTRAL (67.7%)** - Factual/descriptive reporting
   - Keywords: "report", "study", "data", "statistics", "policy"
   - Phrases: "according to", "research shows", "statistics indicate"
   - Focus: Information, demographics, policy details

3. **EMPOWERING (13.9%)** - Active/positive framing
   - Keywords: "active", "vibrant", "contribution", "wisdom", "innovation"
   - Phrases: "active aging", "successful aging", "age-friendly"
   - Focus: Agency, contribution, opportunity, growth

### Confidence Scoring

Otto's confidence formula:
- **Density Score (60%)**: Keyword matches per 100 words
- **Dominance (40%)**: Primary category strength vs. secondary
- **Range**: 0.3 (low) to 1.0 (high)

## Key Findings

### Overall Distribution
- **Limiting:** 2,196 articles (18.4%) - Harmful narratives requiring intervention
- **Neutral:** 8,080 articles (67.7%) - Conversion opportunity
- **Empowering:** 1,653 articles (13.9%) - Amplification targets

### Temporal Trends
- **2023:** 17.9% limiting, 10.0% empowering (baseline)
- **2024:** 20.4% limiting, 13.3% empowering (worsening)
- **2025:** 15.7% limiting, 17.3% empowering (breakthrough!)
- **2026:** 25.8% limiting, 15.2% empowering (alarming regression)

### Top Harmful Outlets (100+ articles)
1. **globalnews.ca** - 26.0% limiting (327 articles)
2. **citynews.ca** - 25.9% limiting (625 articles)
3. **cbc.ca** - 25.9% limiting (266 articles)

### Geographic Insights
- **Ontario:** Highest volume (6,506 articles) and total harm (1,266 limiting)
- **British Columbia:** Lowest harm rate (16.1%) despite high volume (3,192 articles)
- **Quebec:** Small sample (73 articles) but concerning 24.7% limiting rate

### Topic Opportunities
- **Best:** Social_Community (27.7% empowering) - 578 positive articles
- **Worst:** Healthcare_Medical (10.0% empowering) - Needs reframing

## Analysis Components

### 1. Harm Assessment
Identifies limiting narratives requiring intervention:
- Volume and rate of harmful coverage
- Worst offending outlets
- Geographic concentration
- Temporal spikes

### 2. Opportunity Assessment
Identifies empowering narratives for amplification:
- Volume and rate of positive coverage
- Best-performing topics
- Geographic leaders
- Breakthrough periods

### 3. Topic Analysis
Empowering narrative opportunities by category:
- 11 topic categories analyzed
- Ranked by empowering percentage
- Volume and impact metrics

### 4. Outlet Targeting
Media outlets ranked by limiting narrative prevalence:
- Priority engagement tiers
- Volume vs. harm rate analysis
- Intervention strategies

### 5. Geographic Targeting
Provincial analysis of narrative patterns:
- Volume distribution
- Harm rates by province
- Best practice identification

### 6. Temporal Trends
Year-over-year narrative evolution:
- Breakthrough and regression analysis
- Seasonal patterns
- Event correlation

### 7. Counter-Narrative Exemplars
Successful empowering stories for replication:
- High-confidence empowering articles
- Effective framing patterns
- Journalist best practices

### 8. Narrative Landscape
Comprehensive view of aging narratives:
- Overall distribution
- Conversion opportunities (8,080 neutral articles)
- Strategic priorities

## Running the Pipeline

### Prerequisites
- Ascend workspace with DuckDB data plane
- Snowflake connection configured (`snowflake_aging_narratives`)
- Access to `PUBLIC.CLEAN_LONGEVITY_TABLE`

### Manual Execution

```bash
# Run full pipeline
ascend run longevityLab

# Run specific component
ascend run longevityLab --component sentiment_analysis_longevity_data

# Run from specific component forward
ascend run longevityLab --from sentiment_analysis_longevity_data
```

### Automated Execution

The pipeline includes automated triggers:
- **Weekly MediaCloud Update:** Ingests new articles every Monday
- **Weekly Pipeline Summary:** Generates reports every Friday

## Outputs and Artifacts

### Interactive Dashboard
HTML dashboard with 8 analysis sections:
- Overview with executive metrics
- Harm assessment with intervention priorities
- Opportunity assessment with amplification targets
- Topic, outlet, and geographic breakdowns
- Temporal trends with year-over-year comparison
- Narrative landscape with strategic recommendations

**Features:**
- Interactive charts (Chart.js)
- Dark/light theme toggle
- CSV export functionality
- Responsive design

### SQL Analysis Tables
- `executive_summary` - High-level KPIs
- `outlet_accuracy_analysis` - Media outlet performance
- `temporal_distortion_trends` - Year-over-year trends
- `weekly_new_articles_analysis` - Weekly article metrics

## Advocacy Strategy

### Immediate Actions (Tier 1)
1. **Target Top 3 Outlets:** Schedule editorial meetings with Global, CityNews, CBC
2. **Ontario Focus:** Develop province-specific counter-narrative strategy
3. **2026 Spike Investigation:** Identify drivers of 25.8% limiting spike

### Short-Term Actions (Tier 2)
1. **Amplify Social_Community Stories:** Social media campaigns
2. **Study 2025 Breakthrough:** Replicate success factors
3. **Journalist Education:** Balanced aging coverage training

### Long-Term Actions (Tier 3)
1. **Convert Neutral Articles:** Provide empowering story angles (8,080 opportunities)
2. **Learn from BC:** Study low harm rate (16.1%) best practices
3. **Quarterly Monitoring:** Track progress toward 15% empowering / 15% limiting targets

## Technical Details

### Sentiment Analysis Method

**Otto's Approach (Keyword-Based):**
- Lexicon-based classification with 50+ keywords per category
- Multi-word phrase detection (weighted 2x)
- Confidence scoring: density (60%) + dominance (40%)
- Range: 0.3-1.0

**AI Labels (Ground Truth):**
- Context-aware classification
- Pre-labeled in source data
- Used as ground truth for analysis
- 57% agreement rate with Otto

### Performance
- **Dataset Size:** 11,929 articles
- **Processing Time:** ~2-3 minutes (full pipeline)
- **Data Plane:** DuckDB (in-memory analytics)
- **Storage:** Snowflake (persistent storage)

## Contact and Support

**Project Owner:** suha@smartdiversity.ca  
**Workspace:** Suha (suha/dev branch)  
**Instance:** Suha Islaih's Instance

## Version History

- **v2.0** (Feb 2026) - Migrated to CLEAN_LONGEVITY_TABLE (12K articles)
- **v1.5** (Feb 2026) - Added Otto sentiment analysis with comparison
- **v1.0** (Feb 2026) - Initial advocacy intelligence dashboard
- **v0.5** (Jan 2026) - Original LONGEVITY table analysis (33K articles)

## License

Proprietary - Smart Diversity Inc.