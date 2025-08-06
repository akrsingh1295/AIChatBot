"""
Simple load testing script for AI ChatBot
Run with: python simple_load_test.py
"""

import asyncio
import aiohttp
import time
import json
import random
from concurrent.futures import ThreadPoolExecutor
import statistics

class SimpleChatBotLoadTest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_api_key = "test-load-testing-key"
        self.results = []
        
    async def initialize_chatbot(self, session):
        """Initialize a chatbot instance"""
        try:
            async with session.post(f"{self.base_url}/initialize", 
                                  json={"api_key": self.test_api_key}) as response:
                return response.status == 200
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    async def send_chat_message(self, session, message, mode="general"):
        """Send a chat message and measure response time"""
        start_time = time.time()
        try:
            async with session.post(f"{self.base_url}/chat", 
                                  json={"message": message, "mode": mode}) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "response_time": response_time,
                        "status_code": response.status,
                        "message_length": len(data.get("response", "")),
                        "mode": mode
                    }
                else:
                    return {
                        "success": False,
                        "response_time": response_time,
                        "status_code": response.status,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "response_time": end_time - start_time,
                "error": str(e)
            }
    
    async def simulate_user(self, session, user_id, num_messages=5):
        """Simulate a single user's chat session"""
        print(f"👤 User {user_id} starting...")
        
        # Initialize chatbot
        if not await self.initialize_chatbot(session):
            print(f"❌ User {user_id} failed to initialize")
            return []
        
        messages = [
            "Hello, how are you?",
            "What is artificial intelligence?",
            "Explain machine learning",
            "Tell me about Python programming",
            "What are neural networks?",
            "How does natural language processing work?",
            "What is the difference between AI and ML?",
            "Explain deep learning concepts",
            "What are the applications of AI?",
            "How do chatbots work?"
        ]
        
        user_results = []
        for i in range(num_messages):
            message = random.choice(messages)
            result = await self.send_chat_message(session, message)
            result["user_id"] = user_id
            result["message_number"] = i + 1
            user_results.append(result)
            
            # Wait between messages (simulate human typing)
            await asyncio.sleep(random.uniform(1, 3))
        
        print(f"✅ User {user_id} completed {num_messages} messages")
        return user_results
    
    async def run_load_test(self, concurrent_users=10, messages_per_user=5):
        """Run the load test with specified parameters"""
        print(f"🚀 Starting load test:")
        print(f"   Concurrent Users: {concurrent_users}")
        print(f"   Messages per User: {messages_per_user}")
        print(f"   Total Messages: {concurrent_users * messages_per_user}")
        print(f"   Target: {self.base_url}")
        print("-" * 50)
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Create tasks for all users
            tasks = []
            for user_id in range(concurrent_users):
                task = self.simulate_user(session, user_id, messages_per_user)
                tasks.append(task)
            
            # Run all users concurrently
            user_results = await asyncio.gather(*tasks)
            
            # Flatten results
            for user_result in user_results:
                self.results.extend(user_result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        self.analyze_results(total_time)
    
    def analyze_results(self, total_time):
        """Analyze and display test results"""
        print("\n📊 LOAD TEST RESULTS")
        print("=" * 50)
        
        # Basic stats
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.get("success", False))
        failed_requests = total_requests - successful_requests
        
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        print(f"📈 Overall Performance:")
        print(f"   Total Requests: {total_requests}")
        print(f"   Successful: {successful_requests} ({success_rate:.1f}%)")
        print(f"   Failed: {failed_requests}")
        print(f"   Total Time: {total_time:.2f} seconds")
        print(f"   Requests/Second: {total_requests / total_time:.2f}")
        
        # Response time analysis
        if successful_requests > 0:
            response_times = [r["response_time"] for r in self.results if r.get("success", False)]
            
            print(f"\n⏱️  Response Time Analysis:")
            print(f"   Average: {statistics.mean(response_times):.2f}s")
            print(f"   Median: {statistics.median(response_times):.2f}s")
            print(f"   Min: {min(response_times):.2f}s")
            print(f"   Max: {max(response_times):.2f}s")
            print(f"   95th Percentile: {self.percentile(response_times, 95):.2f}s")
            
            # Performance categories
            fast_responses = sum(1 for rt in response_times if rt < 2)
            medium_responses = sum(1 for rt in response_times if 2 <= rt < 5)
            slow_responses = sum(1 for rt in response_times if rt >= 5)
            
            print(f"\n📊 Response Time Distribution:")
            print(f"   Fast (<2s): {fast_responses} ({fast_responses/len(response_times)*100:.1f}%)")
            print(f"   Medium (2-5s): {medium_responses} ({medium_responses/len(response_times)*100:.1f}%)")
            print(f"   Slow (≥5s): {slow_responses} ({slow_responses/len(response_times)*100:.1f}%)")
        
        # Error analysis
        if failed_requests > 0:
            print(f"\n❌ Error Analysis:")
            error_types = {}
            for result in self.results:
                if not result.get("success", False):
                    error = result.get("error", "Unknown")
                    error_types[error] = error_types.get(error, 0) + 1
            
            for error, count in error_types.items():
                print(f"   {error}: {count}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if success_rate < 95:
            print("   ⚠️  Success rate is low - check server capacity")
        if successful_requests > 0:
            avg_response_time = statistics.mean([r["response_time"] for r in self.results if r.get("success", False)])
            if avg_response_time > 5:
                print("   ⚠️  Average response time is high - consider scaling")
            elif avg_response_time < 2:
                print("   ✅ Response times are excellent")
            else:
                print("   ✅ Response times are acceptable")
        
        # Capacity estimation
        if success_rate > 95:
            concurrent_capacity = len(set(r.get("user_id") for r in self.results))
            requests_per_second = total_requests / total_time
            
            print(f"\n🎯 Current Capacity Estimate:")
            print(f"   Concurrent Users Tested: {concurrent_capacity}")
            print(f"   Requests/Second: {requests_per_second:.2f}")
            print(f"   Estimated Daily Capacity: {int(requests_per_second * 86400)} requests")
            
            # Scale recommendations
            if requests_per_second < 5:
                print("   📊 Scale: Good for small applications (100-500 users/day)")
            elif requests_per_second < 20:
                print("   📊 Scale: Good for medium applications (1000-5000 users/day)")
            else:
                print("   📊 Scale: Good for large applications (5000+ users/day)")

    def percentile(self, data, p):
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = (len(sorted_data) - 1) * p / 100
        lower = int(index)
        upper = lower + 1
        weight = index - lower
        
        if upper >= len(sorted_data):
            return sorted_data[-1]
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight

def main():
    """Run different load test scenarios"""
    tester = SimpleChatBotLoadTest()
    
    print("🧪 AI ChatBot Load Testing Suite")
    print("Choose a test scenario:")
    print("1. Light Load (5 users, 3 messages each)")
    print("2. Medium Load (10 users, 5 messages each)")
    print("3. Heavy Load (20 users, 5 messages each)")
    print("4. Stress Test (50 users, 3 messages each)")
    print("5. Custom Test")
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == "1":
        asyncio.run(tester.run_load_test(concurrent_users=5, messages_per_user=3))
    elif choice == "2":
        asyncio.run(tester.run_load_test(concurrent_users=10, messages_per_user=5))
    elif choice == "3":
        asyncio.run(tester.run_load_test(concurrent_users=20, messages_per_user=5))
    elif choice == "4":
        asyncio.run(tester.run_load_test(concurrent_users=50, messages_per_user=3))
    elif choice == "5":
        users = int(input("Number of concurrent users: "))
        messages = int(input("Messages per user: "))
        asyncio.run(tester.run_load_test(concurrent_users=users, messages_per_user=messages))
    else:
        print("Invalid choice. Running default test...")
        asyncio.run(tester.run_load_test(concurrent_users=10, messages_per_user=5))

if __name__ == "__main__":
    main() 