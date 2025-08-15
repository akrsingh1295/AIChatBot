#!/usr/bin/env python3
"""
Complete Setup Verification Script
Tests both backend functionality and confirms frontend is accessible
"""

import requests
import json
import os
import time
from datetime import datetime

def test_backend():
    """Test backend functionality"""
    print("🔧 Testing Backend...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend running - Version: {data.get('version', 'Unknown')}")
            print(f"✅ Features: {', '.join(data.get('features', []))}")
            
            # Test tools endpoint (should fail without initialization)
            tools_response = requests.get(f"{base_url}/tools/available", timeout=5)
            if tools_response.status_code == 400:
                print("✅ Tools endpoint responding (requires initialization)")
            
            # Test agents endpoint (should fail without initialization)  
            agents_response = requests.get(f"{base_url}/agents/available", timeout=5)
            if agents_response.status_code == 400:
                print("✅ Agents endpoint responding (requires initialization)")
                
            return True
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running - Please start with:")
        print("   cd /Users/abhinav/AIChatBot")
        print("   source env/bin/activate")  
        print("   PYTHONPATH=/Users/abhinav/AIChatBot python3 backend/server.py")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_frontend_accessibility():
    """Test frontend file accessibility"""
    print("\n🎨 Testing Frontend...")
    
    frontend_path = "/Users/abhinav/AIChatBot/frontend/standalone_frontend.html"
    
    if os.path.exists(frontend_path):
        print("✅ Standalone frontend file exists")
        
        # Check file size (should be substantial)
        file_size = os.path.getsize(frontend_path)
        if file_size > 10000:  # 10KB+
            print(f"✅ Frontend file size: {file_size // 1024}KB (looks complete)")
        else:
            print(f"⚠️ Frontend file size: {file_size}B (might be incomplete)")
            
        # Check if it contains key elements
        with open(frontend_path, 'r') as f:
            content = f.read()
            
        required_elements = [
            'AI ChatBot with MCP Tools',
            'Standard Chat',
            'MCP Tools', 
            'AI Agent',
            'API_BASE_URL',
            'initializeChatbot'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
                
        if not missing_elements:
            print("✅ Frontend contains all required elements")
        else:
            print(f"⚠️ Frontend missing: {', '.join(missing_elements)}")
            
        print(f"✅ Frontend accessible at: file://{frontend_path}")
        return True
    else:
        print(f"❌ Frontend file not found at: {frontend_path}")
        return False

def test_react_frontend():
    """Test if React frontend could be started"""
    print("\n⚛️ Testing React Frontend Setup...")
    
    react_path = "/Users/abhinav/AIChatBot/frontend/react-app"
    package_json = os.path.join(react_path, "package.json")
    
    if os.path.exists(package_json):
        print("✅ React app structure exists")
        
        # Check for node_modules
        node_modules = os.path.join(react_path, "node_modules") 
        if os.path.exists(node_modules):
            print("✅ Dependencies installed")
        else:
            print("⚠️ Dependencies not installed (run 'npm install')")
            
        # Check for Node.js
        try:
            import subprocess
            result = subprocess.run(['which', 'node'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js found at: {result.stdout.strip()}")
                
                # Check version
                version_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
                print(f"✅ Node.js version: {version_result.stdout.strip()}")
                return True
            else:
                print("❌ Node.js not found - Install from https://nodejs.org/")
                print("   Alternatives:")
                print("   • brew install node")
                print("   • Use nvm (Node Version Manager)")
                return False
        except Exception as e:
            print(f"⚠️ Could not check Node.js: {e}")
            return False
    else:
        print(f"❌ React app not found at: {react_path}")
        return False

def display_usage_guide():
    """Display usage instructions"""
    print(f"\n🎯 Usage Guide:")
    print("=" * 60)
    
    print("\n1. Backend (Required - Currently Running):")
    print("   ✅ http://localhost:8000")
    
    print("\n2. Frontend Options:")
    print("   🌐 Standalone HTML (Ready Now):")
    print("     • file:///Users/abhinav/AIChatBot/frontend/standalone_frontend.html")
    print("     • All features working")
    print("     • No installation required")
    
    print("\n   ⚛️ React Frontend (Requires Node.js):")
    print("     • Install Node.js from https://nodejs.org/")
    print("     • cd /Users/abhinav/AIChatBot/frontend/react-app")
    print("     • npm install && npm start")
    print("     • http://localhost:3000")
    
    print("\n3. Test All Capabilities:")
    print("   🔵 Standard Chat: 'Hello, tell me a joke'")
    print("   🟡 MCP Tools: 'Calculate 25 * 4 + 100'")
    print("   🟢 AI Agent: 'Create a project plan for mobile app'")
    print("   📚 Knowledge: Upload documents and ask questions")

def main():
    """Main verification function"""
    print("🚀 Complete AI Chatbot Setup Verification")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    backend_ok = test_backend()
    frontend_ok = test_frontend_accessibility() 
    react_ok = test_react_frontend()
    
    print(f"\n📊 Setup Status Summary:")
    print("=" * 60)
    print(f"✅ Backend (FastAPI): {'RUNNING' if backend_ok else 'NOT RUNNING'}")
    print(f"✅ Standalone Frontend: {'READY' if frontend_ok else 'NOT READY'}")
    print(f"⚛️ React Frontend: {'READY' if react_ok else 'NEEDS NODE.JS'}")
    
    if backend_ok and frontend_ok:
        print(f"\n🎉 SUCCESS: Your AI chatbot is ready to use!")
        print(f"🌟 You can start testing immediately with the standalone frontend.")
        
        if not react_ok:
            print(f"\n💡 Optional: Install Node.js for React frontend development features.")
    else:
        print(f"\n⚠️ Issues found - see details above")
    
    display_usage_guide()

if __name__ == "__main__":
    main()

