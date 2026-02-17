import re
import spacy
from collections import Counter
import json
import sqlite3

class TextAnalyzer:
    """Analyzes job text for scam patterns, grammar, and key entities."""
    
    def __init__(self, db_path='companies.db'):
        self.db_path = db_path
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Fallback if model not found, though we tried to download it
            print("Warning: Spacy model not found. Some features will be limited.")
            self.nlp = None

    def _load_patterns(self):
        """Load patterns from DB."""
        patterns = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT pattern_text, risk_level, category FROM scam_patterns")
            patterns = cursor.fetchall()
            conn.close()
        except Exception as e:
            print(f"Error loading patterns: {e}")
        return patterns

    def analyze_content(self, text):
        """
        Analyze text content for scams and extract info.
        """
        if not text:
            return {'risk_score': 0, 'matches': [], 'extracted': {}}

        text_lower = text.lower()
        patterns = self._load_patterns()
        
        matches = []
        risk_score = 0
        
        # 1. Pattern Matching
        for pattern_text, level, category in patterns:
            if pattern_text in text_lower:
                match_data = {
                    'pattern': pattern_text,
                    'level': level,
                    'category': category
                }
                matches.append(match_data)
                
                # Simple scoring
                if level == 'critical':
                    risk_score += 40
                elif level == 'high':
                    risk_score += 20
                elif level == 'medium':
                    risk_score += 10
                    
        # 2. Heuristics (Urgency, Money, Bad Grammar indications)
        urgency_words = ['urgent', 'immediately', 'now', 'asap', 'quick']
        money_words = ['bank', 'account', 'transfer', 'fee', 'charge', 'investment']
        
        urgency_count = sum(1 for w in urgency_words if w in text_lower)
        money_count = sum(1 for w in money_words if w in text_lower)
        
        if urgency_count > 2:
            risk_score += 15
            matches.append({'pattern': 'High urgency language', 'level': 'medium', 'category': 'urgency'})
            
        if money_count > 1:
            risk_score += 20
            matches.append({'pattern': 'Payment/Banking language', 'level': 'high', 'category': 'payment'})

        # 3. Entity Extraction (Email, Phone, Links) if NLP available
        extracted = {
            'emails': re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text),
            'phones': re.findall(r'\+?[\d\s-]{10,}', text), # Very basic phone regex
            'urls': re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
        }
        
        # 4. Grammar/Spelling check (Simulated/Proxy)
        # Using a simple heuristic of ALL CAPS usage or excessive exclamation marks
        if len(text) > 0 and sum(1 for c in text if c.isupper()) / len(text) > 0.4:
            risk_score += 10
            matches.append({'pattern': 'Excessive Capitalization', 'level': 'low', 'category': 'style'})
            
        if text.count('!') > 5:
            risk_score += 5
            matches.append({'pattern': 'Excessive Exclamation', 'level': 'low', 'category': 'style'})

        return {
            'risk_score': min(risk_score, 100),
            'matches': matches,
            'extracted': extracted
        }
