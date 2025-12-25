# ZNews Web Crawler

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.15.0%2B-green.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Một công cụ crawl dữ liệu chuyên nghiệp để thu thập bài viết từ ZNews (znews.vn) sử dụng Selenium WebDriver. Dự án được thiết kế với kiến trúc module hóa, dễ bảo trì và mở rộng.

## ✨ Tính năng

- 🔗 **Thu thập links**: Tự động thu thập link bài viết từ các chuyên mục
- 📰 **Crawl nội dung**: Trích xuất tiêu đề, nội dung, hình ảnh và metadata
- 🎯 **Lọc theo năm**: Chỉ thu thập bài viết từ năm mong muốn
- 📝 **Logging**: Ghi log chi tiết quá trình crawl
- ⚙️ **Cấu hình linh hoạt**: Dễ dàng tùy chỉnh thông qua file config
- 🔄 **OOP Design**: Code được tổ chức theo hướng đối tượng
- 🛡️ **Error handling**: Xử lý lỗi toàn diện và an toàn
- 💾 **Xuất JSON**: Lưu dữ liệu dạng JSON với encoding UTF-8

## 📁 Cấu trúc dự án

```
Crawling-data-using-selenium/
├── config/                      # Cấu hình
│   ├── __init__.py
│   └── config.py               # File cấu hình chính
├── src/                        # Source code
│   ├── __init__.py
│   ├── article_crawler.py      # Module crawl bài viết
│   ├── link_collector.py       # Module thu thập links
│   └── utils.py                # Các hàm tiện ích
├── data/                       # Dữ liệu
│   ├── links/                  # Links đã thu thập
│   └── articles/               # Bài viết đã crawl
│       ├── bong_da/
│       ├── giao_duc/
│       └── phap_luat/
├── logs/                       # Log files
│   └── crawler.log
├── chromedriver                # ChromeDriver binary
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # Documentation

# Legacy files (không còn sử dụng)
├── Crawling.py                # → src/article_crawler.py
├── Get_Links.py               # → src/link_collector.py
└── form.py                    # → Deprecated
```

## 🚀 Cài đặt

### Yêu cầu hệ thống

- Python 3.8 trở lên
- Chrome/Chromium browser
- ChromeDriver tương thích với phiên bản Chrome

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd Crawling-data-using-selenium
```

### Bước 2: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Tải ChromeDriver

1. Kiểm tra phiên bản Chrome:
   - Mở Chrome → Settings → About Chrome
   
2. Tải ChromeDriver phù hợp:
   - Truy cập: https://chromedriver.chromium.org/downloads
   - Tải phiên bản tương ứng với Chrome
   
3. Đặt file ChromeDriver vào thư mục gốc dự án:
   ```
   Crawling-data-using-selenium/chromedriver
   ```

**Lưu ý cho Windows**: File sẽ có đuôi `.exe` (`chromedriver.exe`)

**Lưu ý cho Linux/Mac**: Cần cấp quyền thực thi:
```bash
chmod +x chromedriver
```

## 📖 Hướng dẫn sử dụng

### 1. Thu thập Links

#### Sử dụng category có sẵn

```bash
python src/link_collector.py --category bong_da --output links_bongda.txt
```

#### Sử dụng URL tùy chỉnh

```bash
python src/link_collector.py --url "https://znews.vn/phap-luat.html" --output links_phapluat.txt
```

#### Các tùy chọn nâng cao

```bash
python src/link_collector.py \
  --category giao_duc \
  --output links_giaoduc.txt \
  --year 2024 \
  --max-links 200 \
  --method scroll \
  --no-headless
```

**Tham số:**
- `--category`: Chuyên mục có sẵn (`bong_da`, `giao_duc`, `phap_luat`)
- `--url`: URL tùy chỉnh
- `--output`: Tên file output (*.txt)
- `--year`: Năm cần thu thập (mặc định: 2024)
- `--max-links`: Số lượng links tối đa (mặc định: 200)
- `--method`: Phương thức thu thập (`scroll` hoặc `article`)
- `--no-headless`: Hiển thị trình duyệt (để debug)

### 2. Crawl Bài viết

```bash
python src/article_crawler.py data/links/links_bongda.txt --category bong_da
```

#### Các tùy chọn nâng cao

```bash
python src/article_crawler.py data/links/links_phapluat.txt \
  --category phap_luat \
  --start 0 \
  --max 200 \
  --no-headless
