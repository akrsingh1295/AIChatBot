#!/usr/bin/env python3
"""
Backend server startup script for the AI ChatBot application.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if we're in the virtual environment and have required packages."""
    try:
        import fastapi
        import langchain
        import openai
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please activate your virtual environment and install requirements:")
        print("source venv/bin/activate && pip install -r requirements.txt")
        return False

def start_server():
    """Start the FastAPI server."""
    if not check_environment():
        sys.exit(1)
    
    print("🚀 Starting AI ChatBot Backend Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("💡 Make sure to set your OpenAI API key in the frontend!")
    print("\n" + "="*50 + "\n")
    
    try:
        # Change to the project root directory
        os.chdir(Path(__file__).parent)
        
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_server() 