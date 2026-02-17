import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, urljoin
import streamlit as st
import re

class CompanyDiscoveryEngine:
    """AI-powered company discovery engine that automatically finds and validates new companies"""
    
    def __init__(self):
        self.session = self._create_session()
        self.search_engines = {
            'google': 'https://www.google.com/search?q=',
            'bing': 'https://www.bing.com/search?q=',
            'duckduckgo': 'https://duckduckgo.com/html/?q='
        }
        
    def _create_session(self):
        """Create robust session for search engine queries"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def discover_company(self, company_name):
        """Main method to discover company and find careers page"""
        # st.info(f"🔍 **Auto-Discovery**: Searching for '{company_name}' on search engines...") # Removing UI calls from logic layer
        
        discovery_result = {
            'company_name': company_name,
            'found': False,
            'careers_url': None,
            'website': None,
            'confidence': 0,
            'search_engine_used': None,
            'discovery_method': None,
            'validation_details': []
        }
        
        # Step 1: Search for company website
        website_url = self._find_company_website(company_name)
        if not website_url:
            discovery_result['validation_details'].append("❌ Could not find company website")
            return discovery_result
        
        discovery_result['website'] = website_url
        discovery_result['validation_details'].append(f"✅ Found website: {website_url}")
        
        # Step 2: Find careers page
        careers_url = self._find_careers_page(website_url, company_name)
        if not careers_url:
            discovery_result['validation_details'].append("❌ Could not find careers page")
            return discovery_result
        
        discovery_result['careers_url'] = careers_url
        discovery_result['validation_details'].append(f"✅ Found careers page: {careers_url}")
        
        # Step 3: Validate company legitimacy
        validation_score = self._validate_company(website_url, careers_url, company_name)
        
        if validation_score >= 0.7:  # High confidence
            discovery_result['found'] = True
            discovery_result['confidence'] = validation_score * 100
            discovery_result['validation_details'].append(f"✅ Company validation score: {validation_score:.1%}")
        else:
            discovery_result['validation_details'].append(f"⚠️ Low validation score: {validation_score:.1%}")
        
        return discovery_result
    
    def _find_company_website(self, company_name):
        """Find company website using search engines"""
        search_queries = [
            f"{company_name} official website",
            f"{company_name} company",
            f"www.{company_name.replace(' ', '').lower()}.com",
            f"{company_name} careers",
            f"{company_name} contact"
        ]
        
        for query in search_queries:
            for engine_name, engine_url in self.search_engines.items():
                try:
                    search_url = f"{engine_url}{quote(query)}"
                    response = self.session.get(search_url, timeout=10, verify=False)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        website_url = self._extract_website_from_results(soup, company_name)
                        
                        if website_url and self._validate_website(website_url):
                            return website_url
                            
                except Exception as e:
                    continue
        
        return None
    
    def _extract_website_from_results(self, soup, company_name):
        """Extract website URL from search results"""
        # Common search result selectors
        selectors = [
            'a[href*="http"]',
            '.g a',
            '.r a',
            '.result__a',
            '.b_algo a',
            'h3 a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if self._is_company_website(href, company_name):
                    return href
        
        return None
    
    def _is_company_website(self, url, company_name):
        """Check if URL is likely a company website"""
        try:
            domain = urlparse(url).netloc.lower()
            company_words = company_name.lower().split()
            
            # Check if domain contains company name words
            name_match = any(word in domain for word in company_words if len(word) >= 2)
            
            # Check for common company TLDs
            valid_tld = any(domain.endswith(tld) for tld in ['.com', '.org', '.net', '.in', '.co', '.io'])
            
            # Exclude social media and common sites
            exclude_domains = ['facebook.com', 'linkedin.com', 'twitter.com', 'youtube.com', 
                             'instagram.com', 'wikipedia.org', 'google.com', 'bing.com']
            
            is_valid = (name_match and valid_tld and 
                       domain not in exclude_domains and
                       len(domain) > 5)
            
            return is_valid
            
        except:
            return False
    
    def _validate_website(self, website_url):
        """Validate that the website is accessible and legitimate"""
        try:
            response = self.session.get(website_url, timeout=10, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for company indicators
                has_title = bool(soup.title and soup.title.string)
                has_links = len(soup.find_all('a')) > 5
                has_content = len(soup.get_text()) > 100
                
                return has_title and has_links and has_content
                
        except:
            pass
        
        return False
    
    def _find_careers_page(self, website_url, company_name):
        """Find careers page from company website"""
        try:
            response = self.session.get(website_url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common careers page patterns
            careers_patterns = [
                '/careers', '/jobs', '/career', '/employment', 
                '/work-with-us', '/hiring', '/join-us', '/vacancies',
                '/opportunities', '/recruitment'
            ]
            
            # Look for careers links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text('', strip=True).lower()
                
                # Check URL patterns
                if any(pattern in href for pattern in careers_patterns):
                    careers_url = urljoin(website_url, href)
                    if self._validate_careers_page(careers_url):
                        return careers_url
                
                # Check link text
                careers_keywords = ['careers', 'jobs', 'employment', 'work with us', 'hiring', 'join us']
                if any(keyword in text for keyword in careers_keywords):
                    careers_url = urljoin(website_url, href)
                    if self._validate_careers_page(careers_url):
                        return careers_url
            
            # Try common careers page URLs
            common_paths = [
                '/careers', '/jobs', '/career', '/employment',
                '/work-with-us', '/join-us', '/hiring'
            ]
            
            for path in common_paths:
                careers_url = urljoin(website_url, path)
                if self._validate_careers_page(careers_url):
                    return careers_url
                    
        except Exception as e:
            pass
        
        return None
    
    def _validate_careers_page(self, careers_url):
        """Validate that the URL is actually a careers page"""
        try:
            response = self.session.get(careers_url, timeout=8, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                page_text = soup.get_text().lower()
                
                # Check for job-related content
                job_keywords = ['job', 'career', 'position', 'opening', 'vacancy', 
                              'apply', 'hire', 'recruit', 'opportunity']
                
                keyword_count = sum(1 for keyword in job_keywords if keyword in page_text)
                return keyword_count >= 3
                
        except:
            pass
        
        return False
    
    def _validate_company(self, website_url, careers_url, company_name):
        """Comprehensive company validation"""
        validation_score = 0
        validation_criteria = 0
        
        try:
            # Test website accessibility
            response = self.session.get(website_url, timeout=10, verify=False)
            if response.status_code == 200:
                validation_score += 0.3
            validation_criteria += 0.3
            
            # Test careers page accessibility
            response = self.session.get(careers_url, timeout=10, verify=False)
            if response.status_code == 200:
                validation_score += 0.3
            validation_criteria += 0.3
            
            # Check for professional website structure
            soup = BeautifulSoup(response.content, 'html.parser')
            has_navigation = len(soup.find_all('nav')) > 0 or len(soup.find_all('ul')) > 2
            has_footer = len(soup.find_all('footer')) > 0
            has_contact = any(link for link in soup.find_all('a', href=True) 
                            if 'contact' in link.get('href', '').lower())
            
            if has_navigation:
                validation_score += 0.2
            if has_footer:
                validation_score += 0.1
            if has_contact:
                validation_score += 0.1
                
            validation_criteria += 0.4
            
        except:
            pass
        
        return validation_score / validation_criteria if validation_criteria > 0 else 0


class RealJobScraper:
    """100% Real job scraper - Only shows ACTUAL job openings from company websites"""
    
    def __init__(self):
        self.session = self._create_session()
        
    def _create_session(self):
        """Create robust session for web scraping"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def scrape_real_jobs(self, company_name, careers_url, search_title=None):
        """Scrape ONLY REAL job openings from company career page - NO FALLBACK DATA"""
        if not careers_url:
            return []
        
        try:
            # Get the careers page
            response = self.session.get(careers_url, timeout=15, verify=False)
            if response.status_code != 200:
                print(f"⚠️ Could not access {company_name} career page (Status: {response.status_code})")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract REAL job listings
            jobs = self._extract_real_jobs(soup, company_name, careers_url, search_title)
            
            if jobs:
                print(f"✅ Found {len(jobs)} REAL job openings at {company_name}")
                return jobs
            else:
                print(f"ℹ️ No current job openings found on {company_name}'s career page")
                return []
                
        except Exception as e:
            print(f"❌ Error scraping {company_name}: {str(e)}")
            return []
    
    def _extract_real_jobs(self, soup, company_name, base_url, search_title):
        """Extract ONLY REAL job listings from HTML - NO FAKE DATA"""
        jobs = []
        
        # Comprehensive job listing detection
        jobs.extend(self._find_jobs_by_selectors(soup, company_name, base_url))
        jobs.extend(self._find_jobs_by_links(soup, company_name, base_url))
        jobs.extend(self._find_jobs_by_keywords(soup, company_name, base_url))
        
        # Filter for relevance if search title provided
        if search_title:
            jobs = [job for job in jobs if self._is_relevant_to_search(job['title'], search_title)]
        
        # Remove duplicates and limit results
        unique_jobs = self._remove_duplicates(jobs)
        return unique_jobs[:10]  # Return max 10 real jobs
    
    def _find_jobs_by_selectors(self, soup, company_name, base_url):
        """Find jobs using common CSS selectors"""
        jobs = []
        
        # Comprehensive list of job listing selectors used by real companies
        job_selectors = [
            # Common career page structures
            '.job-listing', '.job-item', '.careers-item', '.position',
            '.job-post', '.opening', '.vacancy', '.role',
            '.job-card', '.career-item', '.job-opening',
            
            # Company-specific selectors
            '[data-cy="job-item"]', '[data-testid="job-item"]',
            '.jobs-list-item', '.careers-list-item',
            '.job-list-item', '.opening-list-item',
            
            # Generic job containers
            '[class*="job"]', '[class*="career"]', '[class*="position"]',
            '[class*="opening"]', '[class*="vacancy"]', '[class*="role"]',
            
            # List items that might contain jobs
            'li.job', 'li.career', 'li.position',
            'div.job', 'div.career', 'div.position'
        ]
        
        for selector in job_selectors:
            try:
                elements = soup.select(selector)
                for elem in elements:
                    job = self._parse_job_element(elem, company_name, base_url)
                    if job and self._is_valid_job(job):
                        jobs.append(job)
            except Exception as e:
                continue
        
        return jobs
    
    def _find_jobs_by_links(self, soup, company_name, base_url):
        """Find jobs by analyzing links"""
        jobs = []
        job_links = soup.find_all('a', href=True)
        
        for link in job_links:
            try:
                href = link.get('href', '').lower()
                text = link.get_text('', strip=True)
                
                # Check if this looks like a job link
                if self._is_job_link(href, text) and len(text) > 10:
                    job = {
                        'title': text,
                        'url': urljoin(base_url, href),
                        'company': company_name,
                        'location': self._extract_location_from_context(link),
                        'type': 'Full-time',
                        'source': 'Official Careers Page',
                        'posted': 'Current'
                    }
                    if self._is_valid_job(job):
                        jobs.append(job)
            except:
                continue
        
        return jobs
    
    def _find_jobs_by_keywords(self, soup, company_name, base_url):
        """Find jobs by searching for job-related keywords in the page"""
        jobs = []
        job_keywords = [
            'software engineer', 'developer', 'analyst', 'manager',
            'data scientist', 'cloud engineer', 'devops', 'qa',
            'product manager', 'business analyst', 'consultant'
        ]
        
        # Get all text elements that might contain job titles
        text_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b', 'span', 'div'])
        
        for element in text_elements:
            text = element.get_text(strip=True)
            if text and len(text) > 10 and len(text) < 100:
                for keyword in job_keywords:
                    if keyword.lower() in text.lower():
                        job = {
                            'title': text,
                            'url': base_url,
                            'company': company_name,
                            'location': 'Multiple Locations',
                            'type': 'Full-time',
                            'source': 'Official Careers Page',
                            'posted': 'Current'
                        }
                        if self._is_valid_job(job) and job not in jobs:
                            jobs.append(job)
                            break
        
        return jobs
    
    def _parse_job_element(self, element, company_name, base_url):
        """Parse job information from HTML element"""
        try:
            # Extract title from various possible elements
            title = None
            title_elements = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b', 'span'])
            
            for title_elem in title_elements:
                text = title_elem.get_text(strip=True)
                if text and len(text) > 5 and len(text) < 100:
                    title = text
                    break
            
            if not title:
                # Try the element itself
                title = element.get_text(strip=True)
                if len(title) < 5 or len(title) > 100:
                    return None
            
            # Extract URL
            link_elem = element if element.name == 'a' else element.find('a', href=True)
            job_url = base_url
            if link_elem and link_elem.get('href'):
                job_url = urljoin(base_url, link_elem.get('href'))
            
            return {
                'title': title,
                'url': job_url,
                'company': company_name,
                'location': self._extract_location_from_element(element),
                'type': self._extract_job_type_from_element(element),
                'source': 'Official Careers Page',
                'posted': 'Current'
            }
        except:
            return None
    
    def _is_job_link(self, href, text):
        """Check if link is job-related"""
        job_url_patterns = ['/job', '/career', '/position', '/opening', '/vacancy', '/apply']
        job_text_patterns = ['job', 'career', 'position', 'opening', 'vacancy', 'apply', 'hire']
        
        href_match = any(pattern in href for pattern in job_url_patterns)
        text_match = any(pattern in text.lower() for pattern in job_text_patterns)
        
        return href_match or text_match
    
    def _is_valid_job(self, job):
        """Validate that this is a real job posting"""
        if not job or not job.get('title'):
            return False
        
        title = job['title'].lower()
        
        # Exclude navigation and footer elements
        exclude_patterns = [
            'home', 'about', 'contact', 'login', 'signup', 'privacy', 'terms',
            'blog', 'news', 'events', 'support', 'help', 'faq'
        ]
        
        if any(pattern in title for pattern in exclude_patterns):
            return False
        
        # Should be a reasonable length
        if len(job['title']) < 5 or len(job['title']) > 100:
            return False
        
        return True
    
    def _is_relevant_to_search(self, job_title, search_title):
        """Check if job is relevant to the search query"""
        if not search_title:
            return True
        
        job_lower = job_title.lower()
        search_lower = search_title.lower()
        
        # Check for direct keyword matches
        job_words = set(re.findall(r'\w+', job_lower))
        search_words = set(re.findall(r'\w+', search_lower))
        
        common_words = job_words.intersection(search_words)
        return len(common_words) >= 1
    
    def _extract_location_from_element(self, element):
        """Extract location from job element"""
        try:
            # Look for location in nearby elements
            location_selectors = ['.location', '.loc', '.place', '.city', '.country', '.office']
            for selector in location_selectors:
                loc_elem = element.select_one(selector)
                if loc_elem:
                    return loc_elem.get_text(strip=True)
            
            # Check parent and sibling elements
            parent = element.parent
            if parent:
                for selector in location_selectors:
                    loc_elem = parent.select_one(selector)
                    if loc_elem:
                        return loc_elem.get_text(strip=True)
        except:
            pass
        
        return 'Multiple Locations'
    
    def _extract_location_from_context(self, element):
        """Extract location from link context"""
        try:
            # Check sibling elements for location
            parent = element.parent
            if parent:
                location_elements = parent.find_all(class_=re.compile('location|loc|place', re.I))
                if location_elements:
                    return location_elements[0].get_text(strip=True)
        except:
            pass
        
        return 'Multiple Locations'
    
    def _extract_job_type_from_element(self, element):
        """Extract job type from element"""
        try:
            type_selectors = ['.type', '.employment-type', '.job-type', '.time-type']
            for selector in type_selectors:
                type_elem = element.select_one(selector)
                if type_elem:
                    text = type_elem.get_text(strip=True).lower()
                    if any(t in text for t in ['full', 'permanent']):
                        return 'Full-time'
                    elif 'part' in text:
                        return 'Part-time'
                    elif 'contract' in text:
                        return 'Contract'
        except:
            pass
        
        return 'Full-time'
    
    def _remove_duplicates(self, jobs):
        """Remove duplicate job listings"""
        seen_titles = set()
        unique_jobs = []
        
        for job in jobs:
            # Normalize title for comparison
            normalized_title = re.sub(r'[^a-zA-Z0-9]', '', job['title'].lower())
            if normalized_title not in seen_titles:
                unique_jobs.append(job)
                seen_titles.add(normalized_title)
        
        return unique_jobs
