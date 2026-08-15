#!/usr/bin/env python3
"""
Scrape missing article text in batches with anti-bot bypass
Resumes from where it left off
"""

import pandas as pd
import time
import random
from bs4 import BeautifulSoup
import requests

# Try to import advanced scraping libraries
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    print("Cloudscraper not available - install with: pip install cloudscraper")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available - install with: pip install selenium webdriver-manager")

BATCH_SIZE = 100
REQUEST_DELAY = 1  # Base delay between requests

# List of realistic user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
]

def get_headers():
    """Generate realistic headers with random user agent"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com/'
    }

def extract_article_text(soup):
    """Extract article text from BeautifulSoup object"""
    # Try common article selectors for these sites
    selectors = [
        'article',
        '.article-content',
        '.story-content',
        '[itemprop="articleBody"]',
        'div.content',
        'div.story',
        'div.article-body',
        'div.post-content',
        'main',
        'div#main-content',
        'div.article__content',
        'div.article-text'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            # Get the element with most text
            best_element = max(elements, key=lambda x: len(x.get_text().strip()))
            text = best_element.get_text().strip()
            if len(text) > 100:
                return text
    
    # Fallback: try to find main content area
    main_selectors = ['main', '#content', '.main-content', 'div.content-area']
    for selector in main_selectors:
        element = soup.select_one(selector)
        if element:
            text = element.get_text().strip()
            if len(text) > 100:
                return text
    
    # Last resort: get all text from body
    body = soup.find('body')
    if body:
        text = body.get_text().strip()
        if len(text) > 100:
            return text
    
    return ""

def try_cloudscraper(url):
    """Try with cloudscraper for Cloudflare bypass"""
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            },
            delay=10  # Cloudflare challenge delay
        )
        
        response = scraper.get(url, headers=get_headers(), timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return extract_article_text(soup)
    except Exception as e:
        print(f"    Cloudscraper failed: {e}")
    return None

def try_selenium(url):
    """Try with Selenium as last resort"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # New headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
        
        # Try to use webdriver_manager for automatic driver management
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            # Fallback to standard driver
            driver = webdriver.Chrome(options=chrome_options)
        
        # Try stealth mode if available
        try:
            from selenium_stealth import stealth
            stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                fix_hairline=True,
            )
        except ImportError:
            pass  # Continue without stealth
        
        driver.get(url)
        time.sleep(2)  # Wait for page load
        
        # Scroll to trigger lazy loading
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, 600);")
        time.sleep(0.5)
        
        page_source = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(page_source, 'html.parser')
        return extract_article_text(soup)
                
    except Exception as e:
        print(f"    Selenium failed: {e}")
        try:
            driver.quit()
        except:
            pass
    return None

def scrape_article_text(url):
    """Try multiple methods to scrape article text"""
    print(f"  Scraping: {url[:60]}...")
    
    # Track which method works best for which domain
    domain_method_preference = {
        'guelphtoday.com': 'cloudscraper',
        'barrietoday.com': 'selenium',  # Based on your output
        'timminstoday.com': 'selenium', # Based on your output
    }
    
    # Extract domain from URL
    domain = None
    for d in domain_method_preference.keys():
        if d in url:
            domain = d
            break
    
    # Try preferred method first if known
    if domain and domain_method_preference.get(domain) == 'cloudscraper' and CLOUDSCRAPER_AVAILABLE:
        print(f"    Trying Cloudscraper (preferred for {domain})...")
        text = try_cloudscraper(url)
        if text and len(text.strip()) > 100:
            print(f"    ✓ Success with Cloudscraper")
            return text[:5000]
    
    # Method 1: Cloudscraper (fastest for Cloudflare)
    if CLOUDSCRAPER_AVAILABLE:
        print(f"    Trying Cloudscraper...")
        text = try_cloudscraper(url)
        if text and len(text.strip()) > 100:
            print(f"    ✓ Success with Cloudscraper")
            return text[:5000]
    
    # Method 2: Selenium (slower but more reliable)
    if SELENIUM_AVAILABLE:
        print(f"    Trying Selenium...")
        text = try_selenium(url)
        if text and len(text.strip()) > 100:
            print(f"    ✓ Success with Selenium")
            return text[:5000]
    
    print(f"    ✗ All methods failed")
    return ""

