"""
Multi-Language Support System for AI ChatBot
Handles chat and document uploads in multiple languages including Hindi, Japanese, Chinese, etc.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from langdetect import detect, detect_langs
from langdetect.lang_detect_exception import LangDetectException
import unicodedata
from openai import OpenAI

# Setup logging
logger = logging.getLogger(__name__)

class MultiLanguageSupport:
    """Comprehensive multi-language support for the chatbot"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize multi-language support"""
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        
        # Supported languages configuration
        self.supported_languages = {
            'en': {
                'name': 'English',
                'native_name': 'English',
                'script': 'Latin',
                'rtl': False,
                'content_filter': True,
                'auto_translate': False
            },
            'hi': {
                'name': 'Hindi', 
                'native_name': 'हिन्दी',
                'script': 'Devanagari',
                'rtl': False,
                'content_filter': True,
                'auto_translate': True
            },
            'ja': {
                'name': 'Japanese',
                'native_name': '日本語',
                'script': 'Hiragana/Katakana/Kanji',
                'rtl': False,
                'content_filter': True,
                'auto_translate': True
            },
            'zh': {
                'name': 'Chinese',
                'native_name': '中文',
                'script': 'Chinese',
                'rtl': False,
                'content_filter': True,
                'auto_translate': True
            },
            'zh-cn': {
                'name': 'Chinese Simplified',
                'native_name': '简体中文',
                'script': 'Chinese',
                'rtl': False,
                'content_filter': True,
                'auto_translate': True
            },
            'zh-tw': {
                'name': 'Chinese Traditional',
                'native_name': '繁體中文',
                'script': 'Chinese',
                'rtl': False,
                'content_filter': True,
                'auto_translate': True
            },
            'ko': {
                'name': 'Korean',
                'native_name': '한국어',
                'script': 'Hangul',
                'rtl': False,
                'content_filter': True,
                'auto_translate': True
            },
            'ar': {
                'name': 'Arabic',
                'native_name': 'العربية',
                'script': 'Arabic',
                'rtl': True,
                'content_filter': True,
                'auto_translate': True
            },
            'es': {
                'name': 'Spanish',
                'native_name': 'Español',
                'script': 'Latin',
                'rtl': False,
                'content_filter': True,
                'auto_translate': True
            },
            'fr': {
                'name': 'French',
                'native_name': 'Français',
                'script': 'Latin',
                'rtl': False,
                'content_filter': True,
                'auto_translate': True
            },
            'de': {
                'name': 'German',
                'native_name': 'Deutsch',
                'script': 'Latin',
                'rtl': False,
                'content_filter': True,
                'auto_translate': True
            },
            'pt': {
                'name': 'Portuguese',
                'native_name': 'Português',
                'script': 'Latin',
                'rtl': False,
                'content_filter': True,
                'auto_translate': True
            },
            'ru': {
                'name': 'Russian',
                'native_name': 'Русский',
                'script': 'Cyrillic',
                'rtl': False,
                'content_filter': True,
                'auto_translate': True
            }
        }
        
        # Multi-language blocked content patterns
        self.multilingual_blocked_patterns = {
            'sexual_content': {
                'en': ['sex', 'nude', 'porn', 'adult', 'xxx'],
                'hi': ['यौन', 'नग्न', 'अश्लील'],
                'ja': ['セックス', 'ヌード', 'ポルノ', 'アダルト'],
                'zh': ['性', '裸体', '色情', '成人'],
                'ko': ['섹스', '누드', '포르노', '성인'],
                'ar': ['جنس', 'عاري', 'إباحي'],
                'es': ['sexo', 'desnudo', 'porno', 'adulto'],
                'fr': ['sexe', 'nu', 'porno', 'adulte'],
                'de': ['sex', 'nackt', 'porno', 'erwachsene'],
                'ru': ['секс', 'голый', 'порно', 'взрослый']
            },
            'violence': {
                'en': ['bomb', 'kill', 'murder', 'weapon', 'violence'],
                'hi': ['बम', 'हत्या', 'मारना', 'हथियार', 'हिंसा'],
                'ja': ['爆弾', '殺す', '殺人', '武器', '暴力'],
                'zh': ['炸弹', '杀', '谋杀', '武器', '暴力'],
                'ko': ['폭탄', '죽이다', '살인', '무기', '폭력'],
                'ar': ['قنبلة', 'قتل', 'جريمة قتل', 'سلاح', 'عنف'],
                'es': ['bomba', 'matar', 'asesinato', 'arma', 'violencia'],
                'fr': ['bombe', 'tuer', 'meurtre', 'arme', 'violence'],
                'de': ['bombe', 'töten', 'mord', 'waffe', 'gewalt'],
                'ru': ['бомба', 'убить', 'убийство', 'оружие', 'насилие']
            },
            'hate_speech': {
                'en': ['hate', 'racist', 'nazi', 'terrorism'],
                'hi': ['नफरत', 'जातिवादी', 'आतंकवाद'],
                'ja': ['憎悪', '人種差別', 'テロ'],
                'zh': ['仇恨', '种族主义', '恐怖主义'],
                'ko': ['증오', '인종차별', '테러'],
                'ar': ['كراهية', 'عنصري', 'إرهاب'],
                'es': ['odio', 'racista', 'terrorismo'],
                'fr': ['haine', 'raciste', 'terrorisme'],
                'de': ['hass', 'rassist', 'terrorismus'],
                'ru': ['ненависть', 'расист', 'терроризм']
            }
        }
        
        # Common greetings in different languages
        self.greetings = {
            'en': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
            'hi': ['नमस्ते', 'हैलो', 'सुप्रभात', 'शुभ संध्या'],
            'ja': ['こんにちは', 'おはよう', 'こんばんは', 'はじめまして'],
            'zh': ['你好', '早上好', '晚上好', '您好'],
            'ko': ['안녕하세요', '좋은 아침', '안녕히 주무세요'],
            'ar': ['مرحبا', 'صباح الخير', 'مساء الخير'],
            'es': ['hola', 'buenos días', 'buenas tardes'],
            'fr': ['bonjour', 'bonsoir', 'salut'],
            'de': ['hallo', 'guten morgen', 'guten abend'],
            'ru': ['привет', 'доброе утро', 'добрый вечер']
        }
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of input text
        Returns: (language_code, confidence)
        """
        if not text or len(text.strip()) < 3:
            return 'en', 1.0  # Default to English for very short text
        
        try:
            # Primary detection
            detected_lang = detect(text)
            
            # Get confidence scores
            lang_probabilities = detect_langs(text)
            confidence = next((lang.prob for lang in lang_probabilities if lang.lang == detected_lang), 0.5)
            
            # Map some common variations
            lang_mapping = {
                'zh-cn': 'zh',
                'zh-tw': 'zh',
                'zh-hans': 'zh',
                'zh-hant': 'zh'
            }
            
            detected_lang = lang_mapping.get(detected_lang, detected_lang)
            
            # Verify if language is supported
            if detected_lang not in self.supported_languages:
                logger.warning(f"Detected unsupported language: {detected_lang}, defaulting to English")
                return 'en', 0.5
            
            return detected_lang, confidence
            
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}, defaulting to English")
            return 'en', 0.5
    
    def is_text_mixed_script(self, text: str) -> bool:
        """Check if text contains mixed scripts (multiple languages)"""
        scripts = set()
        
        for char in text:
            if char.isalpha():
                script = unicodedata.name(char, '').split()[0] if unicodedata.name(char, '') else 'UNKNOWN'
                scripts.add(script)
        
        # If more than 2 different scripts, consider it mixed
        return len(scripts) > 2
    
    def check_multilingual_content(self, text: str, detected_lang: str) -> Tuple[bool, str]:
        """
        Check if content violates policies in the detected language
        Returns: (is_safe, reason_if_blocked)
        """
        if not text:
            return True, ""
        
        text_lower = text.lower()
        
        # Check patterns for the detected language
        for category, patterns in self.multilingual_blocked_patterns.items():
            if detected_lang in patterns:
                for pattern in patterns[detected_lang]:
                    if pattern in text_lower:
                        return False, f"Content contains inappropriate material in {self.supported_languages[detected_lang]['name']}: '{pattern}'"
        
        # Also check English patterns as fallback (many users mix English with native language)
        if detected_lang != 'en':
            for category, patterns in self.multilingual_blocked_patterns.items():
                for pattern in patterns.get('en', []):
                    if pattern in text_lower:
                        return False, f"Content contains inappropriate material: '{pattern}'"
        
        return True, ""
    
    def translate_to_english(self, text: str, source_lang: str) -> str:
        """
        Translate text to English for processing
        Uses OpenAI for high-quality translation
        """
        if source_lang == 'en':
            return text
        
        if not self.openai_client:
            logger.warning("OpenAI client not available for translation")
            return text  # Return original text if translation not available
        
        try:
            language_name = self.supported_languages.get(source_lang, {}).get('name', source_lang)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a professional translator. Translate the following {language_name} text to English. Only return the translation, no explanations."
                    },
                    {
                        "role": "user", 
                        "content": text
                    }
                ],
                temperature=0.1,  # Low temperature for consistent translation
                max_tokens=1000
            )
            
            translation = response.choices[0].message.content.strip()
            logger.info(f"Translated {source_lang} to English: {len(text)} -> {len(translation)} chars")
            return translation
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # Return original text if translation fails
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """
        Translate English text to target language
        """
        if target_lang == 'en':
            return text
        
        if not self.openai_client:
            return text
        
        try:
            language_name = self.supported_languages.get(target_lang, {}).get('name', target_lang)
            native_name = self.supported_languages.get(target_lang, {}).get('native_name', language_name)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a professional translator. Translate the following English text to {language_name} ({native_name}). Only return the translation, no explanations. Maintain a professional and helpful tone."
                    },
                    {
                        "role": "user", 
                        "content": text
                    }
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            translation = response.choices[0].message.content.strip()
            logger.info(f"Translated English to {target_lang}: {len(text)} -> {len(translation)} chars")
            return translation
            
        except Exception as e:
            logger.error(f"Translation to {target_lang} failed: {e}")
            return text
    
    def process_multilingual_chat(self, message: str) -> Dict[str, Any]:
        """
        Process a chat message in any language
        Returns comprehensive language analysis and processed content
        """
        # Detect language
        detected_lang, confidence = self.detect_language(message)
        lang_info = self.supported_languages.get(detected_lang, self.supported_languages['en'])
        
        # Check for mixed scripts
        is_mixed = self.is_text_mixed_script(message)
        
        # Check content safety in detected language
        is_safe, safety_reason = self.check_multilingual_content(message, detected_lang)
        
        # Translate to English if needed for AI processing
        english_message = message
        if detected_lang != 'en' and self.openai_client:
            english_message = self.translate_to_english(message, detected_lang)
        
        # Determine greeting
        is_greeting = any(greeting in message.lower() for greeting in self.greetings.get(detected_lang, []))
        
        return {
            'original_message': message,
            'english_message': english_message,
            'detected_language': detected_lang,
            'language_info': lang_info,
            'confidence': confidence,
            'is_mixed_script': is_mixed,
            'is_safe': is_safe,
            'safety_reason': safety_reason,
            'is_greeting': is_greeting,
            'requires_translation': detected_lang != 'en'
        }
    
    def process_multilingual_response(self, english_response: str, target_lang: str) -> str:
        """
        Process AI response and translate back to user's language if needed
        """
        if target_lang == 'en':
            return english_response
        
        # Translate response back to user's language
        translated_response = self.translate_from_english(english_response, target_lang)
        return translated_response
    
    def validate_document_language(self, content: str, filename: str) -> Dict[str, Any]:
        """
        Validate and analyze uploaded document language
        """
        # Detect document language
        detected_lang, confidence = self.detect_language(content)
        lang_info = self.supported_languages.get(detected_lang, self.supported_languages['en'])
        
        # Check content safety
        is_safe, safety_reason = self.check_multilingual_content(content, detected_lang)
        
        # Check if translation is needed for knowledge base
        needs_translation = detected_lang != 'en' and lang_info.get('auto_translate', False)
        
        # Translate content if needed
        english_content = content
        if needs_translation and self.openai_client:
            # For large documents, translate in chunks
            english_content = self._translate_large_text(content, detected_lang)
        
        return {
            'filename': filename,
            'original_content': content,
            'english_content': english_content,
            'detected_language': detected_lang,
            'language_info': lang_info,
            'confidence': confidence,
            'is_safe': is_safe,
            'safety_reason': safety_reason,
            'needs_translation': needs_translation,
            'content_length': len(content),
            'english_length': len(english_content)
        }
    
    def _translate_large_text(self, text: str, source_lang: str, chunk_size: int = 2000) -> str:
        """
        Translate large text by breaking it into chunks
        """
        if len(text) <= chunk_size:
            return self.translate_to_english(text, source_lang)
        
        # Split text into chunks
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Translating chunk {i+1}/{len(chunks)}")
            translated_chunk = self.translate_to_english(chunk, source_lang)
            translated_chunks.append(translated_chunk)
        
        return ' '.join(translated_chunks)
    
    def get_language_statistics(self, text: str) -> Dict[str, Any]:
        """
        Get detailed language statistics for the text
        """
        try:
            lang_probabilities = detect_langs(text)
            
            stats = {
                'primary_language': lang_probabilities[0].lang if lang_probabilities else 'unknown',
                'primary_confidence': lang_probabilities[0].prob if lang_probabilities else 0,
                'all_detected_languages': [
                    {
                        'language': lang.lang,
                        'confidence': round(lang.prob, 3),
                        'name': self.supported_languages.get(lang.lang, {}).get('name', lang.lang)
                    }
                    for lang in lang_probabilities[:5]  # Top 5 detected languages
                ],
                'character_count': len(text),
                'word_count': len(text.split()),
                'unique_scripts': self._get_unicode_scripts(text),
                'is_multilingual': len(lang_probabilities) > 1 and lang_probabilities[1].prob > 0.1
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Language statistics failed: {e}")
            return {
                'primary_language': 'unknown',
                'primary_confidence': 0,
                'error': str(e)
            }
    
    def _get_unicode_scripts(self, text: str) -> List[str]:
        """Get list of Unicode scripts used in the text"""
        scripts = set()
        
        for char in text:
            if char.isalpha():
                try:
                    script = unicodedata.name(char).split()[0]
                    scripts.add(script)
                except ValueError:
                    pass
        
        return list(scripts)
    
    def get_supported_languages_info(self) -> Dict[str, Any]:
        """Get information about all supported languages"""
        return {
            'total_languages': len(self.supported_languages),
            'languages': self.supported_languages,
            'rtl_languages': [code for code, info in self.supported_languages.items() if info.get('rtl', False)],
            'auto_translate_languages': [code for code, info in self.supported_languages.items() if info.get('auto_translate', False)]
        }

# Language-specific content filters
class MultilingualContentFilter:
    """Enhanced content filter with multi-language support"""
    
    def __init__(self, language_support: MultiLanguageSupport):
        self.language_support = language_support
    
    def check_content(self, text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Check content with multi-language awareness
        Returns: (is_safe, reason, language_info)
        """
        # Process the text with language detection
        lang_analysis = self.language_support.process_multilingual_chat(text)
        
        # Return safety status with language context
        return (
            lang_analysis['is_safe'],
            lang_analysis.get('safety_reason', ''),
            lang_analysis
        )

def test_multilingual_support():
    """Test the multi-language support system"""
    lang_support = MultiLanguageSupport()
    
    test_messages = [
        "Hello, how are you?",  # English
        "नमस्ते, आप कैसे हैं?",  # Hindi
        "こんにちは、元気ですか？",  # Japanese  
        "你好，你好吗？",  # Chinese
        "안녕하세요, 어떻게 지내세요?",  # Korean
        "Hola, ¿cómo estás?",  # Spanish
        "Bonjour, comment allez-vous?",  # French
    ]
    
    print("🌍 Multi-Language Support Test")
    print("=" * 50)
    
    for message in test_messages:
        result = lang_support.process_multilingual_chat(message)
        
        print(f"Message: {message}")
        print(f"Language: {result['language_info']['name']} ({result['detected_language']})")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Safe: {'✅' if result['is_safe'] else '❌'}")
        print(f"Greeting: {'👋' if result['is_greeting'] else '❌'}")
        print("-" * 30)

if __name__ == "__main__":
    test_multilingual_support() 