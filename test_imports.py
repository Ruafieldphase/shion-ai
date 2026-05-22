import os
import sys
try:
    import requests
    open(r'c:\workspace2\shion\test_imports_success.txt', 'w').write('success requests only absolute')
except Exception as e:
    open(r'c:\workspace2\shion\test_imports_error.txt', 'w').write(f"{type(e).__name__}: {str(e)}")
