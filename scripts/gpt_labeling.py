"""
GPT-3.5 Sentiment Labeling for Aging Narratives Articles

This script:
1. Loads the 1,000 sampled articles
2. Uses GPT-3.5 to classify each article as empowering/limiting/neutral
3. Saves results with ai_label and confidence columns

Output: Updated CSV with ai_label and confidence filled in
"""

import pandas as pd 
import time
from openai import OpenAI

# ============================================
# CONFIGURATION
# ============================================
INPUT_FILE = r'c:\Users\Suha\Desktop\Suha\ML\longevityLab\newData\cleanData\labeling_sample_1000.csv'
OUTPUT_FILE = r'c:\Users\Suha\Desktop\Suha\ML\longevityLab\newData\cleanData\labeling_sample_1000_labeled.csv'

# OpenAI API Key (hardcoded for one-time use)
# WARNING: Remove this key before committing to git!
API_KEY = "..."

# Processing settings
BATCH_SIZE = 5  # Articles per API call
SAVE_EVERY = 50  # Save progress every N articles
MAX_WORDS = 300  # Max words from article to send to GPT

# ============================================
# INITIALIZE
# ============================================
print("=" * 60)
print("GPT-3.5 SENTIMENT LABELING")
print("=" * 60)

client = OpenAI(api_key=API_KEY)

# Load data
print("\nStep 1: Loading data...")
df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df)} articles")

# Check for existing labels (to resume if interrupted)
if 'ai_label' not in df.columns:
    df['ai_label'] = None
if 'confidence' not in df.columns:
    df['confidence'] = None

# Count already labeled (non-empty, non-NaN)
already_labeled = df['ai_label'].notna() & (df['ai_label'] != '')
n_labeled = already_labeled.sum()
if n_labeled > 0:
    print(f"  Found {n_labeled} already labeled articles - will skip these")

# ============================================
# LABELING FUNCTION
# ============================================
def label_articles_batch(articles_batch):
    """
    Send a batch of articles to GPT-3.5 for sentiment labeling.

    Returns list of (label, confidence) tuples
    """

    # Build the prompt
    articles_text = ""
    for i, row in enumerate(articles_batch):
        # Get first N words of article
        text = str(row['article_text'])
        words = text.split()[:MAX_WORDS]
        snippet = " ".join(words)

        title = str(row['title'])[:100] if pd.notna(row['title']) else "No title"

        articles_text += f"""
Article {i+1}:
Title: {title}
Text: {snippet}...
---
"""

    prompt = f"""You are analyzing news articles about aging and older adults.

For each article, classify the overall narrative/framing as:
- **empowering**: Portrays aging/older adults positively (active, wise, contributing, opportunities)
- **limiting**: Portrays aging/older adults negatively (burden, crisis, decline, problems)
- **neutral**: Balanced or factual reporting without strong positive/negative framing

For each article, respond with ONLY:
LABEL: [empowering/limiting/neutral]
CONFIDENCE: [high/medium/low]

{articles_text}

Respond for each article in order (Article 1, Article 2, etc.):"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500
        )

        result = response.choices[0].message.content.strip()

        # Parse the response
        labels = []
        lines = result.split('\n')

        current_label = None
        current_confidence = None

        for line in lines:
            line = line.strip().upper()

            if 'LABEL:' in line:
                if 'EMPOWERING' in line:
                    current_label = 'empowering'
                elif 'LIMITING' in line:
                    current_label = 'limiting'
                else:
                    current_label = 'neutral'

            elif 'CONFIDENCE:' in line:
                if 'HIGH' in line:
                    current_confidence = 0.9
                elif 'MEDIUM' in line:
                    current_confidence = 0.7
                else:
                    current_confidence = 0.5

                # When we have both, save and reset
                if current_label is not None:
                    labels.append((current_label, current_confidence))
                    current_label = None
                    current_confidence = None

        # If we didn't get enough labels, fill with defaults
        while len(labels) < len(articles_batch):
            labels.append(('neutral', 0.5))

        return labels[:len(articles_batch)]

    except Exception as e:
        print(f"    [ERROR] API call failed: {e}")
        return [('neutral', 0.5)] * len(articles_batch)

# ============================================
# PROCESS ARTICLES
# ============================================
print("\nStep 2: Labeling articles with GPT-3.5...")
print("-" * 60)

# Get indices of articles that need labeling (empty or NaN)
needs_labeling = df[df['ai_label'].isna() | (df['ai_label'] == '')].index.tolist()
total_to_label = len(needs_labeling)

print(f"Articles to label: {total_to_label}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Estimated API calls: {(total_to_label + BATCH_SIZE - 1) // BATCH_SIZE}")
print("-" * 60)

labeled_count = 0
start_time = time.time()

for i in range(0, total_to_label, BATCH_SIZE):
    batch_indices = needs_labeling[i:i+BATCH_SIZE]
    batch_data = [df.loc[idx] for idx in batch_indices]

    # Get labels from GPT
    labels = label_articles_batch(batch_data)

    # Update dataframe
    for j, idx in enumerate(batch_indices):
        df.at[idx, 'ai_label'] = labels[j][0]
        df.at[idx, 'confidence'] = labels[j][1]

    labeled_count += len(batch_indices)

    # Progress update
    elapsed = time.time() - start_time
    rate = labeled_count / elapsed if elapsed > 0 else 0
    remaining = (total_to_label - labeled_count) / rate if rate > 0 else 0

    print(f"  Labeled {labeled_count}/{total_to_label} articles "
          f"({labeled_count/total_to_label*100:.1f}%) - "
          f"ETA: {remaining/60:.1f} min")

    # Save progress periodically
    if labeled_count % SAVE_EVERY == 0:
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"    [Saved progress to {OUTPUT_FILE}]")

    # Small delay to avoid rate limiting
    time.sleep(0.5)

# ============================================
# FINAL SAVE
# ============================================
print("\n" + "-" * 60)
print("Step 3: Saving final results...")
print("-" * 60)

df.to_csv(OUTPUT_FILE, index=False)

# ============================================
# SUMMARY
# ============================================
print(f"\n{'=' * 60}")
print("LABELING COMPLETE!")
print(f"{'=' * 60}")

print(f"\nResults saved to: {OUTPUT_FILE}")

print("\nLabel distribution:")
print(df['ai_label'].value_counts().to_dict())

print("\nConfidence distribution:")
confidence_counts = df['confidence'].value_counts().to_dict()
print(confidence_counts)

# Compare with original phrase_category
if 'phrase_category_clean' in df.columns:
    print("\nComparison with original phrase_category_clean:")
    match = (df['ai_label'] == df['phrase_category_clean']).mean() * 100
    print(f"  Match rate: {match:.1f}%")

    print("\n  Cross-tabulation:")
    cross_tab = pd.crosstab(df['phrase_category_clean'], df['ai_label'], margins=True)
    print(cross_tab)

print(f"\n{'=' * 60}")
print("NEXT STEPS:")
print(f"{'=' * 60}")
print("1. Review the labeled articles in the CSV")
print("2. Fill 'human_label' column with your corrections")
print("3. Use 'human_label' as ground truth for fine-tuning")
print(f"{'=' * 60}")
