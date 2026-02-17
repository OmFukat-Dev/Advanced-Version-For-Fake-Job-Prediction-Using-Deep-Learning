import sys
import os

sys.path.append(os.getcwd())

with open('test_output.txt', 'w') as f:
    try:
        f.write("Starting test...\n")
        
        # Test imports
        try:
            from src.trust import TrustAnalyzer
            f.write("Imported TrustAnalyzer\n")
        except ImportError as e:
            f.write(f"Failed to import TrustAnalyzer: {e}\n")
            
        try:
            from src.text_analysis import TextAnalyzer
            f.write("Imported TextAnalyzer\n")
        except ImportError as e:
            f.write(f"Failed to import TextAnalyzer: {e}\n")
            
        # Test Logic
        f.write("Testing Logic...\n")
        trust = TrustAnalyzer()
        res = trust.analyze_email("test@gmail.com")
        f.write(f"Trust Result: {res}\n")
        
        db_path = 'companies.db'
        if os.path.exists(db_path):
            f.write(f"DB found at {db_path}\n")
        else:
            f.write(f"DB NOT found at {db_path}\n")
            
        text = TextAnalyzer(db_path=db_path)
        res2 = text.analyze_content("Urgent hiring! Send money.")
        f.write(f"Text Result: {res2}\n")
        
        f.write("Reflecting success.\n")
        
    except Exception as e:
        f.write(f"CRITICAL ERROR: {e}\n")
        import traceback
        traceback.print_exc(file=f)

print("Debug test finished")