```

**Tham số:**
- `links_file`: Đường dẫn file chứa links (bắt buộc)
- `--category`: Tên chuyên mục để tổ chức file output
- `--start`: Số thứ tự bắt đầu (mặc định: 0)
- `--max`: Số bài viết tối đa (mặc định: 200)
- `--no-headless`: Hiển thị trình duyệt

### 3. Sử dụng trong code Python

```python
from src.link_collector import LinkCollector
from src.article_crawler import ArticleCrawler
from pathlib import Path

# Thu thập links
with LinkCollector(headless=True) as collector:
    collector.collect_and_save(
        url="https://znews.vn/bong-da-viet-nam.html",
        output_file="links_bongda.txt",
        target_year=2024,
        max_links=200
    )

# Crawl bài viết
with ArticleCrawler(headless=True) as crawler:
    crawler.crawl_from_file(
        links_file=Path("data/links/links_bongda.txt"),
        category="bong_da",
        max_articles=200
    )
```

## ⚙️ Cấu hình

Chỉnh sửa [config/config.py](config/config.py) để tùy chỉnh:

```python
# Crawling settings
SCROLL_PAUSE_TIME = 2           # Thời gian chờ giữa các lần scroll (giây)
MAX_SCROLLS = 50                # Số lần scroll tối đa
TARGET_YEAR = 2024              # Năm mục tiêu
MAX_ARTICLES = 200              # Số bài viết tối đa

# Chrome options
CHROME_OPTIONS = {
    "headless": True,           # Chạy ẩn trình duyệt
    "disable_gpu": True,
    "no_sandbox": True,
}

# URLs
ZNEWS_URLS = {
    "bong_da": "https://znews.vn/bong-da-viet-nam.html",
    "giao_duc": "https://lifestyle.znews.vn/giao-duc.html",
    "phap_luat": "https://zingnews.vn/phap-luat.html"
}
```

## 📊 Định dạng dữ liệu

### File links (*.txt)

```
https://znews.vn/article-1.html
https://znews.vn/article-2.html
https://znews.vn/article-3.html
```

### File bài viết (*.json)

```json
{
    "url": "https://znews.vn/article-1.html",
    "title": "Tiêu đề bài viết",
    "content": "Nội dung bài viết...\n\nCác đoạn văn...",
    "metadata": {
        "images": [
            {
                "url": "https://example.com/image1.jpg",
                "caption": "Mô tả ảnh 1"
            },
            {
                "url": "https://example.com/image2.jpg",
                "caption": "Mô tả ảnh 2"
            }
        ]
    }
}
```

## 📝 Logging

Log được lưu tự động tại `logs/crawler.log`:

```
2024-12-25 10:30:15 - LinkCollector - INFO - Starting link collection from https://znews.vn/bong-da-viet-nam.html
2024-12-25 10:30:20 - LinkCollector - INFO - Collected 150 links
2024-12-25 10:30:25 - ArticleCrawler - INFO - Crawling article 1/150
2024-12-25 10:30:30 - ArticleCrawler - INFO - Successfully crawled: Tiêu đề bài viết
```

## 🔍 Troubleshooting

### Lỗi ChromeDriver

```
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: 
This version of ChromeDriver only supports Chrome version XX
```

**Giải pháp**: Tải ChromeDriver phù hợp với phiên bản Chrome của bạn.

### Lỗi không tìm thấy ChromeDriver

```
FileNotFoundError: [Errno 2] No such file or directory: 'chromedriver'
```

**Giải pháp**: 
1. Đảm bảo file `chromedriver` nằm trong thư mục gốc
2. Trên Linux/Mac, cấp quyền: `chmod +x chromedriver`
3. Cập nhật đường dẫn trong `config/config.py` nếu cần

### Không thu thập được links

**Giải pháp**:
1. Thử tăng `SCROLL_PAUSE_TIME` trong config
2. Chạy với `--no-headless` để xem trình duyệt
3. Kiểm tra cấu trúc HTML của website có thay đổi không

### Lỗi encoding trên Windows

```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Giải pháp**: Đã được xử lý sẵn với `encoding='utf-8'` trong code.

## 🎯 Best Practices

1. **Tôn trọng website**: Không crawl quá nhanh, sử dụng delays hợp lý
2. **Headless mode**: Luôn dùng `headless=True` khi chạy production
3. **Error handling**: Kiểm tra logs thường xuyên
4. **Backup data**: Sao lưu dữ liệu định kỳ
5. **Update ChromeDriver**: Cập nhật khi Chrome được nâng cấp

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- [Selenium](https://www.selenium.dev/) - Web automation framework
- [ChromeDriver](https://chromedriver.chromium.org/) - Chrome WebDriver


⭐ Nếu project này hữu ích, hãy cho nó một star!
