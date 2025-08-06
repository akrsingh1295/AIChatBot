#!/usr/bin/env python3
"""
OpenAI API Key Test Script
Test if your OpenAI API key is working correctly
"""

import os
import sys
from dotenv import load_dotenv

def test_openai_api():
    """Test if OpenAI API key is working"""
    
    print("🧪 OpenAI API Key Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No API key found!")
        print("\n💡 Solutions:")
        print("   1. Create .env file in project root")
        print("   2. Add: OPENAI_API_KEY=sk-proj-your-key-here")
        print("   3. Make sure .env is in .gitignore")
        print("   4. Get your key from: https://platform.openai.com/api-keys")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format!")
        print(f"   Found: {api_key[:20]}...")
        print("\n💡 API key should start with 'sk-proj-' or 'sk-'")
        print("   Check your key at: https://platform.openai.com/api-keys")
        return False
    
    print(f"🔑 Testing API key: {api_key[:20]}...")
    
    # Try importing OpenAI
    try:
        from openai import OpenAI
        print("✅ OpenAI library imported successfully")
    except ImportError:
        print("❌ OpenAI library not found!")
        print("💡 Install with: pip install openai")
        return False
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")
        
        # Test basic API call
        print("🤖 Testing basic chat completion...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello from your ChatBot! API test successful.'"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        message = response.choices[0].message.content
        total_tokens = response.usage.total_tokens
        
        print("✅ API Key Working Perfectly!")
        print(f"🤖 AI Response: {message}")
        print(f"💰 Tokens Used: {total_tokens}")
        print(f"💵 Estimated Cost: ${total_tokens * 0.002 / 1000:.6f}")
        
        # Test model access
        print("\n🔍 Testing model access...")
        models_to_test = ["gpt-3.5-turbo", "gpt-4"]
        
        for model in models_to_test:
            try:
                test_response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                print(f"✅ {model}: Available")
            except Exception as e:
                if "model" in str(e).lower():
                    print(f"❌ {model}: Not available in your plan")
                else:
                    print(f"⚠️ {model}: Error - {e}")
        
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        
        print(f"❌ API Key Test Failed!")
        print(f"   Error: {e}")
        
        # Provide specific troubleshooting
        if "invalid api key" in error_msg:
            print("\n💡 Troubleshooting:")
            print("   1. Check if API key is copied correctly")
            print("   2. Generate a new key at: https://platform.openai.com/api-keys")
            print("   3. Make sure there are no extra spaces")
            
        elif "insufficient" in error_msg or "quota" in error_msg:
            print("\n💡 Billing Issue:")
            print("   1. Add payment method: https://platform.openai.com/account/billing")
            print("   2. Purchase minimum $5 credits")
            print("   3. Check usage: https://platform.openai.com/usage")
            
        elif "rate limit" in error_msg:
            print("\n💡 Rate Limit:")
            print("   1. Wait a moment and try again")
            print("   2. You may be on free tier with limits")
            print("   3. Upgrade plan if needed")
            
        elif "model" in error_msg:
            print("\n💡 Model Access:")
            print("   1. GPT-3.5-turbo should be available")
            print("   2. GPT-4 requires separate access")
            print("   3. Check your plan at: https://platform.openai.com/account/limits")
            
        else:
            print("\n💡 General Troubleshooting:")
            print("   1. Check internet connection")
            print("   2. Try generating a new API key")
            print("   3. Contact OpenAI support if issue persists")
        
        return False

def test_environment_setup():
    """Test if environment is properly set up"""
    
    print("\n🛠️ Environment Setup Check")
    print("=" * 50)
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        # Check if it's in .gitignore
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                gitignore_content = f.read()
                if '.env' in gitignore_content:
                    print("✅ .env is in .gitignore (secure)")
                else:
                    print("⚠️ .env not in .gitignore - add it for security!")
        else:
            print("⚠️ No .gitignore file found")
    else:
        print("❌ .env file not found")
        print("💡 Create with: touch .env")
    
    # Check python-dotenv
    try:
        import dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        print("❌ python-dotenv not installed")
        print("💡 Install with: pip install python-dotenv")
    
    # Check OpenAI library
    try:
        import openai
        print(f"✅ OpenAI library installed (version: {openai.__version__})")
    except ImportError:
        print("❌ OpenAI library not installed")
        print("💡 Install with: pip install openai")

def show_cost_estimates():
    """Show cost estimates for different usage patterns"""
    
    print("\n💰 Cost Estimates (GPT-3.5-turbo)")
    print("=" * 50)
    
    # Cost per 1K tokens
    input_cost_per_1k = 0.0015  # $0.0015 per 1K input tokens
    output_cost_per_1k = 0.002  # $0.002 per 1K output tokens
    
    scenarios = [
        ("Light usage", 50, 10),     # 50 messages, 10 tokens avg response
        ("Medium usage", 200, 20),   # 200 messages, 20 tokens avg response  
        ("Heavy usage", 500, 30),    # 500 messages, 30 tokens avg response
        ("Business usage", 1000, 50) # 1000 messages, 50 tokens avg response
    ]
    
    print("📊 Monthly Cost Estimates:")
    for scenario, messages, avg_tokens in scenarios:
        # Assume average input is also similar to output
        total_input_tokens = messages * avg_tokens
        total_output_tokens = messages * avg_tokens
        
        input_cost = (total_input_tokens / 1000) * input_cost_per_1k
        output_cost = (total_output_tokens / 1000) * output_cost_per_1k
        total_cost = input_cost + output_cost
        
        print(f"   {scenario:15} {messages:4} msgs: ${total_cost:.2f}/month")
    
    print("\n💡 Tips to reduce costs:")
    print("   - Use shorter prompts")
    print("   - Limit max_tokens in API calls")
    print("   - Implement conversation memory limits")
    print("   - Cache common responses")

def main():
    """Run all tests"""
    
    print("🔑 OpenAI API Key Testing Suite")
    print("🤖 For AI ChatBot Setup")
    print("=" * 60)
    
    # Test environment setup
    test_environment_setup()
    
    # Test API key
    api_success = test_openai_api()
    
    # Show cost estimates
    show_cost_estimates()
    
    print("\n" + "=" * 60)
    
    if api_success:
        print("🎉 SUCCESS! Your OpenAI API key is working!")
        print("\n🚀 Next Steps:")
        print("   1. Start your backend: python start_backend.py")
        print("   2. Start your frontend: ./start_frontend.sh")
        print("   3. Open http://localhost:3000")
        print("   4. Initialize chatbot with your API key")
        print("\n✨ Your ChatBot is ready for multi-language conversations!")
    else:
        print("❌ SETUP INCOMPLETE")
        print("\n🔧 Required Actions:")
        print("   1. Get OpenAI API key: https://platform.openai.com/api-keys")
        print("   2. Add payment method and credits")
        print("   3. Create .env file with OPENAI_API_KEY")
        print("   4. Run this test again")
        
        print("\n📚 Full Setup Guide:")
        print("   Check: OPENAI_API_SETUP_GUIDE.md")

if __name__ == "__main__":
    main() 