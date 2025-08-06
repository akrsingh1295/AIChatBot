from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
from backend.chatbot import ChatBot
from backend.middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    LoggingMiddleware,
    HealthCheckMiddleware
)

app = FastAPI(title="ChatBot API", version="1.0.0")

# Security and monitoring middleware (order matters!)
app.add_middleware(HealthCheckMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, calls_per_minute=60)

# CORS middleware for React frontend
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global chatbot instance
chatbot_instance = None

# Pydantic models
class InitializeRequest(BaseModel):
    api_key: str
    memory_window: int = 20  # Optional parameter with default
    temperature: float = 0.7  # Optional temperature setting

class ChatRequest(BaseModel):
    message: str
    mode: str = "general"

class ChatResponse(BaseModel):
    response: str
    mode: str
    sources: List[dict] = []
    timestamp: str
    success: bool

@app.post("/initialize")
async def initialize_chatbot(request: InitializeRequest):
    """Initialize the chatbot with OpenAI API key."""
    global chatbot_instance
    
    try:
        chatbot_instance = ChatBot(
            openai_api_key=request.api_key,
            memory_window=request.memory_window,
            temperature=request.temperature
        )
        return {"success": True, "message": "Chatbot initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to initialize chatbot: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """Send a message to the chatbot."""
    global chatbot_instance
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized")
    
    try:
        # Switch mode if needed
        if chatbot_instance.current_mode != request.mode:
            chatbot_instance.switch_mode(request.mode)
        
        # Get response from chatbot
        response = chatbot_instance.chat(request.message)
        
        return ChatResponse(
            response=response["response"],
            mode=response["mode"],
            sources=response.get("sources", []),
            timestamp=response["timestamp"],
            success=response["success"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/load-knowledge")
async def load_knowledge_base(files: List[UploadFile] = File(...)):
    """Load knowledge base from uploaded files."""
    global chatbot_instance
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized")
    
    try:
        # Save uploaded files temporarily
        temp_files = []
        for file in files:
            if file.content_type not in ["text/plain", "text/csv"]:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_files.append(temp_file.name)
        
        # Load knowledge base
        success = chatbot_instance.load_knowledge_base(temp_files)
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        
        if success:
            return {"success": True, "message": "Knowledge base loaded successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to load knowledge base")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge base loading error: {str(e)}")

@app.post("/clear-memory")
async def clear_memory():
    """Clear chatbot memory."""
    global chatbot_instance
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized")
    
    try:
        chatbot_instance.clear_memory()
        return {"success": True, "message": "Memory cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory clear error: {str(e)}")

@app.get("/status")
async def get_status():
    """Get chatbot status."""
    global chatbot_instance
    
    if not chatbot_instance:
        return {
            "chatbot_ready": False,
            "current_mode": None,
            "knowledge_loaded": False,
            "memory_summary": "Chatbot not initialized"
        }
    
    return {
        "chatbot_ready": True,
        "current_mode": chatbot_instance.current_mode,
        "knowledge_loaded": chatbot_instance.knowledge_chain is not None,
        "memory_summary": chatbot_instance.get_memory_summary()
    }

@app.get("/chat-history")
async def get_chat_history():
    """Get chat history."""
    global chatbot_instance
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized")
    
    return {"history": chatbot_instance.get_chat_history()}

@app.post("/search-knowledge")
async def search_knowledge_base(request: ChatRequest):
    """Search the knowledge base directly."""
    global chatbot_instance
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized")
    
    if not chatbot_instance.knowledge_chain:
        raise HTTPException(status_code=400, detail="Knowledge base not loaded")
    
    try:
        results = chatbot_instance.search_knowledge_base(request.message, k=5)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "ChatBot API is running",
        "version": "1.0.0",
        "endpoints": [
            "/initialize - Initialize chatbot with API key",
            "/chat - Send message to chatbot",
            "/load-knowledge - Upload knowledge base files",
            "/clear-memory - Clear conversation memory",
            "/status - Get chatbot status",
            "/chat-history - Get conversation history",
            "/search-knowledge - Search knowledge base"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 