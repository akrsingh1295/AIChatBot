import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [mode, setMode] = useState('general');
    const [apiKey, setApiKey] = useState('');
    const [knowledgeLoaded, setKnowledgeLoaded] = useState(false);
    const [chatbotReady, setChatbotReady] = useState(false);
    const [availableTools, setAvailableTools] = useState([]);
    const [availableAgents, setAvailableAgents] = useState([]);
    const [selectedAgent, setSelectedAgent] = useState('');
    const messagesEndRef = useRef(null);

    const API_BASE_URL = 'http://localhost:8000';

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const initializeChatbot = async () => {
        try {
            const response = await axios.post(`${API_BASE_URL}/initialize`, {
                api_key: apiKey
            });
            if (response.data.success) {
                setChatbotReady(true);
                
                // Load available tools and agents
                await loadAvailableTools();
                await loadAvailableAgents();
            }
        } catch (error) {
            console.error('Failed to initialize chatbot:', error);
        }
    };

    const loadAvailableTools = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/tools/available`);
            setAvailableTools(response.data.tools || []);
        } catch (error) {
            console.error('Failed to load tools:', error);
        }
    };

    const loadAvailableAgents = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/agents/available`);
            setAvailableAgents(response.data.agents || []);
        } catch (error) {
            console.error('Failed to load agents:', error);
        }
    };

    const sendMessage = async () => {
        if (!input.trim() || !chatbotReady) return;

        const userMessage = { type: 'user', content: input, timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        setLoading(true);

        try {
            let response;
            let endpoint = '/chat';
            let requestData = { message: input };

            // Determine which endpoint to use based on mode
            if (mode === 'enhanced') {
                endpoint = '/chat/enhanced';
                requestData.session_id = 'frontend_session';
            } else if (mode === 'agent') {
                endpoint = '/chat/agent';
                requestData.session_id = 'frontend_session';
                if (selectedAgent) {
                    requestData.preferred_agent = selectedAgent;
                }
            } else {
                // Standard chat
                requestData.mode = mode;
            }

            response = await axios.post(`${API_BASE_URL}${endpoint}`, requestData);

            const botMessage = {
                type: 'assistant',
                content: response.data.response,
                mode: mode,
                sources: response.data.sources || [],
                timestamp: new Date(),
                // Enhanced response data
                enhanced: response.data.enhanced || false,
                tools_used: response.data.tools_used || [],
                agent_used: response.data.agent_used || false,
                agent_role: response.data.agent_role || null,
                steps_completed: response.data.steps_completed || 0
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            const errorMessage = {
                type: 'error',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        }

        setInput('');
        setLoading(false);
    };

    const loadKnowledgeBase = async (files) => {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));

        try {
            const response = await axios.post(`${API_BASE_URL}/load-knowledge`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (response.data.success) {
                setKnowledgeLoaded(true);
            }
        } catch (error) {
            console.error('Failed to load knowledge base:', error);
        }
    };

    const clearMemory = async () => {
        try {
            await axios.post(`${API_BASE_URL}/clear-memory`);
            setMessages([]);
        } catch (error) {
            console.error('Failed to clear memory:', error);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="app">
            {/* Sidebar */}
            <div className="sidebar">
                <div className="sidebar-section">
                    <h3>⚙️ Configuration</h3>

                    <div className="config-item">
                        <label>🔑 OpenAI API Key</label>
                        <input
                            type="password"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            placeholder="Enter your API key"
                            className="api-key-input"
                        />
                        <button
                            onClick={initializeChatbot}
                            disabled={!apiKey}
                            className="btn-primary"
                        >
                            Initialize Chatbot
                        </button>
                        {chatbotReady && <div className="status-success">✅ Chatbot Ready!</div>}
                    </div>

                    <div className="config-item">
                        <label>💬 Chat Mode</label>
                        <div className="radio-group">
                            <label>
                                <input
                                    type="radio"
                                    value="general"
                                    checked={mode === 'general'}
                                    onChange={(e) => setMode(e.target.value)}
                                />
                                🔵 Standard Chat
                            </label>
                            <label>
                                <input
                                    type="radio"
                                    value="knowledge"
                                    checked={mode === 'knowledge'}
                                    onChange={(e) => setMode(e.target.value)}
                                />
                                📚 Knowledge Mode
                            </label>
                            <label>
                                <input
                                    type="radio"
                                    value="enhanced"
                                    checked={mode === 'enhanced'}
                                    onChange={(e) => setMode(e.target.value)}
                                />
                                🟡 MCP Tools
                            </label>
                            <label>
                                <input
                                    type="radio"
                                    value="agent"
                                    checked={mode === 'agent'}
                                    onChange={(e) => setMode(e.target.value)}
                                />
                                🟢 AI Agent
                            </label>
                        </div>
                    </div>

                    {mode === 'agent' && availableAgents.length > 0 && (
                        <div className="config-item">
                            <label>🤖 Select AI Agent</label>
                            <select 
                                value={selectedAgent} 
                                onChange={(e) => setSelectedAgent(e.target.value)}
                                className="agent-select"
                            >
                                <option value="">Auto-select agent</option>
                                {availableAgents.map((agent, index) => (
                                    <option key={index} value={agent.name}>
                                        {agent.name.replace('_', ' ').toUpperCase()} - {agent.description}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    {mode === 'enhanced' && availableTools.length > 0 && (
                        <div className="config-item">
                            <label>🛠️ Available Tools</label>
                            <div className="tools-list">
                                {availableTools.map((tool, index) => (
                                    <div key={index} className="tool-item">
                                        <strong>{tool.name}</strong>: {tool.description}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="config-item">
                        <label>📚 Knowledge Base</label>
                        <input
                            type="file"
                            multiple
                            accept=".txt,.csv"
                            onChange={(e) => loadKnowledgeBase(Array.from(e.target.files))}
                            className="file-input"
                        />
                        {knowledgeLoaded && <div className="status-success">📚 Knowledge Base Loaded</div>}
                    </div>

                    <div className="config-item">
                        <label>🧠 Memory</label>
                        <button onClick={clearMemory} className="btn-secondary">
                            🗑️ Clear Memory
                        </button>
                        <div className="memory-info">
                            {messages.length} messages in memory
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="main-content">
                <header className="header">
                    <h1>🤖 AI ChatBot with MCP Tools & Intelligent Agents</h1>
                    <p>Advanced AI assistant with real-time data access, multi-step problem solving, and business automation</p>

                    <div className="status-bar">
                        <div className={`status-item ${chatbotReady ? 'ready' : 'not-ready'}`}>
                            {chatbotReady ? '🟢 ChatBot Ready' : '🔴 ChatBot Not Ready'}
                        </div>
                        <div className="status-item">
                            {mode === 'knowledge' ? '📚' : 
                             mode === 'enhanced' ? '🟡' :
                             mode === 'agent' ? '🟢' : '🔵'} Mode: {mode.charAt(0).toUpperCase() + mode.slice(1)}
                        </div>
                        <div className={`status-item ${knowledgeLoaded ? 'loaded' : 'not-loaded'}`}>
                            📚 Knowledge Base: {knowledgeLoaded ? '🟢 Loaded' : '🔴 Not Loaded'}
                        </div>
                        {chatbotReady && (
                            <>
                                <div className="status-item">
                                    🛠️ Tools: {availableTools.length} available
                                </div>
                                <div className="status-item">
                                    🤖 Agents: {availableAgents.length} available
                                </div>
                            </>
                        )}
                    </div>
                </header>

                <div className="chat-container">
                    <div className="messages">
                        {messages.map((message, index) => (
                            <div key={index} className={`message ${message.type}`}>
                                <div className="message-header">
                                    <span className="message-sender">
                                        {message.type === 'user' ? '👤 You' :
                                            message.type === 'assistant' ?
                                                `${message.mode === 'knowledge' ? '📚' : 
                                                    message.mode === 'enhanced' ? '🟡' :
                                                    message.mode === 'agent' ? '🟢' : '🔵'} Assistant (${message.mode})` :
                                                '❌ Error'}
                                    </span>
                                    <span className="message-time">
                                        {message.timestamp.toLocaleTimeString()}
                                    </span>
                                </div>
                                <div className="message-content">
                                    {message.content}
                                </div>
                                {message.sources && message.sources.length > 0 && (
                                    <div className="sources">
                                        <h4>📋 Sources:</h4>
                                        {message.sources.map((source, idx) => (
                                            <details key={idx} className="source-item">
                                                <summary>Source {idx + 1} - {source.metadata?.source || 'Unknown'}</summary>
                                                <div className="source-content">
                                                    {source.content}
                                                </div>
                                            </details>
                                        ))}
                                    </div>
                                )}
                                
                                {/* Enhanced MCP Tools Information */}
                                {message.enhanced && message.tools_used && message.tools_used.length > 0 && (
                                    <div className="enhanced-info">
                                        <h4>🛠️ Tools Used:</h4>
                                        <div className="tools-used">
                                            {message.tools_used.map((tool, idx) => (
                                                <span key={idx} className="tool-badge">{tool}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                
                                {/* AI Agent Information */}
                                {message.agent_used && (
                                    <div className="agent-info">
                                        <h4>🤖 AI Agent Details:</h4>
                                        <div className="agent-details">
                                            <div className="agent-detail">
                                                <strong>Agent:</strong> {message.agent_role?.replace('_', ' ').toUpperCase()}
                                            </div>
                                            <div className="agent-detail">
                                                <strong>Steps Completed:</strong> {message.steps_completed}
                                            </div>
                                            {message.tools_used && message.tools_used.length > 0 && (
                                                <div className="agent-detail">
                                                    <strong>Tools Used:</strong> {message.tools_used.join(', ')}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                        {loading && (
                            <div className="message assistant loading">
                                <div className="message-content">
                                    💭 Thinking...
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="input-area">
                        <div className="input-container">
                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Type your message here..."
                                disabled={!chatbotReady}
                                rows="1"
                                className="message-input"
                            />
                            <button
                                onClick={sendMessage}
                                disabled={!input.trim() || !chatbotReady || loading}
                                className="send-button"
                            >
                                📤
                            </button>
                        </div>
                    </div>
                </div>

                <div className="quick-actions">
                    <h3>🚀 Quick Actions</h3>
                    <div className="action-buttons">
                        <button className="action-btn">💡 Sample Questions</button>
                        <button className="action-btn">🔍 Search Knowledge Base</button>
                        <button className="action-btn">📊 Export Chat History</button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;