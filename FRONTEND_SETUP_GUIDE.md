# 🔧 Frontend Setup & Testing Guide

## 🚨 **Issue Identified: Node.js Not Installed**

The React frontend can't start because Node.js and npm are not installed on your system.

## 🎯 **Immediate Solution: Standalone Frontend**

I've created a **standalone HTML frontend** that works without Node.js:

### **✅ Quick Test (No Installation Required):**

1. **Make sure backend is running:**
   ```bash
   cd /Users/abhinav/AIChatBot
   source env/bin/activate
   PYTHONPATH=/Users/abhinav/AIChatBot python3 backend/server.py
   ```

2. **Open the standalone frontend:**
   ```bash
   open /Users/abhinav/AIChatBot/frontend/standalone_frontend.html
   ```
   
   Or manually open in browser: `file:///Users/abhinav/AIChatBot/frontend/standalone_frontend.html`

### **🎨 Standalone Frontend Features:**
- ✅ **All chat modes**: Standard, Knowledge, MCP Tools, AI Agent
- ✅ **Agent selection**: Dropdown with all 5 AI agents
- ✅ **Tool visualization**: Shows available MCP tools
- ✅ **Enhanced messaging**: Tool badges, agent details
- ✅ **Real-time status**: Connection and capability indicators
- ✅ **Beautiful UI**: Same design as React version

## 🔧 **Permanent Solution: Install Node.js**

### **Option 1: Install Node.js directly (Recommended)**

1. **Download Node.js:**
   - Go to https://nodejs.org/
   - Download the LTS version for macOS
   - Run the installer

2. **Verify installation:**
   ```bash
   node --version
   npm --version
   ```

3. **Start React frontend:**
   ```bash
   cd /Users/abhinav/AIChatBot/frontend/react-app
   npm install
   npm start
   ```

### **Option 2: Install via Homebrew**

1. **Install Homebrew:**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Node.js:**
   ```bash
   brew install node
   ```

3. **Start React frontend:**
   ```bash
   cd /Users/abhinav/AIChatBot/frontend/react-app
   npm install
   npm start
   ```

### **Option 3: Install via Node Version Manager (nvm)**

1. **Install nvm:**
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   source ~/.zshrc
   ```

2. **Install Node.js:**
   ```bash
   nvm install --lts
   nvm use --lts
   ```

3. **Start React frontend:**
   ```bash
   cd /Users/abhinav/AIChatBot/frontend/react-app
   npm install
   npm start
   ```

## 🧪 **Complete Testing Workflow**

### **1. Backend Testing:**
```bash
# Terminal 1: Start backend
cd /Users/abhinav/AIChatBot
source env/bin/activate
PYTHONPATH=/Users/abhinav/AIChatBot python3 backend/server.py

# Verify backend is running
curl http://localhost:8000/
```

### **2. Frontend Testing Options:**

#### **Option A: Standalone HTML (Immediate)**
```bash
# Open standalone frontend
open /Users/abhinav/AIChatBot/frontend/standalone_frontend.html
```

#### **Option B: React Frontend (After Node.js installation)**
```bash
# Terminal 2: Start React frontend
cd /Users/abhinav/AIChatBot/frontend/react-app
npm start
# Access at http://localhost:3000
```

### **3. Complete Integration Test:**

#### **Test Scenario 1: Standard Chat**
1. Enter your OpenAI API key
2. Click "Initialize Chatbot"
3. Select "🔵 Standard Chat"
4. Type: "Hello, tell me a joke"
5. **Expected**: Basic conversational response

#### **Test Scenario 2: MCP Tools**
1. Select "🟡 MCP Tools"
2. Type: "Calculate 25 * 4 + 100"
3. **Expected**: Response with calculation + "Tools Used: calculator"

#### **Test Scenario 3: AI Agent**
1. Select "🟢 AI Agent"
2. Type: "Create a marketing campaign for our new product"
3. **Expected**: Multi-step response with agent details

#### **Test Scenario 4: Agent Selection**
1. Select "🟢 AI Agent"
2. Choose "Data Analysis Agent" from dropdown
3. Type: "Analyze our sales trends"
4. **Expected**: Data analysis response with agent info

## 📊 **Feature Comparison**

| Feature | Standalone HTML | React Frontend |
|---------|----------------|----------------|
| **All Chat Modes** | ✅ | ✅ |
| **Agent Selection** | ✅ | ✅ |
| **Tool Visualization** | ✅ | ✅ |
| **Enhanced Messaging** | ✅ | ✅ |
| **Real-time Updates** | ✅ | ✅ |
| **Mobile Responsive** | ✅ | ✅ |
| **Development Tools** | ❌ | ✅ |
| **Hot Reload** | ❌ | ✅ |
| **Component Structure** | ❌ | ✅ |

## 🎯 **Testing Checklist**

### **Backend Functionality:**
- [ ] Server starts without errors
- [ ] All endpoints respond (/, /tools/available, /agents/available)
- [ ] Initialization works with API key
- [ ] All three chat modes operational

### **Frontend Functionality:**
- [ ] UI loads correctly
- [ ] API key input and initialization works
- [ ] Mode switching works (4 modes)
- [ ] Agent selection dropdown populates
- [ ] Tools list displays when in enhanced mode
- [ ] Messages display with correct formatting
- [ ] Enhanced info shows (tools used, agent details)
- [ ] Error handling works

### **Integration Testing:**
- [ ] Frontend successfully calls backend APIs
- [ ] Responses display correctly with metadata
- [ ] Tool badges appear for MCP mode
- [ ] Agent details show for AI Agent mode
- [ ] Status indicators update in real-time

## 🚀 **Troubleshooting**

### **Backend Issues:**
```bash
# If backend won't start:
cd /Users/abhinav/AIChatBot
source env/bin/activate
pip install -r requirements.txt

# If import errors:
PYTHONPATH=/Users/abhinav/AIChatBot python3 backend/server.py
```

### **Frontend Issues:**
```bash
# If React frontend issues after Node.js install:
cd /Users/abhinav/AIChatBot/frontend/react-app
rm -rf node_modules package-lock.json
npm install
npm start

# If port conflicts:
npm start -- --port 3001
```

### **CORS Issues:**
If you get CORS errors, the backend is already configured to allow requests from localhost:3000 and the standalone HTML file.

## 🎉 **Success Indicators**

### **Backend Success:**
- Server responds with version 2.0.0
- All endpoints return data
- Initialization completes without timeout

### **Frontend Success:**
- UI loads with all elements
- Can switch between all 4 chat modes
- Agent dropdown shows 5 agents
- Tools list shows 6 tools
- Messages display with enhanced information

### **Integration Success:**
- Complete conversation flow works
- Tool usage shows visually
- Agent details display correctly
- Real-time status updates work

## 🔄 **Next Steps After Setup**

1. **Test all functionality** with your OpenAI API key
2. **Explore different agents** and their capabilities
3. **Try complex prompts** to see multi-step processing
4. **Monitor performance** through the enhanced UI
5. **Customize for your business** needs

Your AI chatbot frontend is now ready for testing! 🚀

