# Longevity Narratives: Automated Media Language Intelligence System

## 1. THE PROBLEM

Canadian media shapes how millions think about aging. Our analysis of **11,929 articles from 2023-2026** reveals a critical narrative crisis: **18.4% of coverage uses harmful "limiting" language that frames seniors as burdens or crises.**

This systematic bias:
- Influences policy decisions about senior services
- Shapes public perception of older adults' value
- Underrepresents seniors' contributions to society
- Only 13.9% of coverage celebrates their capabilities

**The question:** How can advocates measure, track, and change media language about aging in real-time?

---

## 2. DATA SOURCES & PIPELINE DESIGN

### **Data Architecture**
- **Source 1:** Snowflake CLEAN_LONGEVITY_TABLE (11,929 curated articles, 2023-2026)
- **Source 2:** MediaCloud API (50-200 new articles weekly, automated collection)
- **Processing:** Ascend longevityLab pipeline with DuckDB analytics engine
- **Storage:** Snowflake (persistent, grows weekly)

### **Pipeline Overview**
![System Architecture](Longevity_Narratives_System_Architecture.mmd)

**Dual-Pipeline Design:**
1. **Historical Analysis Pipeline** - Processes complete 11,929-article dataset
   - Sentiment classification (AI labels: limiting/neutral/empowering)
   - Multi-dimensional analysis (outlets, topics, geography, temporal)
   - Generates interactive advocacy dashboard

2. **Weekly Monitoring Pipeline** - Automated real-time tracking
   - Runs every Monday 9 AM UTC (MediaCloud API fetch)
   - Analyzes new articles (sentiment + comparison to baseline)
   - Appends to Snowflake (incremental, non-destructive)
   - Sends Friday report automation (stakeholder updates)

### **System Screenshot**
![Pipeline in Action](Screenshot_2026-02-04_at_11_50_50_PM.png)

**Status:** All components passing ✅ | Last run: 1 hour ago ✅ | Execution time: 13.1 seconds

---

## 3. ASCEND'S AGENTIC FEATURES USED

### **1. Automated Data Collection Agent**
- **Media Cloud API Integration** - Programmatic article fetching from 17 phrases across 4 Canadian provinces
- **Weekly Scheduling** - Runs autonomously every Monday (no manual intervention)
- **Intelligent Retry Logic** - Handles API rate limits, timeouts, gracefully processes empty results

### **2. AI-Powered Sentiment Analysis Agent (Otto)**
- **Dual Sentiment Methods** - Compared GPT-based AI labels (ground truth) with Otto's keyword-based classification
- **57% Agreement Rate** - Both methods capture different nuances; combined approach more accurate
- **Confidence Scoring** - Each article has confidence metric (0.3-1.0) to flag ambiguous narratives

### **3. Multi-Component Orchestration**
- **10+ Coordinated Components** - Data flows sequentially: Read → Clean → Analyze → Transform → Output
- **Conditional Workflows** - Different paths for historical vs. weekly data
- **Error Handling** - Deduplication, schema validation, anomaly detection

### **4. Automated Reporting Agent**
- **SQL Analytics** - Generates executive_summary, outlet_accuracy_analysis, temporal_distortion_trends
- **Visualization Generation** - Creates interactive HTML dashboard with 8 analysis sections
- **Scheduled Distribution** - Email reports sent Friday 9 AM UTC (automated stakeholder communication)

---

## 4. WHAT WE LEARNED

### **Proof That Advocacy Works**
**2025 Breakthrough:** Empowering coverage jumped from 10% (2023) → **17.3%** (2025)
- Limiting coverage dropped from 17.9% → 15.7%
- **This proves media language CAN change with pressure**

### **Geographic Insights**
- **Ontario:** 6,506 articles (54.6% of coverage) with 19.5% limiting = **largest opportunity**
- **BC:** 3,192 articles with 16.1% limiting = **best practice model**
- Different regions respond differently to advocacy strategies

### **Topic Matters**
- **Social_Community stories:** 27.7% empowering (seniors as community contributors)
- **Healthcare coverage:** Only 10% empowering (crisis narratives dominate)
- **8,080 neutral articles:** Massive conversion opportunity (reframe factual stories with empowering angles)

### **Outlet Accountability**
- Top 5 worst outlets (Global, CityNews, CBC) account for ~600+ limiting articles
- Model outlets (The Spectator, Niagara Falls Review) consistently 19%+ empowering
- Small, local outlets demonstrate better narrative quality than national chains

### **System Value**
- **One-time analysis ≠ strategy** - Built production system, not static report
- **Weekly monitoring catches shifts** - 2026 regression (25.8% limiting) would have been invisible without automation
- **Data-driven advocacy** - Stop guessing, start measuring media response to campaigns

---

## DELIVERABLES

### **Interactive Dashboard** 
[View Live Dashboard](Advocacy_Intelligence_Dashboard__Revised_.html)
- 8 analysis sections (harm assessment, opportunity, topics, outlets, geography, trends, narrative landscape)
- Chart.js visualizations (doughnut, bar, line, horizontal)
- Dark/light mode toggle
- Recommended actions in every section
- CSV data export

### **Key Visualizations Included:**
1. **Sentiment Overview** - 18.4% harmful, 67.7% neutral, 13.9% empowering
2. **Top Harmful Outlets** - Ranked by limiting coverage %
3. **Topic Analysis** - Social_Community (27.7% empowering) vs Healthcare (10%)
4. **2025 Breakthrough** - Temporal trend showing +4% improvement then 2026 regression
5. **Geographic Targeting** - Ontario (19.5%) vs BC (16.1%) limiting rates
6. **Outlet Tiers** - Critical, Valuable, and Exemplar classifications

---

## TECHNICAL IMPACT

✅ **Automated Weekly Monitoring** - No manual data collection needed
✅ **Production-Ready System** - Running live, 11,929 articles baseline + growing
✅ **AI-Driven Analysis** - Dual sentiment methods for accuracy validation
✅ **Advocacy Intelligence** - Converts data into actionable targeting strategy
✅ **Measurable Impact** - Proof that advocacy works (2025 breakthrough)

---

## NEXT STEPS

**Immediate (30 days):** Engage Tier 1 outlets (Global, CityNews, CBC) with data-backed media outreach
**Short-term (90 days):** Partner with model outlets (The Spectator) as collaborators; develop journalist training
**Long-term:** Monitor weekly trends, convert 8,080 neutral articles to empowering frame, achieve 15% empowering / 15% limiting targets

---

*System built with Ascend.io orchestration, DuckDB analytics, Snowflake storage, MediaCloud API, and Otto AI agents.*
*Dataset: 11,929 articles from Canadian media (2023-2026)*
*Production Status: LIVE | Automation: Running | Next Update: Monday 9 AM UTC*
