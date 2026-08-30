#ifndef NETWORKMANAGER_H
#define NETWORKMANAGER_H

#include <QWebSocket>

#include "chat.h"
#include "message.h"
#include "messagebox.h"
#include "pch.h"

// Отвечает за работу по сети: соединяется с сервером.
class NetworkManager : public QObject {
  Q_OBJECT
  // Содержит адрес сервера.
  QString m_url;
  // Объект для управления сетевыми запросами.
  QNetworkAccessManager *m_manager;
  // Указатель на связующий объект чата.
  Chat *chat;

  // Текущий обрабатываемый запрос.
  QNetworkReply *m_current_reply;
  // Принимает файловый ответ с сервера.
  QNetworkReply *m_file_reply;
  // Осуществляет соединение с сервером по
  // веб-сокету. Принимает сообщения об
  // аномалиях с сервера.
  QWebSocket *m_web_socket;

  void _reconnect_web_socket();

 public:
  explicit NetworkManager(Chat *chat);
  // Устанавливает адрес сервера.
  void set_url(QString url);

  // Отправляет запрос на сервер.
  void send_message(const Message &message, bool voice = false);

  // Отправляет голосовой запрос на сервер.
  void upload_audio(const QString &file_path, bool voice = false);

 private slots:
  // Обрабатывает файловый ответ с сервера. Сохраняет файлы на компьютере.
  void on_reply_finished(QString file_name);
  // Обрабатывает текстовый ответ с сервера (он попадает в чат
  // в виде сообщения)
  void on_text_reply(QHttpMultiPart *multiPart, bool voice);

 signals:
  // Аудиоответ от сервера получен. После него начало воспроизведения.
  void audio_download_finished(const QString &audio_path);
};

#endif  // NETWORKMANAGER_H
