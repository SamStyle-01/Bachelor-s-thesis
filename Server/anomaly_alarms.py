from fastapi import WebSocket


# Класс соединения сервера и клиента по веб-сокету. Уведомляет клиента о новых аномалиях.
class WSManager:
    def __init__(self):
        self.clients = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.append(ws)

    def disconnect(self, ws: WebSocket):
        self.clients.remove(ws)

    async def send_all(self, msg: str):
        for c in self.clients:
            await c.send_text(msg)
