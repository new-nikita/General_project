from idlelib.run import manage_socket
from typing import Dict

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        # Хранение активных соединений в виде dialogs: {dialog_id: {user_id: WebSocket}}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def get_or_create_dialog(self, user1_id: int, user2_id: int) -> int:
        """
        Создает уникальный ID чата

        :param user1_id: Инициатор диалога
        :param user2_id: Ответчик
        :return: ID чата
        """
        dialog_id = min(user1_id, user2_id) * 10**10 + max(user1_id, user2_id)
        if dialog_id not in self.active_connections:
            self.active_connections[dialog_id] = {}
        return dialog_id

    async def connect(
        self,
        websocket: WebSocket,
        dialog_id: int,
        current_user: int,
    ):
        """
        Устанавливает соединение с пользователем.
        websocket.accept() — подтверждает подключение.
        """
        await websocket.accept()
        if dialog_id not in self.active_connections:
            self.active_connections[dialog_id] = {}

        if current_user in self.active_connections[dialog_id]:
            old_ws = self.active_connections[dialog_id].pop(current_user)
            try:
                await old_ws.close()
            except:
                pass

        self.active_connections[dialog_id][current_user] = websocket

    def disconnect(self, room_id: int, user_id: int):
        """
        Закрывает соединение и удаляет его из списка активных подключений.
        Если в комнате больше нет пользователей, удаляет комнату.
        """
        if (
            room_id in self.active_connections
            and user_id in self.active_connections[room_id]
        ):
            del self.active_connections[room_id][user_id]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message, room_id: int, sender_id: int):
        """
        Рассылает сообщение всем пользователям в комнате.
        """
        if room_id in self.active_connections:
            for user_id, connection in self.active_connections[room_id].items():
                message_with_class = {
                    "text": message,
                    "sender_id": message.sender_id,
                    "created_at": message.created_at.isoformat(),
                    "is_self": user_id == sender_id,
                }
                await connection.send_json(message_with_class)


manager = ConnectionManager()
