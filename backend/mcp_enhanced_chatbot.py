"""
MCP-Enhanced ChatBot Implementation
Extends the existing chatbot with Model Context Protocol tools
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import sqlite3
from pathlib import Path

# Import your existing chatbot
from backend.chatbot import ChatBot
from config import ChatBotConfig

class MCPEnhancedChatBot(ChatBot):
    """Enhanced ChatBot with MCP tool integration"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # MCP tool registry
        self.tools = {}
        self._register_tools()
        
        # Tool usage tracking
        self.tool_usage_stats = {}
        
    def _register_tools(self):
        """Register all available MCP tools"""
        
        # Weather tool
        self.tools['get_weather'] = {
            'function': self._get_weather,
            'description': 'Get current weather for any location',
            'parameters': {'location': 'string'}
        }
        
        # Calculator tool
        self.tools['calculate'] = {
            'function': self._calculate,
            'description': 'Perform mathematical calculations',
            'parameters': {'expression': 'string'}
        }
        
        # File reader tool
        self.tools['read_file'] = {
            'function': self._read_file,
            'description': 'Read content from files',
            'parameters': {'file_path': 'string'}
        }
        
        # Web search tool
        self.tools['search_web'] = {
            'function': self._search_web,
            'description': 'Search the internet for current information',
            'parameters': {'query': 'string'}
        }
        
        # Stock price tool
        self.tools['get_stock_price'] = {
            'function': self._get_stock_price,
            'description': 'Get current stock price information',
            'parameters': {'symbol': 'string'}
        }
        
        # Database query tool
        self.tools['query_data'] = {
            'function': self._query_data,
            'description': 'Query internal data sources',
            'parameters': {'query': 'string'}
        }

    async def chat_with_tools(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Enhanced chat method that can use MCP tools"""
        
        # Analyze if tools are needed
        tool_analysis = await self._analyze_tool_requirements(message)
        
        if tool_analysis['needs_tools']:
            # Execute required tools
            tool_results = await self._execute_tools(tool_analysis['tools'], message)
            
            # Create enhanced context
            enhanced_context = self._create_enhanced_context(message, tool_results)
            
            # Get AI response with tool context
            response = await self.chat(enhanced_context, session_id)
            
            # Track tool usage
            self._track_tool_usage(tool_analysis['tools'])
            
            return {
                "response": response["response"],
                "tools_used": list(tool_results.keys()),
                "tool_results": tool_results,
                "enhanced": True,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Use normal chat flow
            response = await self.chat(message, session_id)
            return {
                "response": response["response"],
                "enhanced": False,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

    async def _analyze_tool_requirements(self, message: str) -> Dict[str, Any]:
        """Analyze message to determine which tools are needed"""
        
        message_lower = message.lower()
        required_tools = []
        
        # Weather-related queries
        if any(word in message_lower for word in ['weather', 'temperature', 'rain', 'sunny', 'cloudy']):
            required_tools.append('get_weather')
        
        # Math calculations
        if any(word in message_lower for word in ['calculate', 'compute', '+', '-', '*', '/', 'math']):
            required_tools.append('calculate')
        
        # File operations
        if any(word in message_lower for word in ['read file', 'file content', 'document']):
            required_tools.append('read_file')
        
        # Web search
        if any(word in message_lower for word in ['search', 'latest', 'current news', 'recent']):
            required_tools.append('search_web')
        
        # Stock prices
        if any(word in message_lower for word in ['stock', 'share price', 'ticker', 'market']):
            required_tools.append('get_stock_price')
        
        # Data queries
        if any(word in message_lower for word in ['data', 'database', 'records', 'analytics']):
            required_tools.append('query_data')
        
        return {
            'needs_tools': len(required_tools) > 0,
            'tools': required_tools,
            'confidence': 0.8 if required_tools else 0.1
        }

    async def _execute_tools(self, tools: List[str], message: str) -> Dict[str, Any]:
        """Execute the required tools"""
        
        results = {}
        
        for tool_name in tools:
            if tool_name in self.tools:
                try:
                    # Extract parameters for the tool
                    params = self._extract_tool_parameters(tool_name, message)
                    
                    # Execute the tool
                    tool_function = self.tools[tool_name]['function']
                    result = await tool_function(**params)
                    
                    results[tool_name] = {
                        'success': True,
                        'data': result,
                        'parameters': params
                    }
                    
                except Exception as e:
                    results[tool_name] = {
                        'success': False,
                        'error': str(e),
                        'parameters': params if 'params' in locals() else {}
                    }
        
        return results

    def _extract_tool_parameters(self, tool_name: str, message: str) -> Dict[str, Any]:
        """Extract parameters for specific tools from the message"""
        
        if tool_name == 'get_weather':
            # Simple location extraction (can be enhanced with NLP)
            location = self._extract_location(message)
            return {'location': location}
        
        elif tool_name == 'calculate':
            # Extract mathematical expression
            expression = self._extract_math_expression(message)
            return {'expression': expression}
        
        elif tool_name == 'read_file':
            # Extract file path
            file_path = self._extract_file_path(message)
            return {'file_path': file_path}
        
        elif tool_name == 'search_web':
            # Extract search query
            query = self._extract_search_query(message)
            return {'query': query}
        
        elif tool_name == 'get_stock_price':
            # Extract stock symbol
            symbol = self._extract_stock_symbol(message)
            return {'symbol': symbol}
        
        elif tool_name == 'query_data':
            # Extract data query
            query = self._extract_data_query(message)
            return {'query': query}
        
        return {}

    # Tool implementations
    async def _get_weather(self, location: str) -> Dict[str, Any]:
        """Get weather information for a location"""
        try:
            # Using OpenWeatherMap API (free tier)
            api_key = os.getenv('OPENWEATHER_API_KEY')
            if not api_key:
                return {"error": "Weather API key not configured"}
            
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': location,
                'appid': api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'location': data['name'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed']
                }
            else:
                return {"error": f"Weather data not found for {location}"}
                
        except Exception as e:
            return {"error": f"Weather service error: {str(e)}"}

    async def _calculate(self, expression: str) -> Dict[str, Any]:
        """Perform mathematical calculations safely"""
        try:
            # Sanitize expression (basic safety)
            allowed_chars = '0123456789+-*/.() '
            clean_expr = ''.join(c for c in expression if c in allowed_chars)
            
            if not clean_expr:
                return {"error": "Invalid mathematical expression"}
            
            # Evaluate safely
            result = eval(clean_expr)
            
            return {
                'expression': expression,
                'result': result,
                'formatted': f"{expression} = {result}"
            }
            
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"}

    async def _read_file(self, file_path: str) -> Dict[str, Any]:
        """Read content from a file"""
        try:
            # Security check - only allow certain directories
            allowed_dirs = ['./uploads', './documents', './data']
            path_obj = Path(file_path)
            
            if not any(str(path_obj).startswith(allowed_dir) for allowed_dir in allowed_dirs):
                return {"error": "File access not allowed in this directory"}
            
            if not path_obj.exists():
                return {"error": f"File not found: {file_path}"}
            
            # Read file content
            with open(path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'file_path': file_path,
                'size_bytes': len(content),
                'content': content[:5000],  # Limit to 5KB for performance
                'truncated': len(content) > 5000
            }
            
        except Exception as e:
            return {"error": f"File read error: {str(e)}"}

    async def _search_web(self, query: str) -> Dict[str, Any]:
        """Search the web for current information"""
        try:
            # Using DuckDuckGo Instant Answer API (free)
            url = f"https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            # Extract relevant information
            result = {
                'query': query,
                'answer': data.get('Answer', ''),
                'abstract': data.get('Abstract', ''),
                'definition': data.get('Definition', ''),
                'related_topics': [topic.get('Text', '') for topic in data.get('RelatedTopics', [])[:3]]
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Web search error: {str(e)}"}

    async def _get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get stock price information"""
        try:
            # Using Alpha Vantage API (free tier)
            api_key = os.getenv('ALPHAVANTAGE_API_KEY')
            if not api_key:
                return {"error": "Stock API key not configured"}
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': quote['01. symbol'],
                    'price': float(quote['05. price']),
                    'change': quote['09. change'],
                    'change_percent': quote['10. change percent'],
                    'volume': quote['06. volume']
                }
            else:
                return {"error": f"Stock data not found for {symbol}"}
                
        except Exception as e:
            return {"error": f"Stock service error: {str(e)}"}

    async def _query_data(self, query: str) -> Dict[str, Any]:
        """Query internal data sources"""
        try:
            # Example: Query a local SQLite database
            db_path = 'data/chatbot_analytics.db'
            
            if not os.path.exists(db_path):
                return {"error": "Analytics database not found"}
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Simple analytics queries
            if 'user count' in query.lower():
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                result = f"Total users: {count}"
            
            elif 'recent chats' in query.lower():
                cursor.execute("SELECT COUNT(*) FROM conversations WHERE date > datetime('now', '-7 days')")
                count = cursor.fetchone()[0]
                result = f"Chats in last 7 days: {count}"
            
            else:
                result = "Available queries: user count, recent chats"
            
            conn.close()
            
            return {
                'query': query,
                'result': result,
                'database': 'chatbot_analytics'
            }
            
        except Exception as e:
            return {"error": f"Data query error: {str(e)}"}

    # Utility methods for parameter extraction
    def _extract_location(self, message: str) -> str:
        """Extract location from message"""
        # Simple extraction - can be enhanced with NLP
        words = message.split()
        for i, word in enumerate(words):
            if word.lower() in ['in', 'at', 'for']:
                if i + 1 < len(words):
                    return words[i + 1].strip('.,!?')
        return "New York"  # Default location

    def _extract_math_expression(self, message: str) -> str:
        """Extract mathematical expression from message"""
        # Look for numbers and operators
        import re
        pattern = r'[\d+\-*/().]+\s*'
        matches = re.findall(pattern, message)
        return ''.join(matches) if matches else "2+2"

    def _extract_file_path(self, message: str) -> str:
        """Extract file path from message"""
        # Look for file paths or file names
        words = message.split()
        for word in words:
            if '.' in word and ('/' in word or '\\' in word):
                return word
        return "./documents/sample.txt"  # Default

    def _extract_search_query(self, message: str) -> str:
        """Extract search query from message"""
        # Remove common question words
        stop_words = ['what', 'is', 'the', 'search', 'for', 'about', 'tell', 'me']
        words = [word for word in message.split() if word.lower() not in stop_words]
        return ' '.join(words)

    def _extract_stock_symbol(self, message: str) -> str:
        """Extract stock symbol from message"""
        # Look for uppercase words that might be stock symbols
        words = message.split()
        for word in words:
            if word.isupper() and 1 <= len(word) <= 5:
                return word
        return "AAPL"  # Default

    def _extract_data_query(self, message: str) -> str:
        """Extract data query from message"""
        return message  # Return full message for now

    def _create_enhanced_context(self, original_message: str, tool_results: Dict[str, Any]) -> str:
        """Create enhanced context for AI with tool results"""
        
        context = f"Original User Message: {original_message}\n\n"
        context += "Tool Results:\n"
        
        for tool_name, result in tool_results.items():
            if result['success']:
                context += f"- {tool_name}: {json.dumps(result['data'], indent=2)}\n"
            else:
                context += f"- {tool_name}: Error - {result['error']}\n"
        
        context += "\nPlease provide a comprehensive response using the tool results above."
        
        return context

    def _track_tool_usage(self, tools: List[str]):
        """Track tool usage for analytics"""
        for tool in tools:
            if tool in self.tool_usage_stats:
                self.tool_usage_stats[tool] += 1
            else:
                self.tool_usage_stats[tool] = 1

    def get_tool_usage_stats(self) -> Dict[str, int]:
        """Get tool usage statistics"""
        return self.tool_usage_stats.copy()

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return [
            {
                'name': name,
                'description': tool['description'],
                'parameters': tool['parameters']
            }
            for name, tool in self.tools.items()
        ]


# Example usage
async def demo_mcp_chatbot():
    """Demonstrate MCP-enhanced chatbot capabilities"""
    
    print("🚀 MCP-Enhanced ChatBot Demo")
    print("=" * 40)
    
    # Initialize enhanced chatbot
    bot = MCPEnhancedChatBot()
    
    # Test messages that will trigger different tools
    test_messages = [
        "What's the weather like in Tokyo?",
        "Calculate 25 * 4 + 100",
        "Search for latest AI news",
        "What's Apple's stock price?",
        "Show me user count data"
    ]
    
    for message in test_messages:
        print(f"\n👤 User: {message}")
        
        response = await bot.chat_with_tools(message)
        
        print(f"🤖 Bot: {response['response']}")
        
        if response['enhanced']:
            print(f"🔧 Tools used: {', '.join(response['tools_used'])}")
    
    # Show tool usage stats
    print(f"\n📊 Tool Usage Stats: {bot.get_tool_usage_stats()}")


if __name__ == "__main__":
    asyncio.run(demo_mcp_chatbot())
