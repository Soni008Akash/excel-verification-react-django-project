"""
Test if Celery task can send messages through channel layer
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from celery import Celery
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time

def test_from_celery_context():
    """Test channel layer from Celery's perspective"""
    print("=" * 60)
    print("Testing Channel Layer from Celery Context")
    print("=" * 60)
    
    # Get channel layer
    channel_layer = get_channel_layer()
    
    if not channel_layer:
        print("❌ Channel layer is None!")
        return False
    
    print(f"✅ Channel layer: {type(channel_layer)}")
    print(f"   Config: {channel_layer}")
    print(f"   Hosts: {getattr(channel_layer, 'hosts', 'N/A')}")
    
    # Try to send a test message
    test_group = 'test_group_123'
    
    print(f"\n📤 Sending test message to group: {test_group}")
    
    try:
        async_to_sync(channel_layer.group_send)(
            test_group,
            {
                'type': 'test_message',
                'data': 'Hello from Celery test!',
                'timestamp': time.time()
            }
        )
        print("✅ Message sent successfully!")
        print(f"   Group: {test_group}")
        print(f"   Type: test_message")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_from_celery_context()
