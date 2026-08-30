import asyncio
import random
import re
import textwrap
import threading

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from playwright.async_api import async_playwright
from traitlets.config import Config

from brain import BrainAPI
from database import listen_db
from ears import EarsAPI
from ml_searcher import CompressorSearcher
from voice import VoiceAPI


# Связующий класс логики в приложении
class Logic:
    # Инициализация и подгрузка всех компонентов системы
    def __init__(self, alarm):
        # Распознавание речи
        self.ears = EarsAPI()
        # Генерация речи
        self.voice = VoiceAPI()
        # Детектор аномалий
        self.anomaly_searcher = CompressorSearcher()
        # Генерация случайного индекса файла, с которого начнётся генерация отчётов
        self.index_file = random.randint(100000, 900000000000)
        # Веб-сокет для рассылки уведомлений об аномалии
        self.alarm = alarm

        loop = asyncio.get_event_loop()
        # Запуск потока детекции аномалий
        listener_thread = threading.Thread(target=listen_db, args=(self.alarm, BrainAPI(), loop, "compressor",
                                                                   "postgres", "ncs", "localhost", "compressor_data"),
                                           daemon=True)
        listener_thread.start()

    # Извлечение всех результатов исполнения ячейки кода. Нужно для итеративной генерации, чтобы модель могла видеть
    # результаты выполнения своего кода и направлять работу в нужное русло. А также чтобы могла исправлять ошибки,
    # переписывая ячейки с кодом.
    @staticmethod
    def extract_outputs(cell):

        result = {
            "stdout": "",
            "result": "",
            "errors": []
        }

        for output in cell.outputs:

            if output.output_type == "stream":

                result["stdout"] += output.text

            elif output.output_type == "execute_result":

                result["result"] += (
                    output["data"]
                    .get("text/plain", "")
                )

            elif output.output_type == "error":

                result["errors"].append({
                    "type": output.ename,
                    "message": output.evalue,
                    "traceback": "\n".join(
                        output.traceback
                    )
                })

        return result

    # Один из ключевых методов работы программы. Генерирует PDF-файл с отчётом по запросу пользователя.
    async def generate_pdf_file(self, request):
        brain = BrainAPI()
        # Если запрос некорректный/содержит маты, то он признаётся негодным и возвращается пользователю с ошибкой.
        if brain.identify_nonsense(request):
            return "7658281"

        chat_text = None
        # Создаётся новый блокнот в Jupiter Notebook
        nb = nbformat.v4.new_notebook()
        client = NotebookClient(nb, kernel_name='python3')
        # Добавляются ячейку по умолчанию
        imports_cell = nbformat.v4.new_code_cell(textwrap.dedent("""
        import warnings
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd
        import numpy as np
        import scipy as sp
        warnings.filterwarnings(\'ignore\')
        import sys
        %matplotlib inline
        if not sys.warnoptions:
            import os
            import warnings
            warnings.simplefilter(\'ignore\')
            os.environ["PYTHONWARNINGS"] = "ignore" """))
        nb.cells.append(imports_cell)

        df_cell = nbformat.v4.new_code_cell(textwrap.dedent("""
        from database import PGDatabase
        
        df = PGDatabase(
        "postgres", "ncs", "localhost", "5432",
        "compressor", "data"
        ).tables["data"]
        df = df.drop("id", axis=1)"""))
        nb.cells.append(df_cell)

        # Делается первый запрос к модели. Модель напишет план, по которому будет проводить анализ. Этот ответ
        # отправится к пользователю в чат. Все последующие ответы будут внутри PDF-отчёта.
        reply = brain.parse_response(brain.generate_response(request))
        print(reply)
        # Исполняются первые ячейки по умолчанию.
        with client.setup_kernel():
            client.execute_cell(
                imports_cell,
                0
            )
            client.execute_cell(
                df_cell,
                1
            )
            # Запросы к модели будут отправляться до тех пор, пока она не обозначит, что анализ закончен.
            # Обозначением является знак |||not_yet. Как только обозначение не появится в очередном ответе,
            # запросы к модели автоматически прекратятся.
            stop_it = False
            while True:
                if "not_yet" not in str(reply) or len(reply) < 3:
                    stop_it = True
                    print("Остановка")

                # Очищаем ответ модели ото всех лишних тегов и символов.
                input_cell = reply[1].replace("|||", "")
                if input_cell is not None:
                    markers = ["code", "first", "text"]
                    for marker in markers:
                        input_cell = re.sub(rf'\n\b{re.escape(marker)}\b', '', input_cell)
                    input_cell = input_cell.strip()

                # Если это было первое отправленной сообщение модели.
                if reply[0] == "first":
                    chat_text = input_cell
                    reply = brain.parse_response(
                        brain.generate_response(
                            "Сообщение было отправлено в чат. Начинай анализ."
                        ))
                # Если модель вернула текст, а не код (формат Markdown).
                elif reply[0] == "text":
                    nb.cells.append(nbformat.v4.new_markdown_cell(input_cell))
                    if stop_it:
                        break
                    reply = brain.parse_response(
                        brain.generate_response(
                            "Текст добавлен в ячейку. Продолжай выполнять анализ, если ещё остались задачи."
                        ))
                # Если модель вернула код.
                elif reply[0] == "code":
                    nb.cells.append(nbformat.v4.new_code_cell(input_cell))
                    try:
                        client.execute_cell(
                            nb.cells[-1],
                            len(nb.cells) - 1
                        )
                    except Exception as e:
                        pass

                    if stop_it:
                        break

                    # Возвращаем модели результат выполнения кода, чтобы модель могла подкорректировать свой следующий шаг.
                    feedback = self.extract_outputs(nb.cells[-1])
                    reply = brain.parse_response(brain.generate_response(textwrap.dedent(f"""
                    Ты выполнил ячейку.
                    stdout:
                    {feedback['stdout']}
                    result:
                    {feedback['result']}
                    errors:
                    {feedback['errors']}
                    Если есть ошибка: исправь код.
                    Если ошибки нет: проанализируй результат и предложи следующую ячейку, если цели анализа ещё не достигнуты.
                    """)))
                    print(feedback)
                    if len(feedback["errors"]):
                        nb.cells.pop()
                        print("Удалена ячейка!!!")

                elif reply[0] == "tech":
                    nb.cells.append(nbformat.v4.new_code_cell(input_cell))
                    try:
                        client.execute_cell(
                            nb.cells[-1],
                            len(nb.cells) - 1
                        )
                    except Exception as e:
                        pass

                    if stop_it:
                        break
                    # Возвращаем модели результат выполнения разведывательного кода, чтобы модель могла
                    # подкорректировать свой следующий шаг.
                    feedback = self.extract_outputs(nb.cells[-1])
                    reply = brain.parse_response(brain.generate_response(textwrap.dedent(f"""
                    Ты выполнил ячейку.
                    stdout:
                    {feedback['stdout']}
                    result:
                    {feedback['result']}
                    errors:
                    {feedback['errors']}
                    Если есть ошибка: исправь код.
                    Если ошибки нет: проанализируй результат и предложи следующую ячейку, если цели анализа ещё не достигнуты.
                    """)))
                    print(feedback)
                    nb.cells.pop()
                print(reply)

        # Создаём файл Jupiter Notebook, куда положим полученный блокнот для дальнейшей конвертации.
        with open('executed_notebook.ipynb', 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)

        # Настраиваем работу конвертора из Jupiter Notebook в HTML-файл.
        c = Config()
        c.HTMLExporter.exclude_input = True
        c.HTMLExporter.exclude_input_prompt = True
        c.HTMLExporter.exclude_output_prompt = True
        try:
            c.HTMLExporter.exclude_mathjax = True
        except Exception:
            print("Выключи ерунду")

        html_exporter = HTMLExporter(config=c)
        html_data, _ = html_exporter.from_notebook_node(nb)

        reset_css = textwrap.dedent("""
        <style>
            html, body { margin: 0 !important; padding: 0 !important; width: 800px !important; min-height: auto !important; height: auto !important; overflow: hidden !important; }
            #notebook-container, .container { width: 800px !important; max-width: none !important; padding: 0 !important; margin: 0 !important; }
            .cell { margin: 0 !important; padding: 6px 0 !important; }
            .output_area, .rendered_html { margin: 0 !important; padding: 0 !important; }
            @page { margin: 0; size: 800px auto; }
            @media print { * { page-break-inside: avoid !important; page-break-before: avoid !important; page-break-after: avoid !important; } }
            img, svg, canvas, .output_png { max-width: 100% !important; height: auto !important; display: block !important; }
        </style>
        """)
        html_data = html_data.replace('</head>', f'{reset_css}</head>')

        # Запуск браузера
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            # Создаём страницу, где разместим версию блокнота без кода
            page = await browser.new_page()
            await page.set_content(html_data, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(1500)

            content_height = await page.evaluate(textwrap.dedent("""() => {
                const container = document.querySelector('#notebook-container') || document.body;
                const rect = container.getBoundingClientRect();
                return Math.ceil(rect.height);
            }"""))

            # Конвертация в PDF-файл
            await page.pdf(
                path=f"files/{self.index_file}.pdf",
                print_background=True,
                width='800px',
                height=f'{content_height}px',
                margin={'top': '20px', 'bottom': '10px', 'left': '10px', 'right': '10px'},
                scale=1.0
            )

            html_exporter = HTMLExporter()
            html_data, _ = html_exporter.from_notebook_node(nb)

            reset_css = textwrap.dedent("""
                    <style>
                        html, body { margin: 0 !important; padding: 0 !important; width: 800px !important; min-height: auto !important; height: auto !important; overflow: hidden !important; }
                        #notebook-container, .container { width: 800px !important; max-width: none !important; padding: 0 !important; margin: 0 !important; }
                        .cell { margin: 0 !important; padding: 6px 0 !important; }
                        .output_area, .rendered_html { margin: 0 !important; padding: 0 !important; }
                        @page { margin: 0; size: 800px auto; }
                        @media print { * { page-break-inside: avoid !important; page-break-before: avoid !important; page-break-after: avoid !important; } }
                        img, svg, canvas, .output_png { max-width: 100% !important; height: auto !important; display: block !important; }
                    </style>
                    """)
            html_data = html_data.replace('</head>', f'{reset_css}</head>')

            # Создаём страницу, где разместим версию блокнота с кодом
            page2 = await browser.new_page()
            await page2.set_content(html_data, wait_until="domcontentloaded", timeout=60000)
            await page2.wait_for_timeout(1500)

            content_height = await page2.evaluate(textwrap.dedent('''() => {
                        const container = document.querySelector('#notebook-container') || document.body;
                        const rect = container.getBoundingClientRect();
                        return Math.ceil(rect.height);
                    }'''))

            # Конвертация в PDF-файл
            await page2.pdf(
                path=f"files/{self.index_file}_2.pdf",
                print_background=True,
                width='800px',
                height=f'{content_height}px',
                margin={'top': '20px', 'bottom': '10px', 'left': '10px', 'right': '10px'},
                scale=1.0
            )
            await browser.close()

        # Увеличиваем индекс от начального на 1, чтобы не перезаписывать файлы
        self.index_file += 1
        return chat_text

    # Распознавание речи
    async def recognize_speech(self, audio_path):
        text = await self.ears.recognize(audio_path)
        print("Распознанный текст:", text)
        return text

    # Генерация речи
    async def make_speech(self, text, path="output_custom_voice.wav"):
        return await self.voice.generate(text, path)
