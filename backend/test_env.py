import os
import sys
sys.path.append('.')
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "dummy":
    print("API KEY STATUS: MISSING_OR_DUMMY")
elif len(api_key) < 10:
    print("API KEY STATUS: TOO_SHORT_INVALID")
else:
    print("API KEY STATUS: PRESENT")
