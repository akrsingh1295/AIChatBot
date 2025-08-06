# 🔑 OpenAI API Key Setup Guide

## 📋 **Overview**

To use your AI ChatBot with GPT-3.5/GPT-4, you need an OpenAI API key. This guide shows you exactly how to get one and set it up safely.

---

## 🚀 **Step 1: Get Your OpenAI API Key**

### **📝 Create OpenAI Account:**

1. **Visit OpenAI Platform:**
   ```
   🌐 Go to: https://platform.openai.com/
   ```

2. **Sign Up or Log In:**
   ```
   ✅ Create account with email/Google/Microsoft
   ✅ Verify your email address
   ✅ Complete profile setup
   ```

3. **Navigate to API Keys:**
   ```
   🔑 Click on your profile (top-right)
   🔑 Select "View API keys"
   🔑 Or go directly to: https://platform.openai.com/api-keys
   ```

4. **Create New API Key:**
   ```
   🔵 Click "Create new secret key"
   📝 Give it a name: "My ChatBot Key"
   💾 Copy the key immediately (you won't see it again!)
   ```

### **⚠️ Important Security Notes:**
```
🔒 Your API key looks like: sk-proj-aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890...
🔒 NEVER share this key publicly
🔒 NEVER commit it to Git/GitHub
🔒 Store it securely (we'll show you how)
```

---

## 💳 **Step 2: Set Up Billing (Required)**

### **📊 Add Payment Method:**

1. **Go to Billing:**
   ```
   💳 Visit: https://platform.openai.com/account/billing/overview
   ```

2. **Add Payment Method:**
   ```
   💳 Click "Add payment method"
   💳 Enter credit/debit card details
   💳 Set spending limit (recommended: $10-20/month for testing)
   ```

3. **Purchase Credits:**
   ```
   💰 Minimum: $5 credit purchase
   💰 Recommended for testing: $10-20
   💰 You only pay for what you use
   ```

### **💰 Cost Estimate for Your ChatBot:**
```
📊 GPT-3.5-turbo pricing:
   - Input: $0.0015 per 1K tokens (~750 words)
   - Output: $0.002 per 1K tokens (~750 words)

📊 Typical usage:
   - 100 messages/day: ~$3-5/month
   - 500 messages/day: ~$15-25/month
   - 1000 messages/day: ~$30-50/month

📊 Translation costs (multi-language):
   - Additional ~$0.002 per 1K characters translated
   - Adds roughly 20-30% to total costs
```

---

## ⚙️ **Step 3: Configure API Key in Your ChatBot**

### **🔐 Method 1: Environment Variables (Recommended)**

#### **For Development (Local Testing):**

1. **Create `.env` file in your project root:**
   ```bash
   # In /Users/akash.singh/Desktop/ChatBot/AIChatBot/
   touch .env
   ```

2. **Add your API key to `.env`:**
   ```bash
   # .env file content
   OPENAI_API_KEY=sk-proj-your-actual-api-key-here
   ENVIRONMENT=development
   DEBUG=true
   ```

3. **Make sure `.env` is in `.gitignore`:**
   ```bash
   # Check if .env is already ignored
   cat .gitignore | grep .env
   
   # If not found, add it:
   echo ".env" >> .gitignore
   ```

4. **Install python-dotenv (if not already installed):**
   ```bash
   pip install python-dotenv
   ```

#### **For Production:**

1. **Use your hosting provider's environment variables:**
   ```bash
   # Example for different platforms:
   
   # Heroku:
   heroku config:set OPENAI_API_KEY=sk-proj-your-key-here
   
   # AWS/Digital Ocean:
   export OPENAI_API_KEY=sk-proj-your-key-here
   
   # Docker:
   docker run -e OPENAI_API_KEY=sk-proj-your-key-here your-app
   ```

### **🔐 Method 2: Direct Input (Frontend)**

The chatbot can accept the API key through the web interface:

1. **Initialize chatbot with API key:**
   ```javascript
   // Frontend sends API key during initialization
   const response = await fetch('/initialize', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({
       api_key: 'sk-proj-your-api-key-here',
       memory_window: 20,
       temperature: 0.7
     })
   });
   ```

---

## 🧪 **Step 4: Test Your API Key**

### **🔍 Quick Test Script:**

Create a test file to verify your API key works:

```python
# test_openai_key.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_api():
    """Test if OpenAI API key is working"""
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No API key found!")
        print("💡 Add OPENAI_API_KEY to your .env file")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format!")
        print("💡 API key should start with 'sk-'")
        return False
    
    print(f"🔑 Testing API key: {api_key[:20]}...")
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Test API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello from your ChatBot!'"}
            ],
            max_tokens=50
        )
        
        message = response.choices[0].message.content
        print(f"✅ API Key Working!")
        print(f"🤖 Response: {message}")
        print(f"💰 Tokens used: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Key Test Failed: {e}")
        return False

if __name__ == "__main__":
    test_openai_api()
```

Run the test:
```bash
python test_openai_key.py
```

### **✅ Expected Success Output:**
```
🔑 Testing API key: sk-proj-aBcDeFgHiJkL...
✅ API Key Working!
🤖 Response: Hello from your ChatBot!
💰 Tokens used: 15
```

---

## 🌐 **Step 5: Start Your ChatBot**

