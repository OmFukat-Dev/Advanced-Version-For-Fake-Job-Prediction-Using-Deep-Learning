from src.verification import JobVerifier
import re

def test_parse():
    print("Testing _parse_input...")
    v = JobVerifier()
    
    # Case 1: Standard Header
    text1 = "GENPACT INDIA PVT. LTD. is HIRING!\nWe are looking for..."
    info1 = v._parse_input(text1, 'text')
    print(f"Input: {text1[:30]}... -> Company: '{info1['company']}'")
    assert info1['company'] == "GENPACT INDIA PVT. LTD."
    
    # Case 2: Just Name
    text2 = "Google\nSoftware Engineer"
    info2 = v._parse_input(text2, 'text')
    print(f"Input: {text2[:30]}... -> Company: '{info2['company']}'")
    assert info2['company'] == "Google"
    
    print("✅ _parse_input logic verified!")

if __name__ == "__main__":
    test_parse()
