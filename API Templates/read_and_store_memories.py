from fastapi import APIRouter
from pydantic import BaseModel
import databutton as db
from datetime import datetime

router = APIRouter()


class MemoryRequest(BaseModel):
    insight: str

class MemoryResponse(BaseModel):
    success: bool
    message: str

@router.post("/store-memory")
def store_memory(body: MemoryRequest) -> MemoryResponse:
    """
    Stores key insights about the user to improve AI personalization.
    
    This endpoint allows AI agents to store user preferences, goals, and relevant details
    to tailor future interactions. The AI should retrieve these stored memories before
    generating responses to maintain continuity.
    
    ### When to Use:
    - When the AI identifies key user preferences, habits, or goals.
    - To retain long-term knowledge about the user for a more personalized experience.
    - When AI needs to track persistent user data across sessions.
    
    ### How to Use:
    1. Send a POST request to `/store-memory` with a JSON payload:
       ```json
       {
           "insight": "User prefers casual conversation tone."
       }
       ```
    2. The AI will store the insight for future reference.
    3. A JSON response confirms success or failure.
    
    ### Response Format:
    - On success:
      ```json
      {
          "success": true,
          "message": "Memory successfully stored."
      }
      ```
    - On failure:
      ```json
      {
          "success": false,
          "message": "Failed to store memory: error details"
      }
      ```
    """
    try:
        MEMORY_KEY = "memories"
        
        try:
            memory_data = db.storage.json.get(MEMORY_KEY)
        except FileNotFoundError:
            memory_data = []
        
        memory_data.append(body.insight)
        db.storage.json.put(MEMORY_KEY, memory_data)
        
        return MemoryResponse(
            success=True,
            message="Memory successfully stored."
        )
    except Exception as e:
        return MemoryResponse(
            success=False,
            message=f"Failed to store memory: {str(e)}"
        )