### **🚀 With Environment Variables:**

1. **Make sure your `.env` file exists:**
   ```bash
   cat .env
   # Should show: OPENAI_API_KEY=sk-proj-...
   ```

2. **Start backend:**
   ```bash
   source venv/bin/activate
   python start_backend.py
   ```

3. **Start frontend:**
   ```bash
   ./start_frontend.sh
   ```

4. **Open chatbot:**
   ```
   🌐 Frontend: http://localhost:3000
   🔗 API Docs: http://localhost:8000/docs
   ```

### **🎯 Initialize via Web Interface:**

If not using environment variables, you can enter the API key in the web interface:

```javascript
// The frontend initialization form will ask for:
{
  "api_key": "sk-proj-your-api-key-here",
  "memory_window": 20,
  "temperature": 0.7
}
```

---

## 🔐 **Security Best Practices**

### **✅ DO:**
```
🔒 Store API key in environment variables
🔒 Use .env files for local development
🔒 Add .env to .gitignore
🔒 Set spending limits on OpenAI account
🔒 Monitor API usage regularly
🔒 Rotate API keys periodically
🔒 Use different keys for dev/staging/production
```

### **❌ DON'T:**
```
❌ Hard-code API key in source code
❌ Commit API key to Git/GitHub
❌ Share API key in emails/messages
❌ Use production key for testing
❌ Leave API key in browser console
❌ Store API key in plain text files
```

---

## 🚨 **Troubleshooting Common Issues**

### **❌ "Invalid API Key" Error:**
```
Problem: API key not recognized
Solutions:
  ✅ Check key format (starts with sk-)
  ✅ Verify key is copied completely
  ✅ Check for extra spaces/characters
  ✅ Try generating a new key
```

### **❌ "Insufficient Credits" Error:**
```
Problem: No billing/credits set up
Solutions:
  ✅ Add payment method to OpenAI account
  ✅ Purchase minimum $5 credits
  ✅ Check billing dashboard
```

### **❌ "Rate Limit Exceeded" Error:**
```
Problem: Too many requests
Solutions:
  ✅ Wait and retry
  ✅ Implement rate limiting in your app
  ✅ Upgrade to higher tier plan
```

### **❌ "Model Not Found" Error:**
```
Problem: Using unsupported model
Solutions:
  ✅ Use gpt-3.5-turbo (default)
  ✅ Check available models in your account
  ✅ Upgrade for GPT-4 access
```

---

## 📊 **Monitoring Usage & Costs**

### **📈 Track API Usage:**

1. **OpenAI Dashboard:**
   ```
   📊 Visit: https://platform.openai.com/usage
   📊 View: Daily/monthly usage
   📊 Monitor: Costs and token consumption
   ```

2. **Set Up Alerts:**
   ```
   🔔 Go to: https://platform.openai.com/account/billing/limits
   🔔 Set: Usage alerts (e.g., $10 warning)
   🔔 Set: Hard limits (e.g., $50 maximum)
   ```

### **💰 Cost Optimization Tips:**
```
🎯 Use gpt-3.5-turbo instead of gpt-4 (10x cheaper)
🎯 Limit max_tokens in API calls
🎯 Cache common responses
🎯 Implement conversation memory limits
🎯 Use shorter prompts when possible
🎯 Monitor and optimize system prompts
```

---

## 🔄 **API Key Management**

### **🔑 Multiple Keys Strategy:**
```
🌍 Development: sk-proj-dev-key-...
🧪 Testing: sk-proj-test-key-...
🚀 Production: sk-proj-prod-key-...
```

### **🔄 Key Rotation:**
```bash
# Monthly key rotation script
# 1. Generate new key in OpenAI dashboard
# 2. Update environment variables
# 3. Test new key
# 4. Delete old key
# 5. Monitor for any issues
```

---

## 🎯 **Quick Start Checklist**

### **📋 Before You Begin:**
- [ ] Create OpenAI account
- [ ] Verify email address
- [ ] Add payment method
- [ ] Purchase minimum $5 credits
- [ ] Generate API key
- [ ] Copy key securely

### **📋 Setup Steps:**
- [ ] Create `.env` file
- [ ] Add `OPENAI_API_KEY=your-key`
- [ ] Add `.env` to `.gitignore`
- [ ] Test API key with test script
- [ ] Start backend server
- [ ] Start frontend application
- [ ] Initialize chatbot with API key

### **📋 Post-Setup:**
- [ ] Test basic chat functionality
- [ ] Test multi-language features
- [ ] Test document upload
- [ ] Set up usage monitoring
- [ ] Configure spending limits

---

## 🆘 **Need Help?**

### **📞 Support Resources:**
```
🌐 OpenAI Documentation: https://platform.openai.com/docs
💬 OpenAI Community: https://community.openai.com/
📧 OpenAI Support: https://help.openai.com/
📚 API Reference: https://platform.openai.com/docs/api-reference
```

### **🧪 Test Commands:**
```bash
# Test API key
python test_openai_key.py

# Test full chatbot
curl -X POST "http://localhost:8000/initialize" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-key-here"}'
```

---

**🎉 You're now ready to use your ChatBot with OpenAI! 🚀**

**Your ChatBot supports GPT-3.5-turbo by default and can be upgraded to GPT-4 when you have access.** 