import requests
import re
import urllib.request
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os
import shutil
import argparse

# Regex pattern to match a URL
HTTP_URL_PATTERN = r"^http[s]*://.+"


class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hyperlinks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and "href" in attrs:
            href = attrs["href"]
            if self.is_webpage_link(href):
                self.hyperlinks.append(href)

    def is_webpage_link(self, href):
        if href.startswith(("mailto:", "tel:")):
            return False
        parts = href.split("/")
        if parts[-1] and "." in parts[-1]:
            return False
        return True


def get_hyperlinks(url):
    try:
        with urllib.request.urlopen(url) as response:
            if not response.info().get("Content-Type").startswith("text/html"):
                return []
            html = response.read().decode("utf-8")
    except Exception as e:
        print(e)
        return []

    parser = HyperlinkParser()
    parser.feed(html)
    return parser.hyperlinks


def get_domain_hyperlinks(local_domain, url, base_path):
    clean_links = []
    for link in set(get_hyperlinks(url)):
        clean_link = None

        if re.search(HTTP_URL_PATTERN, link):
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain and url_obj.path.startswith(base_path):
                clean_link = link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif link.startswith("#") or link.startswith("mailto:"):
                continue

            if link.startswith(base_path[1:]):
                clean_link = "https://" + local_domain + "/" + link

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    return list(set(clean_links))


def crawl(url, max_depth=1):
    parsed_url = urlparse(url)
    local_domain = parsed_url.netloc
    base_path = parsed_url.path

    if os.path.exists("processed/"):
        shutil.rmtree("processed/")
    os.mkdir("processed/")

    queue = deque([(url, 0)])
    seen = set([url])
    combined_content = "<html><body>"

    while queue:
        url, depth = queue.popleft()
        print(f"Crawling {url} at depth {depth}")

        if depth > max_depth:
            continue

        try:
            response = requests.get(url)
            html_content = response.text

            # Extract the main content using BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            main_content = soup.find("main") or soup.find("body")

            if main_content:
                combined_content += f"<h2>{url}</h2>"
                combined_content += str(main_content)
                print(f"HTML content added from: {url}")
            else:
                print(f"Could not extract main HTML content from {url}")
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")

        if depth < max_depth:
            for link in get_domain_hyperlinks(local_domain, url, base_path):
                if link not in seen:
                    queue.append((link, depth + 1))
                    seen.add(link)

    combined_content += "</body></html>"

    # Save all combined content in a single HTML file
    output_file = "processed/combined_content.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(combined_content)
    print(f"Combined HTML file has been created: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument(
        "--url", default="https://udc.es/es/goberno/", help="Full URL to crawl"
    )
    args = parser.parse_args()

    full_url = args.url
    domain = urlparse(full_url).netloc

    crawl(full_url, max_depth=1)
