# Knowledge Base API

A FastAPI-based knowledge management system that allows storing, retrieving, updating, and deleting knowledge items. This API provides a structured way to maintain a domain-specific knowledge base, making information easily accessible and searchable.

## Features

- Add new knowledge items with topics, content, and keywords
- Search the knowledge base using relevance scoring
- List all available knowledge items
- Update existing knowledge entries
- Delete outdated or incorrect information

## Installation

### Prerequisites

- Python 3.7+
- FastAPI
- Pydantic
- Databutton

### Setup

1. Install the required dependencies:

```bash
pip install fastapi pydantic databutton uvicorn
```

2. Import the router in your main FastAPI application:

```python
from fastapi import FastAPI
from knowledge_base import router as knowledge_router

app = FastAPI()
app.include_router(knowledge_router, prefix="/api/knowledge", tags=["Knowledge Base"])
```

## Usage

### Data Models

#### KnowledgeItem

Used to add new knowledge items:

```python
class KnowledgeItem(BaseModel):
    topic: str
    content: str
    keywords: List[str] = []
```

#### KnowledgeUpdateRequest

Used to update existing knowledge items:

```python
class KnowledgeUpdateRequest(BaseModel):
    id: str
    topic: Optional[str] = None
    content: Optional[str] = None
    keywords: Optional[List[str]] = None
```

#### KnowledgeSearchRequest

Used to search the knowledge base:

```python
class KnowledgeSearchRequest(BaseModel):
    query: str
    limit: int = 10  # Maximum 50
```

### API Endpoints

#### Add Knowledge

```
POST /add-knowledge
```

Adds a new piece of knowledge to the knowledge base.

**Request Body:**
```json
{
    "topic": "Solar System",
    "content": "Jupiter is the largest planet in our solar system.",
    "keywords": ["planets", "astronomy", "gas giant", "Jupiter"]
}
```

**Response:**
```json
{
    "success": true,
    "message": "Knowledge item added successfully",
    "data": {
        "id": "kb_20230701143210",
        "topic": "Solar System",
        "content": "Jupiter is the largest planet in our solar system.",
        "keywords": ["planets", "astronomy", "gas giant", "Jupiter"],
        "created_at": "2023-07-01T14:32:10"
    }
}
```

#### Search Knowledge

```
POST /search-knowledge
```

Searches the knowledge base for relevant information using a query string.

**Request Body:**
```json
{
    "query": "Jupiter planet",
    "limit": 5
}
```

**Response:**
```json
{
    "success": true,
    "message": "Found 1 matching items",
    "items": [
        {
            "id": "kb_20230701143210",
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

#### List Knowledge

```
GET /list-knowledge?limit=20
```

Lists all items in the knowledge base, with the most recent first.

**Response:**
```json
{
    "success": true,
    "message": "Retrieved 1 knowledge items",
    "items": [
        {
            "id": "kb_20230701143210",
            "topic": "Solar System",
            "content": "Jupiter is the largest planet in our solar system.",
            "keywords": ["planets", "astronomy", "gas giant", "Jupiter"],
            "created_at": "2023-07-01T14:32:10"
        }
    ],
    "count": 1
}
```

#### Update Knowledge

```
POST /update-knowledge
```

Updates an existing knowledge item.

**Request Body:**
```json
{
    "id": "kb_20230701143210",
    "content": "Jupiter is the largest planet in our solar system, with a mass of 1.898 × 10^27 kg.",
    "keywords": ["planets", "astronomy", "gas giant", "Jupiter", "mass"]
}
```

**Response:**
```json
{
    "success": true,
    "message": "Knowledge item updated successfully",
    "data": {
        "id": "kb_20230701143210",
        "topic": "Solar System",
        "content": "Jupiter is the largest planet in our solar system, with a mass of 1.898 × 10^27 kg.",
        "keywords": ["planets", "astronomy", "gas giant", "Jupiter", "mass"],
        "created_at": "2023-07-01T14:32:10",
        "updated_at": "2023-07-02T09:15:22"
    }
}
```

#### Delete Knowledge

```
DELETE /delete-knowledge/{item_id}
```

Deletes a knowledge item from the knowledge base.

**Response:**
```json
{
    "success": true,
    "message": "Knowledge item deleted successfully"
}
```

## Internal Storage

The knowledge base uses Databutton's JSON storage system to persist data. All knowledge items are stored under a single key (`"knowledge_base"`) as a dictionary, with each item's ID serving as the key within that dictionary.

## Error Handling

All endpoints include appropriate error handling and will return meaningful error messages if something goes wrong during the operation.

## Search Relevance Scoring

The search algorithm uses a simple relevance scoring system:
- 0.5 points for topic matches
- 0.3 points for content matches
- 0.2 points distributed proportionally based on keyword matches

Results are sorted by relevance score in descending order.

## Use Cases

This knowledge base API is designed for:

1. Building and maintaining domain-specific knowledge
2. Storing information that needs to be retrieved later
3. Creating a searchable repository of facts and information
4. Enabling AI agents to remember important information across sessions

## License

[MIT License]
