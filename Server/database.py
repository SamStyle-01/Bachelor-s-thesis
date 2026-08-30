import asyncio
from abc import ABC, abstractmethod

import pandas as pd
import psycopg
import select
from sqlalchemy import create_engine

from instructions import INSTRUCTIONS
from ml_searcher import CompressorSearcher


# Абстрактный класс подключения к базе данных. Обозначает интерфейс для работы БД.
class Database(ABC):
    @abstractmethod
    def reload(self):
        pass


# Подключение к базе данных PostgreSQL.
class PGDatabase(Database):
    def __init__(self, user, password, host, port, database, *args):
        self.DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(self.DATABASE_URL)

        self.tables = dict()
        for table in args:
            with self.engine.connect() as connection:
                self.tables[table] = pd.read_sql(table, con=self.engine)

    def reload(self):
        database = PGDatabase(
            "postgres", "ncs", "localhost", "5432",
            "compressor", "data"
        )
        table_names = [el for el in database.tables.keys()]
        self.tables = dict()
        for table in table_names:
            with self.engine.connect() as connection:
                self.tables[table] = pd.read_sql(table, con=self.engine)

    # Метод нужен для детекции аномалий в новых данных.
    def get_last_12(self, table_name: str):
        query = f"""
        SELECT *
        FROM {table_name}
        ORDER BY id DESC
        LIMIT 12
        """
        with self.engine.connect() as connection:
            df = pd.read_sql(query, connection)

        return df.iloc[::-1].reset_index(drop=True)


# Функция выполняется в отдельном потоке и слушает работу БД. При каждом пополнении БД проверяет новые строки на
# аномалии. Если выявлены, отправляется сообщение пользователю.
def listen_db(alarm, brain, loop, dbname, user, password, host, notify_db):
    conn = psycopg.connect(
        f"dbname={dbname} user={user} password={password} host={host}",
        autocommit=True
    )

    anomaly_searcher = CompressorSearcher()
    database = PGDatabase(user, password, host, "5432",
                          dbname, "data")

    conn.execute(f"LISTEN {notify_db};")

    # В БД реализован триггер, который и отправляет уведомления.
    while True:
        if select.select([conn], [], [], 10)[0]:
            for notify in conn.notifies():
                row_id = int(notify.payload)
                print("Новая строка:", row_id)
                df = database.get_last_12("data")
                is_anomaly = anomaly_searcher.verdict_anomaly(anomaly_searcher.detect_anomaly(df))
                if is_anomaly:
                    print("Обнаружена аномалия!")
                    brain.messages = [{"role": "system", "content": INSTRUCTIONS["info_dataset_1"]}]
                    asyncio.run_coroutine_threadsafe(
                        alarm.send_all(
                            brain.generate_response(INSTRUCTIONS["anomaly_alarm"].format(str(df.drop("id", axis=1))))
                        ), loop)
                    brain.reset_memory()
