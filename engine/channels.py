from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast(group: str, data: dict):
    """Broadcast an event to a group."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(group, data)
