"""
Article crawler for ZNews website
Crawls articles and extracts content, images, and metadata
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from utils import (
    setup_logger,
    create_driver,
    read_links_from_file,
    ensure_dir_exists,
    safe_sleep
)
from config.config import (
    ARTICLES_DIR,
    SELECTORS,
    SCROLL_AMOUNT,
    IMAGE_LOAD_SCROLLS,
    JSON_INDENT,
    ENCODING,
    MAX_ARTICLES,
    START_COUNT
)


class ArticleCrawler:
    """Crawler for extracting article content from ZNews"""
    
    def __init__(self, headless: bool = True):
        """
        Initialize article crawler
        
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
            
    def get_article_content(self, body) -> str:
        """
        Extract article content from body element
        
        Args:
            body: Selenium WebElement representing article body
            
        Returns:
            Article content as string
        """
        try:
            summary = self.driver.find_element(By.CLASS_NAME, SELECTORS["article_summary"])
            summary_text = summary.text
        except NoSuchElementException:
            self.logger.warning("Summary not found")
            summary_text = ""
            
        try:
            # Get only direct paragraph children
            paragraphs = body.find_elements(By.XPATH, "./p")
            all_content = [summary_text] if summary_text else []
            all_content.extend([p.text for p in paragraphs if p.text.strip()])
            return "\n".join(all_content)
        except Exception as e:
            self.logger.error(f"Error extracting content: {e}")
            return summary_text
            
    def get_article_images(self, body) -> List[Tuple[str, str]]:
        """
        Extract images and captions from article
        
        Args:
            body: Selenium WebElement representing article body
            
        Returns:
            List of tuples (image_urls, caption)
        """
        try:
            # Scroll to load images
            actions = ActionChains(self.driver)
            for _ in range(IMAGE_LOAD_SCROLLS):
                actions.scroll_by_amount(0, SCROLL_AMOUNT).perform()
                safe_sleep(0.3)
                
            pictures = body.find_elements(By.CLASS_NAME, SELECTORS["photo_wrapper"])
            pic_cap = []
            
            for picture in pictures:
                links = []
                try:
                    pics = picture.find_elements(By.CLASS_NAME, "pic")
                    for pic in pics:
                        imgs = pic.find_elements(By.TAG_NAME, "img")
                        for img in imgs:
                            src = img.get_attribute("src")
                            if src:
                                links.append(src)
                except Exception as e:
                    self.logger.warning(f"Error extracting image: {e}")
                    
                caption = picture.text.strip()
                if links:
                    pic_cap.append((", ".join(links), caption))
                    
            return pic_cap
            
        except Exception as e:
            self.logger.error(f"Error extracting images: {e}")
            return []
            
    def crawl_article(self, url: str) -> Optional[Dict]:
        """
        Crawl single article
        
        Args:
            url: Article URL
            
        Returns:
            Dictionary containing article data or None if failed
        """
        try:
            self.driver.get(url)
            safe_sleep(2)
            
            # Extract title
            try:
                title = self.driver.find_element(By.CLASS_NAME, SELECTORS["article_title"])
                title_text = title.text
            except NoSuchElementException:
                self.logger.error(f"Title not found for {url}")
                return None
                
            # Extract body
            try:
                body = self.driver.find_element(By.CLASS_NAME, SELECTORS["article_body"])
            except NoSuchElementException:
                self.logger.error(f"Body not found for {url}")
                return None
                
            # Extract content and images
            content = self.get_article_content(body)
            images = self.get_article_images(body)
            
            article_data = {
                "url": url,
                "title": title_text,
                "content": content,
                "metadata": {
                    "images": [{"url": img_url, "caption": caption} 
                              for img_url, caption in images]
                }
            }
            
            self.logger.info(f"Successfully crawled: {title_text}")
            return article_data
            
        except Exception as e:
            self.logger.error(f"Error crawling article {url}: {e}")
            return None
            
    def save_article(self, article_data: Dict, filename: str, output_dir: Optional[Path] = None) -> bool:
        """
        Save article data to JSON file
        
        Args:
            article_data: Article data dictionary
            filename: Output filename
            output_dir: Output directory (default: ARTICLES_DIR)
            
        Returns:
            True if saved successfully
        """
        try:
            if output_dir is None:
                output_dir = ARTICLES_DIR
                
            ensure_dir_exists(output_dir)
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding=ENCODING) as f:
                json.dump(article_data, f, indent=JSON_INDENT, ensure_ascii=False)
                
            self.logger.info(f"Saved article to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving article: {e}")
            return False
            
    def crawl_from_file(self, links_file: Path, 
                       category: str = "general",
                       start_count: int = START_COUNT,
                       max_articles: int = MAX_ARTICLES) -> None:
        """
        Crawl articles from links file
        
        Args:
            links_file: Path to file containing article URLs
            category: Category name for organizing output
            start_count: Starting count for file numbering
            max_articles: Maximum number of articles to crawl
        """
        links = read_links_from_file(links_file)
        self.logger.info(f"Found {len(links)} links to crawl")
        
        output_dir = ARTICLES_DIR / category
        ensure_dir_exists(output_dir)
        
        count = start_count
        successful = 0
        
        for link in links:
            if count >= max_articles:
                self.logger.info(f"Reached maximum articles limit: {max_articles}")
                break
                
            self.logger.info(f"Crawling article {count + 1}/{max_articles}")
            article_data = self.crawl_article(link)
            
            if article_data:
                filename = f"{count}.json"
                if self.save_article(article_data, filename, output_dir):
                    successful += 1
                count += 1
                
        self.logger.info(f"Crawling complete. Successfully saved {successful} articles")


def main():
    """Main function to run article crawler"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Crawl articles from ZNews")
    parser.add_argument("links_file", type=str, help="Path to links file")
    parser.add_argument("--category", type=str, default="general", 
                       help="Category name for organizing articles")
    parser.add_argument("--start", type=int, default=START_COUNT,
                       help="Starting count for file numbering")
    parser.add_argument("--max", type=int, default=MAX_ARTICLES,
                       help="Maximum number of articles to crawl")
    parser.add_argument("--no-headless", action="store_true",
                       help="Run browser in visible mode")
    
    args = parser.parse_args()
    
    with ArticleCrawler(headless=not args.no_headless) as crawler:
        crawler.crawl_from_file(
            Path(args.links_file),
            category=args.category,
            start_count=args.start,
            max_articles=args.max
        )


if __name__ == "__main__":
    main()
