#!/usr/bin/env python3
"""
Aging Narratives - Canada Articles Data (Enhanced Scraping)
FOR YEAR 2024: Jan 1, 2024 to Dec 31, 2024
Saves progress every 100 articles to prevent data loss

Scraping methods (in order of speed):
1. requests + BeautifulSoup (fastest)
2. Cloudscraper (bypasses Cloudflare)
3. Selenium (renders JavaScript, slowest but most reliable)
"""

from datetime import date
import mediacloud.api
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
import random

# Try to import advanced scraping libraries
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    print("Warning: cloudscraper not available - install with: pip install cloudscraper")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Warning: selenium not available - install with: pip install selenium webdriver-manager")

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = '...'
START_DATE = date(2024, 1, 1)
END_DATE = date(2024, 6, 30)
BATCH_SIZE = 100  # Save every 100 articles
OUTPUT_FILE = 'newData/aging_narratives_articles_2024.csv'
MIN_TEXT_LENGTH = 100  # Minimum characters for valid article text

# Narrative phrases to search
NARRATIVES = {
    'limiting': [
        'aging crisis',
        'aging population crisis',
        'elderly burden',
        'aging tsunami',
        'silver tsunami',
        'demographic time bomb'
    ],
    'neutral': [
        'aging population',
        'older adults',
        'senior citizens',
        'elderly population',
        'population aging'
    ],
    'empowering': [
        'active aging',
        'successful aging',
        'healthy aging',
        'aging well',
        'productive aging',
        'elder wisdom'
    ]
}

# Canadian province collection IDs
PROVINCES = {
    'Ontario': 38379397,
    'British Columbia': 38379407,
    'Alberta': 38379399,
    'Quebec': 38379395,
}

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
]

