"""
Clean Dataset - Filter & Label Articles

This script:
1. Filters mergedData.csv to keep ONLY articles about aging/longevity/seniors
2. Labels each relevant article as empowering/limiting/neutral

Both tasks are done in ONE API call for cost efficiency.

Output: Cleaned dataset with only relevant articles + sentiment labels
"""

import pandas as pd
import time
import os
from openai import OpenAI

# ============================================
# CONFIGURATION
# ============================================
INPUT_FILE = r'c:\Users\Suha\Desktop\Suha\ML\longevityLab\newData\cleanData\mergedData.csv'
OUTPUT_FILE = r'c:\Users\Suha\Desktop\Suha\ML\longevityLab\newData\cleanData\mergedData_cleaned.csv'
PROGRESS_FILE = r'c:\Users\Suha\Desktop\Suha\ML\longevityLab\newData\cleanData\cleaning_progress.csv'

# OpenAI API Key
API_KEY = "..."

# ============================================
# BATCH CONTROL - CHANGE THIS FOR EACH RUN
# ============================================
# Run 1: BATCH_NUMBER = 1  (articles 0-4999)
# Run 2: BATCH_NUMBER = 2  (articles 5000-9999)
# Run 3: BATCH_NUMBER = 3  (articles 10000-14999)
# Run 4: BATCH_NUMBER = 4  (articles 15000-19999)
# Run 5: BATCH_NUMBER = 5  (articles 20000-24999)
# Run 6: BATCH_NUMBER = 6  (articles 25000-29999)
# Run 7: BATCH_NUMBER = 7  (articles 30000-34325)

BATCH_NUMBER = 7  # <-- CHANGE THIS FOR EACH RUN (1-7)
ARTICLES_PER_RUN = 5000

# Processing settings
BATCH_SIZE = 10  # Articles per API call
SAVE_EVERY = 100  # Save progress every N articles
MAX_WORDS = 250  # Max words from article to send to GPT

# ============================================
# INITIALIZE
# ============================================
print("=" * 60)
print("DATASET CLEANING - RELEVANCE FILTER")
print("=" * 60)

client = OpenAI(api_key=API_KEY)

# ============================================
# LOAD DATA
# ============================================
print("\nStep 1: Loading data...")
df = pd.read_csv(INPUT_FILE)
print(f"Total articles: {len(df):,}")

# Check for existing progress
if os.path.exists(PROGRESS_FILE):
    print(f"\nFound existing progress file: {PROGRESS_FILE}")
    df_progress = pd.read_csv(PROGRESS_FILE)

    # Merge progress with main dataframe
    if 'is_relevant' in df_progress.columns:
        already_processed = len(df_progress[df_progress['is_relevant'].notna()])
        print(f"  Already processed: {already_processed:,} articles")

        # Update main df with progress
        df['is_relevant'] = df_progress['is_relevant'] if 'is_relevant' in df_progress.columns else None
        df['rejection_reason'] = df_progress['rejection_reason'] if 'rejection_reason' in df_progress.columns else ''
        df['ai_label'] = df_progress['ai_label'] if 'ai_label' in df_progress.columns else ''
        df['confidence'] = df_progress['confidence'] if 'confidence' in df_progress.columns else ''
else:
    df['is_relevant'] = None
    df['rejection_reason'] = ''
    df['ai_label'] = ''
    df['confidence'] = ''

