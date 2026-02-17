import sys
import os

# Add root to path
sys.path.append(os.getcwd())

try:
    print("Testing imports...")
    from src.trust import TrustAnalyzer
    from src.text_analysis import TextAnalyzer
    from src.scraper import CompanyDiscoveryEngine
    from src.verification import JobVerifier
    print("✅ Imports successful")
    
    print("Testing TrustAnalyzer...")
    trust = TrustAnalyzer()
    res = trust.analyze_email("test@gmail.com")
    assert res['is_free_provider'] == True
    print("✅ TrustAnalyzer passed")
    
    print("Testing TextAnalyzer...")
    # Initialize without DB for basic test or mocking
    text = TextAnalyzer(db_path='companies.db') 
    res = text.analyze_content("Urgent hiring! Send money.")
    assert res['risk_score'] > 0
    print("✅ TextAnalyzer passed")
    
    print("ALL MODULES VERIFIED")
    
except Exception as e:
    print(f"❌ Test Failed: {e}")
    sys.exit(1)
