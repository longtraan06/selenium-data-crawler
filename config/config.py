"""
Configuration settings for ZNews crawler
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LINKS_DIR = DATA_DIR / "links"
ARTICLES_DIR = DATA_DIR / "articles"
LOGS_DIR = BASE_DIR / "logs"

# ChromeDriver configuration
CHROMEDRIVER_PATH = str(BASE_DIR / "chromedriver")

# Selenium options
CHROME_OPTIONS = {
    "headless": True,
    "disable_gpu": True,
    "no_sandbox": True,
    "window_size": "1920,1080"
}

# Crawling settings
SCROLL_PAUSE_TIME = 2  # seconds
MAX_SCROLLS = 50
SCROLL_AMOUNT = 600  # pixels
IMAGE_LOAD_SCROLLS = 10

# Target year for articles
TARGET_YEAR = 2024

# URLs configuration
ZNEWS_URLS = {
    "bong_da": "https://znews.vn/bong-da-viet-nam.html",
    "giao_duc": "https://lifestyle.znews.vn/giao-duc.html",
    "phap_luat": "https://zingnews.vn/phap-luat.html"
}

# Article limits
MAX_ARTICLES = 200
START_COUNT = 0

# CSS Selectors
SELECTORS = {
    "article_summary": "the-article-summary",
    "article_title": "the-article-title",
    "article_body": "the-article-body",
    "photo_wrapper": "z-photoviewer-wrapper",
    "news_latest": "news-latest",
    "section_content": "section-content",
    "article_item": "article-item",
    "date": "date",
    "thumbnail": "article-thumbnail"
}

# Output settings
JSON_INDENT = 4
ENCODING = "utf-8"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = str(LOGS_DIR / "crawler.log")
