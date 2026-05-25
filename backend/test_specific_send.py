"""
Test if channel layer can send to specific channels
"""
import os
import django
import redis
import json
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def test_specific_channel():
    """Test sending to a specific channel (not a group)"""
    print("=" * 60)
    print("Testing Specific Channel Send")
    print("=" * 60)
    
    # Connect to Redis
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
    
    # Get channel layer
    channel_layer = get_channel_layer()
    
    print(f"✅ Channel layer: {type(channel_layer)}")
    # print(f"   Config: {channel_layer.config}")
    
    # Get existing group members to find a real channel name
    group_keys = r.keys('asgi:group:*')
    if group_keys:
        test_group_key = group_keys[0]
        members = r.zrange(test_group_key, 0, 0)
        if members:
            channel_name = members[0].decode('utf-8') if isinstance(members[0], bytes) else members[0]
            # Remove the "specific." prefix if present
            if channel_name.startswith('specific.'):
                channel_name = channel_name[9:]  # Remove "specific."
            
            print(f"\n🎯 Testing with channel: {channel_name}")
            
            # Send directly to this channel
            print(f"\n📤 Sending message to channel...")
            try:
                async_to_sync(channel_layer.send)(
                    channel_name,
                    {
                        'type': 'job.progress',
                        'progress': 75,
                        'message': 'Direct channel test'
                    }
                )
                print("✅ Message sent via channel_layer.send()")
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Check Redis
            print(f"\n🔍 Checking Redis...")
            time.sleep(0.1)
            
            # Look for the message queue
            queue_key = f"asgi:{channel_name}"
            print(f"   Looking for: {queue_key}")
            
            if r.exists(queue_key):
                print(f"   ✅ Queue exists!")
                key_type = r.type(queue_key)
                print(f"   Type: {key_type}")
                
                if key_type == 'list':
                    length = r.llen(queue_key)
                    print(f"   Length: {length}")
                    
                    if length > 0:
                        messages = r.lrange(queue_key, 0, -1)
                        for i, msg in enumerate(messages):
                            print(f"   Message {i}: {msg[:100]}")
            else:
                print(f"   ❌ Queue does not exist")
            
            # Show all asgi keys
            print(f"\n📋 All asgi:* keys:")
            asgi_keys = r.keys('asgi:*')
            for key in asgi_keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                print(f"     - {key_str}")
    else:
        print("❌ No groups found to test with")

if __name__ == "__main__":
    test_specific_channel()
