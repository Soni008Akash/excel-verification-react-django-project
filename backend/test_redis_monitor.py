"""
Monitor Redis channel layer activity in real-time
"""
import redis
import json
import time

def monitor_redis_channels():
    """Monitor Redis channels for Django Channels messages"""
    print("=" * 60)
    print("Monitoring Redis Channels")
    print("=" * 60)
    
    # Connect to Redis
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
    
    try:
        # Test connection
        r.ping()
        print("✅ Connected to Redis at localhost:6379")
    except Exception as e:
        print(f"❌ Cannot connect to Redis: {e}")
        return
    
    # Get all keys
    print("\n📋 Current Redis keys:")
    keys = r.keys('*')
    for key in keys[:20]:  # Show first 20 keys
        key_type = r.type(key)
        print(f"  - {key} (type: {key_type})")
    
    if len(keys) > 20:
        print(f"  ... and {len(keys) - 20} more keys")
    
    print(f"\n✅ Total keys in Redis: {len(keys)}")
    
    # Look for Django Channels keys
    print("\n🔍 Looking for Django Channels keys...")
    channel_keys = [k for k in keys if 'asgi' in k.lower() or 'channel' in k.lower()]
    
    if channel_keys:
        print(f"Found {len(channel_keys)} channel-related keys:")
        for key in channel_keys[:10]:
            print(f"  - {key}")
    else:
        print("No channel-related keys found")
    
    # Check specific patterns
    print("\n🔍 Checking for job_* group keys...")
    job_keys = [k for k in keys if 'job_' in k]
    if job_keys:
        print(f"Found {len(job_keys)} job-related keys:")
        for key in job_keys[:10]:
            key_type = r.type(key)
            print(f"  - {key} (type: {key_type})")
            if key_type == 'list':
                length = r.llen(key)
                print(f"    List length: {length}")
            elif key_type == 'string':
                value = r.get(key)
                print(f"    Value: {value[:100] if value else 'None'}...")
    else:
        print("No job-related keys found")

if __name__ == "__main__":
    monitor_redis_channels()
