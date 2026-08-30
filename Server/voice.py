import asyncio
import base64
import concurrent.futures
import os
from abc import ABC, abstractmethod

import soundfile as sf
import torch
from dotenv import load_dotenv
from openai import AsyncOpenAI
from qwen_tts import Qwen3TTSModel


# Абстрактный класс модели генерации речи. Обозначает интерфейс для работы с моделью.
class Voice(ABC):
    @abstractmethod
    async def generate(self, text, filename=None) -> None:
        pass


# Класс для работы с локальной малой моделью Qwen3TTS.
class VoiceQwen3TTS(Voice):
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        self.model = Qwen3TTSModel.from_pretrained(
            "Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            device_map="cuda:0",
            dtype=torch.bfloat16,
            attn_implementation="eager",
        )

    def _generate_sync(self, text, filename):
        # Вся тяжелая работа здесь
        with torch.inference_mode():
            wavs, sr = self.model.generate_voice_design(
                text=text,
                language="Russian",
                speaker="Serena",
                instruct="A measured, confident voice."
            )
        sf.write(filename, wavs[0], sr)
        return filename

    async def generate(self, text, filename="output_custom_voice.wav"):
        loop = asyncio.get_event_loop()

        result = await loop.run_in_executor(
            self.executor,
            self._generate_sync,
            text,
            filename
        )
        print("Saved:", result)


# Класс для работы с облачной моделью gpt-4o-mini-tts.
class VoiceAPI:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('API_KEY_GENERAL')

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://polza.ai/api/v1"
        )

    # Ответ приходит в виде json. Приходится его парсить и дешифровать поле audio из BASE64.
    async def generate(self, text, filename="tests/output.mp3"):
        response = await self.client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="onyx",
            input=text,
            instructions="Говори чётко и естественно. С русским акцентом."
        )

        data = response

        if hasattr(response, "model_dump"):
            data = response.model_dump()

        elif hasattr(response, "json"):
            try:
                data = response.json()
            except:
                pass

        audio_b64 = data.get("audio")

        if not audio_b64:
            raise ValueError("No audio field in response")

        audio_bytes = base64.b64decode(audio_b64)

        with open(filename, "wb") as f:
            f.write(audio_bytes)

        print("Saved:", filename)


# Тестирование работы.
if __name__ == '__main__':
    async def main():
        voice = VoiceAPI()
        text = """
            Компрессор — это устройство, предназначенное для сжатия воздуха или другого газа и подачи его под давлением.
            Он широко используется в промышленности, строительстве и даже в быту.
            Принцип работы компрессора основан на уменьшении объёма газа, что приводит к повышению его давления.
            Существует множество типов компрессоров, включая поршневые, винтовые и центробежные,
            каждый из которых имеет свои особенности и области применения.
            """

        await voice.generate(text, filename="tests/output1.mp3")


    asyncio.run(main())