# ============================================
# VERIFICATION + LABELING FUNCTION (COMBINED)
# ============================================
def verify_and_label_articles_batch(articles_batch):
    """
    Verify if articles are about aging/longevity/seniors AND label sentiment.
    Does both tasks in ONE API call for cost efficiency.

    Returns list of (is_relevant, reason, label, confidence) tuples
    """

    articles_text = ""
    for i, (_, row) in enumerate(articles_batch.iterrows()):
        title = str(row['title'])[:100] if pd.notna(row['title']) else "No title"
        text = str(row['article_text']) if pd.notna(row['article_text']) else ""
        snippet = " ".join(text.split()[:MAX_WORDS])
        articles_text += f"\nArticle {i+1}:\nTitle: {title}\nText: {snippet}...\n---\n"

    prompt = f"""You are classifying news articles for relevance to aging, older adults, or longevity.

**RELEVANCE RULES:**

**YES (Relevant) if ANY of the following are TRUE:**
1. The **main topic** is about older adults (60+), aging population issues, longevity science, senior care, pensions, ageism, or elder health.
2. Older adults are a **primary affected group** in the story (e.g., disaster impact on elderly, healthcare crisis due to aging population, policy change affecting seniors).
3. **Aging demographics or senior welfare** is a substantial part of the analysis, not just a passing mention.
4. The article **focuses on longevity** (research, life extension, anti-aging science).

**NO (Not Relevant) if:**
1. Older adults are mentioned only in passing (e.g., "including seniors" in a list, age given for a victim without broader context).
2. "Aging" refers only to **infrastructure, products, or non-human subjects** (e.g., aging subway, aging wine).
3. The article is primarily about **general news** (politics, sports, entertainment, accidents) and aging/seniors are incidental.

**IMPORTANT GUIDELINES:**
- If "seniors" or "aging population" is cited as a **key driver or major factor** (e.g., "aging population strains hospitals"), mark as RELEVANT.
- If an article about a disaster or system failure **highlights older adults as a vulnerable/rescued group** and discusses their situation substantively, mark as RELEVANT.
- When in doubt, consider: "Would someone researching aging issues find this article useful?" If yes, lean toward YES.

**SENTIMENT (Only if RELEVANT = YES):**
- **EMPOWERING:** Positive portrayal (active, contributing, resilient seniors; opportunities in aging).
- **LIMITING:** Negative portrayal (burden, decline, crisis, vulnerability, age as problem).
- **NEUTRAL:** Factual, balanced, or mixed portrayal without clear positive/negative framing.

For each article below, respond with EXACTLY this format:
RELEVANT: YES or NO
REASON: Brief reason (10 words max)
LABEL: EMPOWERING / LIMITING / NEUTRAL (or N/A if not relevant)
CONFIDENCE: HIGH / MEDIUM / LOW

{articles_text}

Respond for each article in order:"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=2000
        )

        result = response.choices[0].message.content.strip()
        lines = result.split('\n')

        results = []
        current_relevant = None
        current_reason = ""
        current_label = ""
        current_confidence = ""

        for line in lines:
            line_stripped = line.strip()
            line_upper = line_stripped.upper()

            if 'RELEVANT:' in line_upper:
                current_relevant = 'YES' in line_upper

            elif 'REASON:' in line_upper:
                current_reason = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ""

            elif 'LABEL:' in line_upper:
                if 'EMPOWERING' in line_upper:
                    current_label = 'empowering'
                elif 'LIMITING' in line_upper:
                    current_label = 'limiting'
                elif 'NEUTRAL' in line_upper:
                    current_label = 'neutral'
                else:
                    current_label = ''

            elif 'CONFIDENCE:' in line_upper:
                if 'HIGH' in line_upper:
                    current_confidence = 0.9
                elif 'MEDIUM' in line_upper:
                    current_confidence = 0.7
                elif 'LOW' in line_upper:
                    current_confidence = 0.5
                else:
                    current_confidence = ''

                # When we have all fields, save and reset
                if current_relevant is not None:
                    results.append((current_relevant, current_reason, current_label, current_confidence))
                    current_relevant = None
                    current_reason = ""
                    current_label = ""
                    current_confidence = ""

        # Fill missing results
        while len(results) < len(articles_batch):
            results.append((True, "Unable to verify", "neutral", 0.5))

        return results[:len(articles_batch)]

    except Exception as e:
        print(f"\n    [ERROR] API call failed: {e}")
        return [(True, f"Error: {str(e)[:30]}", "neutral", 0.5)] * len(articles_batch)


# ============================================
# PROCESS ARTICLES FOR THIS BATCH
# ============================================
print("\nStep 2: Verifying article relevance...")
print("-" * 60)

# Calculate range for this batch
start_idx = (BATCH_NUMBER - 1) * ARTICLES_PER_RUN
end_idx = min(BATCH_NUMBER * ARTICLES_PER_RUN, len(df))

print(f"BATCH {BATCH_NUMBER}: Processing articles {start_idx:,} to {end_idx-1:,}")
print("-" * 60)

# Get indices of articles in this batch that need processing
batch_range = df.iloc[start_idx:end_idx].index.tolist()
needs_processing = [idx for idx in batch_range if pd.isna(df.at[idx, 'is_relevant'])]
total_to_process = len(needs_processing)

print(f"Articles to process: {total_to_process:,}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Estimated API calls: {(total_to_process + BATCH_SIZE - 1) // BATCH_SIZE:,}")
print("-" * 60)

processed_count = 0
relevant_count = df['is_relevant'].sum() if df['is_relevant'].notna().any() else 0
rejected_count = len(df) - total_to_process - relevant_count if relevant_count else 0

start_time = time.time()

try:
    for i in range(0, total_to_process, BATCH_SIZE):
        batch_indices = needs_processing[i:i+BATCH_SIZE]
        batch = df.loc[batch_indices]

        # Verify AND label batch in one API call
        results = verify_and_label_articles_batch(batch)

        # Update dataframe
        for j, idx in enumerate(batch_indices):
            is_relevant, reason, label, confidence = results[j]
            df.at[idx, 'is_relevant'] = is_relevant
            df.at[idx, 'rejection_reason'] = reason if not is_relevant else ''
            df.at[idx, 'ai_label'] = label if is_relevant else ''
            df.at[idx, 'confidence'] = confidence if is_relevant else ''

            if is_relevant:
                relevant_count += 1
            else:
                rejected_count += 1

        processed_count += len(batch_indices)

        # Progress update
        elapsed = time.time() - start_time
        rate = processed_count / elapsed if elapsed > 0 else 0
        remaining = (total_to_process - processed_count) / rate if rate > 0 else 0

        # Calculate percentages
        total_processed = relevant_count + rejected_count
        relevant_pct = (relevant_count / total_processed * 100) if total_processed > 0 else 0

        print(f"  Processed {processed_count:,}/{total_to_process:,} | "
              f"Relevant: {relevant_count:,} ({relevant_pct:.1f}%) | "
              f"Rejected: {rejected_count:,} | "
              f"ETA: {remaining/60:.1f} min")

        # Save progress periodically
        if processed_count % SAVE_EVERY == 0:
            df.to_csv(PROGRESS_FILE, index=False)
            print(f"    [Progress saved]")

        # Small delay to avoid rate limiting
        time.sleep(0.3)

except KeyboardInterrupt:
    print("\n\n[INTERRUPTED] Saving progress...")
    df.to_csv(PROGRESS_FILE, index=False)
    print(f"Progress saved to: {PROGRESS_FILE}")
    print("Run the script again to resume.")
    exit(0)

# ============================================
# SAVE PROGRESS
# ============================================
print("\n" + "-" * 60)
print("Step 3: Saving progress...")
print("-" * 60)

# Save progress file
df.to_csv(PROGRESS_FILE, index=False)

# ============================================
# SUMMARY FOR THIS BATCH
# ============================================
# Count totals across all processed articles
total_processed = df['is_relevant'].notna().sum()
total_relevant = (df['is_relevant'] == True).sum()
total_rejected = (df['is_relevant'] == False).sum()
total_remaining = len(df) - total_processed

print(f"\n{'=' * 60}")
print(f"BATCH {BATCH_NUMBER} COMPLETE!")
print(f"{'=' * 60}")

print(f"\nThis batch:")
print(f"  Processed: {processed_count:,} articles")
print(f"  Relevant:  {relevant_count:,}")
print(f"  Rejected:  {rejected_count:,}")

print(f"\nOverall progress:")
print(f"  Total processed: {total_processed:,} / {len(df):,} ({total_processed/len(df)*100:.1f}%)")
print(f"  Total relevant:  {total_relevant:,} ({total_relevant/total_processed*100:.1f}% of processed)")
print(f"  Total rejected:  {total_rejected:,}")
print(f"  Remaining:       {total_remaining:,}")

print(f"\nProgress saved to: {PROGRESS_FILE}")

# Show label distribution for this batch
batch_labels = df.iloc[start_idx:end_idx][df.iloc[start_idx:end_idx]['is_relevant'] == True]['ai_label']
if len(batch_labels) > 0:
    print(f"\nLabel distribution (this batch):")
    print(f"  {batch_labels.value_counts().to_dict()}")

# Check if all batches are complete
if total_remaining == 0:
    print(f"\n{'=' * 60}")
    print("ALL BATCHES COMPLETE! Creating final cleaned dataset...")
    print(f"{'=' * 60}")

    # Filter to only relevant articles
    df_clean = df[df['is_relevant'] == True].copy()

    # Remove the verification columns for clean output (keep ai_label and confidence)
    df_clean = df_clean.drop(columns=['is_relevant', 'rejection_reason'], errors='ignore')

    # Save cleaned dataset
    df_clean.to_csv(OUTPUT_FILE, index=False)

    print(f"\nFinal Results:")
    print(f"  Original articles:  {len(df):,}")
    print(f"  Relevant articles:  {len(df_clean):,} ({len(df_clean)/len(df)*100:.1f}%)")
    print(f"  Removed articles:   {len(df) - len(df_clean):,}")

    print(f"\nLabel distribution (all relevant articles):")
    print(f"  {df_clean['ai_label'].value_counts().to_dict()}")

    print(f"\nCleaned dataset saved to: {OUTPUT_FILE}")
else:
    print(f"\n{'=' * 60}")
    print("NEXT STEP:")
    print(f"{'=' * 60}")
    print(f"  1. Open clean_dataset_relevance.py")
    print(f"  2. Change BATCH_NUMBER = {BATCH_NUMBER} to BATCH_NUMBER = {BATCH_NUMBER + 1}")
    print(f"  3. Run the script again")
    print(f"{'=' * 60}")

# Show some rejection reasons from this batch
batch_rejected = df.iloc[start_idx:end_idx][df.iloc[start_idx:end_idx]['is_relevant'] == False]
if len(batch_rejected) > 0:
    print("\nSample rejection reasons from this batch:")
    for _, row in batch_rejected.head(5).iterrows():
        title = str(row['title'])[:50] if pd.notna(row['title']) else "No title"
        reason = row['rejection_reason']
        print(f"  - \"{title}...\" -> {reason}")
