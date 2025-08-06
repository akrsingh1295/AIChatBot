#!/usr/bin/env python3
"""
Test script to demonstrate different memory window sizes
and their effects on conversation context.
"""

from config import ChatBotConfig

def demonstrate_memory_windows():
    """Demonstrate different memory window configurations"""
    
    print("🧠 Memory Window Configuration Guide")
    print("=" * 50)
    
    # Show all available presets
    print("\n📋 Available Memory Presets:")
    for preset_name, window_size in ChatBotConfig.MEMORY_PRESETS.items():
        usage = ChatBotConfig.get_memory_usage_estimate(window_size)
        print(f"  {preset_name.capitalize():12} | Window: {window_size:3d} | {usage}")
    
    print(f"\n⚙️  Current Configuration:")
    print(f"  Memory Window: {ChatBotConfig.MEMORY_WINDOW}")
    print(f"  Temperature: {ChatBotConfig.TEMPERATURE}")
    print(f"  Model: {ChatBotConfig.MODEL_NAME}")
    print(f"  Usage: {ChatBotConfig.get_memory_usage_estimate(ChatBotConfig.MEMORY_WINDOW)}")
    
    print("\n" + "=" * 50)
    
    # Demonstrate conversation scenarios
    print("\n💬 Conversation Scenarios by Memory Window:")
    
    scenarios = [
        {
            "window": 5,
            "scenario": "Short Q&A Session",
            "example": "Quick customer support questions",
            "pros": ["Fast responses", "Low memory usage"],
            "cons": ["Forgets context quickly", "Poor for complex topics"]
        },
        {
            "window": 10,
            "scenario": "Standard Chat",
            "example": "General purpose chatbot",
            "pros": ["Good balance", "Reasonable context"],
            "cons": ["May forget important details in long chats"]
        },
        {
            "window": 20,
            "scenario": "Extended Conversation",
            "example": "Educational tutoring, problem-solving",
            "pros": ["Maintains good context", "Better for complex topics"],
            "cons": ["Higher memory usage", "Slightly slower"]
        },
        {
            "window": 50,
            "scenario": "Comprehensive Discussion",
            "example": "Research assistance, detailed analysis",
            "pros": ["Excellent context retention", "Handles complex workflows"],
            "cons": ["High memory usage", "Expensive API calls"]
        },
        {
            "window": 100,
            "scenario": "Maximum Context",
            "example": "Long-form writing, complex projects",
            "pros": ["Maximum context", "Handles very long conversations"],
            "cons": ["Very high memory usage", "May hit API limits"]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎯 Window Size: {scenario['window']}")
        print(f"   Use Case: {scenario['scenario']}")
        print(f"   Example: {scenario['example']}")
        print(f"   Pros: {', '.join(scenario['pros'])}")
        print(f"   Cons: {', '.join(scenario['cons'])}")
        print(f"   Memory Usage: {ChatBotConfig.get_memory_usage_estimate(scenario['window'])}")

def simulate_conversation_memory(window_size):
    """Simulate how memory works with different window sizes"""
    
    print(f"\n🔄 Memory Simulation (Window Size: {window_size})")
    print("-" * 40)
    
    # Simulate 15 conversation pairs
    conversations = [
        ("Hi, I'm John", "Hello John! Nice to meet you."),
        ("I work at Microsoft", "That's great! Microsoft is a wonderful company."),
        ("I like Python programming", "Python is an excellent programming language!"),
        ("What's the weather today?", "I don't have access to current weather data."),
        ("Can you help with coding?", "Absolutely! I'd be happy to help with coding."),
        ("I'm working on a web app", "Web development is exciting! What framework are you using?"),
        ("Using React and FastAPI", "Great choice! React and FastAPI work well together."),
        ("Need help with authentication", "I can help with authentication. What type do you need?"),
        ("JWT tokens for API", "JWT tokens are perfect for API authentication."),
        ("How to secure endpoints?", "Use middleware to validate JWT tokens on protected routes."),
        ("What about CORS issues?", "CORS middleware in FastAPI handles cross-origin requests."),
        ("Database recommendations?", "PostgreSQL or MongoDB are excellent choices."),
        ("Best practices for React?", "Use hooks, components, and proper state management."),
        ("What's my name again?", "Your name is John! (if still in memory)"),
        ("Where do I work?", "You work at Microsoft! (if still in memory)")
    ]
    
    memory = []
    
    for i, (user_msg, ai_msg) in enumerate(conversations, 1):
        # Add new conversation pair
        memory.append((user_msg, ai_msg))
        
        # Keep only the last 'window_size' pairs
        if len(memory) > window_size:
            forgotten = memory.pop(0)
            status = f"💭 Conversation {i}: Added | 🗑️  Forgot: '{forgotten[0][:30]}...'"
        else:
            status = f"💭 Conversation {i}: Added | 📝 Memory: {len(memory)}/{window_size}"
        
        print(f"   {status}")
        
        # Check if important info is still remembered
        if i == 14:  # "What's my name again?"
            name_remembered = any("John" in pair[0] or "John" in pair[1] for pair in memory)
            print(f"   🔍 Can remember name 'John': {'✅ Yes' if name_remembered else '❌ No'}")
            
        if i == 15:  # "Where do I work?"
            work_remembered = any("Microsoft" in pair[0] or "Microsoft" in pair[1] for pair in memory)
            print(f"   🔍 Can remember work 'Microsoft': {'✅ Yes' if work_remembered else '❌ No'}")

if __name__ == "__main__":
    demonstrate_memory_windows()
    
    print("\n" + "=" * 50)
    print("🧪 Memory Simulation Examples:")
    
    # Test different window sizes
    for window_size in [5, 10, 20]:
        simulate_conversation_memory(window_size)
        print()
    
    print("🎯 Recommendation:")
    print("  - For customer support: 5-10")
    print("  - For general chat: 10-20") 
    print("  - For complex tasks: 20-50")
    print("  - For research/writing: 50-100")
    
    print(f"\n⚙️  To change memory window, edit MEMORY_WINDOW in config.py")
    print(f"   Current setting: {ChatBotConfig.MEMORY_WINDOW}")
    print(f"   Current usage: {ChatBotConfig.get_memory_usage_estimate(ChatBotConfig.MEMORY_WINDOW)}") 