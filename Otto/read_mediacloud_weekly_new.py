import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ascend.application.context import ComponentExecutionContext
from ascend.common.events import log
from ascend.resources import read, test, RetryStrategy

# Media Cloud API configuration
MEDIACLOUD_API_KEY = "9e047cbfc9e1cd397857c21eb52c78902fc5f181"
MEDIACLOUD_BASE_URL = "https://api.mediacloud.org/api/v2/stories_public/list"

# Search phrases by narrative category
SEARCH_PHRASES = {
    "limiting": [
        "aging crisis",
        "aging population crisis",
        "elderly burden",
        "aging tsunami",
        "silver tsunami",
        "demographic time bomb"
    ],
    "neutral": [
        "aging population",
        "older adults",
        "senior citizens",
        "elderly population",
        "population aging"
    ],
    "empowering": [
        "active aging",
        "successful aging",
        "healthy aging",
        "aging well",
        "productive aging",
        "elder wisdom"
    ]
}

# Canadian province collection IDs
PROVINCE_COLLECTIONS = {
    "Ontario": 38379397,
    "British Columbia": 38379407,
    "Alberta": 38379399,
    "Quebec": 38379395
}

@read(
    strategy="incremental",
    incremental_strategy="append",
    on_schema_change="sync_all_columns",
    retry_strategy=RetryStrategy(
        stop_after_attempt=3,
        stop_after_delay=300
    )
)
def read_mediacloud_weekly_new(context: ComponentExecutionContext) -> pd.DataFrame:
    """
    Fetch new aging narratives articles from Media Cloud API for the last 7 days.
    
    This component searches for specific phrases across Canadian provinces and
    categorizes articles by narrative framing (limiting/neutral/empowering).
    
    Args:
        context (ComponentExecutionContext): The execution context
    
    Returns:
        pd.DataFrame: New articles with columns: url, title, publish_date, media_name,
                     article_text, phrase, phrase_category, province
    """
    # Calculate date range: last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    log(f"Fetching Media Cloud articles from {start_date.date()} to {end_date.date()}")
    
    all_articles = []
    total_api_calls = 0
    
    # Iterate through each province
    for province_name, collection_id in PROVINCE_COLLECTIONS.items():
        log(f"Processing province: {province_name} (Collection ID: {collection_id})")
        
        # Iterate through each phrase category
        for category, phrases in SEARCH_PHRASES.items():
            for phrase in phrases:
                try:
                    # Build API request parameters
                    params = {
                        "key": MEDIACLOUD_API_KEY,
                        "q": f'"{phrase}"',  # Exact phrase match
                        "fq": f"tags_id_media:{collection_id}",  # Filter by collection
                        "last_processed_stories_id": 0,
                        "rows": 100,  # Max results per request
                        "wc": "true"  # Include word count
                    }
                    
                    # Make API request
                    log(f"Searching for phrase: '{phrase}' in {province_name}")
                    response = requests.get(MEDIACLOUD_BASE_URL, params=params, timeout=30)
                    total_api_calls += 1
                    
                    # Handle rate limiting
                    if response.status_code == 429:
                        log(f"Rate limit hit, waiting 60 seconds...")
                        import time
                        time.sleep(60)
                        response = requests.get(MEDIACLOUD_BASE_URL, params=params, timeout=30)
                        total_api_calls += 1
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract articles from response
                    stories = data.get("stories", [])
                    
                    if not stories:
                        log(f"No articles found for '{phrase}' in {province_name}")
                        continue
                    
                    # Filter articles by date range
                    for story in stories:
                        publish_date_str = story.get("publish_date", "")
                        
                        # Parse publish date
                        try:
                            publish_date = datetime.strptime(publish_date_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            # Try alternative format
                            try:
                                publish_date = datetime.strptime(publish_date_str.split()[0], "%Y-%m-%d")
                            except:
                                log(f"Could not parse date: {publish_date_str}, skipping article")
                                continue
                        
                        # Only include articles from last 7 days
                        if start_date <= publish_date <= end_date:
                            article = {
                                "url": story.get("url", ""),
                                "title": story.get("title", ""),
                                "publish_date": publish_date,
                                "media_name": story.get("media_name", ""),
                                "article_text": story.get("story_text", ""),
                                "phrase": phrase,
                                "phrase_category": category,
                                "province": province_name
                            }
                            all_articles.append(article)
                    
                    log(f"Found {len(stories)} articles for '{phrase}' in {province_name}")
                    
                except requests.exceptions.RequestException as e:
                    log(f"API request failed for '{phrase}' in {province_name}: {str(e)}")
                    continue
                except Exception as e:
                    log(f"Error processing '{phrase}' in {province_name}: {str(e)}")
                    continue
    
    # Convert to DataFrame
    if not all_articles:
        log("No new articles found in the last 7 days")
        # Return empty DataFrame with correct schema
        return pd.DataFrame(columns=[
            "url", "title", "publish_date", "media_name", "article_text",
            "phrase", "phrase_category", "province"
        ])
    
    df = pd.DataFrame(all_articles)
    
    # Remove duplicates by URL (keep first occurrence)
    initial_count = len(df)
    df = df.drop_duplicates(subset=["url"], keep="first")
    duplicates_removed = initial_count - len(df)
    
    if duplicates_removed > 0:
        log(f"Removed {duplicates_removed} duplicate URLs")
    
    # Log summary statistics
    log(f"Successfully fetched {len(df)} unique articles")
    log(f"Total API calls made: {total_api_calls}")
    log(f"Articles by category: {df['phrase_category'].value_counts().to_dict()}")
    log(f"Articles by province: {df['province'].value_counts().to_dict()}")
    
    # Add metadata columns
    df["ingestion_timestamp"] = datetime.now()
    df["data_source"] = "mediacloud_weekly"
    
    return df