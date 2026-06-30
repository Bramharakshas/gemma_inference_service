import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Local Gemma-3 Inference Gateway",
    description="Enterprise-ready REST API wrapping local Google Gemma 3 via Ollama.",
    version="1.0.0"
)

# Ollama local endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"

# Input validation model
class ChatPayload(BaseModel):
    prompt: str
    model: str = "gemma3:4b"  # Maps directly to your local setup
    temperature: float = 0.3  # Lower temperature for precise/structured answers

# Output validation model
class ChatResponse(BaseModel):
    model: str
    response: str
    status: str

@app.post("/v1/chat", response_model=ChatResponse)
async def process_chat(payload: ChatPayload):
    """
    Exposes an endpoint to pass prompts to the locally running Gemma 3 instance.
    Includes connection timeout safety and clean validation.
    """
    # Preparing payload for Ollama's internal native structure
    ollama_payload = {
        "model": payload.model,
        "prompt": payload.prompt,
        "options": {"temperature": payload.temperature},
        "stream": False  # Handled statically for clean initial testing
    }
    
    try:
        # Forward request to local Ollama daemon
        response = requests.post(OLLAMA_URL, json=ollama_payload, timeout=45)
        response.raise_for_status()
        raw_result = response.json()
        
        return ChatResponse(
            model=payload.model,
            response=raw_result.get("response", ""),
            status="success"
        )
    except requests.exceptions.RequestException as error:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to communicate with local Ollama engine: {str(error)}"
        )
    
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # Expose the app on all interfaces at port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)