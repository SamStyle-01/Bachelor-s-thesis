import torch.nn as nn


# Схема LSTM-Autoencoder для загрузки модели из файла.
class LSTMAutoencoder(nn.Module):
    def __init__(self, seq_len, no_features, embedding_dim=64):
        super(LSTMAutoencoder, self).__init__()
        self.seq_len = seq_len
        self.no_features = no_features

        # Кодировщик
        self.encoder_lstm1 = nn.LSTM(
            input_size=no_features,
            hidden_size=embedding_dim,
            num_layers=1,
            batch_first=True
        )

        self.encoder_lstm2 = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=embedding_dim // 2,
            num_layers=1,
            batch_first=True
        )

        # Декодировщик
        self.decoder_lstm1 = nn.LSTM(
            input_size=embedding_dim // 2,
            hidden_size=embedding_dim,
            num_layers=1,
            batch_first=True
        )
        self.decoder_output = nn.Linear(embedding_dim, no_features)

    def forward(self, x):
        x, (hidden, cell) = self.encoder_lstm1(x)
        x, (hidden, cell) = self.encoder_lstm2(x)
        latent = hidden[-1].unsqueeze(1).repeat(1, self.seq_len, 1)

        x, (hidden, cell) = self.decoder_lstm1(latent)
        x = self.decoder_output(x)
        return x
