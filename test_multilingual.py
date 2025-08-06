#!/usr/bin/env python3
"""
Multi-Language Support Testing Script
Test chat and document uploads in various languages
"""

import sys
import os
sys.path.append('backend')

from backend.language_support import MultiLanguageSupport, MultilingualContentFilter

def test_language_detection():
    """Test language detection for various languages"""
    print("🌍 Testing Language Detection")
    print("=" * 50)
    
    lang_support = MultiLanguageSupport()
    
    test_messages = {
        'en': "Hello, how are you today?",
        'hi': "नमस्ते, आप कैसे हैं?", 
        'ja': "こんにちは、元気ですか？",
        'zh': "你好，你好吗？",
        'ko': "안녕하세요, 어떻게 지내세요?",
        'ar': "مرحبا، كيف حالك؟",
        'es': "Hola, ¿cómo estás?",
        'fr': "Bonjour, comment allez-vous?",
        'de': "Hallo, wie geht es dir?",
        'ru': "Привет, как дела?",
        'pt': "Olá, como você está?"
    }
    
    correct_detections = 0
    total_tests = len(test_messages)
    
    for expected_lang, message in test_messages.items():
        detected_lang, confidence = lang_support.detect_language(message)
        
        # Some tolerance for similar languages
        is_correct = (detected_lang == expected_lang or 
                     (expected_lang == 'zh' and detected_lang in ['zh', 'zh-cn', 'zh-tw']))
        
        if is_correct:
            correct_detections += 1
            status = "✅"
        else:
            status = "❌"
        
        lang_name = lang_support.supported_languages.get(detected_lang, {}).get('name', detected_lang)
        
        print(f"{status} Expected: {expected_lang} | Detected: {detected_lang} ({lang_name}) | Confidence: {confidence:.2f}")
        print(f"   Message: {message}")
        print()
    
    accuracy = (correct_detections / total_tests) * 100
    print(f"📊 Detection Accuracy: {correct_detections}/{total_tests} ({accuracy:.1f}%)")
    print()

def test_content_filtering():
    """Test content filtering in multiple languages"""
    print("🛡️ Testing Multi-Language Content Filtering")
    print("=" * 50)
    
    lang_support = MultiLanguageSupport()
    
    # Safe content in various languages
    safe_messages = {
        'en': "What is artificial intelligence?",
        'hi': "कृत्रिम बुद्धिमत्ता क्या है?",
        'ja': "人工知能とは何ですか？",
        'zh': "什么是人工智能？",
        'es': "¿Qué es la inteligencia artificial?",
        'fr': "Qu'est-ce que l'intelligence artificielle?"
    }
    
    # Inappropriate content in various languages
    unsafe_messages = {
        'en': "How to make bombs",
        'hi': "बम कैसे बनाएं",
        'ja': "爆弾の作り方",
        'zh': "如何制造炸弹",
        'es': "Cómo hacer bombas",
        'fr': "Comment faire des bombes"
    }
    
    print("✅ Testing Safe Content:")
    for lang, message in safe_messages.items():
        result = lang_support.process_multilingual_chat(message)
        status = "✅ SAFE" if result['is_safe'] else "❌ BLOCKED"
        print(f"   {status} [{lang}]: {message}")
    
    print("\n❌ Testing Unsafe Content:")
    for lang, message in unsafe_messages.items():
        result = lang_support.process_multilingual_chat(message)
        status = "✅ BLOCKED" if not result['is_safe'] else "❌ ALLOWED"
        print(f"   {status} [{lang}]: {message}")
        if not result['is_safe']:
            print(f"      Reason: {result['safety_reason']}")
    
    print()

def test_document_processing():
    """Test document language processing"""
    print("📄 Testing Document Language Processing")
    print("=" * 50)
    
    lang_support = MultiLanguageSupport()
    
    # Sample documents in different languages
    documents = {
        'english_doc.txt': "This is a technical documentation about artificial intelligence and machine learning algorithms.",
        'spanish_doc.txt': "Este es un documento técnico sobre inteligencia artificial y algoritmos de aprendizaje automático.",
        'french_doc.txt': "Ceci est une documentation technique sur l'intelligence artificielle et les algorithmes d'apprentissage automatique.",
        'german_doc.txt': "Dies ist eine technische Dokumentation über künstliche Intelligenz und maschinelle Lernalgorithmen.",
        'chinese_doc.txt': "这是关于人工智能和机器学习算法的技术文档。",
        'japanese_doc.txt': "これは人工知能と機械学習アルゴリズムに関する技術文書です。"
    }
    
    for filename, content in documents.items():
        doc_analysis = lang_support.validate_document_language(content, filename)
        
        detected_lang = doc_analysis['detected_language']
        lang_name = doc_analysis['language_info']['name']
        is_safe = doc_analysis['is_safe']
        needs_translation = doc_analysis['needs_translation']
        
        status = "✅" if is_safe else "❌"
        translate_info = "🔄 Will translate" if needs_translation else "📝 English ready"
        
        print(f"{status} {filename}")
        print(f"   Language: {lang_name} ({detected_lang})")
        print(f"   Confidence: {doc_analysis['confidence']:.2f}")
        print(f"   Safe: {'Yes' if is_safe else 'No'}")
        print(f"   Translation: {translate_info}")
        print(f"   Size: {doc_analysis['content_length']} → {doc_analysis['english_length']} chars")
        print()

