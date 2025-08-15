from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
from backend.chatbot import ChatBot
from backend.mcp_enhanced_chatbot import MCPEnhancedChatBot
from backend.ai_agent_chatbot import AIAgentChatBot
from backend.content_filter import ContentFilter, ContentModerationLogger, BusinessContentFilter
from backend.language_support import MultiLanguageSupport, MultilingualContentFilter
from backend.middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    LoggingMiddleware,
    HealthCheckMiddleware
)

app = FastAPI(title="ChatBot API", version="1.0.0")

# Initialize content filtering and language support systems
content_filter = None
language_support = None
multilingual_filter = None
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

# Global chatbot instances
chatbot_instance = None
enhanced_chatbot_instance = None
agent_chatbot_instance = None

# Pydantic models
class InitializeRequest(BaseModel):
    api_key: str
    memory_window: int = 20  # Optional parameter with default
    temperature: float = 0.7  # Optional temperature setting

class ChatRequest(BaseModel):
    message: str
    mode: str = "general"
    session_id: Optional[str] = "default"

class EnhancedChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    use_tools: bool = True

class AgentChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    use_agent: bool = True
    preferred_agent: Optional[str] = None  # customer_support, data_analyst, research_agent, project_manager

class ChatResponse(BaseModel):
    response: str
    mode: str
    sources: List[dict] = []
    timestamp: str
    success: bool

