#include "networkmanager.h"

NetworkManager::NetworkManager(Chat *chat) : QObject(chat), chat(chat) {
  this->m_manager = new QNetworkAccessManager(chat);

  QFile file("resources\\url.cfg");
  QString url;
  if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
    QTextStream stream(&file);
    url = stream.readAll();
    file.close();
  }
  this->set_url(url);
  this->m_file_reply = nullptr;
  this->m_web_socket = new QWebSocket();
  this->m_web_socket->setParent(this->m_manager);
  this->m_web_socket->open(
      QUrl("ws" + url.right(url.size() - 4) + "ws/anomalies"));

  // Если соединение отсутствует - переподключаемся
  connect(this->m_web_socket, &QWebSocket::disconnected, this,
          &NetworkManager::_reconnect_web_socket);
  // Если соединение оборвано - переподключаемся
  connect(this->m_web_socket, &QWebSocket::errorOccurred, this,
          &NetworkManager::_reconnect_web_socket);

  connect(this->m_web_socket, &QWebSocket::textMessageReceived, this,
          [this](const QString &message) {
            this->chat->add_message(Message(Sender::SYSTEM, message));
          });
}

void NetworkManager::set_url(QString url) { this->m_url = url; }

void NetworkManager::send_message(const Message &message,
                                  bool voice /*= false*/) {
  QNetworkRequest request(QUrl(m_url + "send-message"));
  request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");

  QJsonObject json;
  json["text"] = message.get_content();
  json["voice"] = voice ? "ON" : "OFF";
  QJsonDocument doc(json);

  this->m_current_reply = m_manager->post(request, doc.toJson());

  connect(this->m_current_reply, &QNetworkReply::finished, this,
          [this, voice]() { on_text_reply(nullptr, voice); });
}

// Если соединение отсутствует - переподключаемся
void NetworkManager::_reconnect_web_socket() {
  QTimer::singleShot(300, this, [this]() {
    QString ws_url = "ws" + m_url.right(m_url.size() - 4) + "ws/anomalies";
    m_web_socket->open(QUrl(ws_url));
  });
}

void NetworkManager::upload_audio(const QString &file_path,
                                  bool voice /*= false*/) {
  QFileInfo file_info(file_path);
  if (!file_info.exists()) {
    message_box(this->chat, QMessageBox::Critical, "Ошибка",
                "Файл для отправки не найден: " + file_path);
    return;
  }

  QHttpMultiPart *multi_part = new QHttpMultiPart(QHttpMultiPart::FormDataType);

  QHttpPart file_part;
  file_part.setHeader(QNetworkRequest::ContentTypeHeader,
                      QVariant("audio/wav"));

  QString disposition = QString("form-data; name=\"file\"; filename=\"%1\"")
                            .arg(file_info.fileName());
  file_part.setHeader(QNetworkRequest::ContentDispositionHeader,
                      QVariant(disposition));

  QFile *file = new QFile(file_path);
  if (!file->open(QIODevice::ReadOnly)) {
    message_box(this->chat, QMessageBox::Critical, "Ошибка",
                "Не удалось открыть файл для чтения: " + file_path);
    delete multi_part;
    delete file;
    return;
  }
  file_part.setBodyDevice(file);

  multi_part->append(file_part);

  QHttpPart text_part;
  text_part.setHeader(QNetworkRequest::ContentDispositionHeader,
                      QVariant("form-data; name=\"voice\""));
  text_part.setBody(voice ? "ON" : "OFF");

  multi_part->append(text_part);

  QUrl url("http://127.0.0.1:8000/upload-audio/");
  QNetworkRequest request(url);
  this->m_current_reply = this->m_manager->post(request, multi_part);
  multi_part->setParent(this->m_current_reply);
  file->setParent(multi_part);

  connect(this->m_current_reply, &QNetworkReply::finished, this,
          [this, multi_part, voice]() { on_text_reply(multi_part, voice); });
}

void NetworkManager::on_text_reply(QHttpMultiPart *multi_part, bool voice) {
  this->chat->btns_on();
  if (this->m_current_reply->error() == QNetworkReply::NoError) {
    QByteArray response = this->m_current_reply->readAll();
    QJsonDocument doc = QJsonDocument::fromJson(response);

    if (doc.isObject()) {
      QString code = doc.object()["code"].toString();
      QString message = doc.object()["response_text"].toString();
      if (message == "7658281") {
        if (code == "2")
          chat->add_message(
              Message(Sender::HUMAN, "Запрос не пригоден к обработке."), false);
        chat->add_message(Message(Sender::ROBOT, "Некорректный запрос."));
      } else {
        QString file_name = doc.object()["file_name"].toString();
        if (code == "2") {
          QString user_request = doc.object()["user_request"].toString();
          chat->add_message(Message(Sender::HUMAN, user_request), false);
        }

        chat->add_message(
            Message(Sender::ROBOT, message, "files/" + file_name));

        QNetworkRequest request(QUrl(m_url + "get-file/" + file_name));
        this->m_file_reply = m_manager->get(request);
        connect(m_file_reply, &QNetworkReply::finished, this,
                [this, file_name, voice]() {
                  QString name_without_extension =
                      file_name.left(file_name.size() - 4);
                  on_reply_finished(name_without_extension + "_2.pdf");

                  QNetworkRequest request_with_code(QUrl(
                      m_url + "get-file/" + name_without_extension + "_2.pdf"));
                  this->m_file_reply = m_manager->get(request_with_code);
                  connect(m_file_reply, &QNetworkReply::finished, this,
                          [this, file_name, name_without_extension, voice]() {
                            on_reply_finished(file_name);
                            if (voice) {
                              QNetworkRequest request_for_audio(
                                  QUrl(m_url + "get-file/" +
                                       name_without_extension + ".mp3"));
                              this->m_file_reply =
                                  m_manager->get(request_for_audio);
                              connect(m_file_reply, &QNetworkReply::finished,
                                      this, [this, name_without_extension]() {
                                        on_reply_finished(
                                            name_without_extension + ".mp3");
                                      });
                            }
                          });
                });
      }
    }
  } else {
    chat->add_message(
        Message(Sender::ROBOT, "Ошибка на стороне сервера. Повторите запрос."));
  }

  this->m_current_reply->deleteLater();
  if (multi_part != nullptr) multi_part->deleteLater();
}

void NetworkManager::on_reply_finished(QString file_name) {
  if (!m_file_reply) return;

  if (m_file_reply->error() != QNetworkReply::NoError) {
    m_file_reply->deleteLater();
    return;
  }

  QDir dir("files");
  if (!dir.exists()) dir.mkpath(".");

  QDir dir2("audio");
  if (!dir2.exists()) dir2.mkpath(".");

  QString content_type =
      m_file_reply->header(QNetworkRequest::ContentTypeHeader).toString();

  if (content_type.contains("application/pdf")) {
    QFile file("files/" + file_name);
    if (file.open(QIODevice::WriteOnly)) {
      file.write(m_file_reply->readAll());
      file.close();
    }
  } else if (content_type.contains("audio/mpeg") ||
             content_type.contains("audio/wav")) {
    QFile file("audio/" + file_name);
    if (file.open(QIODevice::WriteOnly)) {
      file.write(m_file_reply->readAll());
      file.close();
      emit audio_download_finished("audio/" + file_name);
    }
  }

  m_file_reply->deleteLater();
}
