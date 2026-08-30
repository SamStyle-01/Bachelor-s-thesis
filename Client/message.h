#ifndef MESSAGE_H
#define MESSAGE_H

// Отправителем могут быть: человек (пользователь),
// система (детектор аномалий) и робот
// (ответы на запросы пользователя).
enum class Sender { HUMAN, SYSTEM, ROBOT };

// Класс логики работы сообщения.
class Message {
  // Определяет, кто отправил сообщение.
  Sender m_sender;
  // Определяет текстовое содержание ответа.
  // Будет отображаться в чате.
  QString m_content;
  // Определяет при наличии привязку к файлу.
  // Если есть, содержит относительный путь к
  // файлу.
  QString m_binding;

public:
  explicit Message(Sender sender, QString content, QString binding = "");
  Message();

  // Возвращает отправителя сообщения.
  Sender get_sender() const;
  // Возвращает содеражение сообщения.
  QString get_content() const;
  // Возвращает привязку к файлу сообщения.
  QString get_binding() const;
};

#endif // MESSAGE_H
