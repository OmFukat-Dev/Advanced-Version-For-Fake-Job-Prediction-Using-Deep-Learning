import re
import socket
import whois
import datetime
import urllib.parse
from urllib.parse import urlparse

class TrustAnalyzer:
    """Analyzes trust signals for domains, emails, and URLs."""
    
    def __init__(self):
        self.free_email_providers = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
            'aol.com', 'protonmail.com', 'zoho.com', 'icloud.com'
        }
        
    def analyze_email(self, email, company_domain=None):
        """
        Analyze email address for trustworthiness.
        
        Returns:
            dict: {
                'score': float (0-1),
                'is_free_provider': bool,
                'domain_match': bool,
                'details': list
            }
        """
        if not email or '@' not in email:
            return {'score': 0, 'details': ['Invalid email format']}
            
        domain = email.split('@')[1].lower()
        details = []
        score = 1.0
        
        # Check for free provider
        is_free = domain in self.free_email_providers
        if is_free:
            score -= 0.6
            details.append(f"Email uses free provider: {domain}")
        else:
            details.append("Professional email domain")
            
        # Check domain match if provided
        match = False
        if company_domain:
            company_root = self._get_root_domain(company_domain)
            email_root = self._get_root_domain(domain)
            if company_root == email_root:
                match = True
                score += 0.2  # Bonus for matching
                details.append("Email matches company domain")
            elif not is_free:
                # Corporate domain mismatch is suspicious
                score -= 0.3
                details.append(f"Email domain ({domain}) does not match company ({company_domain})")
                
        return {
            'score': min(max(score, 0), 1),
            'is_free_provider': is_free,
            'domain_match': match,
            'details': details
        }

    def analyze_domain(self, domain):
        """
        Analyze domain for age and validity using Whois.
        WARNING: This can be slow and rate-limited.
        """
        details = []
        score = 0.5 # Neutral start
        
        try:
            # Basic validation
            if not self._is_valid_domain(domain):
                return {'score': 0, 'details': ['Invalid domain format']}

            # Whois check
            try:
                w = whois.whois(domain)
                
                # Check creation date
                creation_date = w.creation_date
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                    
                if creation_date:
                    age_days = (datetime.datetime.now() - creation_date).days
                    if age_days < 30:
                        score = 0.0
                        details.append(f"CRITICAL: Domain is very new ({age_days} days old)")
                    elif age_days < 180:
                        score = 0.4
                        details.append(f"WARNING: Domain is relatively new ({age_days} days old)")
                    else:
                        score = 1.0
                        details.append(f"Domain is established ({age_days // 365} years old)")
                else:
                    details.append("Could not verify domain age")
                    
            except Exception as e:
                details.append(f"Whois lookup failed: {str(e)}")
                
        except Exception as e:
            details.append(f"Domain analysis error: {str(e)}")
            
        return {
            'score': score,
            'details': details
        }
        
    def analyze_url(self, url):
        """Check URL for safety (redirects, shorteners)."""
        details = []
        score = 1.0
        
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {'score': 0, 'details': ['Invalid URL']}
            
        # Check for URL shorteners (basic list)
        shorteners = {'bit.ly', 'goo.gl', 't.co', 'tinyurl.com', 'is.gd'}
        if parsed.netloc.lower() in shorteners:
            score = 0.2
            details.append("Suspicious: Uses URL shortener")
        
        # Check for suspicious TLDs
        risky_tlds = {'.xyz', '.top', '.loan', '.click'}
        if any(parsed.netloc.lower().endswith(tld) for tld in risky_tlds):
            score -= 0.4
            details.append("Suspicious TLD detected")
            
        return {'score': score, 'details': details}

    def _get_root_domain(self, domain):
        """Extract root domain from subdomain (e.g. mail.google.com -> google.com)"""
        parts = domain.split('.')
        if len(parts) > 2:
            return '.'.join(parts[-2:])
        return domain

    def _is_valid_domain(self, domain):
        """Regex check for domain validity"""
        pattern = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}$"
        return re.match(pattern, domain) is not None
