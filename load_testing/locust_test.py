"""
Load testing script using Locust for AI ChatBot
Run with: locust -f locust_test.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import json
import random
import time

class ChatBotUser(HttpUser):
    wait_time = between(1, 5)  # Wait 1-5 seconds between requests
    
    def on_start(self):
        """Called when a user starts - initialize chatbot"""
        self.api_key = "test-api-key-for-load-testing"  # Use a test key
        self.chatbot_ready = False
        self.knowledge_loaded = False
        
        # Initialize chatbot
        response = self.client.post("/initialize", json={
            "api_key": self.api_key,
            "memory_window": 10,
            "temperature": 0.7
        })
        
        if response.status_code == 200:
            self.chatbot_ready = True
            print(f"✅ User {self.environment.runner.user_count} initialized chatbot")
        else:
            print(f"❌ Failed to initialize chatbot: {response.text}")
    
    @task(3)
    def chat_general(self):
        """Test general chat functionality (most common use case)"""
        if not self.chatbot_ready:
            return
            
        messages = [
            "Hello, how are you?",
            "What is Python programming?",
            "Explain machine learning in simple terms",
            "What's the weather like?",
            "Tell me a joke",
            "How does blockchain work?",
            "What are the benefits of AI?",
            "Explain quantum computing",
            "What is cloud computing?",
            "How do neural networks work?"
        ]
        
        message = random.choice(messages)
        
        with self.client.post("/chat", json={
            "message": message,
            "mode": "general"
        }, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                response_time = response.elapsed.total_seconds()
                if response_time > 10:  # Flag slow responses
                    response.failure(f"Response too slow: {response_time:.2f}s")
                else:
                    response.success()
            else:
                response.failure(f"Chat failed: {response.status_code}")
    
    @task(1)
    def chat_knowledge(self):
        """Test knowledge-based chat (less common but important)"""
        if not self.chatbot_ready:
            return
            
        knowledge_questions = [
            "What services does TechCorp offer?",
            "What is the company's tech stack?",
            "Who are the team members?",
            "What are the recent projects?",
            "What industries do you serve?",
            "What is the contact information?",
            "What are the office hours?",
            "Do you work with startups?"
        ]
        
        message = random.choice(knowledge_questions)
        
        with self.client.post("/chat", json={
            "message": message,
            "mode": "knowledge"
        }, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                response_time = response.elapsed.total_seconds()
                if response_time > 15:  # Knowledge queries can be slower
                    response.failure(f"Knowledge response too slow: {response_time:.2f}s")
                else:
                    response.success()
            else:
                response.failure(f"Knowledge chat failed: {response.status_code}")
    
    @task(1)
    def get_status(self):
        """Test status endpoint (health check)"""
        with self.client.get("/status", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status check failed: {response.status_code}")
    
    @task(1)
    def get_chat_history(self):
        """Test chat history endpoint"""
        if not self.chatbot_ready:
            return
            
        with self.client.get("/chat-history", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Chat history failed: {response.status_code}")
    
    def on_stop(self):
        """Called when user stops - cleanup"""
        if self.chatbot_ready:
            self.client.post("/clear-memory")

class HighVolumeUser(HttpUser):
    """Simulates heavy users who chat a lot"""
    wait_time = between(0.5, 2)  # Faster interaction
    
    def on_start(self):
        self.api_key = "heavy-user-test-key"
        response = self.client.post("/initialize", json={
            "api_key": self.api_key,
            "memory_window": 20,  # Larger memory for heavy users
            "temperature": 0.8
        })
        self.chatbot_ready = response.status_code == 200
    
    @task(5)
    def rapid_chat(self):
        """Simulate rapid-fire chatting"""
        if not self.chatbot_ready:
            return
            
        quick_messages = [
            "Yes", "No", "Continue", "Tell me more", "Explain",
            "What about...", "How so?", "Really?", "Interesting",
            "Go on"
        ]
        
        message = random.choice(quick_messages)
        self.client.post("/chat", json={
            "message": message,
            "mode": "general"
        })

class StressTestUser(HttpUser):
    """Simulates stress testing with complex queries"""
    wait_time = between(0.1, 1)  # Very aggressive
    
    def on_start(self):
        self.api_key = "stress-test-key"
        response = self.client.post("/initialize", json={
            "api_key": self.api_key,
            "memory_window": 50,  # Maximum memory
            "temperature": 1.0
        })
        self.chatbot_ready = response.status_code == 200
    
    @task
    def complex_query(self):
        """Send complex, long queries"""
        if not self.chatbot_ready:
            return
            
        complex_queries = [
            "Explain the differences between supervised, unsupervised, and reinforcement learning in machine learning, including real-world examples and implementation strategies for each approach.",
            "What are the key architectural patterns in microservices, how do they compare to monolithic architectures, and what are the trade-offs in terms of scalability, maintainability, and deployment complexity?",
            "Describe the process of implementing a complete CI/CD pipeline with automated testing, security scanning, and deployment strategies across multiple environments.",
            "How does blockchain technology work at a fundamental level, what are the different consensus mechanisms, and what are the practical applications beyond cryptocurrency?",
            "Explain the concept of distributed systems, including CAP theorem, eventual consistency, and strategies for handling network partitions and data replication."
        ]
        
        message = random.choice(complex_queries)
        self.client.post("/chat", json={
            "message": message,
            "mode": "general"
        }) 