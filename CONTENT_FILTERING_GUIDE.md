# 🛡️ Content Filtering & Moderation System

## 📋 **Overview**

Your AI ChatBot now includes a comprehensive content filtering system that automatically blocks inappropriate content, sexual material, controversial documents, and potentially harmful requests. This ensures a safe and professional user experience.

---

## 🔒 **What Gets Blocked**

### **💬 Chat Messages:**
```
❌ Sexual Content: "nude photos", "adult content", "xxx"
❌ Violence: "how to make bombs", "kill", "murder"
❌ Hate Speech: "racist", "nazi", "terrorism"
❌ Illegal Activities: "hack", "piracy", "drugs"
❌ Self-Harm: "suicide", "kill myself"
❌ Business Sensitive: "confidential", "layoffs"
```

### **📁 File Uploads:**
```
❌ Executable Files: .exe, .bat, .cmd, .js, .jar
❌ Large Files: > 10MB individual, > 50MB total
❌ Inappropriate Content: Text files with blocked words
❌ Malicious Signatures: Binary executables, suspicious patterns
❌ Sensitive Data: Files containing passwords, API keys
```

### **✅ What's Allowed:**
```
✅ Text Files: .txt, .csv, .md, .json
✅ Educational Content: Biology, health, science topics
✅ Business Queries: Product info, support requests
✅ Technical Questions: Programming, AI, technology
✅ Normal Conversations: Greetings, thanks, help requests
```

---

## 🎯 **Multi-Layer Protection**

### **Layer 1: Keyword Filtering**
- **Built-in wordlist** with 40+ inappropriate terms
- **Pattern matching** for dangerous phrases
- **Business-specific** blocked terms

### **Layer 2: OpenAI Moderation API**
- **AI-powered detection** of subtle inappropriate content
- **Category classification**: hate, sexual, violence, etc.
- **Real-time analysis** of all messages

### **Layer 3: File Security**
- **File type validation** - only safe formats allowed
- **Content scanning** - text files analyzed for inappropriate content
- **Malware detection** - checks for executable signatures
- **Size limits** - prevents resource exhaustion

### **Layer 4: Business Protection**
- **Sensitive data detection** - blocks passwords, API keys
- **Confidential content** - prevents leaks of internal information
- **Competitor mentions** - configurable business filtering

---

## ⚙️ **Configuration Levels**

### **🔒 Strict (Production Default)**
```python
✅ All filtering enabled
✅ OpenAI Moderation API
✅ Maximum security
✅ Business-grade protection
✅ Complete logging
```

### **⚖️ Moderate (Balanced)**
```python
✅ Core filtering enabled  
✅ Educational exceptions
✅ Balanced approach
✅ Some flexibility
```

### **🟡 Lenient (Development)**
```python
⚠️ Basic filtering only
⚠️ Educational content allowed
⚠️ Testing-friendly
⚠️ Reduced restrictions
```

---

## 🛠️ **How It Works**

### **When User Sends Message:**
```
1. 🔍 Check message for blocked words
2. 🤖 Send to OpenAI Moderation API  
3. 📏 Verify message length limits
4. 📊 Categorize and log request
5. ✅ Allow or ❌ Block with reason
```

### **When User Uploads File:**
```
1. 📁 Check file extension (.txt, .csv allowed)
2. 📏 Verify file size (< 10MB)
3. 🔍 Scan file content for inappropriate text
4. 🛡️ Check for malicious signatures
5. 🧹 Sanitize filename (remove ../../../)
6. ✅ Allow or ❌ Block with reason
```

### **When AI Responds:**
```
1. 🤖 Generate AI response
2. 🔍 Filter AI response (safety check)
3. 🛡️ Replace with safe message if needed
4. 📊 Log response for monitoring
5. ✅ Send filtered response to user
```

---

## 📊 **Real-Time Monitoring**

### **Security Logs:**
```
📝 All blocked content attempts
📝 File upload attempts  
📝 Suspicious activity patterns
📝 User IP addresses
📝 Timestamps and details
```

### **Alerts:**
```
🚨 Multiple blocks from same IP
🚨 Unusual upload patterns
🚨 Potential attacks detected
🚨 System health issues
```

---

## 🎪 **Usage Examples**

### **✅ Safe Interactions:**
```
User: "How do I use machine learning for business?"
✅ ALLOWED: Educational/business question

User: "What are your company's services?"  
✅ ALLOWED: Business inquiry

User: [uploads] "product_specs.txt" (2MB, contains technical docs)
✅ ALLOWED: Safe file type and content
```

