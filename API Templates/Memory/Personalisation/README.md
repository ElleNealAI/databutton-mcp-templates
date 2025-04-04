# Read and Store Memories API

A simple yet powerful API that allows your AI agent to store and retrieve key insights about users, enabling more personalized interactions and long-term memory across conversations.

## Features
- Store important user preferences, habits, and goals
- Maintain continuity across multiple conversations
- Create a persistent memory system for your AI agent
- Simple API with minimal configuration required
- Uses Databutton's built-in storage (no external dependencies)

## When to Use This API
- When building personalized AI assistants that remember user preferences
- To improve user experience by avoiding repetitive questions
- When creating agents that adapt to individual users over time
- To store important information that should persist between sessions
- For implementing "memory" capabilities in conversational agents

## Dependencies
- `fastapi`: Web framework for building the API
- `pydantic`: Data validation and settings management
- `databutton`: Already installed in your Databutton environment

## Installation
1. Create a new API in your Databutton application
2. Create a folder structure: `API Templates > Memory > ReadAndStoreMemories`
3. Copy the `read_and_store_memories.py` file into this folder
4. Save and deploy the API

## How It Works
The API provides a simple endpoint for storing "insights" about users. These insights are text snippets containing important information like preferences, habits, goals, or other relevant details. The API stores these memories in Databutton's persistent storage as a JSON array, making them available for future interactions. The agent can retrieve these memories before generating responses, enabling personalized conversations.

## Configuration Options
- `insight`: The user insight to store (required) - this can be any text string containing information about the user

## Example Usage
Your AI agent can use this API with a request like:

```json
{
  "insight": "User prefers casual communication style and dislikes technical jargon."
}
```

Example response:
```json
{
  "success": true,
  "message": "Memory successfully stored."
}
```

To retrieve memories:
```python
# In your agent's code or within Databutton
try:
    memories = db.storage.json.get("memories")
    # Use memories to personalize interaction
except FileNotFoundError:
    memories = []
```

## Limitations
- Simple key-value storage (no complex querying or filtering)
- No built-in categorization of memories (manual tagging required)
- Limited to text-based insights (no structured data support)
- No automatic prioritization or relevance scoring
- All memories are stored in a single list (could grow large over time)
- No automatic cleanup or memory management

## Agent Integration Tip
Add these instructions to your agent: 
1. "Before responding to the user, check for any stored memories that might be relevant to the current conversation."
2. "When you learn important information about the user, store it as a memory using the Store Memory API."
3. "Use memories to personalize your responses, but do so naturally without explicitly mentioning that you're using stored information."
