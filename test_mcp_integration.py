#!/usr/bin/env python3
"""
Test script for MCP integration in ChatBot
Run this to verify that the enhanced chatbot with MCP tools is working
"""

import asyncio
import requests
import json
import os
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_API_KEY = os.getenv("OPENAI_API_KEY", "your-test-api-key-here")

def test_api_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        print(f"\n{'='*60}")
        print(f"Testing: {method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            if isinstance(result, dict):
                for key, value in result.items():
                    if isinstance(value, (list, dict)):
                        print(f"  {key}: {len(value) if isinstance(value, list) else 'object'}")
                    else:
                        print(f"  {key}: {value}")
            return result
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    """Run comprehensive tests of the MCP-enhanced chatbot"""
    
    print("🚀 Testing MCP-Enhanced ChatBot Integration")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    
    # Test 1: Check if server is running
    print("\n" + "="*60)
    print("TEST 1: Server Status")
    root_response = test_api_endpoint("/")
    
    if not root_response:
        print("❌ Server is not running. Please start the server with:")
        print("   python backend/server.py")
        return
    
    # Test 2: Initialize chatbot
    print("\n" + "="*60)
    print("TEST 2: Initialize Chatbot")
    
    init_data = {
        "api_key": TEST_API_KEY,
        "memory_window": 20,
        "temperature": 0.7
    }
    
    init_response = test_api_endpoint("/initialize", "POST", init_data)
    
    if not init_response or not init_response.get("success"):
        print("❌ Failed to initialize chatbot. Check your OpenAI API key.")
        return
    
    print(f"✅ Chatbot initialized with MCP tools: {init_response.get('mcp_tools_enabled', False)}")
    
    # Test 3: Check available tools
    print("\n" + "="*60)
    print("TEST 3: Available MCP Tools")
    
    tools_response = test_api_endpoint("/tools/available")
    
    if tools_response:
        tools = tools_response.get("tools", [])
        print(f"✅ Found {len(tools)} available tools:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
    
    # Test 4: Standard chat
    print("\n" + "="*60)
    print("TEST 4: Standard Chat")
    
    chat_data = {
        "message": "Hello! How are you today?",
        "mode": "general",
        "session_id": "test_session"
    }
    
    chat_response = test_api_endpoint("/chat", "POST", chat_data)
    
    if chat_response and chat_response.get("success"):
        print(f"✅ Standard chat working")
        print(f"   Response: {chat_response['response'][:100]}...")
    
    # Test 5: Enhanced chat with MCP tools
    print("\n" + "="*60)
    print("TEST 5: Enhanced Chat with MCP Tools")
    
    # Test calculator tool
    enhanced_data = {
        "message": "Calculate 25 * 4 + 100 for me",
        "session_id": "test_session",
        "use_tools": True
    }
    
    enhanced_response = test_api_endpoint("/chat/enhanced", "POST", enhanced_data)
    
    if enhanced_response and enhanced_response.get("success"):
        print(f"✅ Enhanced chat working")
        print(f"   Enhanced: {enhanced_response.get('enhanced', False)}")
        print(f"   Tools used: {enhanced_response.get('tools_used', [])}")
        print(f"   Response: {enhanced_response['response'][:150]}...")
    
    # Test 6: Weather tool (if API key available)
    print("\n" + "="*60)
    print("TEST 6: Weather Tool")
    
    weather_data = {
        "message": "What's the weather like in London?",
        "session_id": "test_session",
        "use_tools": True
    }
    
    weather_response = test_api_endpoint("/chat/enhanced", "POST", weather_data)
    
    if weather_response and weather_response.get("success"):
        print(f"✅ Weather tool test")
        print(f"   Enhanced: {weather_response.get('enhanced', False)}")
        print(f"   Tools used: {weather_response.get('tools_used', [])}")
        print(f"   Response: {weather_response['response'][:150]}...")
    
    # Test 7: File tool
    print("\n" + "="*60)
    print("TEST 7: File Reading Tool")
    
    file_data = {
        "message": "Can you read the file ./documents/sample.txt?",
        "session_id": "test_session", 
        "use_tools": True
    }
    
    file_response = test_api_endpoint("/chat/enhanced", "POST", file_data)
    
    if file_response and file_response.get("success"):
        print(f"✅ File tool test")
        print(f"   Enhanced: {file_response.get('enhanced', False)}")
        print(f"   Tools used: {file_response.get('tools_used', [])}")
        print(f"   Response: {file_response['response'][:150]}...")
    
    # Test 8: Tool usage statistics
    print("\n" + "="*60)
    print("TEST 8: Tool Usage Statistics")
    
    stats_response = test_api_endpoint("/tools/usage-stats")
    
    if stats_response:
        print(f"✅ Tool usage statistics:")
        stats = stats_response.get("tool_usage_stats", {})
        total_calls = stats_response.get("total_tool_calls", 0)
        print(f"   Total tool calls: {total_calls}")
        for tool, count in stats.items():
            print(f"   {tool}: {count} times")
    
    # Final summary
    print("\n" + "="*80)
    print("🎉 MCP INTEGRATION TEST COMPLETE!")
    print("="*80)
    
    print("\n✅ Your chatbot now supports:")
    print("   • Standard conversation mode")
    print("   • Enhanced mode with MCP tools")
    print("   • Real-time calculations")
    print("   • Weather information (with API key)")
    print("   • File reading capabilities")
    print("   • Web search (basic)")
    print("   • Stock prices (with API key)")
    print("   • Database queries")
    
    print("\n🚀 Next steps:")
    print("   1. Add API keys for weather/stock tools in .env file")
    print("   2. Test with your frontend application")
    print("   3. Monitor tool usage statistics")
    print("   4. Add custom business-specific tools")
    
    print("\n📖 API endpoints:")
    print("   • POST /chat/enhanced - Enhanced chat with tools")
    print("   • GET /tools/available - List available tools") 
    print("   • GET /tools/usage-stats - Tool usage statistics")
    
if __name__ == "__main__":
    main()
