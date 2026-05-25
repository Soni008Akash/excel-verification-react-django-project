"""
WebSocket consumers for real-time job progress updates
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class JobProgressConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for job progress updates
    Clients connect to ws://localhost:8000/ws/job/{job_id}/
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.job_id = self.scope['url_route']['kwargs']['job_id']  # type: ignore[index]
        self.job_group_name = f'job_{self.job_id}'
        
        print(f"[Consumer] WebSocket connecting for job: {self.job_id}")
        print(f"[Consumer] Joining group: {self.job_group_name}")
        
        # Join job-specific channel group
        await self.channel_layer.group_add(
            self.job_group_name,
            self.channel_name
        )
        
        print(f"[Consumer] Added to channel group successfully")
        
        await self.accept()
        
        print(f"[Consumer] Connection accepted")
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to job {self.job_id}',
            'job_id': self.job_id
        }))
        
        print(f"[Consumer] Confirmation message sent")
    
    async def disconnect(self, code):
        """Handle WebSocket disconnection"""
        print(f"[Consumer] WebSocket disconnecting with code: {code}")
        # Leave job-specific channel group
        await self.channel_layer.group_discard(
            self.job_group_name,
            self.channel_name
        )
        print(f"[Consumer] Removed from channel group")
    
    async def receive(self, text_data=None, bytes_data=None):
        """Handle messages from WebSocket (optional - for ping/pong)"""
        try:
            if text_data:
                data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
        except json.JSONDecodeError:
            pass
    
    # Handler for job.progress messages sent from Celery
    async def job_progress(self, event):
        """
        Receive job progress update from channel layer and send to WebSocket
        """
        print(f"[Consumer] Received progress event: {event.get('progress')}% - {event.get('current_step')}")
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            'job_id': event['job_id'],
            'status': event['status'],
            'progress': event['progress'],
            'current_step': event.get('current_step', ''),
            'total_rows': event.get('total_rows', 0),
            'valid_rows': event.get('valid_rows', 0),
            'invalid_rows': event.get('invalid_rows', 0),
            'error_count': event.get('error_count', 0),
            'error_message': event.get('error_message'),
            'timestamp': event.get('timestamp')
        }))
    
    # Handler for job.completed messages
    async def job_completed(self, event):
        """
        Receive job completion message from channel layer and send to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'job_completed',
            'job_id': event['job_id'],
            'status': 'completed',
            'progress': 100,
            'total_rows': event.get('total_rows', 0),
            'valid_rows': event.get('valid_rows', 0),
            'invalid_rows': event.get('invalid_rows', 0),
            'error_count': event.get('error_count', 0),
            'status_message': event.get('status_message', ''),
            'timestamp': event.get('timestamp')
        }))
    
    # Handler for job.failed messages
    async def job_failed(self, event):
        """
        Receive job failure message from channel layer and send to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'job_failed',
            'job_id': event['job_id'],
            'status': 'failed',
            'error_message': event.get('error_message', 'Unknown error'),
            'timestamp': event.get('timestamp')
        }))
