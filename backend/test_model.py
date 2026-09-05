import os
import sys
import asyncio
sys.path.append('.')
from dotenv import load_dotenv

load_dotenv(override=True)
from src.llm.client import client

async def verify_model():
    print("--- Starting Model Verification ---")
    
    # Check what the client is returning (model & provider)
    # We will pass a dummy tenant_id, so it falls back to environment variables
    
    # Actual Gemini Inference
    print("Sending prompt to Gemini: 'Reply with exactly: CAUSELY_MODEL_OK'")
    try:
        response = await client.complete("Reply with exactly: CAUSELY_MODEL_OK")
        print(f"RAW RESPONSE: {response}")
        
        if "CAUSELY_MODEL_OK" in response:
            print("INFERENCE: PASS")
        else:
            print("INFERENCE: FAIL (Unexpected response)")
            
    except Exception as e:
        print(f"INFERENCE ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_model())
