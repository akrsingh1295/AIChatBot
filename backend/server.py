from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
from backend.chatbot import ChatBot
from backend.content_filter import ContentFilter, ContentModerationLogger, BusinessContentFilter
from backend.middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    LoggingMiddleware,
    HealthCheckMiddleware
)

app = FastAPI(title="ChatBot API", version="1.0.0")

# Initialize content filtering system
content_filter = None
moderation_logger = ContentModerationLogger()

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
async def initialize_chatbot(request: InitializeRequest, http_request: Request):
    """Initialize the chatbot with OpenAI API key."""
    global chatbot_instance, content_filter
    
    try:
        # Initialize content filter with the same API key
        content_filter = BusinessContentFilter(openai_api_key=request.api_key)
        
        chatbot_instance = ChatBot(
            openai_api_key=request.api_key,
            memory_window=request.memory_window,
            temperature=request.temperature
        )
        
        # Log successful initialization
        client_ip = http_request.client.host
        moderation_logger.logger.info(f"Chatbot initialized successfully - IP: {client_ip}")
        
        return {"success": True, "message": "Chatbot initialized successfully with content filtering enabled"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to initialize chatbot: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest, http_request: Request):
    """Send a message to the chatbot with content filtering."""
    global chatbot_instance, content_filter
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized")
    
    if not content_filter:
        raise HTTPException(status_code=400, detail="Content filter not initialized")
    
    # Get client IP for logging
    client_ip = http_request.client.host
    
    try:
        # STEP 1: Check if the user's message is appropriate
        is_safe, reason = content_filter.check_text_content(request.message)
        if not is_safe:
            moderation_logger.log_blocked_content("user_message", reason, client_ip)
            raise HTTPException(
                status_code=400, 
                detail=f"Message blocked by content filter: {reason}"
            )
        
        # STEP 2: Categorize and log the request
        content_category = content_filter.get_content_category(request.message)
        moderation_logger.logger.info(f"CHAT: {content_category} - IP: {client_ip}")
        
        # STEP 3: Switch mode if needed
        if chatbot_instance.current_mode != request.mode:
            chatbot_instance.switch_mode(request.mode)
        
        # STEP 4: Get response from chatbot
        response = chatbot_instance.chat(request.message)
        
        # STEP 5: Filter the AI response as well (safety check)
        ai_response = response["response"]
        is_response_safe, response_reason = content_filter.check_text_content(ai_response)
        if not is_response_safe:
            moderation_logger.log_suspicious_activity("ai_response_blocked", response_reason, client_ip)
            # Provide a safe fallback response
            ai_response = "I apologize, but I cannot provide that information. Please ask a different question."
        
        return ChatResponse(
            response=ai_response,
            mode=response["mode"],
            sources=response.get("sources", []),
            timestamp=response["timestamp"],
            success=response["success"]
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        moderation_logger.log_suspicious_activity("chat_error", str(e), client_ip)
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/load-knowledge")
async def load_knowledge_base(files: List[UploadFile] = File(...), http_request: Request = None):
    """Load knowledge base from uploaded files with content filtering."""
    global chatbot_instance, content_filter
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized")
    
    if not content_filter:
        raise HTTPException(status_code=400, detail="Content filter not initialized")
    
    # Get client IP for logging
    client_ip = http_request.client.host if http_request else "unknown"
    
    try:
        # Check file count limit
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed per upload")
        
        temp_files = []
        total_size = 0
        
        for file in files:
            # Read file content
            content = await file.read()
            file_size = len(content)
            total_size += file_size
            
            # Log file upload attempt
            moderation_logger.log_file_upload(file.filename, file_size, "processing", client_ip)
            
            # STEP 1: Check file size and type
            is_file_safe, file_reason = content_filter.check_file_upload(file.filename, content)
            if not is_file_safe:
                moderation_logger.log_blocked_content("file_upload", f"{file.filename}: {file_reason}", client_ip)
                raise HTTPException(status_code=400, detail=f"File '{file.filename}' rejected: {file_reason}")
            
            # STEP 2: Additional file content checks for knowledge base
            try:
                text_content = content.decode('utf-8', errors='ignore')
                is_content_safe, content_reason = content_filter.check_knowledge_base_content(text_content)
                if not is_content_safe:
                    moderation_logger.log_blocked_content("knowledge_content", f"{file.filename}: {content_reason}", client_ip)
                    raise HTTPException(status_code=400, detail=f"File '{file.filename}' contains inappropriate content: {content_reason}")
            except Exception as e:
                # If we can't decode as text, it might be binary - reject it
                moderation_logger.log_blocked_content("file_decode_error", f"{file.filename}: {str(e)}", client_ip)
                raise HTTPException(status_code=400, detail=f"Could not process file '{file.filename}': {str(e)}")
            
            # STEP 3: Sanitize filename and create temporary file
            safe_filename = content_filter.sanitize_filename(file.filename)
            
            with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=os.path.splitext(safe_filename)[1]) as temp_file:
                temp_file.write(content)
                temp_files.append(temp_file.name)
        
        # Check total upload size
        if total_size > 50 * 1024 * 1024:  # 50MB total limit
            raise HTTPException(status_code=400, detail="Total file size exceeds 50MB limit")
        
        # STEP 4: Load knowledge base
        success = chatbot_instance.load_knowledge_base(temp_files)
        
        # STEP 5: Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except OSError:
                pass  # File might already be deleted
        
        if success:
            moderation_logger.logger.info(f"Knowledge base loaded successfully - {len(files)} files - IP: {client_ip}")
            return {
                "success": True, 
                "message": f"Successfully loaded {len(files)} files into knowledge base",
                "files_processed": len(files),
                "total_size_mb": round(total_size / (1024*1024), 2)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to load knowledge base")
            
    except HTTPException:
        # Clean up temp files on error
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except OSError:
                pass
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        # Clean up temp files on error
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except OSError:
                pass
        moderation_logger.log_suspicious_activity("file_upload_error", str(e), client_ip)
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

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