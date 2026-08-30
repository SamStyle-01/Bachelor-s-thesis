import asyncio

import uvicorn

# Схема LSTM-модели, чтобы программа корректно импортировала файл модели. Иначе ошибка.
from lstm_encoder import LSTMAutoencoder

# Скрипт запуска сервера
if __name__ == "__main__":
    # Устанавливает Proactor вместо стандартного Selector. Фикс для работы асинхронных операций. Нужно для
    # генерации PDF-файла в браузере.
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Запуск сервера
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        loop="asyncio"
    )
