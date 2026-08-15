"""
Smart Stratified Sampling for Sentiment Analysis Labeling

This script:
1. Analyzes topics in the dataset using GPT-3.5
2. Selects articles using multi-dimensional stratified sampling:
   - Time distribution (publish_date)
   - Text length variation
   - Source diversity (media_name)
   - Phrase category balance
3. Verifies each article is truly about aging/longevity/seniors using GPT-3.5
   - Rejects articles that mention "aging" but aren't about older people
   - Replaces rejected articles with new ones from the pool
4. Classifies articles into topics

Output: CSV file with 1,000 verified articles ready for labeling
"""

import pandas as pd
import numpy as np
from openai import OpenAI

# ============================================
# CONFIGURATION
# ============================================
INPUT_FILE = r'c:\Users\Suha\Desktop\Suha\ML\longevityLab\newData\cleanData\mergedData.csv'
OUTPUT_FILE = r'c:\Users\Suha\Desktop\Suha\ML\longevityLab\newData\cleanData\labeling_sample_1000.csv'
SAMPLE_SIZE = 1000
RANDOM_STATE = 42

# OpenAI API Key (hardcoded for one-time use)
# WARNING: Remove this key before committing to git!
API_KEY = "..."

# ============================================
# LOAD DATA
# ============================================
print("=" * 60)
print("SMART STRATIFIED SAMPLING")
print("=" * 60)

print("\nStep 1: Loading data...")
df = pd.read_csv(INPUT_FILE)
print(f"Total articles: {len(df):,}")

# ============================================
# STEP 1: TOPIC ANALYSIS WITH GPT-3.5
# ============================================
print("\n" + "-" * 60)
print("Step 2: Analyzing topics with GPT-3.5...")
print("-" * 60)

def analyze_topics_gpt(df, sample_size=500):
    """Use GPT-3.5 to identify main topics in the dataset"""

    if API_KEY is None:
        print("  [SKIPPED] No OpenAI API key provided")
        print("  Set OPENAI_API_KEY environment variable or edit API_KEY in script")
        return None

    client = OpenAI(api_key=API_KEY)

    # Sample articles for topic analysis
    sample_df = df.sample(min(sample_size, len(df)), random_state=RANDOM_STATE)

    # Get snippets from article_text (first 200 words each)
    def get_snippet(text, max_words=200):
        if pd.isna(text):
            return ""
        words = str(text).split()[:max_words]
        return " ".join(words)

    snippets = sample_df['article_text'].apply(get_snippet).tolist()[:50]  # 50 articles
    articles_text = "\n---\n".join(snippets)

    topics_prompt = f"""
    Analyze these aging/longevity news article snippets. Identify the 5-7 most common topics or themes.

    Articles: {articles_text[:4000]}

    Return as a numbered list:
    1. Topic name - brief description
    2. Topic name - brief description
    ...
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": topics_prompt}],
            temperature=0,
            max_tokens=500
        )

        topics = response.choices[0].message.content
        print("\n  Main topics identified:")
        print("  " + topics.replace("\n", "\n  "))
        return topics

    except Exception as e:
        print(f"  [ERROR] GPT analysis failed: {e}")
        return None

# Run topic analysis
topics = analyze_topics_gpt(df)

def verify_article_relevance(client, articles_batch):
    """
    Verify that articles are truly about aging/longevity/senior people.

    Returns list of (is_relevant, reason) tuples
    """
    articles_text = ""
    for i, (_, row) in enumerate(articles_batch.iterrows()):
        title = str(row['title'])[:100] if pd.notna(row['title']) else "No title"
        snippet = " ".join(str(row['article_text']).split()[:200])
        articles_text += f"\nArticle {i+1}:\nTitle: {title}\nText: {snippet}...\n---\n"

    prompt = f"""You are verifying if news articles are related to aging, longevity, or senior/older people.