def get_random_headers():
    """Generate headers with random user agent"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def extract_text_from_soup(soup):
    """Extract article text from BeautifulSoup object"""
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
        element.decompose()

    # Try common article selectors first
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

    # Fallback: get all paragraphs
    paragraphs = soup.find_all('p')
    text = ' '.join([p.get_text().strip() for p in paragraphs])

    return text

# ============================================================================
# SCRAPING METHOD 1: requests + BeautifulSoup (fastest)
# ============================================================================

def try_requests(url):
    """Try scraping with basic requests + BeautifulSoup"""
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = extract_text_from_soup(soup)
            if len(text) > MIN_TEXT_LENGTH:
                return text
    except Exception as e:
        pass  # Silent fail, will try next method
    return None

# ============================================================================
# SCRAPING METHOD 2: Cloudscraper (bypasses Cloudflare)
# ============================================================================

def try_cloudscraper(url):
    """Try scraping with cloudscraper for Cloudflare bypass"""
    if not CLOUDSCRAPER_AVAILABLE:
        return None

    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False},
            delay=10
        )
        response = scraper.get(url, headers=get_random_headers(), timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = extract_text_from_soup(soup)
            if len(text) > MIN_TEXT_LENGTH:
                return text
    except Exception as e:
        pass  # Silent fail, will try next method
    return None

# ============================================================================
# SCRAPING METHOD 3: Selenium (renders JavaScript, slowest)
# ============================================================================

def try_selenium(url):
    """Try scraping with Selenium for JavaScript-rendered pages"""
    if not SELENIUM_AVAILABLE:
        return None

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

        # Try to use webdriver_manager for automatic driver management
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            driver = webdriver.Chrome(options=chrome_options)

        # Try stealth mode if available
        try:
            from selenium_stealth import stealth
            stealth(driver, languages=["en-US", "en"], vendor="Google Inc.",
                   platform="Win32", fix_hairline=True)
        except ImportError:
            pass

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
        text = extract_text_from_soup(soup)
        if len(text) > MIN_TEXT_LENGTH:
            return text

    except Exception as e:
        if driver:
            try:
                driver.quit()
            except:
                pass
    return None

# ============================================================================
# MAIN SCRAPING FUNCTION (tries all methods)
# ============================================================================

def scrape_article_text(url):
    """
    Scrape article text using multiple methods as fallbacks.
    Order: requests (fast) -> cloudscraper (medium) -> selenium (slow)
    """
    # Method 1: Basic requests (fastest)
    text = try_requests(url)
    if text:
        return text[:5000], "requests"

    # Method 2: Cloudscraper (medium speed, bypasses Cloudflare)
    if CLOUDSCRAPER_AVAILABLE:
        text = try_cloudscraper(url)
        if text:
            return text[:5000], "cloudscraper"

    # Method 3: Selenium (slowest, but handles JavaScript)
    if SELENIUM_AVAILABLE:
        text = try_selenium(url)
        if text:
            return text[:5000], "selenium"

    # All methods failed
    return "", "failed"

# ============================================================================
# DATA MANAGEMENT FUNCTIONS
# ============================================================================

def load_existing_data():
    """Load existing data if available, returns DataFrame and set of scraped URLs"""
    if os.path.exists(OUTPUT_FILE):
        try:
            df = pd.read_csv(OUTPUT_FILE)
            scraped_urls = set(df['url'].tolist())
            print(f"Loaded {len(df)} existing articles from {OUTPUT_FILE}")
            print(f"Will skip {len(scraped_urls)} already scraped URLs")
            return df.to_dict('records'), scraped_urls
        except Exception as e:
            print(f"Error loading existing data: {e}")
    return [], set()

def save_data(rows):
    """Save current data to CSV"""
    os.makedirs('newData', exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"  [SAVED] {len(rows)} articles to {OUTPUT_FILE}")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Generate articles data for all Canadian provinces"""
    print("="*70)
    print("AGING NARRATIVES - CANADA ARTICLES DATA (2024)")
    print("="*70)
    print(f"Date range: {START_DATE} to {END_DATE}")
    print(f"Batch size: {BATCH_SIZE} (saves every {BATCH_SIZE} articles)")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"\nAvailable scraping methods:")
    print(f"  1. requests + BeautifulSoup: YES (always available)")
    print(f"  2. Cloudscraper:             {'YES' if CLOUDSCRAPER_AVAILABLE else 'NO'}")
    print(f"  3. Selenium:                 {'YES' if SELENIUM_AVAILABLE else 'NO'}")
    print("="*70)

    mc = mediacloud.api.SearchApi(API_KEY)

    # Load existing data to resume from where we left off
    all_rows, scraped_urls = load_existing_data()
    articles_since_last_save = 0

    # Track scraping method statistics
    method_stats = {"requests": 0, "cloudscraper": 0, "selenium": 0, "failed": 0}

    for province_name, collection_id in PROVINCES.items():
        print(f"\nProcessing {province_name}...")

        for category, phrases in NARRATIVES.items():
            for phrase in phrases:
                print(f"  '{phrase}' in {province_name}...")

                time.sleep(0.5)

                try:
                    story_result = mc.story_list(
                        phrase,
                        start_date=START_DATE,
                        end_date=END_DATE,
                        collection_ids=[collection_id]
                    )

                    stories = story_result[0]
                    print(f"    Found {len(stories)} articles")

                    for story in stories:
                        url = story.get('url', '')

                        # Skip if already scraped
                        if url in scraped_urls:
                            continue

                        print(f"    Scraping: {url[:55]}...", end=" ")

                        # Scrape with fallback methods
                        article_text, method_used = scrape_article_text(url)
                        method_stats[method_used] += 1

                        if method_used != "failed":
                            print(f"[{method_used}]")
                        else:
                            print("[FAILED]")

                        row = {
                            'url': url,
                            'title': story.get('title', ''),
                            'publish_date': story.get('publish_date', ''),
                            'media_name': story.get('media_name', ''),
                            'phrase': phrase,
                            'phrase_category': category,
                            'province': province_name,
                            'article_text': article_text,
                            'scrape_method': method_used
                        }

                        all_rows.append(row)
                        scraped_urls.add(url)
                        articles_since_last_save += 1

                        # Save every BATCH_SIZE articles
                        if articles_since_last_save >= BATCH_SIZE:
                            save_data(all_rows)
                            articles_since_last_save = 0

                        # Delay based on method used
                        if method_used == "selenium":
                            time.sleep(1)  # Longer delay after selenium
                        else:
                            time.sleep(0.3)

                except Exception as e:
                    print(f"    Error: {e}")
                    # Save on error to preserve progress
                    if all_rows:
                        save_data(all_rows)
                        articles_since_last_save = 0

    # Final save
    save_data(all_rows)

    # Print statistics
    print("\n" + "="*70)
    print("SCRAPING COMPLETE!")
    print("="*70)
    print(f"Total articles: {len(all_rows)}")
    print(f"\nScraping method statistics:")
    print(f"  requests:     {method_stats['requests']} articles")
    print(f"  cloudscraper: {method_stats['cloudscraper']} articles")
    print(f"  selenium:     {method_stats['selenium']} articles")
    print(f"  failed:       {method_stats['failed']} articles")

    total_attempted = sum(method_stats.values())
    if total_attempted > 0:
        success_rate = ((total_attempted - method_stats['failed']) / total_attempted) * 100
        print(f"\nSuccess rate: {success_rate:.1f}%")

    print(f"\nSaved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
