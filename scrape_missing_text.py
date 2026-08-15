#!/usr/bin/env python3
"""
Scrape missing article text in batches
Resumes from where it left off
"""

from newspaper import Article
import pandas as pd
import requests
import time

BATCH_SIZE = 100

def scrape_article_text(url):
    """Scrape article text using newspaper3k with browser headers"""
    try:
        article = Article(url, browser_user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        article.download()
        article.parse()
        
        text = article.text
        return text[:5000] if text else ""
    except Exception as e:
        print(f"    Error: {e}")
        return ""



def main():
    print("="*60)
    print("SCRAPING MISSING ARTICLE TEXT")
    print("="*60)
    
    # Load current data
    df = pd.read_csv('data/aging_narratives_articles.csv')
    
    # Find rows with missing text
    missing_mask = df['article_text'].isna() | (df['article_text'] == '') | (df['article_text'].str.len() < 100)
    missing_indices = df[missing_mask].index.tolist()
    
    print(f"Total articles: {len(df)}")
    print(f"Missing text: {len(missing_indices)}")
    
    # Process in batches
    for i in range(0, len(missing_indices), BATCH_SIZE):
        batch_indices = missing_indices[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (len(missing_indices) // BATCH_SIZE) + 1
        
        print(f"\nBatch {batch_num}/{total_batches}")
        
        for idx in batch_indices:
            url = df.at[idx, 'url']
            print(f"  Scraping: {url[:50]}...")
            
            text = scrape_article_text(url)
            df.at[idx, 'article_text'] = text
            time.sleep(0.3)
        
        # Save after each batch
        df.to_csv('data/aging_narratives_articles.csv', index=False)
        print(f"  Saved progress.")
    
    print("\n" + "="*60)
    print("Done!")

if __name__ == "__main__":
    main()

