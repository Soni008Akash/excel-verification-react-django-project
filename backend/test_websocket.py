"""
Test WebSocket connection directly
"""
import asyncio
import websockets
import json

async def test_websocket():
    # Test with a sample job ID
    job_id = "4f4724e3-8505-4ab5-8f9e-eb02c5ccd666"
    uri = f"ws://localhost:8000/ws/job/{job_id}/"
    
    print(f"Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")
            
            # Wait for connection_established message
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"Received: {message}")
            data = json.loads(message)
            print(f"Message type: {data.get('type')}")
            
            # Send a ping
            await websocket.send(json.dumps({"type": "ping", "timestamp": 12345}))
            print("Sent ping")
            
            # Wait for pong
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"Received: {message}")
            
            # Wait a bit to see if any progress messages come through
            print("Waiting for progress messages (10 seconds)...")
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    print(f"Received: {message}")
            except asyncio.TimeoutError:
                print("No more messages received (timeout)")
            
            print("✅ Test completed successfully")
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Connection rejected with status: {e.status_code}")
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except ConnectionRefusedError:
        print("❌ Connection refused - is Daphne running?")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())