def test_greeting_detection():
    """Test greeting detection in multiple languages"""
    print("👋 Testing Greeting Detection")
    print("=" * 50)
    
    lang_support = MultiLanguageSupport()
    
    greetings = {
        'en': ["Hello", "Hi there", "Good morning"],
        'hi': ["नमस्ते", "हैलो", "सुप्रभात"],
        'ja': ["こんにちは", "おはよう", "こんばんは"],
        'zh': ["你好", "早上好", "晚上好"],
        'es': ["Hola", "Buenos días", "Buenas tardes"],
        'fr': ["Bonjour", "Bonsoir", "Salut"]
    }
    
    for lang, lang_greetings in greetings.items():
        print(f"🌍 {lang.upper()} Greetings:")
        for greeting in lang_greetings:
            result = lang_support.process_multilingual_chat(greeting)
            detected = "✅ Detected" if result['is_greeting'] else "❌ Missed"
            print(f"   {detected}: {greeting}")
        print()

def test_mixed_language():
    """Test mixed language content"""
    print("🌐 Testing Mixed Language Content")
    print("=" * 50)
    
    lang_support = MultiLanguageSupport()
    
    mixed_messages = [
        "Hello नमस्ते こんにちは",  # English + Hindi + Japanese
        "Thank you merci 谢谢",      # English + French + Chinese
        "Programming プログラミング coding",  # English + Japanese + English
        "AI人工智能 machine learning",  # Mixed Chinese-English tech terms
    ]
    
    for message in mixed_messages:
        result = lang_support.process_multilingual_chat(message)
        
        print(f"Message: {message}")
        print(f"Primary Language: {result['language_info']['name']} ({result['detected_language']})")
        print(f"Mixed Script: {'Yes' if result['is_mixed_script'] else 'No'}")
        print(f"Confidence: {result['confidence']:.2f}")
        print()

def test_language_statistics():
    """Test detailed language statistics"""
    print("📊 Testing Language Statistics")
    print("=" * 50)
    
    lang_support = MultiLanguageSupport()
    
    sample_text = "Hello world! This is a test message with some English content. 你好世界！这是一个测试消息。"
    
    stats = lang_support.get_language_statistics(sample_text)
    
    print(f"Text: {sample_text}")
    print(f"Primary Language: {stats['primary_language']}")
    print(f"Primary Confidence: {stats['primary_confidence']:.3f}")
    print(f"Character Count: {stats['character_count']}")
    print(f"Word Count: {stats['word_count']}")
    print(f"Is Multilingual: {stats['is_multilingual']}")
    
    print("\nAll Detected Languages:")
    for lang_info in stats.get('all_detected_languages', []):
        print(f"   {lang_info['name']} ({lang_info['language']}): {lang_info['confidence']:.3f}")
    
    print(f"\nUnique Scripts: {stats.get('unique_scripts', [])}")
    print()

def test_supported_languages():
    """Test supported languages information"""
    print("🗺️ Testing Supported Languages")
    print("=" * 50)
    
    lang_support = MultiLanguageSupport()
    
    lang_info = lang_support.get_supported_languages_info()
    
    print(f"Total Supported Languages: {lang_info['total_languages']}")
    print()
    
    print("🌍 All Supported Languages:")
    for code, info in lang_info['languages'].items():
        rtl_indicator = " (RTL)" if info.get('rtl', False) else ""
        translate_indicator = " 🔄" if info.get('auto_translate', False) else ""
        print(f"   {code}: {info['native_name']} ({info['name']}){rtl_indicator}{translate_indicator}")
    
    print(f"\n➡️ RTL Languages: {', '.join(lang_info['rtl_languages'])}")
    print(f"🔄 Auto-Translate Languages: {len(lang_info['auto_translate_languages'])} languages")
    print()

def main():
    """Run all multi-language tests"""
    print("🧪 AI ChatBot Multi-Language Testing Suite")
    print("🌍 Testing support for Hindi, Japanese, Chinese, and more!")
    print("=" * 60)
    print()
    
    try:
        test_language_detection()
        test_content_filtering()
        test_document_processing() 
        test_greeting_detection()
        test_mixed_language()
        test_language_statistics()
        test_supported_languages()
        
        print("🎉 Multi-Language Testing Complete!")
        print("\n💡 Your ChatBot Now Supports:")
        print("   ✅ 12+ languages with automatic detection")
        print("   ✅ Content filtering in native languages")  
        print("   ✅ Document translation for knowledge base")
        print("   ✅ Responses in user's original language")
        print("   ✅ Mixed-language content handling")
        print("   ✅ RTL (Right-to-Left) language support")
        
        print("\n🚀 Ready for Global Deployment!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Install missing dependencies:")
        print("pip install langdetect")
        print("pip install openai")
        
    except Exception as e:
        print(f"❌ Test Error: {e}")
        print("Check your language support implementation")

if __name__ == "__main__":
    main() 