# 🤖 Smart AI ChatBot with Memory & Knowledge Base

A full-stack intelligent chatbot application built with **React**, **FastAPI**, **LangChain**, and **OpenAI GPT**, featuring conversation memory and document-based knowledge retrieval.

## ✨ Features

- **🧠 Dual Chat Modes**: 
  - **General**: Natural conversation with GPT
  - **Knowledge**: Document-based Q&A with source citations
- **💾 Conversation Memory**: Maintains context across messages
- **📚 Knowledge Base**: Upload and search through TXT/CSV files
- **🔍 Vector Search**: Semantic similarity search using embeddings
- **🎨 Modern UI**: Beautiful React interface with real-time status
- **📱 Responsive Design**: Works on desktop and mobile
- **🔐 Secure**: API key handling and file upload validation

## 🏗️ Architecture

```
AIChatBot/
├── backend/                 # FastAPI server
│   ├── server.py           # Main API endpoints
│   ├── chatbot.py          # LangChain chatbot logic
│   └── knowledge_processor.py # Document processing & vector DB
├── frontend/react-app/      # React frontend
│   ├── src/App.js          # Main React component
│   └── src/App.css         # Styles
├── data/                   # Sample knowledge base
│   └── knowledge_base.txt  # TechCorp company info
├── venv/                   # Python virtual environment
├── requirements.txt        # Python dependencies
└── .gitignore             # Git ignore rules
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 14+**
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### 1. Clone & Setup Python Environment
```bash
cd AIChatBot

# Activate virtual environment (already created)
source venv/bin/activate

# Install Python dependencies (already done)
pip install -r requirements.txt
```

### 2. Start Backend Server
```bash
# Option 1: Using the startup script
python start_backend.py

# Option 2: Direct command
source venv/bin/activate
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```
Backend will be available at: **http://localhost:8000**

### 3. Start Frontend (New Terminal)
```bash
# Option 1: Using the startup script
chmod +x start_frontend.sh
./start_frontend.sh

# Option 2: Manual setup
cd frontend/react-app
npm install
npm start
```
Frontend will be available at: **http://localhost:3000**

## 📖 Usage Guide

### Initial Setup
1. **Enter OpenAI API Key** in the sidebar
2. **Click "Initialize Chatbot"** to connect to OpenAI
3. **Upload Knowledge Base** (optional) - use `data/knowledge_base.txt` or your own files

### Chat Modes
- **General Mode**: Free-form conversation with GPT
- **Knowledge Mode**: Ask questions about uploaded documents

### Example Interactions

**General Mode:**
```
You: "Explain quantum computing in simple terms"
Bot: "Quantum computing is like having a super-powerful computer..."
```

**Knowledge Mode** (with TechCorp data loaded):
```
You: "What services does TechCorp offer?"
Bot: "TechCorp Solutions offers 5 main services:
1. Web Application Development...
[Sources: TechCorp company info]"
```

## 🛠️ API Endpoints

The FastAPI backend provides these endpoints:

- `POST /initialize` - Initialize chatbot with API key
- `POST /chat` - Send message to chatbot  
- `POST /load-knowledge` - Upload knowledge base files
- `POST /clear-memory` - Clear conversation history
- `GET /status` - Get chatbot status
- `GET /chat-history` - Get conversation history
- `POST /search-knowledge` - Search knowledge base directly

**API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables
Create a `.env` file (optional):
```bash
OPENAI_API_KEY=your_api_key_here
```

### Customization
- **Memory Window**: Change `memory_window` in `chatbot.py` (default: 10 messages)
- **Chunk Size**: Modify `chunk_size` in `knowledge_processor.py` (default: 1000 chars)
- **Model**: Update `model_name` in `chatbot.py` (default: gpt-3.5-turbo)

## 📁 File Formats Supported

- **Text Files (.txt)**: Plain text documents
- **CSV Files (.csv)**: Structured data with automatic column parsing

## 🧪 Testing

### Test Backend
```bash
# Test API endpoints
curl http://localhost:8000/
curl -X POST http://localhost:8000/initialize -d '{"api_key":"your_key"}'
```

### Test Frontend
Open http://localhost:3000 and verify:
- ✅ UI loads correctly
- ✅ API key input works
- ✅ File upload functions
- ✅ Chat responses appear

## 📚 Knowledge Base

The included `data/knowledge_base.txt` contains information about **TechCorp Solutions**, including:
- Company overview and services
- Technology stack and team info
- Recent projects and case studies
- FAQ and contact information

Upload this file to test knowledge-based chat!

## 🔍 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend connection errors:**
- Verify backend is running on port 8000
- Check CORS settings in `server.py`

**OpenAI API errors:**
- Verify API key is valid and has credits
- Check API key permissions

**Memory issues:**
- Clear conversation memory via UI
- Restart backend server

## 🚧 Development

### Adding New Features

1. **Backend**: Add endpoints in `backend/server.py`
2. **Frontend**: Add components in `frontend/react-app/src/`
3. **Knowledge**: Extend `knowledge_processor.py` for new file types

### Dependencies
- **Backend**: FastAPI, LangChain, OpenAI, ChromaDB, HuggingFace
- **Frontend**: React, Axios, modern CSS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙋‍♂️ Support

If you encounter any issues:
1. Check the troubleshooting section
2. Review API documentation at http://localhost:8000/docs
3. Check console logs in browser developer tools
4. Verify all dependencies are installed correctly

---

**Enjoy chatting with your AI assistant! 🤖✨** 