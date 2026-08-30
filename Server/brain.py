import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from openai import OpenAI

from instructions import INSTRUCTIONS


# Абстрактный класс LLM-модели. Обозначает интерфейс для работы с моделью.
class Brain(ABC):
    @abstractmethod
    def generate_response(self, message) -> str:
        pass

    @abstractmethod
    def identify_nonsense(self, message) -> bool:
        pass

    @staticmethod
    def parse_response(response: str):
        return response.split("|||")


# Создаём системный промпт, который будет отправлен модели. Содержит:
# Инструкцию по созданию структуры ответа, информацию по датасету и первые всегда исполняемые ячейки в ответе.
SYSTEM_PROMPT = INSTRUCTIONS["system_prompt"] \
                + "\n" + INSTRUCTIONS["info_dataset_1"] + "\n" + INSTRUCTIONS["first_cells"]


# Используется облачная модель google/gemini-3.5-flash.
class BrainAPI(Brain):
    load_dotenv()
    # Загружаем API-ключ
    api_key = os.getenv('API_KEY_GENERAL')
    client = OpenAI(api_key=api_key, base_url="https://polza.ai/api/v1")

    def __init__(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    def generate_response(self, message):
        self.messages.append({"role": "user", "content": message})

        response = BrainAPI.client.chat.completions.create(
            model="google/gemini-3.5-flash",
            messages=self.messages
        )
        self.messages.append({"role": "assistant", "content": str(response.choices[0].message.content)})
        return response.choices[0].message.content

    # Сбрасывает память модели.
    def reset_memory(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Находит некорректные сообщения. Если некорректное сообщение, то оно не обрабатывается, а возвращается
    # ошибкой клиенту.
    def identify_nonsense(self, message) -> bool:
        response = BrainAPI.client.chat.completions.create(
            model="google/gemini-3.5-flash",
            messages=[{"role": "system",
                       "content": "If the message contains profanity or is meaningless and does not relate to the task, "
                                  "then write the code 7658281 in response. If the message is appropriate, then write "
                                  "the code 6161774 in response."},
                      {"role": "user", "content": message}]
        )
        return True if "7658281" in response.choices[0].message.content else False


# Используется локальная модель google/gemma-4-12b-qat.
class BrainLocal(Brain):
    client = OpenAI(api_key="lm-studio", base_url="http://localhost:1234/v1")

    def __init__(self):
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\nDon't do anything that goes beyond the request."}]

    def generate_response(self, message):
        self.messages.append({"role": "user", "content": message})

        response = BrainLocal.client.chat.completions.create(
            model="google/gemma-4-12b-qat",
            messages=self.messages
        )
        self.messages.append({"role": "assistant", "content": str(response.choices[0].message.content)})
        return response.choices[0].message.content

    # Сбрасывает память модели.
    def reset_memory(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Находит некорректные сообщения. Если некорректное сообщение, то оно не обрабатывается, а возвращается
    # ошибкой клиенту.
    def identify_nonsense(self, message) -> bool:
        response = BrainLocal.client.chat.completions.create(
            model="google/gemma-4-12b-qat",
            messages=[{"role": "system",
                       "content": "If the message contains profanity or is meaningless and does not relate to the task, "
                                  "then write the code 7658281 in response. If the message is appropriate, then write "
                                  "the code 6161774 in response."},
                      {"role": "user", "content": message}]
        )
        return True if "7658281" in response.choices[0].message.content else False


# Тестирование работы.
if __name__ == "__main__":
    brain = BrainLocal()
    print(brain.generate_response(
        "Сделай график работы компрессора за время с 01.01.2021 по 05.05.2021. И второй график - степень сжатия в компрессоре за период с 05.05.2021 по 15.05.2021."
    ))
