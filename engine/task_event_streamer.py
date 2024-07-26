import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class TaskEventStreamConsumer(WebsocketConsumer):
    """Handles the websocket connection for communication between task and client."""

    def connect(self):
        self.task_id = self.scope["url_route"]["kwargs"]["pk"]
        async_to_sync(self.channel_layer.group_add)(self.task_id, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.task_id, self.channel_name)

    def receive(self, text_data, **kwargs):
        pass

    def event(self, event):
        self.send(text_data=json.dumps(event))

    def status_update(self, status):
        self.send(text_data=json.dumps(status))

    def user_message(self, msg):
        self.send(text_data=json.dumps(msg))

    def title_update(self, title):
        self.send(text_data=json.dumps(title))
