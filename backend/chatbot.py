import os
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from config import ChatBotConfig
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain, ConversationChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from backend.knowledge_processor import KnowledgeProcessor
import json
from datetime import datetime


class ChatBot:
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 model_name: str = ChatBotConfig.MODEL_NAME,
                 temperature: float = ChatBotConfig.TEMPERATURE,
                 memory_window: int = ChatBotConfig.MEMORY_WINDOW):
        """Initialize the ChatBot with memory and knowledge capabilities."""
        
        # Set up OpenAI API key
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        elif not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key is required")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=memory_window,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Initialize knowledge processor
        self.knowledge_processor = KnowledgeProcessor()
        
        # Initialize chains
        self._setup_chains()
        
        # Chat modes
        self.current_mode = "general"  # "general" or "knowledge"
        
        # Chat history for UI
        self.chat_history = []
    
    def _setup_chains(self):
        """Set up conversation chains for different modes."""
        
                 # General conversation chain (no knowledge base)
         general_prompt = PromptTemplate(
             input_variables=["history", "input"],
             template="""You are a helpful AI assistant. Have a natural conversation with the user. Previous conversation: {history} Human: {input} Assistant:""")
         
         self.general_chain = ConversationChain(
             llm=self.llm,
             memory=self.memory,
             prompt=general_prompt,
             verbose=False
         )
         
         # Knowledge-based conversation chain will be set up when needed
         self.knowledge_chain = None
    
    def load_knowledge_base(self, file_paths: List[str]) -> bool:
        """Load knowledge base from files and set up retrieval chain."""
        try:
            success = self.knowledge_processor.process_knowledge_base(file_paths)
            if success:
                # Set up knowledge-based retrieval chain
                vectorstore = self.knowledge_processor.get_vectorstore()
                
                self.knowledge_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                    memory=self.memory,
                    return_source_documents=True,
                    verbose=False
                )
                return True
            return False
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return False
    
    def switch_mode(self, mode: str):
        """Switch between general and knowledge chat modes."""
        if mode in ["general", "knowledge"]:
            self.current_mode = mode
            return True
        return False
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """Main chat method that handles both modes."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if self.current_mode == "knowledge" and self.knowledge_chain:
                # Knowledge-based chat
                response = self.knowledge_chain({
                    "question": user_input,
                    "chat_history": self.memory.chat_memory.messages
                })
                
                answer = response["answer"]
                sources = response.get("source_documents", [])
                
                # Format source information
                source_info = []
                for doc in sources:
                    source_info.append({
                        "content": doc.page_content[:200] + "...",
                        "metadata": doc.metadata
                    })
                
                result = {
                    "response": answer,
                    "mode": "knowledge",
                    "sources": source_info,
                    "timestamp": timestamp,
                    "success": True
                }
            else:
                # General conversation
                response = self.general_chain.predict(input=user_input)
                
                result = {
                    "response": response,
                    "mode": "general",
                    "sources": [],
                    "timestamp": timestamp,
                    "success": True
                }
            
            # Add to chat history
            self.chat_history.append({
                "user": user_input,
                "assistant": result["response"],
                "mode": result["mode"],
                "timestamp": timestamp,
                "sources": result.get("sources", [])
            })
            
            return result
            
        except Exception as e:
            error_result = {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "mode": self.current_mode,
                "sources": [],
                "timestamp": timestamp,
                "success": False,
                "error": str(e)
            }
            return error_result
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get the complete chat history."""
        return self.chat_history
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()
        self.chat_history = []
    
    def search_knowledge_base(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search the knowledge base directly."""
        try:
            docs = self.knowledge_processor.search_similar_documents(query, k)
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            return results
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []
    
    def get_memory_summary(self) -> str:
        """Get a summary of the current conversation memory."""
        try:
            messages = self.memory.chat_memory.messages
            if not messages:
                return "No conversation history"
            
            summary = f"Conversation has {len(messages)} messages. "
            summary += f"Current mode: {self.current_mode}. "
            
            if self.knowledge_chain:
                summary += "Knowledge base is loaded and available."
            else:
                summary += "No knowledge base loaded."
            
            return summary
        except Exception as e:
            return f"Error getting memory summary: {e}" 