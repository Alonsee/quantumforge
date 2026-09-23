#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import time
from urllib.parse import urlparse
import re
import shutil

import requests
from bs4 import BeautifulSoup

def extract_title_from_first_line(text):
    lines = text.split('\n')
    if not lines:
        return text, "unknown"

    first_line = lines[0].strip()

    parts = first_line.split(' | ')
    if parts:
        title_part = parts[0].strip()

        lines[0] = title_part

        cleaned_text = '\n'.join(lines)

        safe_title = re.sub(r'[^\w\s-]', '', title_part)
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        safe_title = safe_title.strip('-_')

        return cleaned_text, safe_title

    return text, "unknown"

def clear_text(html_content) -> str:
    """
    removes html tags
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'table']):
        element.decompose()

    for img in soup.find_all('img'):
        img.decompose()

    for div in soup.find_all(['div', 'span'], class_=re.compile(r'menu|nav|sidebar|footer|header')):
        div.decompose()

    text = soup.get_text()

    text = text.replace("- We are currently in the application process for electing a new admin. If you're interested, visit this page to apply", "")
    text = text.replace("Jump to content", "")
    text = text.replace("From Wikipedia, the free encyclopedia", "")
    text = text.replace("Fictional character from the American sitcom Buddys", "")
    text = text.replace("Fictional character", "")
    text = text.replace("READ MORE", "")
    text = text.replace("Advertisement", "")
    text = text.replace("Skip to content", "")
    text = text.replace(" | Friends Central | Fandom", "")
    text = text.replace(" | Fandom", "")
    text = text.replace(" - Wikipedia", "")

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines if line.strip() for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    re.sub(r'^$', '', text)

    return text

def download_page(url):
    """
    download page from url
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)

        response.raise_for_status()

        if response.encoding.lower() != 'utf-8':
            response.encoding = 'utf-8'

        return response.text

    except requests.exceptions.RequestException as e:
        print(f"failed to download from URL {url}: {e}")
        return None
    except Exception as e:
        print(f"failed to download from URL {url}: {e}")
        return None

def save_text_to_file(text, url, counter, title):
    """
    save page content to file
    """
    if title and title != 'unknown':
        filename = f"raw_data/{title}.txt"
    else:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('.', '_')
        path = parsed_url.path.replace('/', '_').replace('?', '_').replace('=', '_')[:50]

        filename = f"raw_data/{counter:03d}_{domain}_{path}.txt"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"saved: {filename}")
    except Exception as e:
        print(f"failed to save file {filename}: {e}")

def main():
    if os.path.exists('raw_data'):
        shutil.rmtree('raw_data')
    os.makedirs('raw_data', exist_ok=True)

    json_file = "etc/raw_data_url_list.json"

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            urls = json.load(f)

        print(f"loaded {len(urls)} URL from {json_file}")

    except FileNotFoundError:
        print(f"not found file {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"failed to read JSON {json_file}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"unknown error during reading file: {e}")
        sys.exit(1)

    downloaded_count = 0

    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] start to process URL: {url}")

        html_content = download_page(url)
        if html_content is None:
            print(f"skip error URL: {url}")
            continue

        clean_text = clear_text(html_content)

        if not clean_text or len(clean_text.strip()) < 100:
            print(f"small page content: ({len(clean_text)} chars): {url}")
            continue

        modified_text, title = extract_title_from_first_line(clean_text)

        save_text_to_file(clean_text, url, downloaded_count + 1, title)
        downloaded_count += 1

        print(f"successfully: {downloaded_count}/{len(urls)}")

        time.sleep(1)

    print(f"\nall URLs processed")
    print(f"all URLs processed, loaded {downloaded_count} pages")

if __name__ == "__main__":
    main()
