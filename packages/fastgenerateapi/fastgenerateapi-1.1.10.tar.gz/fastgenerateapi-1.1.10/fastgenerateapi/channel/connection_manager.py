from typing import Dict

from starlette.websockets import WebSocket


class ConnectionManager:
    active_connections: Dict[str, WebSocket] = {}
    active_group_connections: Dict[str, Dict[str, WebSocket]] = {}

    @classmethod
    def add_connection(cls, user_id: str, websocket: WebSocket):
        cls.active_connections[user_id] = websocket

    @classmethod
    def del_connection(cls, user_id: str):
        if user_id in cls.active_connections:
            del cls.active_connections[user_id]

    @classmethod
    def add_group_connection(cls, group_id: str, user_id: str, connection: WebSocket):
        cls.active_group_connections.setdefault(group_id, {})[user_id] = connection

    @classmethod
    def del_group_connection(cls, group_id: str, user_id: str):
        if group_id in cls.active_group_connections:
            user_dict = cls.active_group_connections[group_id]
            if user_id in user_dict:
                del user_dict[user_id]
                if not user_dict:
                    del cls.active_group_connections[group_id]
