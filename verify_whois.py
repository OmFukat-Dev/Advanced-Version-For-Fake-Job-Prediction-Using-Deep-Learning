import sys
with open('whois_status.txt', 'w') as f:
    try:
        import whois
        f.write("SUCCESS: whois imported\n")
        f.write(f"File: {whois.__file__}\n")
    except ImportError as e:
        f.write(f"FAILURE: {e}\n")
    except Exception as e:
        f.write(f"ERROR: {e}\n")
    f.write(f"Path: {sys.path}\n")
