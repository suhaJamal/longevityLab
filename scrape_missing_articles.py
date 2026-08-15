#!/usr/bin/env python3
"""
Scrape articles that are in metadata but missing from the main articles CSV
Uses anti-bot bypass techniques (cloudscraper, selenium)
Saves progress in batches to prevent data loss
"""

import pandas as pd
import time
import random
import os
from bs4 import BeautifulSoup

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

# ============================================================================
# CONFIGURATION
# ============================================================================

METADATA_FILE = 'newData/article_metadata.csv'
ARTICLES_FILE = 'newData/aging_narratives_articles.csv'
BATCH_SIZE = 50  # Save every 50 articles (scraping is slow)
REQUEST_DELAY = 1
MIN_TEXT_LENGTH = 100  # Minimum characters for valid article text

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
            best_element = max(elements, key=lambda x: len(x.get_text().strip()))
            text = best_element.get_text().strip()
            if len(text) > MIN_TEXT_LENGTH:
                return text

    # Fallback: main content area
    main_selectors = ['main', '#content', '.main-content', 'div.content-area']
    for selector in main_selectors:
        element = soup.select_one(selector)
        if element:
            text = element.get_text().strip()
            if len(text) > MIN_TEXT_LENGTH:
                return text

    # Last resort: body text
    body = soup.find('body')
    if body:
        text = body.get_text().strip()
        if len(text) > MIN_TEXT_LENGTH:
            return text

    return ""

def try_cloudscraper(url):
    """Try with cloudscraper for Cloudflare bypass"""
    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False},
            delay=10
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
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            driver = webdriver.Chrome(options=chrome_options)

        try:
            from selenium_stealth import stealth
            stealth(driver, languages=["en-US", "en"], vendor="Google Inc.",
                   platform="Win32", fix_hairline=True)
        except ImportError:
            pass

        driver.get(url)
        time.sleep(2)
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
        if driver:
            try:
                driver.quit()
            except:
                pass
    return None

def scrape_article_text(url):
    """Try multiple methods to scrape article text"""
    print(f"  Scraping: {url[:60]}...")

    # Method 1: Cloudscraper
    if CLOUDSCRAPER_AVAILABLE:
        print(f"    Trying Cloudscraper...")
        text = try_cloudscraper(url)
        if text and len(text.strip()) > MIN_TEXT_LENGTH:
            print(f"    Success with Cloudscraper ({len(text)} chars)")
            return text[:5000]

    # Method 2: Selenium
    if SELENIUM_AVAILABLE:
        print(f"    Trying Selenium...")
        text = try_selenium(url)
        if text and len(text.strip()) > MIN_TEXT_LENGTH:
            print(f"    Success with Selenium ({len(text)} chars)")
            return text[:5000]

    print(f"    All methods failed")
    return ""

def main():
    print("="*60)
    print("SCRAPING MISSING ARTICLES")
    print("="*60)

    # Check available libraries
    print(f"\nAvailable libraries:")
    print(f"  - Cloudscraper: {'YES' if CLOUDSCRAPER_AVAILABLE else 'NO'}")
    print(f"  - Selenium: {'YES' if SELENIUM_AVAILABLE else 'NO'}")

    if not CLOUDSCRAPER_AVAILABLE and not SELENIUM_AVAILABLE:
        print("\nERROR: No scraping libraries available!")
        print("Install with: pip install cloudscraper selenium webdriver-manager")
        return

    # Load metadata
    if not os.path.exists(METADATA_FILE):
        print(f"\nERROR: Metadata file not found: {METADATA_FILE}")
        print("Run fetch_article_metadata.py first!")
        return

    metadata_df = pd.read_csv(METADATA_FILE)
    print(f"\nLoaded {len(metadata_df)} articles from metadata")

    # Load existing articles (if any)
    existing_urls = set()
    existing_rows = []
    if os.path.exists(ARTICLES_FILE):
        articles_df = pd.read_csv(ARTICLES_FILE)
        # URLs with valid text (non-empty, > MIN_TEXT_LENGTH chars)
        valid_mask = articles_df['article_text'].notna() & (articles_df['article_text'].str.len() > MIN_TEXT_LENGTH)
        existing_urls = set(articles_df[valid_mask]['url'].tolist())
        existing_rows = articles_df.to_dict('records')
        print(f"Loaded {len(articles_df)} existing articles ({len(existing_urls)} with valid text)")

    # Find missing URLs
    all_metadata_urls = set(metadata_df['url'].tolist())
    missing_urls = all_metadata_urls - existing_urls
    print(f"\nArticles to scrape: {len(missing_urls)}")

    if not missing_urls:
        print("No articles to scrape!")
        return

    # Get metadata for missing URLs
    missing_df = metadata_df[metadata_df['url'].isin(missing_urls)].copy()

    # Track progress
    all_rows = existing_rows.copy()
    scraped_urls = existing_urls.copy()
    articles_since_save = 0
    successful = 0
    failed = 0

    print(f"\nStarting scraping (batch size: {BATCH_SIZE})...")
    print("="*60)

    for idx, row in missing_df.iterrows():
        url = row['url']

        if url in scraped_urls:
            continue

        # Scrape the article
        text = scrape_article_text(url)

        # Create article record
        article_row = {
            'url': url,
            'title': row.get('title', ''),
            'publish_date': row.get('publish_date', ''),
            'media_name': row.get('media_name', ''),
            'phrase': row.get('phrase', ''),
            'phrase_category': row.get('phrase_category', ''),
            'province': row.get('province', ''),
            'article_text': text
        }

        all_rows.append(article_row)
        scraped_urls.add(url)
        articles_since_save += 1

        if text and len(text) > MIN_TEXT_LENGTH:
            successful += 1
        else:
            failed += 1

        # Save every BATCH_SIZE articles
        if articles_since_save >= BATCH_SIZE:
            os.makedirs('newData', exist_ok=True)
            df = pd.DataFrame(all_rows)
            df.to_csv(ARTICLES_FILE, index=False)
            print(f"\n  [SAVED] {len(all_rows)} articles | Success: {successful} | Failed: {failed}")
            articles_since_save = 0

        # Random delay
        delay = REQUEST_DELAY + random.random() * 2
        time.sleep(delay)

    # Final save
    os.makedirs('newData', exist_ok=True)
    df = pd.DataFrame(all_rows)
    df.to_csv(ARTICLES_FILE, index=False)

    print("\n" + "="*60)
    print("SCRAPING COMPLETE!")
    print("="*60)
    print(f"Total articles: {len(all_rows)}")
    print(f"Successfully scraped: {successful}")
    print(f"Failed to scrape: {failed}")
    if successful + failed > 0:
        print(f"Success rate: {successful/(successful+failed)*100:.1f}%")
    print(f"Saved to: {ARTICLES_FILE}")

if __name__ == "__main__":
    main()
