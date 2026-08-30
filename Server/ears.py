import asyncio
import concurrent.futures
import json
import os
from abc import ABC, abstractmethod

import torch
import whisper
from dotenv import load_dotenv
from openai import AsyncOpenAI


# Абстрактный класс модели распознавания речи. Обозначает интерфейс для работы с моделью.
class Ears(ABC):
    @abstractmethod
    async def recognize(self, audio_path) -> str:
        pass


# Класс для работы с локальной малой моделью Whisper.
class EarsWhisper(Ears):
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = whisper.load_model("small").to(self.device)

    def _transcribe(self, audio_path):
        return self.whisper_model.transcribe(audio_path)["text"]

    async def recognize(self, audio_path):
        loop = asyncio.get_event_loop()

        result = await loop.run_in_executor(
            self.executor,
            self._transcribe,
            audio_path
        )
        return result


# Класс для работы с облачной моделью gpt-4o-transcribe.
class EarsAPI(Ears):
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('API_KEY_GENERAL')
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://polza.ai/api/v1")

    async def recognize(self, audio_path):
        with open(audio_path, "rb") as audio_file:
            transcription = await self.client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                response_format="text"
            )

            text = json.loads(transcription).get("text")
            return text


# Тестирование работы.
if __name__ == '__main__':
    async def main():
        ears = EarsWhisper()
        text1 = await ears.recognize("./tests/voice.mp3")
        print(text1)


    asyncio.run(main())
