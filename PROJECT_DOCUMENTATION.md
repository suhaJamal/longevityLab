# Aging Narratives in Canadian Media: A Decolonial Analysis

## Project Overview

This research project analyzes how aging is portrayed in Canadian news media during 2023. Using machine learning sentiment analysis, we examine whether media narratives frame aging as a crisis/burden (limiting), neutral, or empowering. The goal is to provide evidence-based insights to policymakers and advocates working to improve public discourse around aging.

---

## Research Questions

1. How do Canadian media narratives frame aging populations?
2. What is the ratio of limiting vs. empowering narratives across provinces?
3. Which provinces have more positive or negative aging discourse?
4. How do phrase-based assumptions compare to ML-predicted sentiment?

---

## Data Source

### Media Cloud API
- **Source:** [Media Cloud](https://mediacloud.org/) - an open-source platform for media analysis
- **Time Period:** January 1, 2023 - December 31, 2023
- **Geographic Scope:** Canadian news media by province

### Canadian Media Collections (Media Cloud IDs)
| Province | Collection ID | Sources |
|----------|---------------|---------|
| Ontario | 38379397 | 394 |
| British Columbia | 38379407 | 277 |
| Alberta | 38379399 | 195 |
| Quebec | 38379395 | 181 |
| Saskatchewan | 38379406 | 79 |
| Manitoba | 38379405 | 72 |
| Nova Scotia | 38379416 | 59 |
| New Brunswick | 38379411 | 40 |
| PEI | 38379414 | 8 |

---

## Search Phrases

Articles were collected using 17 phrases across three narrative categories:

### Limiting Narratives (Crisis/Burden Framing)
- aging crisis
- aging population crisis
- elderly burden
- aging tsunami
- silver tsunami
- demographic time bomb

### Neutral Narratives (Factual/Descriptive)
- aging population
- older adults
- senior citizens
- elderly population
- population aging

### Empowering Narratives (Active/Positive Framing)
- active aging
- successful aging
- healthy aging
- aging well
- productive aging
- elder wisdom

---

## Datasets

### 1. aging_narratives_articles.csv (Raw Data)
Full article dataset with scraped text content.

| Column | Description |
|--------|-------------|
| url | Article URL |
| title | Article headline |
| publish_date | Publication date |
| media_name | News outlet name |
| phrase | Search phrase that found this article |
| phrase_category | Pre-assigned category (limiting/neutral/empowering) |
| province | Canadian province |
| article_text | Scraped article content |

### 2. aging_narratives_articles_merged.csv
Combined dataset including all provinces.

### 3. aging_narratives_volume.json
Story counts by phrase and province.

### 4. aging_narratives_temporal.csv
Daily story counts for trend analysis.

| Column | Description |
|--------|-------------|
| date | Publication date |
| count | Number of articles |
| phrase | Search phrase |
| category | Narrative category |
| province | Province |

---

## Methodology

### Phase 1: Data Collection (Completed)
1. Query Media Cloud API for articles containing target phrases
2. Filter by Canadian provincial media collections
3. Scrape full article text from URLs
4. Store metadata and content

### Phase 2: ML Sentiment Analysis (Upcoming)
1. Clean and preprocess article text
2. Apply sentiment/classification model to predict actual narrative tone
3. Compare `phrase_category` (assumption) vs `predicted_category` (ML result)
4. Identify articles where phrase-based categorization differs from actual content

### Phase 3: Analysis & Visualization (Upcoming)
1. Build Streamlit dashboard for interactive exploration
2. Generate statistical summaries by province
3. Identify temporal trends and patterns
4. Create visualizations for policy presentations

---

## Key Insight

**Why ML matters:** An article containing "aging crisis" might actually:
- Criticize the crisis framing
- Use it in a neutral reporting context
- Argue against the narrative

Phrase-based categorization assumes the phrase reflects the article's stance. ML classification reads the full text to determine the actual tone.

---

## Expected Outcomes

### Quantitative Findings
- Narrative distribution across provinces
- Limiting-to-empowering ratio
- Temporal trends (spikes around policy debates, elections)
- Provincial comparisons

### Qualitative Insights
- Which media outlets use more empowering language
- Common framing patterns in limiting narratives
- Voice representation (whose perspectives are centered)

---

## Beneficiaries

### 1. Government Leaders & Policymakers
- Evidence for policy decisions affecting aging populations
- Understanding of public discourse around aging
- Data to support age-friendly initiatives

### 2. Advocacy Organizations
- Documentation of ageist media framing
- Data for awareness campaigns
- Provincial comparisons for targeted advocacy

### 3. Healthcare Sector
- Insights into how aging is communicated publicly
- Support for public health messaging
- Understanding of regional differences

### 4. Academic Researchers
- Replicable methodology for media analysis
- Decolonial framework application
- Cross-provincial comparative data

### 5. Journalists & Media Organizations
- Self-reflection on aging coverage
- Alternative framing suggestions
- Best practices for inclusive language

---

## Project Structure

```
longevityLab/
├── data/
│   ├── aging_narratives_articles.csv          # Raw articles (Ontario, BC)
│   ├── aging_narratives_articles_missing_provinces.csv  # Other provinces
│   ├── aging_narratives_articles_merged.csv   # Combined dataset
│   ├── aging_narratives_temporal.csv          # Time series data
│   └── aging_narratives_volume.json           # Volume statistics
├── notebooks/
│   └── 01_data_exploration.ipynb              # Data exploration
├── src/
│   └── generate_missing_provinces.py          # Fetch missing provinces
├── generate_volume_data.py                    # Generate volume stats
├── generate_temporal_data.py                  # Generate time series
├── generate_articles_data.py                  # Fetch articles
├── scrape_missing_text.py                     # Scrape missing text
└── PROJECT_DOCUMENTATION.md                   # This file
```

---

## Technical Requirements

```bash
pip install mediacloud pandas beautifulsoup4 cloudscraper newspaper3k
```

---

## Citation

```
Aging Narratives in Canadian Media: A Decolonial Discourse Analysis (2023)
Data Source: Media Cloud API
Analysis Period: January - December 2023
```

---

## Contact

For questions about this research project, please contact the project lead.

---

*This project aims to shift public discourse around aging from crisis-based framing toward more empowering, rights-based narratives that recognize the contributions and dignity of older adults.*
