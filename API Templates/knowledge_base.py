from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import databutton as db
from typing import List, Dict, Optional
from datetime import datetime
import re

router = APIRouter()

# Define data models
class KnowledgeItem(BaseModel):
    topic: str = Field(..., description="The main topic or category of this knowledge item")
    content: str = Field(..., description="The actual information or fact to store")
    keywords: List[str] = Field(default_factory=list, description="Related keywords for easier searching")
    
class KnowledgeUpdateRequest(BaseModel):
    id: str = Field(..., description="ID of the knowledge item to update")
    topic: Optional[str] = Field(None, description="Updated topic (if changing)")
    content: Optional[str] = Field(None, description="Updated content (if changing)")
    keywords: Optional[List[str]] = Field(None, description="Updated keywords (if changing)")

class KnowledgeResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., description="Search term to find relevant knowledge items")
    limit: int = Field(10, description="Maximum number of results to return", ge=1, le=50)

class KnowledgeListResponse(BaseModel):
    success: bool
    message: str
    items: List[Dict] = []
    count: int = 0

# Storage key for the knowledge base
KNOWLEDGE_BASE_KEY = "knowledge_base"

def get_knowledge_base():
    """Helper function to retrieve the knowledge base from storage"""
    try:
        return db.storage.json.get(KNOWLEDGE_BASE_KEY)
    except FileNotFoundError:
        # Initialize with empty dict if doesn't exist yet
        empty_kb = {}
        db.storage.json.put(KNOWLEDGE_BASE_KEY, empty_kb)
        return empty_kb

def save_knowledge_base(kb_data):
    """Helper function to save the knowledge base to storage"""
    db.storage.json.put(KNOWLEDGE_BASE_KEY, kb_data)

@router.post("/add-knowledge")
def add_knowledge(item: KnowledgeItem) -> KnowledgeResponse:
    """
    Adds a new piece of knowledge to the knowledge base.
    
    This endpoint allows AI agents to build and maintain a domain-specific knowledge base
    by storing information that can be retrieved later.
    
    ### When to Use:
    - When you encounter important information that should be remembered
    - To build a collection of facts about a specific domain
    - When information needs to be retrievable for future conversations
    
    ### How to Use:
    Send a POST request with a JSON body containing:
    ```json
    {
        "topic": "Solar System",
        "content": "Jupiter is the largest planet in our solar system.",
        "keywords": ["planets", "astronomy", "gas giant", "Jupiter"]
    }
    ```
    
    ### Response Format:
    - Success:
    ```json
    {
        "success": true,
        "message": "Knowledge item added successfully",
        "data": {
            "id": "kb_item_1234",
            "topic": "Solar System",
            "content": "Jupiter is the largest planet in our solar system.",
            "keywords": ["planets", "astronomy", "gas giant", "Jupiter"],
            "created_at": "2023-07-01T14:32:10"
        }
    }
    ```
    - Failure:
    ```json
    {
        "success": false,
        "message": "Failed to add knowledge item: error details"
    }
    ```
    """
    try:
        kb = get_knowledge_base()
        
        # Create a unique ID for the knowledge item
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        item_id = f"kb_{timestamp}"
        
        # Store the item with metadata
        kb[item_id] = {
            "id": item_id,
            "topic": item.topic,
            "content": item.content,
            "keywords": item.keywords,
            "created_at": datetime.now().isoformat()
        }
        
        save_knowledge_base(kb)
        
        return KnowledgeResponse(
            success=True,
            message="Knowledge item added successfully",
            data=kb[item_id]
        )
    except Exception as e:
        return KnowledgeResponse(
            success=False,
            message=f"Failed to add knowledge item: {str(e)}"
        )