An article is RELEVANT if it:
- Mentions senior citizens, older adults, elderly, retirees, or aging population
- Discusses topics affecting older people (health, retirement, care, etc.)
- Talks about longevity, life expectancy, or aging demographics
- Mentions aging in a human/biological context
- Has ANY connection to older people or human aging

An article is NOT RELEVANT only if:
- "Aging" refers to non-human things (aging wine, aging cheese, aging infrastructure, aging buildings, aging technology, aging equipment)
- The article has ZERO connection to older people or human aging

Be LENIENT - if there's any reasonable connection to older people or human aging, mark it as RELEVANT.

For each article, respond with ONLY:
RELEVANT: YES or NO
REASON: Brief explanation (10 words max)

{articles_text}

Respond for each article in order:"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1000
        )

        result = response.choices[0].message.content.strip()
        lines = result.split('\n')

        results = []
        current_relevant = None
        current_reason = ""

        for line in lines:
            line_upper = line.strip().upper()

            if 'RELEVANT:' in line_upper:
                current_relevant = 'YES' in line_upper

            elif 'REASON:' in line.strip():
                current_reason = line.split(':', 1)[1].strip() if ':' in line else ""

                if current_relevant is not None:
                    results.append((current_relevant, current_reason))
                    current_relevant = None
                    current_reason = ""

        # Fill missing results
        while len(results) < len(articles_batch):
            results.append((True, "Unable to verify"))

        return results[:len(articles_batch)]

    except Exception as e:
        print(f"    [ERROR] Verification failed: {e}")
        return [(True, "Error - assumed relevant")] * len(articles_batch)


