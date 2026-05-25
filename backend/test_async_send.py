"""
Test channel layer with proper async context
"""
import os
import django
import redis
import asyncio
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from channels.layers import get_channel_layer

async def test_async_send():
    """Test sending with proper async context"""
    print("=" * 60)
    print("Testing Channel Layer in Async Context")
    print("=" * 60)
    
    # Connect to Redis
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
    
    # Get channel layer
    channel_layer = get_channel_layer()
    
    print(f"✅ Channel layer: {type(channel_layer)}")
    
    # Get existing group
    group_keys = r.keys('asgi:group:*')
    if not group_keys:
        print("❌ No groups found")
        return
    
    test_group_key = group_keys[0]
    test_group_name = test_group_key.decode('utf-8') if isinstance(test_group_key, bytes) else test_group_key
    test_group_name = test_group_name.replace('asgi:group:', '')
    
    print(f"\n🎯 Testing with group: {test_group_name}")
    
    # Get members
    members = r.zrange(test_group_key, 0, -1)
    print(f"   Members: {len(members)}")
    
    # Send message using ASYNC method
    print(f"\n📤 Sending message via await channel_layer.group_send()...")
    try:
        await channel_layer.group_send(
            test_group_name,
            {
                'type': 'job_progress',
                'progress': 88,
                'message': 'ASYNC TEST MESSAGE'
            }
        )
        print("✅ Message sent successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Wait a moment
    await asyncio.sleep(0.2)
    
    # Check Redis
    print(f"\n🔍 Checking Redis for message queues...")
    
    for member in members:
        member_str = member.decode('utf-8') if isinstance(member, bytes) else member
        queue_key = f"asgi:{member_str}"
        
        print(f"\n   Checking: {queue_key}")
        if r.exists(queue_key):
            print(f"   ✅ Queue EXISTS!")
            key_type = r.type(queue_key)
            print(f"   Type: {key_type}")
            
            if key_type == 'list':
                length = r.llen(queue_key)
                print(f"   Length: {length}")
                
                if length > 0:
                    messages = r.lrange(queue_key, 0, -1)
                    for i, msg in enumerate(messages):
                        try:
                            msg_str = msg.decode('utf-8') if isinstance(msg, bytes) else msg
                            msg_data = json.loads(msg_str)
                            print(f"   Message {i}: Type={msg_data.get('type')}, Progress={msg_data.get('progress')}")
                        except:
                            print(f"   Message {i}: {str(msg)[:100]}")
        else:
            print(f"   ❌ Queue does NOT exist")
    
    # Show all asgi keys
    print(f"\n📋 All asgi:* keys in Redis:")
    asgi_keys = r.keys('asgi:*')
    for key in asgi_keys:
        key_str = key.decode('utf-8') if isinstance(key, bytes) else key
        key_type = r.type(key)
        print(f"     - {key_str} (type: {key_type})")

if __name__ == "__main__":
    asyncio.run(test_async_send())
