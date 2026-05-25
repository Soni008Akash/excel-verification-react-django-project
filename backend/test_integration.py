"""
Complete integration test: Upload, validate, and monitor via WebSocket
"""
import asyncio
import websockets
import json
import requests
from pathlib import Path

API_BASE = "http://localhost:8000/api/excel-uploads"
WS_BASE = "ws://localhost:8000/ws/job"

async def monitor_job(job_id):
    """Monitor a job via WebSocket"""
    uri = f"{WS_BASE}/{job_id}/"
    
    print(f"\n[WebSocket] Connecting to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("[WebSocket] ✅ Connected!")
            
            # Wait for messages
            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'connection_established':
                    print(f"[WebSocket] Connection confirmed for job {data.get('job_id')}")
                
                elif msg_type == 'progress_update':
                    progress = data.get('progress', 0)
                    step = data.get('current_step', '')
                    print(f"[WebSocket] Progress: {progress}% - {step}")
                
                elif msg_type == 'job_completed':
                    print(f"[WebSocket] ✅ Job completed!")
                    print(f"  Total: {data.get('total_rows')}")
                    print(f"  Valid: {data.get('valid_rows')}")
                    print(f"  Invalid: {data.get('invalid_rows')}")
                    break
                
                elif msg_type == 'job_failed':
                    print(f"[WebSocket] ❌ Job failed: {data.get('error_message')}")
                    break
                
                else:
                    print(f"[WebSocket] Received: {msg_type}")
                    
    except Exception as e:
        print(f"[WebSocket] ❌ Error: {e}")

def start_validation_workflow():
    """Upload file, map headers, and start validation"""
    
    # 1. Upload file
    file_path = r"C:\Users\User\OneDrive - Premier Sales Promotions\Desktop\SaleUpload Excel\Bulk Achievements Target Based.xlsx"
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return None
    
    print(f"[API] Uploading file...")
    with open(file_path, 'rb') as f:
        response = requests.post(
            f"{API_BASE}/upload/",
            files={'file': f}
        )
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return None
    
    upload_data = response.json()
    print(f"[DEBUG] Upload response: {upload_data}")
    file_id = upload_data.get('id') or upload_data.get('file_id')
    if not file_id:
        print(f"❌ No ID in upload response")
        return None
    headers = upload_data.get('headers', [])
    print(f"[API] ✅ File uploaded with ID: {file_id}")
    print(f"[API] Headers: {', '.join([h['original'] if isinstance(h, dict) else h for h in headers])}")
    
    # 2. Map headers (simple mapping - all to themselves with 'none' validation)
    print(f"\n[API] Mapping headers...")
    header_names = [h['original'] if isinstance(h, dict) else h for h in headers]
    mappings = {
        'mappings': [
            {'source_header': h, 'target_field': h, 'validation_rule': 'none'}
            for h in header_names
        ],
        'validation_options': {
            'hash_fields': []
        }
    }
    
    response = requests.post(
        f"{API_BASE}/{file_id}/map_headers/",
        json=mappings
    )
    
    if response.status_code != 200:
        print(f"❌ Mapping failed: {response.status_code}")
        print(response.text)
        return None
    
    print(f"[API] ✅ Headers mapped")
    
    # 3. Start validation
    print(f"\n[API] Starting validation...")
    response = requests.post(f"{API_BASE}/{file_id}/validate/")
    
    if response.status_code != 202:
        print(f"❌ Validation start failed: {response.status_code}")
        print(response.text)
        return None
    
    result = response.json()
    job_id = result['job_id']
    print(f"[API] ✅ Validation started with job_id: {job_id}")
    
    return job_id

def main():
    print("=" * 60)
    print("WebSocket Integration Test")
    print("=" * 60)
    
    # Start validation workflow
    job_id = start_validation_workflow()
    
    if not job_id:
        print("\n❌ Failed to start validation workflow")
        return
    
    print(f"\n" + "=" * 60)
    print(f"Monitoring job: {job_id}")
    print("=" * 60)
    
    # Monitor via WebSocket
    asyncio.run(monitor_job(job_id))
    
    print("\n✅ Test completed")

if __name__ == "__main__":
    main()
