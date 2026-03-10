"""
URL Crawling Service
Fetches and extracts text content from web pages
"""

import re

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify


class CrawlError(Exception):
    pass


def _find_main_content(soup: BeautifulSoup) -> BeautifulSoup:
    """Try to find the main content area, fall back to body."""
    # Prefer semantic content containers
    for selector in ["article", "main", '[role="main"]', ".post-content", ".article-content", ".entry-content"]:
        el = soup.select_one(selector)
        if el and len(el.get_text(strip=True)) > 200:
            return el

    return soup.body or soup


async def crawl_url(url: str) -> str:
    """Crawl a URL and extract its main text content as markdown."""
    if not url.startswith(("http://", "https://")):
        raise CrawlError("URL must start with http:// or https://")

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; Explaino/1.0)"},
            )
            response.raise_for_status()
    except httpx.TimeoutException:
        raise CrawlError("Request timed out")
    except httpx.HTTPStatusError as e:
        raise CrawlError(f"HTTP error {e.response.status_code}")
    except httpx.RequestError as e:
        raise CrawlError(f"Failed to fetch URL: {e}")

    soup = BeautifulSoup(response.text, "lxml")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "iframe", "aside", "form"]):
        tag.decompose()

    content = _find_main_content(soup)

    # Convert HTML to markdown — preserves headings, lists, links, bold/italic, etc.
    md = markdownify(str(content), heading_style="ATX", strip=["img"])

    # Clean up excessive blank lines
    md = re.sub(r"\n{3,}", "\n\n", md).strip()

    if not md:
        raise CrawlError("No text content found on the page")

    return md
