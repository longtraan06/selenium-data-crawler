"""
Utility functions for web crawling
"""
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from config.config import (
    CHROME_OPTIONS,
    CHROMEDRIVER_PATH,
    LOG_FILE,
    LOG_FORMAT,
    LOG_LEVEL
)


def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    
    return logger


def create_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Create and configure Chrome WebDriver
    
    Args:
        headless: Run in headless mode
        
    Returns:
        Configured Chrome WebDriver instance
    """
    options = Options()
    
    if headless or CHROME_OPTIONS.get("headless", True):
        options.add_argument("--headless")
    if CHROME_OPTIONS.get("disable_gpu", True):
        options.add_argument("--disable-gpu")
    if CHROME_OPTIONS.get("no_sandbox", True):
        options.add_argument("--no-sandbox")
    if "window_size" in CHROME_OPTIONS:
        options.add_argument(f"--window-size={CHROME_OPTIONS['window_size']}")
    
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver


def parse_date_from_text(date_text: str) -> Optional[datetime]:
    """
    Parse date from text format 'DD/MM/YYYY'
    
    Args:
        date_text: Date string in format DD/MM/YYYY
        
    Returns:
        datetime object or None if parsing fails
    """
    try:
        parts = date_text.split('/')
        if len(parts) == 3:
            day, month, year = parts
            return datetime(int(year), int(month), int(day))
    except (ValueError, IndexError):
        pass
    return None


def parse_iso_date(date_str: str) -> Optional[datetime]:
    """
    Parse ISO format date string
    
    Args:
        date_str: ISO format date string
        
    Returns:
        datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            pass
    return None


def ensure_dir_exists(directory: Path) -> None:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Path to directory
    """
    directory.mkdir(parents=True, exist_ok=True)


def save_links_to_file(links: list, filepath: Path) -> None:
    """
    Save list of links to text file
    
    Args:
        links: List of URLs
        filepath: Path to output file
    """
    ensure_dir_exists(filepath.parent)
    with open(filepath, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(f"{link}\n")


def read_links_from_file(filepath: Path) -> list:
    """
    Read links from text file
    
    Args:
        filepath: Path to input file
        
    Returns:
        List of URLs
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f.readlines() if line.strip()]
    return links


def safe_sleep(seconds: float) -> None:
    """
    Safe sleep with exception handling
    
    Args:
        seconds: Sleep duration in seconds
    """
    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        raise
    except Exception:
        pass
