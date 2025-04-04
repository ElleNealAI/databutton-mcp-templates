# URL Content Extractor API

An API that extracts and processes content from web pages, focusing on the main text while filtering out navigation, ads, and other non-essential elements.

## Features
- Extracts main text content from web pages
- Retrieves page metadata (title, description)
- Optionally extracts links with their text
- Optionally extracts images with their attributes
- Cleans and formats content for better readability
- Handles relative URLs and converts them to absolute URLs
- Provides word count and processing time metrics

## When to Use This API
- When you need to analyze the content of specific web pages
- To extract the main text from news articles or blog posts
- To gather detailed information from pages found in search results
- When you need to process web content before analyzing it
- To extract structured data like links and images from web pages

## Dependencies
- `fastapi`: Web framework for building the API
- `pydantic`: Data validation and settings management
- `requests`: HTTP client for fetching web pages
- `beautifulsoup4`: HTML parsing and content extraction
- `databutton`: Already installed in your Databutton environment

## Installation
1. Create a new API in your Databutton application
2. Create a folder structure: `API Templates > Search > URLContentExtractor`
3. Copy the `url_content_extractor.py` file into this folder
4. Install the required dependencies:
   ```
   pip install requests beautifulsoup4
   ```
5. Save and deploy the API

## How It Works
The API sends an HTTP request to the specified URL, retrieves the HTML content, and uses BeautifulSoup to parse and extract the main content. It identifies the most likely content area (such as article or main tags), removes navigation and advertisement elements, and extracts the text. Additionally, it can extract links and images, normalizing relative URLs to absolute ones.

## Configuration Options
- `url`: The web page URL to extract content from (required)
- `extract_links`: Whether to extract links from the page (default: false)
- `extract_images`: Whether to extract image information (default: false)
- `timeout`: Request timeout in seconds (default: 10, range: 3-30)

## Example Usage
Your AI agent can use this API with a request like:

```json
{
  "url": "https://example.com/article/renewable-energy-advances",
  "extract_links": true,
  "extract_images": false,
  "timeout": 15
}
```

Example response:
```json
{
  "success": true,
  "message": "Content extracted successfully",
  "url": "https://example.com/article/renewable-energy-advances",
  "title": "Recent Advances in Renewable Energy Technologies",
  "content": "New breakthroughs in solar efficiency and wind turbine design are revolutionizing the renewable energy sector...",
  "description": "An overview of the latest developments in renewable energy technology",
  "word_count": 1250,
  "links": [
    {
      "url": "https://example.com/related/solar-panels",
      "text": "Advanced Solar Panel Technology"
    },
    {
      "url": "https://example.com/related/wind-energy",
      "text": "Offshore Wind Farm Innovations"
    }
  ],
  "images": null,
  "fetch_time": 0.86
}
```

## Limitations
- Complex JavaScript-rendered content may not be properly extracted
- Some websites block automated requests
- Very large pages may have content truncated
- The API focuses on text content and may not extract specialized content like tables or complex layouts
- Cannot bypass paywalls or access protected content
- Content quality depends on the structure of the original website

## Agent Integration Tip
Add this instruction to your agent: "When you need detailed information from a specific web page, first use the DuckDuckGo Search API to find relevant pages, then use the URL Content Extractor API to get the full content from the most promising results."
