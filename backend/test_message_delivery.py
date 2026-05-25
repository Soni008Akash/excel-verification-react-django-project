"""
Test sending a message to a channel group and verify it reaches Redis
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

def test_message_delivery():
    """Test if messages sent via group_send actually reach Redis queues"""
    print("=" * 60)
    print("Testing Message Delivery to Redis")
    print("=" * 60)
    
    # Connect to Redis
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
    
    # Get existing groups
    group_keys = r.keys('asgi:group:*')
    print(f"\n📋 Existing groups: {len(group_keys)}")
    
    if not group_keys:
        print("❌ No groups found in Redis")
        return
    
    # Use the first group for testing
    test_group_key = group_keys[0]
    test_group_name = test_group_key.decode('utf-8') if isinstance(test_group_key, bytes) else test_group_key
    test_group_name = test_group_name.replace('asgi:group:', '')
    
    print(f"🎯 Testing with group: {test_group_name}")
    
    # Get group members
    members = r.zrange(test_group_key, 0, -1)
    print(f"   Members: {len(members)}")
    for member in members:
        member_str = member.decode('utf-8') if isinstance(member, bytes) else member
        print(f"     - {member_str}")
        # Check for existing queue
        queue_key = f"asgi:{member_str}"
        if r.exists(queue_key):
            print(f"       ✅ Queue exists: {queue_key}")
        else:
            print(f"       ❌ No queue: {queue_key}")
    
    # Get channel layer
    channel_layer = get_channel_layer()
    
    # Send a test message
    print(f"\n📤 Sending test message to group: {test_group_name}")
    
    try:
        async_to_sync(channel_layer.group_send)(
            test_group_name,
            {
                'type': 'job_progress',
                'job_id': 'test-job-123',
                'status': 'processing',
                'progress': 50,
                'current_step': 'TEST MESSAGE',
                'timestamp': time.time()
            }
        )
        print("✅ Message sent via channel_layer.group_send()")
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # IMMEDIATELY check Redis for the message
    print(f"\n🔍 Checking Redis for message queues...")
    time.sleep(0.1)  # Brief pause to let message propagate
    
    # Check for specific channel queues
    for member in members:
        member_str = member.decode('utf-8') if isinstance(member, bytes) else member
        queue_key = f"asgi:{member_str}"
        
        if r.exists(queue_key):
            key_type = r.type(queue_key)
            print(f"\n✅ Found queue: {queue_key} (type: {key_type})")
            
            if key_type == 'list':
                length = r.llen(queue_key)
                print(f"   Queue length: {length}")
                
                if length > 0:
                    # Peek at messages
                    messages = r.lrange(queue_key, 0, -1)
                    print(f"   Messages in queue:")
                    for i, msg in enumerate(messages):
                        try:
                            msg_str = msg.decode('utf-8') if isinstance(msg, bytes) else msg
                            msg_data = json.loads(msg_str)
                            print(f"     [{i}] Type: {msg_data.get('type')}, Progress: {msg_data.get('progress')}")
                        except Exception as e:
                            print(f"     [{i}] Raw: {str(msg)[:100]}")
                else:
                    print(f"   Queue is empty (message already consumed?)")
        else:
            print(f"\n❌ No queue found for: {queue_key}")
    
    print(f"\n\n🔍 Checking ALL asgi:* keys in Redis...")
    asgi_keys = r.keys('asgi:*')
    print(f"Found {len(asgi_keys)} asgi keys:")
    for key in asgi_keys:
        key_str = key.decode('utf-8') if isinstance(key, bytes) else key
        key_type = r.type(key)
        print(f"  - {key_str} (type: {key_type})")

if __name__ == "__main__":
    test_message_delivery()
