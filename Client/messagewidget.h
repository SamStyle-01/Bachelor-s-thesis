#ifndef MESSAGEWIDGET_H
#define MESSAGEWIDGET_H

#include <QLabel>

#include "message.h"

// Отвечает за отображение сообщения в чате.
class MessageWidget : public QLabel {
  Q_OBJECT
  // Выделено ли сообщение сейчас.
  bool m_pressed;
  // Объект логики сообщения.
  Message m_message;

public:
  explicit MessageWidget(Message &message, QWidget *parent = nullptr);
  // Возвращает копию объекта логики сообщения m_message.
  Message get_message() const;
  // Настраивает нужный стиль для сообщения.
  static void select_style_message(QLabel *message, Sender sender);

signals:
  void clicked();
  void right_clicked();

protected:
  void mousePressEvent(QMouseEvent *event) override;
  void mouseReleaseEvent(QMouseEvent *event) override;
};

#endif // MESSAGEWIDGET_H