@router.post("/search-knowledge")
def search_knowledge(search: KnowledgeSearchRequest) -> KnowledgeListResponse:
    """
    Searches the knowledge base for relevant information.
    
    This endpoint allows an AI agent to retrieve stored knowledge based on
    search terms, making it possible to recall information from previous interactions.
    
    ### When to Use:
    - When you need to retrieve specific information from the knowledge base
    - To check if certain information is already known before asking the user
    - When answering questions that might benefit from previously stored knowledge
    
    ### How to Use:
    Send a POST request with a JSON body containing:
    ```json
    {
        "query": "Jupiter planet",
        "limit": 5
    }
    ```
    
    ### Response Format:
    - Success with results:
    ```json
    {
        "success": true,
        "message": "Found 1 matching items",
        "items": [
            {
                "id": "kb_item_1234",
                "topic": "Solar System",
                "content": "Jupiter is the largest planet in our solar system.",
                "keywords": ["planets", "astronomy", "gas giant", "Jupiter"],
                "created_at": "2023-07-01T14:32:10",
                "relevance_score": 0.85
            }
        ],
        "count": 1
    }
    ```
    - Success with no results:
    ```json
    {
        "success": true,
        "message": "No matching items found",
        "items": [],
        "count": 0
    }
    ```
    - Failure:
    ```json
    {
        "success": false,
        "message": "Failed to search knowledge base: error details",
        "items": [],
        "count": 0
    }
    ```
    """
    try:
        kb = get_knowledge_base()
        query = search.query.lower()
        query_terms = set(re.findall(r'\w+', query))
        
        results = []
        
        # Search through all knowledge items
        for item_id, item in kb.items():
            # Check for matches in topic, content, and keywords
            topic_match = query.lower() in item['topic'].lower()
            content_match = query.lower() in item['content'].lower()
            
            # Calculate keyword overlap
            item_keywords = [k.lower() for k in item['keywords']]
            keyword_matches = sum(1 for term in query_terms if any(term in kw for kw in item_keywords))
            
            # Calculate a simple relevance score
            relevance = 0
            if topic_match:
                relevance += 0.5
            if content_match:
                relevance += 0.3
            relevance += 0.2 * (keyword_matches / max(1, len(query_terms)))
            
            if relevance > 0:
                result_item = item.copy()
                result_item["relevance_score"] = round(relevance, 2)
                results.append(result_item)
        
        # Sort by relevance score
        results = sorted(results, key=lambda x: x['relevance_score'], reverse=True)
        
        # Apply limit
        results = results[:search.limit]
        
        if results:
            return KnowledgeListResponse(
                success=True,
                message=f"Found {len(results)} matching items",
                items=results,
                count=len(results)
            )
        else:
            return KnowledgeListResponse(
                success=True,
                message="No matching items found",
                items=[],
                count=0
            )
            
    except Exception as e:
        return KnowledgeListResponse(
            success=False,
            message=f"Failed to search knowledge base: {str(e)}",
            items=[],
            count=0
        )

@router.get("/list-knowledge")
def list_knowledge(limit: int = 20) -> KnowledgeListResponse:
    """
    Lists all items in the knowledge base, most recent first.
    
    This endpoint allows AI agents to view the contents of the knowledge base.
    
    ### When to Use:
    - To get an overview of what information is already stored
    - When preparing a summary of known information
    - To check if the knowledge base contains enough information on a topic
    
    ### How to Use:
    Send a GET request to `/list-knowledge?limit=20`
    
    ### Response Format:
    - Success:
    ```json
    {
        "success": true,
        "message": "Retrieved 20 knowledge items",
        "items": [{...}, {...}],
        "count": 20
    }
    ```
    - Empty knowledge base:
    ```json
    {
        "success": true,
        "message": "Knowledge base is empty",
        "items": [],
        "count": 0
    }
    ```
    - Failure:
    ```json
    {
        "success": false,
        "message": "Failed to retrieve knowledge items: error details",
        "items": [],
        "count": 0
    }
    ```
    """
    try:
        kb = get_knowledge_base()
        
        if not kb:
            return KnowledgeListResponse(
                success=True,
                message="Knowledge base is empty",
                items=[],
                count=0
            )
        
        # Convert to list and sort by creation date, newest first
        items = list(kb.values())
        items.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Apply limit
        items = items[:limit]
        
        return KnowledgeListResponse(
            success=True,
            message=f"Retrieved {len(items)} knowledge items",
            items=items,
            count=len(items)
        )
    
    except Exception as e:
        return KnowledgeListResponse(
            success=False,
            message=f"Failed to retrieve knowledge items: {str(e)}",
            items=[],
            count=0
        )

