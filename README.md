# Aging Narratives Analysis - Media Cloud Study 2023

## Decolonial Discourse Analysis of Aging in Media

This project analyzes how aging is framed in 2023 media coverage, examining the balance between **limiting** (crisis/burden), **neutral** (factual/descriptive), and **empowering** (active/wise) narratives. The analysis employs a decolonial framework to investigate whose voices are centered, how colonial structures shape aging discourse, and patterns of ageism.

---

## 📋 Quick Start

### Prerequisites
```bash
pip install mediacloud pandas matplotlib seaborn
```

### Your API Key
```
9e047cbfc9e1cd397857c21eb52c78902fc5f181
```

### Run Complete Analysis
```bash
python aging_narrative_complete_analysis.py
```

This will:
1. Query Media Cloud for all narrative phrases (2023)
2. Calculate volume statistics and imbalance ratios
3. Extract temporal trends (daily story counts)
4. Retrieve sample articles for manual coding
5. Export all results to multiple formats

**Expected Runtime:** 15-30 minutes depending on API speed

---

## 📊 Analysis Pipeline

### STEP 1: Data Collection (Automated)
**Script:** `aging_narrative_complete_analysis.py`

**What it does:**
- Searches Media Cloud for 18 phrases across 3 narrative categories
- Retrieves story counts for volume analysis
- Extracts time series data for temporal trends
- Downloads sample articles (up to 1000 per phrase)
- Exports results to JSON and CSV

**Narrative Categories:**

**Limiting Narratives** (crisis/burden framing):
- aging crisis
- aging population crisis
- elderly burden
- aging tsunami
- silver tsunami
- demographic time bomb

**Neutral Narratives** (factual/descriptive):
- aging population
- older adults
- senior citizens
- elderly population
- population aging

**Empowering Narratives** (active/positive framing):
- active aging
- successful aging
- healthy aging
- aging well
- productive aging
- elder wisdom

**Output Files:**
- `aging_narratives_volume.json` - Story counts by phrase and category
- `aging_narratives_temporal.csv` - Daily time series data
- `aging_narratives_all_articles.json` - Full article metadata
- `aging_narratives_coding_sample.csv` - Stratified sample for manual coding
- `aging_narratives_summary.txt` - Quick reference summary

---

### STEP 2: Manual Narrative Coding (Human Analysis)
**Guide:** `decolonial_analysis_framework.py`
**Spreadsheet:** `aging_narratives_coding_sample.csv`

**What you do:**
1. Open `aging_narratives_coding_sample.csv`
2. Read each article (click URL)
3. Code using the framework in `decolonial_analysis_framework.py`
4. Fill in columns:
   - `coded_narrative`: Your assessment (limiting/neutral/empowering)
   - `ageism_present`: yes/no/ambiguous
   - `voice_representation`: whose voices are centered
   - `notes`: qualitative observations

**Coding Categories:**
1. **Narrative Type** - Primary framing
2. **Ageism Indicators** - Benevolent, hostile, ambivalent
3. **Voice & Representation** - Whose perspectives matter
4. **Racialized/Colonized Aging** - Race visibility, structural analysis
5. **Economic Framing** - Burden vs. rights-based
6. **Cultural Knowledge Systems** - What ways of knowing are valued
7. **Agency & Power** - How older adults are positioned
8. **Temporal Orientation** - Decline vs. developmental

**Decolonial Lens Questions:**
- Who has authority to define "successful aging"?
- Whose aging experiences are centered vs. marginalized?
- How is Western biomedicine colonizing aging discourse?
- Are Indigenous/racialized elders visible or erased?
- Who profits from "crisis" narratives?

**Tips:**
- Code 10-20 articles, then take a break to refine your understanding
- Make rich qualitative notes - quotes, patterns, reactions
- If working with others, code 20% independently for inter-rater reliability
- Flag particularly striking examples

---

### STEP 3: Visualization & Statistical Analysis (Automated)
**Script:** `aging_narrative_visualizations.py`

**Run after completing Step 2:**
```bash
python aging_narrative_visualizations.py
```

**What it generates:**

**Visualizations:**
1. `viz_narrative_distribution.png` - Pie chart and bar chart of volume
2. `viz_temporal_trends.png` - Line graphs showing trends over 2023
3. `viz_monthly_heatmap.png` - Heatmap of narrative intensity by month
4. `viz_phrase_comparison.png` - Horizontal bar chart of all phrases
5. `viz_imbalance_ratio.png` - Visual of limiting:empowering ratio
6. `viz_coded_analysis.png` - Patterns from manual coding

**Statistics:**
- `analysis_summary_stats.txt` - Comprehensive statistical summary

---

## 📁 Project Files

### Core Scripts
- `aging_narrative_complete_analysis.py` - Main data collection script
- `decolonial_analysis_framework.py` - Coding guide and framework
- `aging_narrative_visualizations.py` - Visualization generator

### Data Files (Generated)
- `aging_narratives_volume.json` - Volume statistics
- `aging_narratives_temporal.csv` - Time series data
- `aging_narratives_all_articles.json` - Full article database
- `aging_narratives_coding_sample.csv` - **Manual coding spreadsheet**
- `aging_narratives_summary.txt` - Quick summary

### Analysis Outputs
- `viz_*.png` - All visualizations (6 files)
- `analysis_summary_stats.txt` - Statistical summary

---

## 🔍 Expected Findings

Based on preliminary analysis, you should investigate:

### Quantitative Patterns
- **Imbalance ratio**: Likely 3-10 limiting stories per 1 empowering story
- **Temporal spikes**: Do limiting narratives spike around policy debates?
- **Voice marginalization**: % of articles centering older adults' voices
- **Race erasure**: How often are racialized/Indigenous elders visible?

