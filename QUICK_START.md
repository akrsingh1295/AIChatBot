# 🚀 Quick Start Guide

## 📋 **Get Your ChatBot Running in 5 Minutes**

Follow these simple steps to get your AI ChatBot working with OpenAI API.

---

## 🔑 **Step 1: Get OpenAI API Key (2 minutes)**

### **1. Create OpenAI Account:**
```
🌐 Visit: https://platform.openai.com/
🔐 Sign up with email/Google/Microsoft
✅ Verify your email
```

### **2. Get Your API Key:**
```
🔑 Go to: https://platform.openai.com/api-keys
🔵 Click "Create new secret key"
📝 Name it: "My ChatBot Key"
💾 Copy the key (starts with sk-proj-...)
```

### **3. Add Billing (Required):**
```
💳 Go to: https://platform.openai.com/account/billing
💳 Add payment method (credit/debit card)
💰 Purchase $5-10 credits (minimum)
```

---

## ⚙️ **Step 2: Configure Your ChatBot (1 minute)**

### **Create `.env` file:**
```bash
# In your project folder: /Users/akash.singh/Desktop/ChatBot/AIChatBot/
touch .env
```

### **Add your API key to `.env`:**
```bash
# Edit .env file with your key
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

---

## 🧪 **Step 3: Test Your Setup (30 seconds)**

```bash
# Install dependencies (if not done)
pip install python-dotenv openai

# Test your API key
python test_openai_key.py
```

**Expected Output:**
```
✅ API Key Working Perfectly!
🤖 AI Response: Hello from your ChatBot! API test successful.
```

---

## 🚀 **Step 4: Start Your ChatBot (1 minute)**

### **Terminal 1 - Start Backend:**
```bash
source venv/bin/activate
python start_backend.py
```

### **Terminal 2 - Start Frontend:**
```bash
./start_frontend.sh
```

### **Open Your ChatBot:**
```
🌐 Open: http://localhost:3000
🎯 Initialize with your API key
🤖 Start chatting!
```

---

## 🌍 **Features You Can Test**

### **Multi-Language Chat:**
```
English: "What is artificial intelligence?"
Hindi: "कृत्रिम बुद्धिमत्ता क्या है?"
Chinese: "什么是人工智能？"
Japanese: "人工知能とは何ですか？"
Spanish: "¿Qué es la inteligencia artificial?"
```

### **Document Upload:**
```
📁 Upload text files in any language
🔄 Automatic translation to English
💾 Stored in knowledge base
🔍 Searchable in any language
```

---

## 💰 **Cost Information**

### **Typical Costs (GPT-3.5-turbo):**
```
💬 100 messages/day: ~$3-5/month
💬 500 messages/day: ~$15-25/month
💬 1000 messages/day: ~$30-50/month
🌍 Multi-language: +20-30% (for translations)
```

### **Free Tier Limits:**
```
⚠️ New accounts get $5 free credits
⚠️ Rate limits apply on free tier
✅ Upgrade for higher limits
```

---

## 🚨 **Troubleshooting**

### **❌ "Invalid API Key":**
```
🔧 Solution:
1. Check if key starts with 'sk-'
2. Make sure no extra spaces
3. Generate a new key if needed
```

### **❌ "Insufficient Credits":**
```
🔧 Solution:
1. Add payment method to OpenAI account
2. Purchase minimum $5 credits
3. Check billing dashboard
```

### **❌ "Rate Limit Exceeded":**
```
🔧 Solution:
1. Wait a moment and try again
2. You may be on free tier
3. Consider upgrading your plan
```

---

## 📞 **Need Help?**

### **📚 Detailed Guides:**
- `OPENAI_API_SETUP_GUIDE.md` - Complete API setup
- `MULTILINGUAL_GUIDE.md` - Multi-language features
- `CONTENT_FILTERING_GUIDE.md` - Content safety
- `DEPLOYMENT.md` - Production deployment

### **🧪 Test Scripts:**
```bash
python test_openai_key.py      # Test API key
python test_multilingual.py    # Test languages
python test_content_filter.py  # Test content filtering
```

### **🌐 Support:**
- OpenAI Documentation: https://platform.openai.com/docs
- OpenAI Community: https://community.openai.com/

---

## 🎯 **Quick Checklist**

```
□ Created OpenAI account
□ Generated API key (sk-proj-...)
□ Added payment method & credits
□ Created .env file with API key
□ Tested API key (python test_openai_key.py)
□ Started backend (python start_backend.py)
□ Started frontend (./start_frontend.sh)
□ Opened http://localhost:3000
□ Initialized chatbot with API key
□ Tested basic chat
□ Tested multi-language features
```

---

**🎉 Congratulations! Your AI ChatBot is now running with OpenAI! 🚀**

**You can now chat in 12+ languages with automatic translation and content filtering!** 