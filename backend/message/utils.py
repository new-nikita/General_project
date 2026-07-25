from typing import Dict
from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        # dialog_id -> {user_id: websocket}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, dialog_id: int, user_id: int):
        await websocket.accept()

        if dialog_id not in self.active_connections:
            self.active_connections[dialog_id] = {}

        self.active_connections[dialog_id][user_id] = websocket

    def disconnect(self, dialog_id: int, user_id: int):

        if dialog_id in self.active_connections:

            self.active_connections[dialog_id].pop(user_id, None)

            if not self.active_connections[dialog_id]:
                del self.active_connections[dialog_id]

    async def broadcast(self, message, dialog_id: int, sender_id: int):
        """

        :param message:
        :param dialog_id: id диалога
        :param sender_id: id апонента диалога
        :return:
        """

        if dialog_id not in self.active_connections:
            return

        for user_id, ws in self.active_connections[dialog_id].items():
            is_sender = user_id == sender_id
            await ws.send_json(
                {
                    "type": "message",
                    "id": message.id,
                    "text": message.text,
                    "sender_id": message.sender_id,
                    "created_at": message.created_at.isoformat(),
                    "is_self": is_sender,
                    "is_read_by_me": is_sender,
                    "is_read_by_companion": False,
                }
            )

    async def broadcast_read(
        self,
        dialog_id: int,
        reader_id: int,
        up_to_message_id: int,
    ):
        if dialog_id not in self.active_connections:
            return

        for user_id, ws in self.active_connections[dialog_id].items():
            await ws.send_json(
                {
                    "type": "read",
                    "reader_id": reader_id,
                    "up_to_message_id": up_to_message_id,
                }
            )


manager = ConnectionManager()
