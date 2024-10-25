# smalltools
Small tool scripts

# Web Crawler `webcrawler.py`

This repository contains a Python script called `webcrawler.py`, which functions as a web crawler designed to extract and combine content from a specified website and its linked pages.

## Purpose

1. Crawl a given website up to a specified depth.
2. Extract the main content from each page.
3. Combine the extracted content into a single HTML file.

## Usage

1. Run the script from the command line.
2. Use the `--url` argument to specify the starting URL for crawling.
3. The script will create a "processed" folder and save the combined content in "processed/combined_content.html".

Example usage: `python webcrawler.py --url https://udc.es/es/goberno/`

