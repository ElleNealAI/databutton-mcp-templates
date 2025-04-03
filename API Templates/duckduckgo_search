from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
import databutton as db
from typing import List, Dict, Optional
from duckduckgo_search import DDGS
import time
import traceback
from contextlib import contextmanager

router = APIRouter()

# Initialize DuckDuckGo Search
ddgs = DDGS(timeout=10)  # Set a timeout of 10 seconds for DuckDuckGo searches

class SearchRequest(BaseModel):
    query: str = Field(..., description="The search query to run.")
    max_results: int = Field(10, description="Maximum number of search results to return (1-20).", ge=1, le=20)
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str

class SearchResponse(BaseModel):
    success: bool
    message: str
    results: List[SearchResult] = []
    query: str
    execution_time: float

@contextmanager
def timeout_handler(seconds, operation_name="Operation"):
    """Context manager to handle timeouts on operations."""
    start_time = time.time()
    try:
        yield
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"{operation_name} failed after {elapsed:.2f} seconds with error: {str(e)}")
        print(traceback.format_exc())
        raise
    finally:
        elapsed = time.time() - start_time
        print(f"{operation_name} completed in {elapsed:.2f} seconds")

def search_duckduckgo(query: str, max_results: int = 10) -> List[Dict]:
    """Perform a search on DuckDuckGo and return results."""
    try:
        with timeout_handler(15, f"DuckDuckGo search for '{query}'"):
            # Use the text search feature of DDGS
            results = ddgs.text(query, max_results=max_results)
            
            # Convert generator to list and add some safety limits
            results_list = []
            results_count = 0
            
            # Process search results with a hard limit on processing time
            start_time = time.time()
            for result in results:
                results_list.append(result)
                results_count += 1
                
                # Break if we exceed max results or take too long
                if results_count >= max_results or (time.time() - start_time) > 8:
                    break
                    
            print(f"Found {len(results_list)} results for query: '{query}'")
            return results_list
    except Exception as e:
        print(f"Error searching DuckDuckGo: {str(e)}")
        print(traceback.format_exc())
        return []



@router.post("/search")
def perform_search(body: SearchRequest) -> SearchResponse:
    """Perform a web search using DuckDuckGo.
    
    What this API does:
    This endpoint executes a simple web search query using DuckDuckGo's search engine and returns the most relevant results.
    
    When to use it:
    - When you need to find up-to-date information on any topic
    - When your application needs to query external web sources 
    - For getting quick answers to user questions that require current information
    
    How to use it:
    Send a POST request with a JSON body containing:
    - query: The search term or question (required)
    - max_results: Number of results to return (optional, default: 10, max: 20)
    
    What to expect in the response:
    - A list of search results with title, URL, and a text snippet for each
    - Metadata about the search execution (timing, success status)
    
    Limitations and considerations:
    - Results are limited to what DuckDuckGo can find and may vary over time
    - Search queries should be concise and specific for best results
    - The API will timeout after 15 seconds to prevent long-running queries
    - There's a limit of 20 results per request for performance reasons
    """
    # Set an overall execution start time
    start_time = time.time()
    print(f"Starting search for query: '{body.query}'")
    
    try:
        query = body.query.strip()
        max_results = min(body.max_results, 20)  # Limit to 20 results max
        
        # Perform the search
        search_results = search_duckduckgo(query, max_results)
        
        if not search_results:
            print("No search results found")
            execution_time = time.time() - start_time
            return SearchResponse(
                success=False,
                message=f"No search results found for query: {query}",
                results=[],
                query=query,
                execution_time=execution_time
            )
        
        # Convert the raw results to the response format
        formatted_results = []
        for result in search_results:
            formatted_results.append(SearchResult(
                title=result.get('title', 'No title'),
                url=result.get('href', 'No URL'),
                snippet=result.get('body', 'No snippet')
            ))
        
        # Calculate total execution time
        execution_time = time.time() - start_time
        print(f"Search completed in {execution_time:.2f} seconds with {len(formatted_results)} results")
        
        return SearchResponse(
            success=True,
            message=f"Found {len(formatted_results)} results for query: {query}",
            results=formatted_results,
            query=query,
            execution_time=execution_time
        )
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"Error performing search after {execution_time:.2f} seconds: {str(e)}")
        print(traceback.format_exc())
        
        # Create a valid response even in case of error
        return SearchResponse(
            success=False,
            message=f"Search error: {str(e)}",
            results=[],
            query=body.query,
            execution_time=execution_time
        )