def main():
    print("="*60)
    print("SCRAPING MISSING ARTICLE TEXT WITH ANTI-BOT BYPASS")
    print("="*60)
    
    # Check available libraries
    print(f"Available libraries:")
    print(f"  - Cloudscraper: {'✓' if CLOUDSCRAPER_AVAILABLE else '✗'}")
    print(f"  - Selenium: {'✓' if SELENIUM_AVAILABLE else '✗'}")
    
    if not CLOUDSCRAPER_AVAILABLE and not SELENIUM_AVAILABLE:
        print("\nERROR: No anti-bot libraries available!")
        print("Please install: pip install cloudscraper selenium webdriver-manager")
        return
    
    # Load current data
    try:
        df = pd.read_csv('data/aging_narratives_articles.csv')
    except FileNotFoundError:
        print("ERROR: CSV file not found at 'data/aging_narratives_articles.csv'")
        return
    except Exception as e:
        print(f"ERROR loading CSV: {e}")
        return
    
    # Find rows with missing text
    missing_mask = df['article_text'].isna() | (df['article_text'] == '') | (df['article_text'].str.len() < 100)
    missing_indices = df[missing_mask].index.tolist()
    
    print(f"\nTotal articles: {len(df)}")
    print(f"Missing text: {len(missing_indices)}")
    
    if not missing_indices:
        print("No articles need scraping!")
        return
    
    # Process in batches
    total_batches = (len(missing_indices) + BATCH_SIZE - 1) // BATCH_SIZE
    successful_scrapes = 0
    
    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(missing_indices))
        batch_indices = missing_indices[start_idx:end_idx]
        
        print(f"\n{'='*40}")
        print(f"Batch {batch_num + 1}/{total_batches} ({len(batch_indices)} articles)")
        print(f"{'='*40}")
        
        batch_success = 0
        for idx in batch_indices:
            url = df.at[idx, 'url']
            
            # Scrape article
            text = scrape_article_text(url)
            df.at[idx, 'article_text'] = text
            
            if text and len(text.strip()) > 100:
                batch_success += 1
            
            # Random delay to avoid rate limiting (but less for Selenium since it's already slow)
            if 'selenium' in text or not text:  # If Selenium was used or failed
                delay = 2 + random.random() * 3  # Longer delay for Selenium
            else:
                delay = REQUEST_DELAY + random.random() * 1  # Shorter for Cloudscraper
            
            time.sleep(delay)
        
        # Save after each batch
        df.to_csv('data/aging_narratives_articles.csv', index=False)
        successful_scrapes += batch_success
        
        print(f"\n  Saved progress after batch {batch_num + 1}")
        print(f"  Successfully scraped: {batch_success}/{len(batch_indices)}")
        print(f"  Total success so far: {successful_scrapes}/{start_idx + len(batch_indices)}")
        
        # Estimate time remaining
        if batch_num < total_batches - 1:
            remaining = total_batches - batch_num - 1
            est_minutes = (remaining * len(batch_indices) * 3) / 60  # ~3 seconds per article
            print(f"  Estimated time remaining: ~{est_minutes:.1f} minutes")
    
    print("\n" + "="*60)
    
    # Final statistics
    final_missing = (df['article_text'].isna() | (df['article_text'] == '') | (df['article_text'].str.len() < 100)).sum()
    success_rate = ((len(missing_indices) - final_missing) / len(missing_indices) * 100) if missing_indices else 100
    
    print(f"SCRAPING COMPLETE!")
    print(f"Articles still missing text: {final_missing}")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Total articles with text: {len(df) - final_missing}/{len(df)}")
    
    # Save a backup copy
    backup_file = f'data/aging_narratives_articles_backup_{time.strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(backup_file, index=False)
    print(f"Backup saved to: {backup_file}")

if __name__ == "__main__":
    main()
    