def classify_article_topic(client, articles_batch, topics_list):
    """Classify a batch of articles into topics using GPT-3.5"""

    articles_text = ""
    for i, (_, row) in enumerate(articles_batch.iterrows()):
        snippet = " ".join(str(row['article_text']).split()[:150])  # First 150 words
        articles_text += f"\nArticle {i+1}: {snippet[:500]}...\n"

    prompt = f"""
Given these topics:
{topics_list}

Classify each article into ONE of the above topics. Return ONLY the topic name for each article, one per line.

{articles_text}

Return format (one topic per line, matching article order):
Topic for Article 1
Topic for Article 2
...
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500
        )

        result = response.choices[0].message.content.strip()
        topics_assigned = result.split('\n')
        return [t.strip() for t in topics_assigned]

    except Exception as e:
        print(f"    [ERROR] Classification failed: {e}")
        return ['unknown'] * len(articles_batch)

# ============================================
# STEP 2: PREPARE STRATIFICATION DIMENSIONS
# ============================================
print("\n" + "-" * 60)
print("Step 3: Preparing stratification dimensions...")
print("-" * 60)

# Create a working copy
df_work = df.copy()

# Dimension 1: Time periods (from publish_date)
if 'publish_date' in df_work.columns:
    df_work['publish_date'] = pd.to_datetime(df_work['publish_date'], errors='coerce')
    df_work = df_work.sort_values('publish_date')

    # Create time period bins (10 equal periods)
    df_work['time_period'] = pd.qcut(
        df_work['publish_date'].rank(method='first'),
        q=10,
        labels=[f'period_{i}' for i in range(10)]
    )
    print(f"  ✓ Time periods: 10 equal periods based on publish_date")
else:
    df_work['time_period'] = 'unknown'
    print("  ✗ No publish_date column found")

# Dimension 2: Text length categories
df_work['word_count'] = df_work['article_text'].apply(
    lambda x: len(str(x).split()) if pd.notna(x) else 0
)

df_work['length_category'] = pd.qcut(
    df_work['word_count'].rank(method='first'),
    q=5,
    labels=['very_short', 'short', 'medium', 'long', 'very_long']
)
print(f"  ✓ Length categories: {df_work['length_category'].value_counts().to_dict()}")

# Dimension 3: Source diversity (media_name)
if 'media_name' in df_work.columns:
    # Get top 10 sources, group others as 'other'
    top_sources = df_work['media_name'].value_counts().head(10).index.tolist()
    df_work['source_group'] = df_work['media_name'].apply(
        lambda x: x if x in top_sources else 'other'
    )
    print(f"  ✓ Source groups: {len(df_work['source_group'].unique())} groups")
else:
    df_work['source_group'] = 'unknown'
    print("  ✗ No media_name column found")

# Dimension 4: Phrase category (existing)
if 'phrase_category_clean' in df_work.columns:
    print(f"  ✓ Phrase categories: {df_work['phrase_category_clean'].value_counts().to_dict()}")
else:
    df_work['phrase_category_clean'] = 'unknown'
    print("  ✗ No phrase_category_clean column found")

# ============================================
# STEP 3: SMART STRATIFIED SAMPLING
# ============================================
print("\n" + "-" * 60)
print("Step 4: Performing smart stratified sampling...")
print("-" * 60)

def smart_stratified_sample(df, target_size=1000, random_state=42):
    """
    Multi-dimensional stratified sampling to ensure diversity across:
    - Phrase category (primary)
    - Time period
    - Text length
    - Source
    """
    np.random.seed(random_state)

    # Primary stratification: phrase_category_clean
    # This ensures we maintain the original distribution
    categories = df['phrase_category_clean'].unique()
    category_counts = df['phrase_category_clean'].value_counts(normalize=True)

    sampled_indices = []

    for category in categories:
        # Number of samples for this category (proportional)
        n_category = int(target_size * category_counts[category])

        # Get articles in this category
        category_df = df[df['phrase_category_clean'] == category]

        # Secondary stratification: time period
        time_periods = category_df['time_period'].unique()
        n_per_time = max(1, n_category // len(time_periods))

        for time_period in time_periods:
            time_df = category_df[category_df['time_period'] == time_period]

            if len(time_df) == 0:
                continue

            # Tertiary stratification: length category
            length_cats = time_df['length_category'].unique()
            n_per_length = max(1, n_per_time // len(length_cats))

            for length_cat in length_cats:
                length_df = time_df[time_df['length_category'] == length_cat]

                if len(length_df) == 0:
                    continue

                # Sample from this stratum
                n_sample = min(n_per_length, len(length_df))
                if n_sample > 0:
                    sampled = length_df.sample(n_sample, random_state=random_state)
                    sampled_indices.extend(sampled.index.tolist())

    # Remove duplicates
    sampled_indices = list(set(sampled_indices))

    # If we have fewer than target, add more randomly
    if len(sampled_indices) < target_size:
        remaining = df[~df.index.isin(sampled_indices)]
        n_additional = target_size - len(sampled_indices)

        if len(remaining) >= n_additional:
            additional = remaining.sample(n_additional, random_state=random_state)
            sampled_indices.extend(additional.index.tolist())

    # If we have more than target, randomly select
    if len(sampled_indices) > target_size:
        sampled_indices = np.random.choice(sampled_indices, target_size, replace=False).tolist()

    return df.loc[sampled_indices].copy()

# Perform initial sampling (get extra articles for replacements)
INITIAL_SAMPLE_SIZE = int(SAMPLE_SIZE * 1.3)  # 30% extra for potential rejections
df_sample = smart_stratified_sample(df_work, target_size=INITIAL_SAMPLE_SIZE, random_state=RANDOM_STATE)

print(f"\n  Initial sample: {len(df_sample):,} articles")

# ============================================
# STEP 4: VERIFY ARTICLE RELEVANCE
# ============================================
print("\n" + "-" * 60)
print("Step 5: Verifying article relevance with GPT-3.5...")
print("-" * 60)
print("  Checking if articles are truly about aging/longevity/seniors...")

if API_KEY is not None:
    client = OpenAI(api_key=API_KEY)

    # Track verification results
    df_sample['is_relevant'] = None
    df_sample['rejection_reason'] = ''

    # Process in batches of 10
    batch_size = 10
    verified_count = 0
    rejected_count = 0

    indices = df_sample.index.tolist()

    for i in range(0, len(indices), batch_size):
        batch_indices = indices[i:i+batch_size]
        batch = df_sample.loc[batch_indices]

        results = verify_article_relevance(client, batch)

        for j, idx in enumerate(batch_indices):
            is_relevant, reason = results[j]
            df_sample.at[idx, 'is_relevant'] = is_relevant
            df_sample.at[idx, 'rejection_reason'] = reason

            if is_relevant:
                verified_count += 1
            else:
                rejected_count += 1

        print(f"  Verified {min(i+batch_size, len(indices))}/{len(indices)} - "
              f"Relevant: {verified_count}, Rejected: {rejected_count}")

    # Filter to only relevant articles
    df_relevant = df_sample[df_sample['is_relevant'] == True].copy()

    print(f"\n  Verification complete:")
    print(f"    Relevant articles: {len(df_relevant)}")
    print(f"    Rejected articles: {rejected_count}")

    # If we don't have enough, sample more from remaining pool
    if len(df_relevant) < SAMPLE_SIZE:
        print(f"\n  Need {SAMPLE_SIZE - len(df_relevant)} more articles...")

        # Get indices already used
        used_indices = set(df_sample.index.tolist())
        remaining_pool = df_work[~df_work.index.isin(used_indices)]

        if len(remaining_pool) > 0:
            # Sample additional articles
            n_needed = min(SAMPLE_SIZE - len(df_relevant), len(remaining_pool))
            additional = remaining_pool.sample(n_needed, random_state=RANDOM_STATE + 1)

            # Verify additional articles
            print(f"  Verifying {len(additional)} additional articles...")
            additional['is_relevant'] = None
            additional['rejection_reason'] = ''

            add_indices = additional.index.tolist()
            for i in range(0, len(add_indices), batch_size):
                batch_indices = add_indices[i:i+batch_size]
                batch = additional.loc[batch_indices]
                results = verify_article_relevance(client, batch)

                for j, idx in enumerate(batch_indices):
                    is_relevant, reason = results[j]
                    additional.at[idx, 'is_relevant'] = is_relevant
                    additional.at[idx, 'rejection_reason'] = reason

            # Add relevant additional articles
            additional_relevant = additional[additional['is_relevant'] == True]
            df_relevant = pd.concat([df_relevant, additional_relevant])

            print(f"  Added {len(additional_relevant)} more relevant articles")

    # Trim to exact sample size
    if len(df_relevant) > SAMPLE_SIZE:
        df_relevant = df_relevant.head(SAMPLE_SIZE)

    df_sample = df_relevant.copy()
    print(f"\n  Final verified sample: {len(df_sample)} articles")

    # Show rejection reasons
    if rejected_count > 0:
        print(f"\n  Sample rejection reasons:")
        rejected = df_sample[df_sample['is_relevant'] == False] if 'is_relevant' in df_sample.columns else pd.DataFrame()
        # Get from original sample before filtering
        original_rejected = df_work.loc[df_work.index.isin(
            [idx for idx in indices if df_sample.get('is_relevant', {}).get(idx) == False]
        )] if len(indices) > 0 else pd.DataFrame()

else:
    print("  [SKIPPED] No API key - skipping verification")
    df_sample['is_relevant'] = True
    df_sample['rejection_reason'] = ''
    if len(df_sample) > SAMPLE_SIZE:
        df_sample = df_sample.head(SAMPLE_SIZE)

print(f"\n  Final sample size: {len(df_sample)} articles")

# ============================================
# STEP 6: VALIDATE SAMPLE DIVERSITY
# ============================================
print("\n" + "-" * 60)
print("Step 6: Validating sample diversity...")
print("-" * 60)

print("\n  Phrase category distribution:")
print("    Original:", df_work['phrase_category_clean'].value_counts(normalize=True).round(3).to_dict())
print("    Sample:  ", df_sample['phrase_category_clean'].value_counts(normalize=True).round(3).to_dict())

print("\n  Time period coverage:")
original_periods = df_work['time_period'].nunique()
sample_periods = df_sample['time_period'].nunique()
print(f"    Original: {original_periods} periods")
print(f"    Sample:   {sample_periods} periods ({sample_periods/original_periods*100:.0f}% coverage)")

print("\n  Length category distribution:")
print("    Original:", df_work['length_category'].value_counts(normalize=True).round(3).to_dict())
print("    Sample:  ", df_sample['length_category'].value_counts(normalize=True).round(3).to_dict())

print("\n  Source diversity:")
original_sources = df_work['source_group'].nunique()
sample_sources = df_sample['source_group'].nunique()
print(f"    Original: {original_sources} source groups")
print(f"    Sample:   {sample_sources} source groups ({sample_sources/original_sources*100:.0f}% coverage)")

# ============================================
# STEP 7: CLASSIFY ARTICLES INTO TOPICS
# ============================================
print("\n" + "-" * 60)
print("Step 7: Classifying articles into topics with GPT-3.5...")
print("-" * 60)

if topics is not None and API_KEY is not None:
    client = OpenAI(api_key=API_KEY)

    # Process in batches of 10 articles
    batch_size = 10
    all_topics = []

    for i in range(0, len(df_sample), batch_size):
        batch = df_sample.iloc[i:i+batch_size]
        batch_topics = classify_article_topic(client, batch, topics)

        # Ensure we have the right number of topics
        while len(batch_topics) < len(batch):
            batch_topics.append('unknown')

        all_topics.extend(batch_topics[:len(batch)])

        print(f"  Classified {min(i+batch_size, len(df_sample))}/{len(df_sample)} articles...")

    df_sample['topic'] = all_topics
    print(f"\n  Topic distribution:")
    print(f"    {df_sample['topic'].value_counts().to_dict()}")
else:
    df_sample['topic'] = 'unknown'
    print("  [SKIPPED] No topics available - topic column set to 'unknown'")

# ============================================
# STEP 8: PREPARE OUTPUT
# ============================================
print("\n" + "-" * 60)
print("Step 8: Preparing output file...")
print("-" * 60)

# Select and order columns for output
output_columns = [
    'url',
    'title',
    'article_text',
    'phrase',
    'phrase_category_clean',
    'media_name',
    'publish_date',
    'word_count',
    'length_category'
]

# Add topic if it exists
if 'topic' in df_sample.columns:
    output_columns.insert(5, 'topic')

output_df = df_sample[output_columns].copy()

# Add labeling workflow columns
output_df['ai_label'] = ''           # GPT-3.5 will fill this
output_df['human_label'] = ''        # Human reviewer will fill this
output_df['confidence'] = ''         # GPT-3.5 confidence score
output_df['notes'] = ''              # Optional notes from reviewer

# Reset index and add article IDs
output_df = output_df.reset_index(drop=True)
output_df.insert(0, 'article_id', range(1, len(output_df) + 1))

# ============================================
# SAVE OUTPUT
# ============================================
output_df.to_csv(OUTPUT_FILE, index=False)

print(f"\n{'=' * 60}")
print("SUCCESS!")
print(f"{'=' * 60}")
print(f"\nSaved {len(output_df):,} articles to:")
print(f"  {OUTPUT_FILE}")

print("\nOutput columns:")
for col in output_df.columns:
    sample_val = output_df[col].iloc[0] if len(output_df) > 0 else ''
    if isinstance(sample_val, str) and len(str(sample_val)) > 30:
        sample_val = str(sample_val)[:30] + "..."
    print(f"  - {col}: {sample_val}")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("1. Run GPT-3.5 to fill 'ai_label' and 'confidence' columns")
print("2. Review each article and fill 'human_label' column")
print("3. Use 'human_label' as ground truth for fine-tuning")
print("=" * 60)