### Qualitative Themes
- **Dominant metaphors**: tsunami, crisis, burden, bomb
- **Whose expertise counts**: Doctors/economists vs. elder wisdom
- **Neoliberal framing**: Individual responsibility vs. collective care
- **Colonial knowledge hierarchies**: Western biomedicine universalized

### Decolonial Insights
- How ageism intersects with racism, capitalism, ableism
- Whose aging is normalized vs. pathologized
- Invisibility of Indigenous aging knowledge
- Who benefits from positioning elders as burdens
- Resistance narratives and counter-stories

---

## 📊 Key Metrics to Track

### Volume Analysis
```
Limiting:    X,XXX stories (XX%)
Neutral:     X,XXX stories (XX%)  
Empowering:  X,XXX stories (XX%)

Imbalance Ratio: XX.X : 1
```

### Voice Representation (from coding)
- % with older adult voices centered
- % expert/institutional dominated
- % with no direct voices
- % with Indigenous/racialized perspectives

### Ageism Detection
- % with hostile ageism
- % with benevolent ageism
- % with no ageism detected

---

## 🎯 Research Questions Addressed

1. **What is the narrative imbalance?** How do limiting narratives dominate?
2. **Whose voices matter?** Who has authority in aging discourse?
3. **How is race (in)visible?** Are Indigenous/racialized elders present?
4. **What colonial structures?** How do power hierarchies shape narratives?
5. **Economic framing?** Burden vs. entitlement vs. collective care?
6. **Alternative possibilities?** Where are empowering narratives found?

---

## 📝 Writing Your Analysis

### Structure Suggestions

**1. Introduction**
- Research question and significance
- Decolonial framework rationale
- Methods overview

**2. Methods**
- Media Cloud data source
- Search strategy (18 phrases)
- Coding framework
- Decolonial lens application

**3. Findings**

**Volume Analysis:**
- Present imbalance ratio with visualizations
- Discuss percentage distribution
- Interpret implications

**Temporal Trends:**
- Identify spikes and patterns
- Correlate with events (policy debates, elections, etc.)
- Compare narrative trajectories

**Coded Discourse Analysis:**
- Voice representation patterns
- Ageism types and frequency
- Racialized aging (in)visibility
- Economic framing variations
- Colonial knowledge hierarchies

**4. Decolonial Discussion**
- Power relations in aging discourse
- Whose knowledge is legitimized
- Intersections of ageism/racism/capitalism
- Indigenous erasure
- Resistance possibilities

**5. Implications**
- For journalism covering aging
- For gerontology research
- For policy advocacy
- For decolonizing aging discourse

---

## 🛠️ Troubleshooting

### Common Issues

**"Module not found" error:**
```bash
pip install mediacloud pandas matplotlib seaborn
```

**API connection issues:**
- Check internet connection
- Verify API key is correct
- Media Cloud servers may be temporarily down

**No articles returned:**
- Verify date format: `date(2023, 1, 1)` not strings
- Check if phrase has any results with `story_count()` first

**Coding spreadsheet won't open:**
- Use Excel, Google Sheets, or LibreOffice
- File is standard CSV format

**Visualizations fail:**
- Ensure you ran Step 1 first
- Check that JSON/CSV files exist in same directory
- Install missing libraries: `pip install matplotlib seaborn`

---

## 📚 Further Reading

### Decolonial Gerontology
- Aging, Media and Culture (Krainitzki & Chivers)
- Critical perspectives on aging (Calasanti & Slevin)
- Decolonizing methodologies (Tuhiwai Smith)

### Ageism & Discourse Analysis
- Gendron et al. (2016) "The language of ageism"
- Rozanova (2010) "Discourse of successful aging"
- Critical discourse analysis frameworks

### Media Representation
- Media representations of aging (Harwood)
- Framing theory in journalism studies

---

## 📧 Support

### Questions about this analysis?
- Review the coding framework: `decolonial_analysis_framework.py`
- Check the example coded entry in the framework file
- Examine the generated summary files for data validation

### Media Cloud API Help
- Documentation: https://mediacloud.org/
- API docs: https://search.mediacloud.org/docs

---

## ✅ Analysis Checklist

- [ ] Install required Python packages
- [ ] Run `aging_narrative_complete_analysis.py`
- [ ] Verify output files generated
- [ ] Review `aging_narratives_summary.txt`
- [ ] Open `aging_narratives_coding_sample.csv`
- [ ] Study `decolonial_analysis_framework.py`
- [ ] Code sample articles (30-90 articles)
- [ ] Run `aging_narrative_visualizations.py`
- [ ] Review all visualizations
- [ ] Read `analysis_summary_stats.txt`
- [ ] Write findings section
- [ ] Apply decolonial analysis
- [ ] Draft implications and recommendations

---

## 🎓 Citation

If using this analysis framework, please cite:

```
Aging Narratives Analysis: A Decolonial Discourse Study of Media Coverage (2023)
Media Cloud API. Data collection: [Date]
Decolonial framework adapted from Indigenous and critical gerontology scholarship
```

---

## 📄 License

Research use permitted. Educational and non-commercial analysis encouraged.
For Media Cloud data terms of use, see: https://mediacloud.org/

---

**Good luck with your analysis! This is important work for decolonizing aging discourse.**

---

## 🚀 Quick Command Reference

```bash
# Install dependencies
pip install mediacloud pandas matplotlib seaborn

# Run complete data collection
python aging_narrative_complete_analysis.py

# After manual coding, generate visualizations
python aging_narrative_visualizations.py

# View the coding framework
python decolonial_analysis_framework.py
```

**Output files to keep:**
- All CSV and JSON files (your raw data)
- All PNG visualizations (for presentations/papers)
- aging_narratives_coding_sample.csv (your coded work - back this up!)
