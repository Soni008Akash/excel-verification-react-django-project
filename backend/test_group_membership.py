"""
Check Django Channels group membership and message queues
"""
import redis
import json

def check_channel_groups():
    """Check Django Channels group membership details"""
    print("=" * 60)
    print("Checking Django Channels Groups")
    print("=" * 60)
    
    # Connect to Redis
    r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)
    
    # Find all group keys
    group_keys = r.keys('asgi:group:*')
    
    print(f"\n📋 Found {len(group_keys)} channel groups:")
    
    for group_key in group_keys:
        print(f"\n🔹 {group_key}")
        
        # Get group members (zset members)
        members = r.zrange(group_key, 0, -1, withscores=True)
        print(f"   Members ({len(members)}):")
        for member, score in members:
            print(f"     - {member} (score: {score})")
            
            # Check if there's a message queue for this channel
            channel_key = f"asgi:specific.{member}"
            if r.exists(channel_key):
                key_type = r.type(channel_key)
                print(f"       Has message queue: {channel_key} (type: {key_type})")
                
                if key_type == 'list':
                    length = r.llen(channel_key)
                    print(f"       Queue length: {length}")
                    
                    # Peek at messages without removing them
                    if length > 0:
                        messages = r.lrange(channel_key, 0, min(2, length-1))
                        print(f"       First messages:")
                        for msg in messages:
                            try:
                                msg_data = json.loads(msg)
                                print(f"         - Type: {msg_data.get('type', 'N/A')}")
                            except:
                                print(f"         - Raw: {msg[:50]}...")
    
    # Also check for any specific.* keys (channel message queues)
    print(f"\n\n🔍 Looking for channel message queues...")
    specific_keys = r.keys('asgi:specific.*')
    
    if specific_keys:
        print(f"Found {len(specific_keys)} channel message queues:")
        for key in specific_keys[:10]:
            key_type = r.type(key)
            print(f"  - {key} (type: {key_type})")
            if key_type == 'list':
                length = r.llen(key)
                print(f"    Length: {length}")
    else:
        print("No channel message queues found")

if __name__ == "__main__":
    check_channel_groups()
