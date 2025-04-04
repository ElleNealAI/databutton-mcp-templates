# DuckDuckGo Search API

A web search tool that enables your AI agent to search the internet using DuckDuckGo's search engine. This API requires no API key and provides current information from the web.

## Features
- Free web searching with no API keys required
- Configurable number of search results (up to 20)
- Returns structured search results with title, URL, and snippet text
- Handles timeouts and errors gracefully
- Built-in performance optimizations

## When to Use This API
- When your agent needs to find current information on any topic
- To answer user questions that require up-to-date information
- For researching specific topics on the web
- To provide information beyond your agent's knowledge cutoff date

## Dependencies
- `fastapi`: Web framework for building the API
- `pydantic`: Data validation and settings management
- `duckduckgo_search`: Python wrapper for DuckDuckGo search
- `databutton`: Already installed in your Databutton environment

## Installation
1. Create a new API in your Databutton application
2. Create a folder structure: `API Templates > Search > DuckDuckGo`
3. Copy the `duckduckgo_search.py` file into this folder
4. Install the required dependency:
   ```
   pip install duckduckgo_search
   ```
5. Save and deploy the API

## How It Works
The API sends search queries to DuckDuckGo using the `duckduckgo_search` package. It processes the results, formats them in a structured way, and returns them as JSON. The API includes timeout handling to prevent long-running queries and has built-in error handling for reliability.

## Configuration Options
- `query`: The search term or question (required)
- `max_results`: Number of results to return (optional, default: 10, max: 20)
- `timeout`: Internal timeout setting (10 seconds, can be adjusted in code)

## Example Usage
Your AI agent can use this API with a request like:

```json
{
  "query": "latest developments in renewable energy",
  "max_results": 5
}
```

Example response:
```json
{
  "success": true,
  "message": "Found 5 results for query: latest developments in renewable energy",
  "results": [
    {
      "title": "Recent Advances in Renewable Energy Technologies",
      "url": "https://example.com/renewable-energy-advances",
      "snippet": "New breakthroughs in solar efficiency and wind turbine design are revolutionizing the renewable energy sector..."
    },
    ...
  ],
  "query": "latest developments in renewable energy",
  "execution_time": 0.85
}
```

## Limitations
- Results are limited to what DuckDuckGo can find and may vary over time
- Maximum of 20 results per request for performance reasons
- The API has a 15-second timeout to prevent long-running queries
- No access to specialized search features like image search or news filtering
- DuckDuckGo may occasionally block automated requests if used very frequently

## Agent Integration Tip
Add this instruction to your agent: "When you need to find current information, use the DuckDuckGo Search API first, then analyze the results to provide the most relevant and up-to-date answer."
