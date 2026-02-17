import json
import re
from datetime import datetime
from urllib.parse import urlparse
import sqlite3

from .trust import TrustAnalyzer
from .text_analysis import TextAnalyzer
from .scraper import CompanyDiscoveryEngine

class JobVerifier:
    """
    Main orchestration class for job verification.
    Combines signals from TrustAnalyzer, TextAnalyzer, and CompanyDiscoveryEngine.
    """
    
    def __init__(self, db_path='companies.db'):
        self.db_path = db_path
        self.trust_analyzer = TrustAnalyzer()
        self.text_analyzer = TextAnalyzer(db_path)
        self.discovery_engine = CompanyDiscoveryEngine()
        
    def verify_job(self, text_input, input_type='auto'):
        """
        Verify a job posting based on text input or URL.
        
        Args:
            text_input (str): The job text or URL or company name.
            input_type (str): 'auto', 'url', 'text', 'company'.
            
        Returns:
            dict: Comprehensive verification report.
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'input_preview': text_input[:100] + '...',
            'scores': {},
            'flags': [],
            'details': {},
            'final_verdict': 'Unknown'
        }
        
        # 1. Detect Input Type & Extract Basic Info
        extracted_info = self._parse_input(text_input, input_type)
        report['extracted_info'] = extracted_info
        
        # 2. Company Verification
        company_status = self._verify_company(extracted_info.get('company'))
        report['company_analysis'] = company_status
        
        # 3. Trust Analysis (Email & URL)
        trust_report = self._analyze_trust_signals(extracted_info)
        report['trust_analysis'] = trust_report
        
        # 4. Content/Text Analysis
        content_report = self.text_analyzer.analyze_content(extracted_info.get('full_text', ''))
        report['content_analysis'] = content_report
        
        # 5. Calculate Final Score
        final_score, risk_level = self._calculate_score(company_status, trust_report, content_report)
        
        report['scores']['authenticity'] = final_score
        report['final_verdict'] = risk_level
        
        return report

    def _parse_input(self, text, input_type):
        """Parse input to extract structural data."""
        info = {
            'full_text': text,
            'company': None,
            'urls': [],
            'emails': []
        }
        
        # Simple extraction heuristics
        # If it looks like a URL
        if input_type == 'url' or (input_type == 'auto' and text.startswith(('http', 'www'))):
            info['urls'].append(text)
            # Todo: Scraping logic if it's a URL (not implementing full scraping of job board URLs yet)
            
        # Emails
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if emails:
            info['emails'] = emails
            
        # Company Name Extraction (Very naive - needs NER or user input ideally)
        # Using a simple heuristic: Assume first line or capitalized words might be company if short
        lines = text.split('\n')
        if len(lines) > 0 and len(lines[0]) < 50:
             # Just a potentially lucky guess if the user pasted "Google\nJob Description..."
             candidate = lines[0].strip()
             # Basic cleanup: remove common suffix words if they appear at the end like " is hiring"
             clean_candidate = re.sub(r'(?i)\s+(is hiring|hiring|job opening|vacancy|wanted).*', '', candidate)
             if len(clean_candidate) > 2:
                info['company'] = clean_candidate
             
        # If user explicitly provides company name in a structured way elsewhere, we handle it.
        # For now, we rely on the TextAnalyzer's extraction or what we can guess.
        
        return info

    def _verify_company(self, company_name):
        """Check DB or Auto-Discover company."""
        if not company_name:
            return {'status': 'unknown', 'score': 0, 'details': 'No company name detected'}
            
        # Check DB
        db_company = self._get_company_from_db(company_name)
        if db_company:
            return {
                'status': 'verified',
                'source': 'database',
                'score': 100, 
                'details': db_company
            }
            
        # Auto-Discover
        discovery = self.discovery_engine.discover_company(company_name)
        if discovery['found']:
            # Save to DB for future
            self._save_company_to_db(discovery)
            return {
                'status': 'verified', 
                'source': 'web_search',
                'score': discovery['confidence'],
                'details': discovery
            }
            
        return {'status': 'unverified', 'score': 0, 'details': discovery['validation_details']}

    def _analyze_trust_signals(self, info):
        """Run trust analysis on extracted artifacts."""
        results = {
            'email_scores': [],
            'url_scores': [],
            'overall_trust': 1.0
        }
        
        for email in info['emails']:
            res = self.trust_analyzer.analyze_email(email)
            results['email_scores'].append(res)
            
        for url in info['urls']:
            res = self.trust_analyzer.analyze_url(url)
            results['url_scores'].append(res)
            
        return results

    def _calculate_score(self, company, trust, content):
        """Weighted scoring algorithm."""
        base_score = 100
        
        # Penalties
        risk_score = content['risk_score'] # 0-100
        base_score -= risk_score
        
        # Trust Penalties
        for email_res in trust['email_scores']:
            if email_res['score'] < 0.5:
                base_score -= 20
        
        for url_res in trust['url_scores']:
            if url_res['score'] < 0.5:
                base_score -= 10
                
        # Company Bonus/Penalty
        if company['status'] == 'verified':
            base_score += 10
        elif company['status'] == 'unverified' and company['score'] == 0:
            base_score -= 10
            
        final_score = max(0, min(100, base_score))
        
        if final_score > 80:
            verdict = 'Genuine'
        elif final_score > 40:
            verdict = 'Suspicious'
        else:
            verdict = 'Likely Fake'
            
        return final_score, verdict

    def _get_company_from_db(self, name):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM companies WHERE name LIKE ?", (f"%{name}%",))
            row = cursor.fetchone()
            conn.close()
            return row
        except:
            return None

    def _save_company_to_db(self, data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO companies (name, website, careers_url, verification_confidence, verified)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['company_name'], data.get('website'), data.get('careers_url'), 
                  data['confidence']/100, 1))
            conn.commit()
            conn.close()
        except:
            pass
