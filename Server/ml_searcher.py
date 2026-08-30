import pickle
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
import torch
from joblib import load


# Абстрактный класс детектора аномалий. Обозначает интерфейс для работы с его подклассами.
class MLSearcher(ABC):
    @abstractmethod
    def detect_anomaly(self, data: pd.DataFrame):
        pass


# Детектор, подготовленный для работы с датасетом по компрессору.
class CompressorSearcher(MLSearcher):
    # Загрузка и подготовка всех предобученных моделей из файлов.
    def __init__(self):
        # Скейлер, подготовленный для ML-моделей.
        self.robust_scaler = load('detecting_anomalies_models/robust_scaler.joblib')

        # Модель Isolation Forest от Scikit-Learn
        self.iso_forest = load('detecting_anomalies_models/if_model.joblib')
        # Модель EllipticEnvelope от Scikit-Learn
        self.ee_model = load('detecting_anomalies_models/ee_model.joblib')
        # Модель One-Class SVM от Scikit-Learn
        self.ocsvm_model = load('detecting_anomalies_models/ocsvm_model.joblib')

        # Модель PineForest от conifer
        self.conifer_model_threshold = -0.5418828400208143
        self.conifer_model = load('detecting_anomalies_models/conifer_model.joblib')

        # Модель LSTM-Autoencoder, сделанная с помощью PyTorch
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.lstm = torch.load('LSTM_model_anomalies/lstm_autoencoder_full.pth', map_location=self.device,
                               weights_only=False)
        self.lstm_threshold = 1.470137
        # Загрузка скейлера, сделанного специально для LSTM-модели
        with open('LSTM_model_anomalies/scaler.pkl', 'rb') as f:
            self.lstm_scaler = pickle.load(f)
        self.lstm.eval()

    # Метод для детекции аномалий. Возвращает список ответов 5 моделей: 1 или 0.
    def detect_anomaly(self, data: pd.DataFrame):
        data = data.drop(["datetime", "id"], axis=1)

        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.fillna(data.median())

        data_ml = self.robust_scaler.transform(data)

        is_anomaly = [np.where(self.iso_forest.predict(data_ml[-1].reshape(1, -1)) == -1, 1, 0),
                      np.where(self.ee_model.predict(data_ml[-1].reshape(1, -1)) == -1, 1, 0),
                      np.where(self.ocsvm_model.predict(data_ml[-1].reshape(1, -1)) == -1, 1, 0),
                      np.where(
                          self.conifer_model.score_samples(data_ml[-1].reshape(1, -1)) < self.conifer_model_threshold,
                          1, 0)]

        data_lstm = data.iloc[:, :18]
        data_lstm = self.lstm_scaler.transform(data_lstm)
        seq_len = 12
        if len(data_lstm) < seq_len:
            raise ValueError(f"Недостаточно данных для LSTM: нужно {seq_len}, есть {len(data_lstm)}")

        X_lstm = data_lstm[-seq_len:].reshape(1, seq_len, -1)

        X = torch.tensor(X_lstm, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            output = self.lstm(X)
            mse = torch.mean((X - output) ** 2, dim=(1, 2)).cpu().numpy()

        if mse[0] > self.lstm_threshold:
            is_anomaly_lstm = 1
        else:
            is_anomaly_lstm = 0
        is_anomaly.append(is_anomaly_lstm)

        return is_anomaly

    # Выносит вердикт, исходя из списка ответов моделей.
    @staticmethod
    def verdict_anomaly(odds: list):
        return (sum(odds) >= 3)[0]


# Тестирование работы.
if __name__ == '__main__':
    searcher = CompressorSearcher()

    import warnings
    import pandas as pd
    import numpy as np

    warnings.filterwarnings('ignore')
    import sys

    if not sys.warnoptions:
        import os
    import warnings

    warnings.simplefilter('ignore')
    os.environ["PYTHONWARNINGS"] = "ignore"

    from database import PGDatabase

    df = PGDatabase(
        "postgres", "ncs", "localhost", "5432",
        "compressor", "data"
    ).tables["data"]

    df2 = df.iloc[-12:]

    print(CompressorSearcher.verdict_anomaly(searcher.detect_anomaly(df2)))
