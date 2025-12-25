"""
Link collector for ZNews articles
Collects article links from category pages
"""
import time
from pathlib import Path
from typing import Set, Optional
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from utils import (
    setup_logger,
    create_driver,
    parse_date_from_text,
    parse_iso_date,
    save_links_to_file,
    safe_sleep
)
from config.config import (
    LINKS_DIR,
    SELECTORS,
    SCROLL_PAUSE_TIME,
    MAX_SCROLLS,
    TARGET_YEAR,
    ZNEWS_URLS
)


class LinkCollector:
    """Collector for gathering article links from ZNews category pages"""
    
    def __init__(self, headless: bool = True):
        """
        Initialize link collector
        
        Args:
            headless: Run browser in headless mode
        """
        self.logger = setup_logger(self.__class__.__name__)
        self.headless = headless
        self.driver = None
        
    def __enter__(self):
        """Context manager entry"""
        self.driver = create_driver(self.headless)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.driver:
            self.driver.quit()
            
    def check_article_year(self, article_element, target_year: int) -> Optional[int]:
        """
        Extract and check year from article element
        
        Args:
            article_element: Selenium WebElement representing an article
            target_year: Target year to check against
            
        Returns:
            Year as integer or None if not found
        """
        try:
            # Try format 1: datetime attribute (ISO format)
            try:
                time_element = article_element.find_element(By.CSS_SELECTOR, 'time')
                date_str = time_element.get_attribute('datetime')
                if date_str:
                    date_obj = parse_iso_date(date_str)
                    if date_obj:
                        return date_obj.year
            except NoSuchElementException:
                pass
                
            # Try format 2: date class with DD/MM/YYYY format
            try:
                date_element = article_element.find_element(By.CLASS_NAME, SELECTORS["date"])
                date_text = date_element.text.strip()
                if date_text:
                    date_obj = parse_date_from_text(date_text)
                    if date_obj:
                        return date_obj.year
            except NoSuchElementException:
                pass
                
        except Exception as e:
            self.logger.debug(f"Error parsing date: {e}")
            
        return None
        
    def collect_links_scroll_based(self, url: str, 
                                   target_year: int = TARGET_YEAR,
                                   max_links: int = 200) -> Set[str]:
        """
        Collect article links by scrolling (for news-latest based pages)
        
        Args:
            url: Category page URL
            target_year: Target year for articles
            max_links: Maximum number of links to collect
            
        Returns:
            Set of article URLs
        """
        self.logger.info(f"Starting link collection from {url}")
        self.driver.get(url)
        safe_sleep(5)
        
        links = set()
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        
        while scroll_count < MAX_SCROLLS:
            try:
                # Find articles container
                news_box = self.driver.find_element(By.ID, SELECTORS["news_latest"])
                content_box = news_box.find_element(By.CLASS_NAME, SELECTORS["section_content"])
                articles = content_box.find_elements(By.CLASS_NAME, SELECTORS["article_item"])
                
                # Process articles in reverse order (newest first)
                for article in reversed(articles):
                    year = self.check_article_year(article, target_year)
                    
                    if year and year > target_year:
                        # Skip future articles
                        continue
                    elif year and year == target_year:
                        # Extract link
                        try:
                            thumbnail = article.find_element(By.CLASS_NAME, SELECTORS["thumbnail"])
                            link_element = thumbnail.find_element(By.CSS_SELECTOR, 'a')
                            link = link_element.get_attribute('href')
                            if link:
                                links.add(link)
                                self.logger.debug(f"Found link: {link}")
                        except NoSuchElementException:
                            continue
                    elif year and year < target_year:
                        # Reached older articles, stop
                        self.logger.info(f"Reached articles from {year}, stopping")
                        return links
                        
                    if len(links) >= max_links:
                        self.logger.info(f"Reached maximum links: {max_links}")
                        return links
                        
            except NoSuchElementException as e:
                self.logger.warning(f"Element not found: {e}")
                
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            safe_sleep(SCROLL_PAUSE_TIME)
            
            # Check if page height changed
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                self.logger.info("No more content to load")
                break
            last_height = new_height
            scroll_count += 1
            
        self.logger.info(f"Collected {len(links)} links")
        return links
        
    def collect_links_article_based(self, url: str,
                                    target_year: int = TARGET_YEAR,
                                    max_links: int = 200) -> Set[str]:
        """
        Collect article links (for article-based listing pages)
        
        Args:
            url: Category page URL
            target_year: Target year for articles
            max_links: Maximum number of links to collect
            
        Returns:
            Set of article URLs
        """
        self.logger.info(f"Starting link collection from {url}")
        self.driver.get(url)
        safe_sleep(3)
        
        links = set()
        scroll_count = 0
        
        while scroll_count < MAX_SCROLLS and len(links) < max_links:
            # Find all articles
            articles = self.driver.find_elements(By.CSS_SELECTOR, 'article')
            
            for article in articles:
                year = self.check_article_year(article, target_year)
                
                if year == target_year:
                    try:
                        link_element = article.find_element(By.CSS_SELECTOR, 'a')
                        link = link_element.get_attribute('href')
                        if link and link not in links:
                            links.add(link)
                            self.logger.debug(f"Found link: {link}")
                    except NoSuchElementException:
                        continue
                        
                if len(links) >= max_links:
                    break
                    
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            safe_sleep(SCROLL_PAUSE_TIME)
            scroll_count += 1
            
        self.logger.info(f"Collected {len(links)} links")
        return links
        
    def collect_and_save(self, url: str, output_file: str,
                        target_year: int = TARGET_YEAR,
                        max_links: int = 200,
                        method: str = "scroll") -> None:
        """
        Collect links and save to file
        
        Args:
            url: Category page URL
            output_file: Output filename (without path)
            target_year: Target year for articles
            max_links: Maximum number of links to collect
            method: Collection method ("scroll" or "article")
        """
        if method == "scroll":
            links = self.collect_links_scroll_based(url, target_year, max_links)
        else:
            links = self.collect_links_article_based(url, target_year, max_links)
            
        if links:
            output_path = LINKS_DIR / output_file
            save_links_to_file(list(links), output_path)
            self.logger.info(f"Saved {len(links)} links to {output_path}")
        else:
            self.logger.warning("No links collected")


def main():
    """Main function to run link collector"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect article links from ZNews")
    parser.add_argument("--url", type=str, help="Category URL to crawl")
    parser.add_argument("--category", type=str, 
                       choices=list(ZNEWS_URLS.keys()),
                       help="Predefined category to crawl")
    parser.add_argument("--output", type=str, required=True,
                       help="Output filename (e.g., links_thethao.txt)")
    parser.add_argument("--year", type=int, default=TARGET_YEAR,
                       help=f"Target year (default: {TARGET_YEAR})")
    parser.add_argument("--max-links", type=int, default=200,
                       help="Maximum number of links to collect")
    parser.add_argument("--method", type=str, choices=["scroll", "article"],
                       default="scroll", help="Collection method")
    parser.add_argument("--no-headless", action="store_true",
                       help="Run browser in visible mode")
    
    args = parser.parse_args()
    
    # Determine URL
    if args.category:
        url = ZNEWS_URLS.get(args.category)
        if not url:
            print(f"Unknown category: {args.category}")
            return
    elif args.url:
        url = args.url
    else:
        print("Please specify either --url or --category")
        return
    
    with LinkCollector(headless=not args.no_headless) as collector:
        collector.collect_and_save(
            url=url,
            output_file=args.output,
            target_year=args.year,
            max_links=args.max_links,
            method=args.method
        )


if __name__ == "__main__":
    main()
