import pandas as pd
import re
from datetime import datetime

from ascend.application.context import ComponentExecutionContext
from ascend.common.events import log
from ascend.resources import transform, test, ref

@transform(
    inputs=[
        ref("read_mediacloud_weekly_new"),
    ],
    input_data_format="pandas",
    tests=[
        test("not_null", column="url"),
        test("not_null", column="title"),
        test("not_null", column="article_text"),
        test("count_greater_than", count=0, severity="warn"),
    ],
    on_schema_change="sync_all_columns",
)
def cleaned_mediacloud_data(
    read_mediacloud_weekly_new: pd.DataFrame,
    context: ComponentExecutionContext
) -> pd.DataFrame:
    """
    Clean and standardize Media Cloud article data.
    
    Args:
        read_mediacloud_weekly_new (pd.DataFrame): Raw Media Cloud articles
        context (ComponentExecutionContext): The execution context
    
    Returns:
        pd.DataFrame: Cleaned article data
    """
    log(f"Cleaning {len(read_mediacloud_weekly_new)} Media Cloud articles")
    
    df = read_mediacloud_weekly_new.copy()
    
    # Standardize column names to match Snowflake schema (uppercase)
    df = df.rename(columns={
        'url': 'URL',
        'title': 'TITLE',
        'publish_date': 'PUBLISH_DATE',
        'media_name': 'MEDIA_NAME',
        'article_text': 'ARTICLE_TEXT',
        'phrase': 'PHRASE',
        'phrase_category': 'PHRASE_CATEGORY',
        'province': 'PROVINCE'
    })
    
    # Clean article text
    def clean_text(text):
        if pd.isna(text) or text == "":
            return ""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', str(text))
        # Remove common navigation/footer text
        text = re.sub(r'(Subscribe|Sign up|Newsletter|Cookie Policy|Privacy Policy)', '', text, flags=re.IGNORECASE)
        return text.strip()
    
    df['ARTICLE_TEXT'] = df['ARTICLE_TEXT'].apply(clean_text)
    
    # Clean title
    df['TITLE'] = df['TITLE'].apply(lambda x: clean_text(x) if pd.notna(x) else "")
    
    # Standardize phrase category
    df['PHRASE_CATEGORY'] = df['PHRASE_CATEGORY'].str.lower().str.strip()
    
    # Extract year from publish_date
    df['YEAR'] = pd.to_datetime(df['PUBLISH_DATE']).dt.year
    
    # Remove articles with empty text (likely headers/navigation)
    initial_count = len(df)
    df = df[df['ARTICLE_TEXT'].str.len() > 100]  # At least 100 characters
    removed = initial_count - len(df)
    
    if removed > 0:
        log(f"Removed {removed} articles with insufficient text content")
    
    # Remove duplicates by URL
    df = df.drop_duplicates(subset=['URL'], keep='first')
    
    log(f"Cleaned data: {len(df)} articles remaining")
    
    return df