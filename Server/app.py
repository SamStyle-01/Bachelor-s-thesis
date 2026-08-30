import os

from fastapi import FastAPI, File, Form, UploadFile, WebSocket
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from anomaly_alarms import WSManager
from logic import Logic

# Сервер
app = FastAPI()
# Веб-сокет
alarm = WSManager()
# Центральный объект логики программы
logic = Logic(alarm)


@app.websocket("/ws/anomalies")
async def ws_anomalies(ws: WebSocket):
    """
    Уведомления о новых аномалиях
    """
    await alarm.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except:
        alarm.disconnect(ws)


class MessageRequest(BaseModel):
    text: str
    voice: str


@app.post("/send-message")
async def handle_message(request: MessageRequest):
    """
    Обработка текстовых запросов пользователя
    """
    user_text = request.text
    # Если у пользователя активирована функция озвучивания ответа, то генерируем речь
    voice = (request.voice == "ON")

    # Вызываем функцию генерации PDF-файла
    response = await logic.generate_pdf_file(user_text)

    if voice:
        await logic.make_speech(response.strip(), f"files/{logic.index_file - 1}.mp3")

    return JSONResponse({
        # Код 2 значит, что ответное сообщение не содержит текстовую расшифровку запроса пользователя,
        # поскольку запрос и так был текстовым
        "code": "1",
        "response_text": response.strip(),
        "file_name": f"{logic.index_file - 1}.pdf",
        "audio_name": f"{logic.index_file - 1}.mp3" if voice else "None"
    })


# Директория с загружаемым голосовым запросом
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...), voice: str = Form(...)):
    """
    Обработка голосовых запросов пользователя
    """
    # Если у пользователя активирована функция озвучивания ответа, то генерируем речь
    voice = (voice == "ON")

    file_location = os.path.join(UPLOAD_DIR, str(logic.index_file - 1) + ".mp3")
    with open(file_location, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Распознаём голосовой запрос пользователя
    request = await logic.recognize_speech(file_location)
    # Вызываем функцию генерации PDF-файла
    response = await logic.generate_pdf_file(request)

    if voice:
        await logic.make_speech(response.strip(), f"files/{logic.index_file - 1}.mp3")

    return JSONResponse({
        # Код 2 значит, что ответное сообщение содержит текстовую расшифровку запроса пользователя
        "code": "2",
        "user_request": request.strip(),
        "response_text": response.strip(),
        "file_name": f"{logic.index_file - 1}.pdf",
        "audio_name": f"{logic.index_file - 1}.mp3" if voice else "None"
    })


@app.get("/get-file/{file_name}")
async def get_file(file_name: str):
    """
    Отправление PDF-файлов с анализом и аудиоответа, если был создан
    """
    file_path = os.path.join("files", file_name)

    if not os.path.exists(file_path):
        return {"error": "Файл не найден"}

    media_type = None
    if file_name.endswith('.mp3'):
        media_type = "audio/mpeg"
    elif file_name.endswith('.wav'):
        media_type = "audio/wav"
    elif file_name.endswith('.pdf'):
        media_type = "application/pdf"

    return FileResponse(
        "files/" + file_name,
        media_type=media_type,
        filename=file_name
    )