@router.post("/update-knowledge")
def update_knowledge(update: KnowledgeUpdateRequest) -> KnowledgeResponse:
    """
    Updates an existing knowledge item.
    
    This endpoint allows AI agents to modify existing knowledge items when information
    changes or needs to be corrected.
    
    ### When to Use:
    - When information has changed and needs to be updated
    - To correct inaccurate information
    - To add more keywords to improve searchability
    
    ### How to Use:
    Send a POST request with a JSON body containing:
    ```json
    {
        "id": "kb_item_1234",
        "content": "Jupiter is the largest planet in our solar system, with a mass of 1.898 × 10^27 kg.",
        "keywords": ["planets", "astronomy", "gas giant", "Jupiter", "mass"]
    }
    ```
    
    ### Response Format:
    - Success:
    ```json
    {
        "success": true,
        "message": "Knowledge item updated successfully",
        "data": {
            "id": "kb_item_1234",
            "topic": "Solar System",
            "content": "Jupiter is the largest planet in our solar system, with a mass of 1.898 × 10^27 kg.",
            "keywords": ["planets", "astronomy", "gas giant", "Jupiter", "mass"],
            "created_at": "2023-07-01T14:32:10",
            "updated_at": "2023-07-02T09:15:22"
        }
    }
    ```
    - Item not found:
    ```json
    {
        "success": false,
        "message": "Knowledge item with ID kb_item_1234 not found"
    }
    ```
    - Failure:
    ```json
    {
        "success": false,
        "message": "Failed to update knowledge item: error details"
    }
    ```
    """
    try:
        kb = get_knowledge_base()
        
        if update.id not in kb:
            return KnowledgeResponse(
                success=False,
                message=f"Knowledge item with ID {update.id} not found"
            )
        
        # Update the specified fields
        if update.topic is not None:
            kb[update.id]['topic'] = update.topic
        
        if update.content is not None:
            kb[update.id]['content'] = update.content
            
        if update.keywords is not None:
            kb[update.id]['keywords'] = update.keywords
        
        # Add updated timestamp
        kb[update.id]['updated_at'] = datetime.now().isoformat()
        
        save_knowledge_base(kb)
        
        return KnowledgeResponse(
            success=True,
            message="Knowledge item updated successfully",
            data=kb[update.id]
        )
    
    except Exception as e:
        return KnowledgeResponse(
            success=False,
            message=f"Failed to update knowledge item: {str(e)}"
        )

@router.delete("/delete-knowledge/{item_id}")
def delete_knowledge(item_id: str) -> KnowledgeResponse:
    """
    Deletes a knowledge item from the knowledge base.
    
    This endpoint allows AI agents to remove outdated or incorrect information.
    
    ### When to Use:
    - When information is no longer relevant or accurate
    - To clean up the knowledge base
    - When information was stored by mistake
    
    ### How to Use:
    Send a DELETE request to `/delete-knowledge/kb_item_1234`
    
    ### Response Format:
    - Success:
    ```json
    {
        "success": true,
        "message": "Knowledge item deleted successfully"
    }
    ```
    - Item not found:
    ```json
    {
        "success": false,
        "message": "Knowledge item with ID kb_item_1234 not found"
    }
    ```
    - Failure:
    ```json
    {
        "success": false,
        "message": "Failed to delete knowledge item: error details"
    }
    ```
    """
    try:
        kb = get_knowledge_base()
        
        if item_id not in kb:
            return KnowledgeResponse(
                success=False,
                message=f"Knowledge item with ID {item_id} not found"
            )
        
        # Remove the item
        deleted_item = kb.pop(item_id)
        save_knowledge_base(kb)
        
        return KnowledgeResponse(
            success=True,
            message="Knowledge item deleted successfully"
        )
    
    except Exception as e:
        return KnowledgeResponse(
            success=False,
            message=f"Failed to delete knowledge item: {str(e)}"
        )