### **❌ Blocked Interactions:**
```
User: "How to hack into systems?"
❌ BLOCKED: "Content contains inappropriate material: 'hack'"

User: "I want to see adult content"
❌ BLOCKED: "Content flagged for: sexual"

User: [uploads] "passwords.txt" (contains "password: admin123")
❌ BLOCKED: "File contains sensitive information: password"
```

---

## 🔧 **Customization Options**

### **1. Adjust Filter Level:**
```python
# In content_filter_config.py
FILTER_LEVEL = "strict"    # strict, moderate, lenient
```

### **2. Add Custom Blocked Words:**
```python
CUSTOM_BLOCKED_WORDS = {
    'your_company_competitor',
    'internal_project_codename',
    'sensitive_term'
}
```

### **3. Configure File Types:**
```python
ALLOWED_FILE_EXTENSIONS = {
    '.txt', '.csv', '.md', '.json'
    # Add '.pdf' if you add PDF support
}
```

### **4. Adjust Size Limits:**
```python
MAX_INDIVIDUAL_FILE_SIZE_MB = 10    # Per file
MAX_TOTAL_FILE_SIZE_MB = 50         # All files combined
MAX_MESSAGE_LENGTH = 10000          # Characters
```

---

## 🏢 **Business Configurations**

### **Corporate Environment:**
```python
from backend.content_filter import BusinessContentFilter

# Stricter filtering for business
filter = BusinessContentFilter(api_key="your-openai-key")
```

### **Educational Institution:**
```python  
from backend.content_filter import EducationalContentFilter

# Allows educational content
filter = EducationalContentFilter(api_key="your-openai-key")
```

---

## 🧪 **Testing Your Setup**

### **Run Content Filter Tests:**
```bash
# Test the filtering system
python test_content_filter.py

# Expected output:
✅ Safe content allowed
❌ Inappropriate content blocked  
📊 File filtering working
🛡️ Security features active
```

### **Test with Real Examples:**
```bash
# Test chat filtering
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How to make bombs"}'

# Expected: 400 error with "Message blocked by content filter"
```

---

## 📈 **Production Recommendations**

### **🔒 Security Best Practices:**
1. **Always use OpenAI Moderation API** for best results
2. **Enable all logging** for security monitoring  
3. **Review blocked content logs** regularly
4. **Set up alerts** for suspicious activity
5. **Test with your specific use cases**

### **⚡ Performance Optimization:**
1. **Cache moderation results** for repeated content
2. **Use rate limiting** to prevent abuse
3. **Monitor API usage** costs
4. **Regular security audits**

### **📊 Monitoring Dashboard:**
```
📈 Messages processed: 1,247 today
❌ Content blocked: 23 (1.8%)
📁 Files uploaded: 45
🚨 Security alerts: 0
⚡ Response time: <200ms
```

---

## 🚨 **Emergency Procedures**

### **If Content Filter Fails:**
```python
# Fallback to basic filtering
FILTER_LEVEL = "strict"
USE_OPENAI_MODERATION = False  # Temporary
LOG_ALL_CONTENT = True         # For investigation
```

### **If Under Attack:**
```python
# Enhanced security mode
SUSPICIOUS_ACTIVITY_THRESHOLD = 3  # Lower threshold
ENABLE_IP_BLOCKING = True         # Block repeat offenders
REQUIRE_AUTHENTICATION = True     # No anonymous usage
```

---

## 🎯 **Quick Reference**

### **Configuration Files:**
- `backend/content_filter.py` - Main filtering logic
- `content_filter_config.py` - Configuration settings
- `test_content_filter.py` - Testing script

### **Key Features:**
```
🛡️ Multi-layer content filtering
🤖 OpenAI Moderation API integration
📁 Comprehensive file security
📊 Real-time monitoring & logging
⚙️ Configurable filter levels
🏢 Business-specific protections
```

### **API Responses:**
```json
// Blocked content
{
  "detail": "Message blocked by content filter: Content contains inappropriate material: 'bomb'"
}

// Blocked file  
{
  "detail": "File 'document.exe' rejected: File type '.exe' is not allowed for security reasons"
}
```

---

**Your chatbot is now protected with enterprise-grade content filtering! 🛡️**

**For support or custom configurations, refer to the configuration files and test scripts provided.** 