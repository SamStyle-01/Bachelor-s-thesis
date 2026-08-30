import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from database import PGDatabase


# Не является полноценной частью сервера. Генерирует аномалии и добавляет в датасет. Нужен для тестирования.
class SyntheticCompressorGenerator:

    def __init__(self):
        self.database = PGDatabase(
            "postgres",
            "ncs",
            "localhost",
            "5432",
            "compressor"
        )

        self.current_time = datetime(
            2023,
            1,
            1,
            0,
            10
        )

    def generate(self):
        TI8500 = np.random.normal(40, 1)
        TI8590 = np.random.normal(42, 1)
        TI8591 = np.random.normal(45, 1)
        TI8592 = np.random.normal(50, 1)
        TI8593 = np.random.normal(55, 1)
        TI8501 = np.random.normal(80, 2)
        PI8500 = np.random.normal(
            1.6,
            0.05
        )
        PI8501 = np.random.normal(
            2.75,
            0.07
        )
        ZI8583 = np.random.normal(
            0.18,
            0.01
        )
        ZI8584 = np.random.normal(
            0.19,
            0.01
        )
        VI8582 = np.random.normal(
            0.5,
            0.05
        )
        VI8581 = np.random.normal(
            1.7,
            0.1
        )
        compression_ratio = (
                PI8501 /
                PI8500
        )
        delta_temp = (
                TI8501 -
                TI8500
        )
        rod_diff = abs(
            ZI8583 -
            ZI8584
        )
        vibration_diff = abs(
            VI8582 -
            VI8581
        )
        row = {
            "datetime": self.current_time,
            "TI8500.PV": TI8500,
            "TI8590.PV": TI8590,
            "TI8591.PV": TI8591,
            "TI8592.PV": TI8592,
            "TI8593.PV": TI8593,
            "TI8501.PV": TI8501,
            "PI8500.PV": PI8500,
            "PI8501.PV":
                PI8501,
            "ZI8583.PV":
                ZI8583,
            "ZI8584.PV":
                ZI8584,
            "VI8582.PV":
                VI8582,
            "VI8581.PV":
                VI8581,
            "compression_ratio":
                compression_ratio,
            "delta_temp":
                delta_temp,
            "rod_diff":
                rod_diff,
            "vibration_diff":
                vibration_diff,
            "discharge_valve_diff":
                np.random.random(),
            "suction_valve_diff":
                np.random.random(),
            "TI8501_diff":
                np.random.normal(0, 1),
            "PI8501_diff":
                np.random.normal(0, 0.05),
            "VI8582_diff":
                np.random.normal(0, 0.05),
            "VI8581_diff":
                np.random.normal(0, 0.1),
            "TI8501_mean":
                TI8501,
            "TI8501_std":
                np.random.random(),
            "PI8501_mean":
                PI8501,
            "PI8501_std":
                np.random.random()
        }

        self.current_time += timedelta(
            minutes=10
        )
        return row

    def insert(self):
        row = self.generate()
        df = pd.DataFrame([row])
        df.to_sql(
            "data",
            self.database.engine,
            if_exists="append",
            index=False
        )
        print(
            "Добавлено:",
            row["datetime"]
        )


# Тестирование работы.
if __name__ == "__main__":
    generator = SyntheticCompressorGenerator()
    while True:
        generator.insert()
        time.sleep(20)
