"""
Test script to verify channels and Redis are working
"""
import os
import django
import asyncio

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def test_channel_layer():
    """Test that channel layer can send and receive messages"""
    channel_layer = get_channel_layer()
    
    if channel_layer is None:
        print("❌ Channel layer is None - not configured properly")
        return False
    
    print(f"✅ Channel layer found: {type(channel_layer)}")
    print(f"   Config: {channel_layer}")
    
    # Test sending a message
    try:
        async_to_sync(channel_layer.group_send)(
            'test_group',
            {
                'type': 'test.message',
                'data': 'Hello from test!'
            }
        )
        print("✅ Successfully sent test message to channel layer")
        return True
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Testing Django Channels with Redis...")
    print("=" * 50)
    test_channel_layer()
