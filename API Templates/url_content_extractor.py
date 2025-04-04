from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl, validator
import databutton as db
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
import re
import traceback
from urllib.parse import urlparse

router = APIRouter()

class ExtractRequest(BaseModel):
    url: str = Field(..., description="The URL to extract content from")
    extract_links: bool = Field(False, description="Whether to extract links from the page")
    extract_images: bool = Field(False, description="Whether to extract image information")
    timeout: int = Field(10, description="Request timeout in seconds", ge=3, le=30)
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        # Simple URL validation
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL")
        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")
        return v

class ContentResponse(BaseModel):
    success: bool
    message: str
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    word_count: Optional[int] = None
    links: Optional[List[Dict[str, str]]] = None
    images: Optional[List[Dict[str, str]]] = None
    fetch_time: float

# List of common block elements for content extraction
BLOCK_ELEMENTS = [
    "div", "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "article", "section", "main", "header", "footer"
]

# List of elements to exclude from content extraction
EXCLUDE_ELEMENTS = [
    "nav", "sidebar", "advertisement", "ad", "footer", "comment", 
    "menu", "sidebar", "related", "promo", "banner", "popup"
]

# User agent string to mimic a browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def clean_text(text):
    """Clean up extracted text by removing extra whitespace."""
    # Replace multiple newlines with a single one
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # Replace multiple spaces with a single one
    text = re.sub(r' +', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()

def extract_main_content(soup):
    """Extract the main text content from the page, focusing on article/content areas."""
    # Try to find the main content area (common patterns)
    main_content_candidates = soup.select('article, [role="main"], main, .content, .post, .article, #content, #main')
    
    # If a likely main content area is found, extract from there
    if main_content_candidates:
        main_element = main_content_candidates[0]
        # Remove unwanted elements from the content area
        for element in main_element.select(','.join([f'.{cls}' for cls in EXCLUDE_ELEMENTS]) + ',' + 
                                         ','.join([f'#{cls}' for cls in EXCLUDE_ELEMENTS])):
            element.decompose()
        
        # Extract and join text from all paragraph elements
        paragraphs = main_element.find_all('p')
        if paragraphs:
            return '\n\n'.join([p.get_text() for p in paragraphs])
        
        # If no paragraphs, just get all the text
        return main_element.get_text()
    
    # Fallback: get all paragraph text
    paragraphs = soup.find_all('p')
    if paragraphs:
        return '\n\n'.join([p.get_text() for p in paragraphs])
    
    # Last resort: just get all text from the body
    body = soup.find('body')
    if body:
        for element in body.select(','.join([f'.{cls}' for cls in EXCLUDE_ELEMENTS]) + ',' + 
                                  ','.join([f'#{cls}' for cls in EXCLUDE_ELEMENTS])):
            element.decompose()
        return body.get_text()
    
    # If we can't find anything, return empty string
    return ""

def extract_links(soup, base_url):
    """Extract links from the page with their text."""
    links = []
    link_elements = soup.find_all('a', href=True)
    
    for link in link_elements:
        href = link['href']
        
        # Skip empty links, javascript, and anchor links
        if not href or href.startswith(('javascript:', '#', 'mailto:', 'tel:')):
            continue
        
        # Handle relative URLs
        if not href.startswith(('http://', 'https://')):
            # Parse the base URL
            parsed_base = urlparse(base_url)
            base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
            
            if href.startswith('/'):
                href = f"{base_domain}{href}"
            else:
                path_parts = parsed_base.path.split('/')
                if len(path_parts) > 0:
                    path_parts.pop()  # Remove the last part (filename or empty)
                base_path = '/'.join(path_parts)
                href = f"{base_domain}{base_path}/{href}"
        
        # Extract text and clean it
        text = link.get_text().strip()
        if text:
            links.append({
                "url": href,
                "text": text
            })
    
    return links

def extract_images(soup, base_url):
    """Extract image information from the page."""
    images = []
    img_elements = soup.find_all('img')
    
    for img in img_elements:
        src = img.get('src', '')
        if not src:
            continue
        
        # Handle relative URLs for images
        if not src.startswith(('http://', 'https://', 'data:')):
            # Parse the base URL
            parsed_base = urlparse(base_url)
            base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
            
            if src.startswith('/'):
                src = f"{base_domain}{src}"
            else:
                path_parts = parsed_base.path.split('/')
                if len(path_parts) > 0:
                    path_parts.pop()  # Remove the last part (filename or empty)
                base_path = '/'.join(path_parts)
                src = f"{base_domain}{base_path}/{src}"
        
        alt_text = img.get('alt', '')
        
        images.append({
            "src": src,
            "alt": alt_text,
            "width": img.get('width', ''),
            "height": img.get('height', '')
        })
    
    return images

@router.post("/extract")
def extract_content(body: ExtractRequest) -> ContentResponse:
    """
    Extracts and processes content from a URL.
    
    This API fetches a web page, extracts the main content, title, description, 
    and optionally links and images. It's designed to get the most relevant information
    from web pages while filtering out navigation, ads, and other non-content elements.
    
    ### When to Use:
    - When you need to analyze the content of a specific web page
    - When you want to extract the main text content from an article
    - When you need to gather information from a web page that was found in search results
    - When you need to extract structured data (links, images) from a web page
    
    ### How to Use:
    Send a POST request with a JSON body containing:
    ```json
    {
        "url": "https://example.com/article",
        "extract_links": true,
        "extract_images": false,
        "timeout": 10
    }
    ```
    
    ### Response Format:
    - Success:
    ```json
    {
        "success": true,
        "message": "Content extracted successfully",
        "url": "https://example.com/article",
        "title": "Example Article Title",
        "content": "This is the main text content of the article...",
        "description": "Article meta description if available",
        "word_count": 1250,
        "links": [
            {"url": "https://example.com/related", "text": "Related Article"}
        ],
        "images": null,
        "fetch_time": 0.85
    }
    ```
    - Failure:
    ```json
    {
        "success": false,
        "message": "Failed to extract content: Connection timeout",
        "url": "https://example.com/article",
        "title": null,
        "content": null,
        "description": null,
        "word_count": null,
        "links": null,
        "images": null,
        "fetch_time": 10.02
    }
    ```
    
    ### Limitations:
    - Complex JavaScript-rendered content may not be properly extracted
    - Some websites block automated requests
    - Very large pages may be truncated
    - The API focuses on text content and may not extract specialized content like tables
    """
    start_time = time.time()
    
    try:
        # Send HTTP request to get the page
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        print(f"Fetching URL: {body.url}")
        response = requests.get(
            body.url, 
            headers=headers, 
            timeout=body.timeout,
            allow_redirects=True
        )
        
        # Check if the request was successful
        if response.status_code != 200:
            fetch_time = time.time() - start_time
            return ContentResponse(
                success=False,
                message=f"Failed to fetch URL: HTTP status {response.status_code}",
                url=body.url,
                fetch_time=fetch_time
            )
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type and 'application/xhtml+xml' not in content_type:
            fetch_time = time.time() - start_time
            return ContentResponse(
                success=False,
                message=f"URL does not contain HTML content (Content-Type: {content_type})",
                url=body.url,
                fetch_time=fetch_time
            )
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else None
        
        # Extract description
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        description = meta_desc['content'].strip() if meta_desc and 'content' in meta_desc.attrs else None
        
        # Extract main content
        content = extract_main_content(soup)
        cleaned_content = clean_text(content)
        
        # Calculate word count
        word_count = len(re.findall(r'\w+', cleaned_content)) if cleaned_content else 0
        
        # Extract links if requested
        links = None
        if body.extract_links:
            links = extract_links(soup, body.url)
        
        # Extract images if requested
        images = None
        if body.extract_images:
            images = extract_images(soup, body.url)
        
        # Calculate fetch and processing time
        fetch_time = time.time() - start_time
        
        return ContentResponse(
            success=True,
            message="Content extracted successfully",
            url=body.url,
            title=title,
            content=cleaned_content[:100000],  # Limit content length to avoid exceeding response size limits
            description=description,
            word_count=word_count,
            links=links,
            images=images,
            fetch_time=fetch_time
        )
    
    except requests.exceptions.Timeout:
        fetch_time = time.time() - start_time
        return ContentResponse(
            success=False,
            message=f"Request timed out after {body.timeout} seconds",
            url=body.url,
            fetch_time=fetch_time
        )
    
    except requests.exceptions.RequestException as e:
        fetch_time = time.time() - start_time
        error_message = str(e)
        print(f"Request error: {error_message}")
        print(traceback.format_exc())
        
        return ContentResponse(
            success=False,
            message=f"Failed to fetch URL: {error_message}",
            url=body.url,
            fetch_time=fetch_time
        )
    
    except Exception as e:
        fetch_time = time.time() - start_time
        error_message = str(e)
        print(f"Processing error: {error_message}")
        print(traceback.format_exc())
        
        return ContentResponse(
            success=False,
            message=f"Failed to process content: {error_message}",
            url=body.url,
            fetch_time=fetch_time
        )
