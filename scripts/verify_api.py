import asyncio
import httpx
import sys
import json

BASE_URL = "http://localhost:8000"

async def run_verification():
    print(f"🚀 Starting API Verification against {BASE_URL}...")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Health Check
        print("\n1️⃣  Checking Health...")
        try:
            resp = await client.get("/health")
            resp.raise_for_status()
            print(f"✅ Health OK: {json.dumps(resp.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Health Check Failed: {e}")
            return

        # 2. Chat Test (Simplified Endpoint)
        print("\n2️⃣  Testing /api/v1/chat (Simplified)...")
        try:
            payload = {"content": "Hello Marcus, who are you?"}
            resp = await client.post("/api/v1/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"   PAD State: {data['pad_state']}")
            print(f"   Mood: {data['mood_label']}")
            
            if "response" not in data or "pad_state" not in data:
                print("❌ Invalid Response Schema")
                return
        except Exception as e:
            print(f"❌ Chat Test Failed: {e}")
            # print(resp.text)
            return

        # 3. Emotional State Test (Sad)
        print("\n3️⃣  Testing Emotional Reactivity (Sadness)...")
        try:
            payload = {"content": "I am feeling very sad and lonely today."}
            resp = await client.post("/api/v1/chat", json=payload)
            data = resp.json()
            pleasure = data['pad_state']['pleasure']
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"   PAD State: {data['pad_state']}")
            
            if pleasure < 0:
                print("✅ Emotional Reaction Verified (Pleasure dropped)")
            else:
                print(f"⚠️ Warning: Pleasure did not drop as expected ({pleasure})")
        except Exception as e:
            print(f"❌ Emotional Test Failed: {e}")

        # 4. Emotional State Test (Happy)
        print("\n4️⃣  Testing Emotional Reactivity (Happiness)...")
        try:
            payload = {"content": "Actually, I just got great news! I'm happy now!"}
            resp = await client.post("/api/v1/chat", json=payload)
            data = resp.json()
            pleasure = data['pad_state']['pleasure']
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"   PAD State: {data['pad_state']}")
            
            if pleasure > -0.2: # Should recover
                print("✅ Emotional Recovery Verified")
            else:
                print(f"⚠️ Warning: Pleasure did not recover as expected ({pleasure})")
        except Exception as e:
            print(f"❌ Emotional Test Failed: {e}")

    print("\n✨ Verification Complete!")

if __name__ == "__main__":
    asyncio.run(run_verification())