@app.post("/initialize")
async def initialize_chatbot(request: InitializeRequest, http_request: Request):
    """Initialize the chatbot with OpenAI API key and multi-language support."""
    global chatbot_instance, enhanced_chatbot_instance, content_filter, language_support, multilingual_filter
    
    try:
        # Initialize multi-language support
        language_support = MultiLanguageSupport(openai_api_key=request.api_key)
        
        # Initialize content filter with language support
        content_filter = BusinessContentFilter(openai_api_key=request.api_key)
        multilingual_filter = MultilingualContentFilter(language_support)
        
        # Initialize both standard and enhanced chatbots
        chatbot_instance = ChatBot(
            openai_api_key=request.api_key,
            memory_window=request.memory_window,
            temperature=request.temperature
        )
        
        enhanced_chatbot_instance = MCPEnhancedChatBot(
            openai_api_key=request.api_key,
            memory_window=request.memory_window,
            temperature=request.temperature
        )
        
        agent_chatbot_instance = AIAgentChatBot(
            openai_api_key=request.api_key,
            memory_window=request.memory_window,
            temperature=request.temperature
        )
        
        # Log successful initialization
        client_ip = http_request.client.host
        moderation_logger.logger.info(f"Chatbot initialized with multi-language support and MCP tools - IP: {client_ip}")
        
        # Get supported languages info
        lang_info = language_support.get_supported_languages_info()
        
        return {
            "success": True, 
            "message": "Chatbot initialized successfully with multi-language support, content filtering, MCP tools, and AI Agents",
            "supported_languages": lang_info['total_languages'],
            "auto_translate_enabled": True,
            "rtl_support": len(lang_info['rtl_languages']) > 0,
            "mcp_tools_enabled": True,
            "ai_agents_enabled": True,
            "available_tools": enhanced_chatbot_instance.get_available_tools() if enhanced_chatbot_instance else [],
            "available_agents": ["customer_support", "data_analyst", "research_agent", "project_manager", "task_planner"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to initialize chatbot: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest, http_request: Request):
    """Send a message to the chatbot with multi-language support and content filtering."""
    global chatbot_instance, content_filter, language_support, multilingual_filter
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized")
    
    if not content_filter or not language_support:
        raise HTTPException(status_code=400, detail="Content filter or language support not initialized")
    
    # Get client IP for logging
    client_ip = http_request.client.host
    
    try:
        # STEP 1: Process multi-language message
        lang_analysis = language_support.process_multilingual_chat(request.message)
        
        # Log language detection
        detected_lang = lang_analysis['detected_language']
        lang_name = lang_analysis['language_info']['name']
        moderation_logger.logger.info(f"LANGUAGE: {lang_name} ({detected_lang}) - Confidence: {lang_analysis['confidence']:.2f} - IP: {client_ip}")
        
        # STEP 2: Check content safety in detected language
        if not lang_analysis['is_safe']:
            moderation_logger.log_blocked_content("multilingual_message", lang_analysis['safety_reason'], client_ip)
            raise HTTPException(
                status_code=400, 
                detail=f"Message blocked by content filter: {lang_analysis['safety_reason']}"
            )
        
        # STEP 3: Use English message for AI processing
        english_message = lang_analysis['english_message']
        
        # STEP 4: Additional English content filtering
        is_safe, reason = content_filter.check_text_content(english_message)
        if not is_safe:
            moderation_logger.log_blocked_content("translated_message", reason, client_ip)
            raise HTTPException(
                status_code=400, 
                detail=f"Message blocked by content filter: {reason}"
            )
        
        # STEP 5: Categorize and log the request
        content_category = content_filter.get_content_category(english_message)
        moderation_logger.logger.info(f"CHAT: {content_category} - {lang_name} - IP: {client_ip}")
        
        # STEP 6: Switch mode if needed
        if chatbot_instance.current_mode != request.mode:
            chatbot_instance.switch_mode(request.mode)
        
        # STEP 7: Get response from chatbot (using English message)
        response = chatbot_instance.chat(english_message)
        
        # STEP 8: Filter the AI response
        ai_response = response["response"]
        is_response_safe, response_reason = content_filter.check_text_content(ai_response)
        if not is_response_safe:
            moderation_logger.log_suspicious_activity("ai_response_blocked", response_reason, client_ip)
            ai_response = "I apologize, but I cannot provide that information. Please ask a different question."
        
        # STEP 9: Translate response back to user's language if needed
        final_response = ai_response
        if detected_lang != 'en' and lang_analysis['language_info'].get('auto_translate', False):
            final_response = language_support.process_multilingual_response(ai_response, detected_lang)
            moderation_logger.logger.info(f"TRANSLATED_RESPONSE: {detected_lang} - IP: {client_ip}")
        
        return ChatResponse(
            response=final_response,
            mode=response["mode"],
            sources=response.get("sources", []),
            timestamp=response["timestamp"],
            success=response["success"]
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        moderation_logger.log_suspicious_activity("multilingual_chat_error", str(e), client_ip)
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/chat/enhanced")
async def enhanced_chat_with_bot(request: EnhancedChatRequest, http_request: Request):
    """Send a message to the MCP-enhanced chatbot with tool capabilities."""
    global enhanced_chatbot_instance, content_filter, language_support, multilingual_filter
    
    if not enhanced_chatbot_instance:
        raise HTTPException(status_code=400, detail="Enhanced chatbot not initialized")
    
    if not content_filter or not language_support:
        raise HTTPException(status_code=400, detail="Content filter or language support not initialized")
    
    # Get client IP for logging
    client_ip = http_request.client.host
    
    try:
        # STEP 1: Process multi-language message
        lang_analysis = language_support.process_multilingual_chat(request.message)
        
        # Log language detection
        detected_lang = lang_analysis['detected_language']
        lang_name = lang_analysis['language_info']['name']
        moderation_logger.logger.info(f"ENHANCED_CHAT_LANGUAGE: {lang_name} ({detected_lang}) - Confidence: {lang_analysis['confidence']:.2f} - IP: {client_ip}")
        
        # STEP 2: Check content safety in detected language
        if not lang_analysis['is_safe']:
            moderation_logger.log_blocked_content("multilingual_message", lang_analysis['safety_reason'], client_ip)
            raise HTTPException(
                status_code=400, 
                detail=f"Message blocked by content filter: {lang_analysis['safety_reason']}"
            )
        
        # STEP 3: Use English message for AI processing
        english_message = lang_analysis['english_message']
        
        # STEP 4: Additional English content filtering
        is_safe, reason = content_filter.check_text_content(english_message)
        if not is_safe:
            moderation_logger.log_blocked_content("translated_message", reason, client_ip)
            raise HTTPException(
                status_code=400, 
                detail=f"Message blocked by content filter: {reason}"
            )
        
        # STEP 5: Categorize and log the request
        content_category = content_filter.get_content_category(english_message)
        moderation_logger.logger.info(f"ENHANCED_CHAT: {content_category} - {lang_name} - IP: {client_ip}")
        
        # STEP 6: Get response from enhanced chatbot with tools
        enhanced_response = await enhanced_chatbot_instance.chat_with_tools(
            message=english_message,
            session_id=request.session_id
        )
        
        # STEP 7: Filter the AI response
        ai_response = enhanced_response["response"]
        is_response_safe, response_reason = content_filter.check_text_content(ai_response)
        if not is_response_safe:
            moderation_logger.log_suspicious_activity("ai_response_blocked", response_reason, client_ip)
            ai_response = "I apologize, but I cannot provide that information. Please ask a different question."
            enhanced_response["response"] = ai_response
        
        # STEP 8: Translate response back to user's language if needed
        final_response = ai_response
        if detected_lang != 'en' and lang_analysis['language_info'].get('auto_translate', False):
            final_response = language_support.process_multilingual_response(ai_response, detected_lang)
            moderation_logger.logger.info(f"ENHANCED_TRANSLATED_RESPONSE: {detected_lang} - IP: {client_ip}")
            enhanced_response["response"] = final_response
        
        # Log tool usage if tools were used
        if enhanced_response.get("enhanced", False):
            tools_used = enhanced_response.get("tools_used", [])
            moderation_logger.logger.info(f"MCP_TOOLS_USED: {', '.join(tools_used)} - {lang_name} - IP: {client_ip}")
        
        return {
            "success": True,
            "response": enhanced_response["response"],
            "enhanced": enhanced_response.get("enhanced", False),
            "tools_used": enhanced_response.get("tools_used", []),
            "tool_results": enhanced_response.get("tool_results", {}),
            "session_id": enhanced_response.get("session_id", request.session_id),
            "timestamp": enhanced_response.get("timestamp"),
            "language_detected": lang_name,
            "language_code": detected_lang
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        moderation_logger.log_suspicious_activity("enhanced_chat_error", str(e), client_ip)
        raise HTTPException(status_code=500, detail=f"Enhanced chat error: {str(e)}")

@app.post("/chat/agent")
async def agent_chat_with_bot(request: AgentChatRequest, http_request: Request):
    """Send a message to the AI Agent chatbot for intelligent multi-step problem solving."""
    global agent_chatbot_instance, content_filter, language_support, multilingual_filter
    
    if not agent_chatbot_instance:
        raise HTTPException(status_code=400, detail="AI Agent chatbot not initialized")
    
    if not content_filter or not language_support:
        raise HTTPException(status_code=400, detail="Content filter or language support not initialized")
    
    # Get client IP for logging
    client_ip = http_request.client.host
    
    try:
        # STEP 1: Process multi-language message
        lang_analysis = language_support.process_multilingual_chat(request.message)
        
        # Log language detection
        detected_lang = lang_analysis['detected_language']
        lang_name = lang_analysis['language_info']['name']
        moderation_logger.logger.info(f"AGENT_CHAT_LANGUAGE: {lang_name} ({detected_lang}) - Confidence: {lang_analysis['confidence']:.2f} - IP: {client_ip}")
        
        # STEP 2: Check content safety in detected language
        if not lang_analysis['is_safe']:
            moderation_logger.log_blocked_content("multilingual_message", lang_analysis['safety_reason'], client_ip)
            raise HTTPException(
                status_code=400, 
                detail=f"Message blocked by content filter: {lang_analysis['safety_reason']}"
            )
        
        # STEP 3: Use English message for AI processing
        english_message = lang_analysis['english_message']
        
        # STEP 4: Additional English content filtering
        is_safe, reason = content_filter.check_text_content(english_message)
        if not is_safe:
            moderation_logger.log_blocked_content("translated_message", reason, client_ip)
            raise HTTPException(
                status_code=400, 
                detail=f"Message blocked by content filter: {reason}"
            )
        
        # STEP 5: Categorize and log the request
        content_category = content_filter.get_content_category(english_message)
        moderation_logger.logger.info(f"AGENT_CHAT: {content_category} - {lang_name} - IP: {client_ip}")
        
        # STEP 6: Get response from AI agent with intelligent planning
        agent_response = await agent_chatbot_instance.chat_with_agent(
            message=english_message,
            session_id=request.session_id
        )
        
        # STEP 7: Filter the AI response
        ai_response = agent_response["response"]
        is_response_safe, response_reason = content_filter.check_text_content(ai_response)
        if not is_response_safe:
            moderation_logger.log_suspicious_activity("ai_response_blocked", response_reason, client_ip)
            ai_response = "I apologize, but I cannot provide that information. Please ask a different question."
            agent_response["response"] = ai_response
        
        # STEP 8: Translate response back to user's language if needed
        final_response = ai_response
        if detected_lang != 'en' and lang_analysis['language_info'].get('auto_translate', False):
            final_response = language_support.process_multilingual_response(ai_response, detected_lang)
            moderation_logger.logger.info(f"AGENT_TRANSLATED_RESPONSE: {detected_lang} - IP: {client_ip}")
            agent_response["response"] = final_response
        
        # Log agent usage
        if agent_response.get("agent_used", False):
            agent_role = agent_response.get("agent_role", "unknown")
            steps_completed = agent_response.get("steps_completed", 0)
            tools_used = agent_response.get("tools_used", [])
            moderation_logger.logger.info(f"AI_AGENT_USED: {agent_role} - {steps_completed} steps - Tools: {', '.join(tools_used)} - {lang_name} - IP: {client_ip}")
        
        return {
            "success": True,
            "response": agent_response["response"],
            "agent_used": agent_response.get("agent_used", False),
            "agent_role": agent_response.get("agent_role", None),
            "plan": agent_response.get("plan", {}),
            "steps_completed": agent_response.get("steps_completed", 0),
            "tools_used": agent_response.get("tools_used", []),
            "execution_time": agent_response.get("execution_time", 0),
            "session_id": agent_response.get("session_id", request.session_id),
            "timestamp": agent_response.get("timestamp"),
            "language_detected": lang_name,
            "language_code": detected_lang
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        moderation_logger.log_suspicious_activity("agent_chat_error", str(e), client_ip)
        raise HTTPException(status_code=500, detail=f"AI Agent chat error: {str(e)}")

@app.post("/load-knowledge")
async def load_knowledge_base(files: List[UploadFile] = File(...), http_request: Request = None):
    """Load knowledge base from uploaded files with multi-language support and content filtering."""
    global chatbot_instance, content_filter, language_support
    
    if not chatbot_instance:
        raise HTTPException(status_code=400, detail="Chatbot not initialized")
    
    if not content_filter or not language_support:
        raise HTTPException(status_code=400, detail="Content filter or language support not initialized")
    
    # Get client IP for logging
    client_ip = http_request.client.host if http_request else "unknown"
    
    try:
        # Check file count limit
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed per upload")
        
        temp_files = []
        total_size = 0
        processed_files_info = []
        
        for file in files:
            # Read file content
            content = await file.read()
            file_size = len(content)
            total_size += file_size
            
            # Log file upload attempt
            moderation_logger.log_file_upload(file.filename, file_size, "processing", client_ip)
            
            # STEP 1: Basic file validation
            is_file_safe, file_reason = content_filter.check_file_upload(file.filename, content)
            if not is_file_safe:
                moderation_logger.log_blocked_content("file_upload", f"{file.filename}: {file_reason}", client_ip)
                raise HTTPException(status_code=400, detail=f"File '{file.filename}' rejected: {file_reason}")
            
            # STEP 2: Process multi-language document content
            try:
                text_content = content.decode('utf-8', errors='ignore')
                
                # Analyze document language
                doc_analysis = language_support.validate_document_language(text_content, file.filename)
                
                detected_lang = doc_analysis['detected_language']
                lang_name = doc_analysis['language_info']['name']
                
                # Log document language
                moderation_logger.logger.info(f"DOCUMENT_LANGUAGE: {file.filename} - {lang_name} ({detected_lang}) - Confidence: {doc_analysis['confidence']:.2f} - IP: {client_ip}")
                
                # Check content safety in detected language
                if not doc_analysis['is_safe']:
                    moderation_logger.log_blocked_content("multilingual_document", f"{file.filename}: {doc_analysis['safety_reason']}", client_ip)
                    raise HTTPException(status_code=400, detail=f"File '{file.filename}' contains inappropriate content: {doc_analysis['safety_reason']}")
                
                # STEP 3: Use English content for knowledge base (translated if needed)
                final_content = doc_analysis['english_content']
                
                # Additional safety check on English content
                is_content_safe, content_reason = content_filter.check_knowledge_base_content(final_content)
                if not is_content_safe:
                    moderation_logger.log_blocked_content("translated_document", f"{file.filename}: {content_reason}", client_ip)
                    raise HTTPException(status_code=400, detail=f"File '{file.filename}' contains inappropriate content: {content_reason}")
                
                processed_files_info.append({
                    'filename': file.filename,
                    'original_language': lang_name,
                    'language_code': detected_lang,
                    'translated': doc_analysis['needs_translation'],
                    'original_size': doc_analysis['content_length'],
                    'processed_size': doc_analysis['english_length']
                })
                
            except UnicodeDecodeError as e:
                moderation_logger.log_blocked_content("file_decode_error", f"{file.filename}: {str(e)}", client_ip)
                raise HTTPException(status_code=400, detail=f"Could not process file '{file.filename}': Invalid text encoding")
            except Exception as e:
                moderation_logger.log_blocked_content("file_processing_error", f"{file.filename}: {str(e)}", client_ip)
                raise HTTPException(status_code=400, detail=f"Could not process file '{file.filename}': {str(e)}")
            
            # STEP 4: Sanitize filename and create temporary file
            safe_filename = content_filter.sanitize_filename(file.filename)
            
            with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=os.path.splitext(safe_filename)[1]) as temp_file:
                # Write the processed (possibly translated) content
                temp_file.write(final_content.encode('utf-8'))
                temp_files.append(temp_file.name)
        
        # Check total upload size
        if total_size > 50 * 1024 * 1024:  # 50MB total limit
            raise HTTPException(status_code=400, detail="Total file size exceeds 50MB limit")
        
        # STEP 5: Load knowledge base with processed files
        success = chatbot_instance.load_knowledge_base(temp_files)
        
        # STEP 6: Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except OSError:
                pass  # File might already be deleted
        
        if success:
            # Log successful processing with language details
            languages_processed = list(set(info['original_language'] for info in processed_files_info))
            translated_count = sum(1 for info in processed_files_info if info['translated'])
            
            moderation_logger.logger.info(f"KNOWLEDGE_BASE_LOADED: {len(files)} files - Languages: {', '.join(languages_processed)} - {translated_count} translated - IP: {client_ip}")
            
            return {
                "success": True, 
                "message": f"Successfully loaded {len(files)} files into knowledge base",
                "files_processed": len(files),
                "total_size_mb": round(total_size / (1024*1024), 2),
                "languages_detected": languages_processed,
                "files_translated": translated_count,
                "file_details": processed_files_info
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
        moderation_logger.log_suspicious_activity("multilingual_file_upload_error", str(e), client_ip)
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

@app.get("/tools/available")
async def get_available_tools():
    """Get list of available MCP tools."""
    global enhanced_chatbot_instance
    
    if not enhanced_chatbot_instance:
        raise HTTPException(status_code=400, detail="Enhanced chatbot not initialized")
    
    return {
        "tools": enhanced_chatbot_instance.get_available_tools(),
        "usage_stats": enhanced_chatbot_instance.get_tool_usage_stats()
    }

@app.get("/tools/usage-stats")
async def get_tool_usage_stats():
    """Get tool usage statistics."""
    global enhanced_chatbot_instance
    
    if not enhanced_chatbot_instance:
        raise HTTPException(status_code=400, detail="Enhanced chatbot not initialized")
    
    return {
        "tool_usage_stats": enhanced_chatbot_instance.get_tool_usage_stats(),
        "total_tool_calls": sum(enhanced_chatbot_instance.get_tool_usage_stats().values())
    }

@app.get("/agents/available")
async def get_available_agents():
    """Get list of available AI agents."""
    global agent_chatbot_instance
    
    if not agent_chatbot_instance:
        raise HTTPException(status_code=400, detail="AI Agent chatbot not initialized")
    
    return {
        "agents": [
            {
                "name": "customer_support",
                "description": "Handles customer service issues and complaints",
                "capabilities": ["issue analysis", "resolution planning", "follow-up creation"]
            },
            {
                "name": "data_analyst", 
                "description": "Analyzes data and provides business insights",
                "capabilities": ["data analysis", "trend identification", "recommendations"]
            },
            {
                "name": "research_agent",
                "description": "Conducts comprehensive research and information gathering",
                "capabilities": ["web research", "competitive analysis", "report generation"]
            },
            {
                "name": "project_manager",
                "description": "Creates and manages project plans and timelines",
                "capabilities": ["project planning", "timeline creation", "resource allocation"]
            },
            {
                "name": "task_planner",
                "description": "Plans and executes general multi-step tasks",
                "capabilities": ["task breakdown", "execution planning", "workflow automation"]
            }
        ]
    }

@app.get("/agents/stats")
async def get_agent_stats():
    """Get AI agent performance statistics."""
    global agent_chatbot_instance
    
    if not agent_chatbot_instance:
        raise HTTPException(status_code=400, detail="AI Agent chatbot not initialized")
    
    return {
        "agent_stats": agent_chatbot_instance.get_agent_stats(),
        "message": "AI Agent performance metrics"
    }

@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "ChatBot API is running with MCP Tools",
        "version": "2.0.0",
        "features": [
            "Multi-language support",
            "Content filtering",
            "MCP tool integration",
            "Real-time data access"
        ],
        "endpoints": [
            "/initialize - Initialize chatbot with API key",
            "/chat - Send message to standard chatbot", 
            "/chat/enhanced - Send message to MCP-enhanced chatbot with tools",
            "/chat/agent - Send message to AI Agent for intelligent multi-step problem solving",
            "/tools/available - Get list of available MCP tools",
            "/tools/usage-stats - Get tool usage statistics",
            "/agents/available - Get list of available AI agents",
            "/agents/stats - Get AI agent performance statistics",
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