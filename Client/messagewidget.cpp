#include "messagewidget.h"

MessageWidget::MessageWidget(Message &message, QWidget *parent /*= nullptr*/)
    : QLabel(message.get_content(), parent), m_message(message) {
  select_style_message(this, message.get_sender());

  this->m_pressed = false;
}

void MessageWidget::mousePressEvent(QMouseEvent *event) {
  if (event->button() == Qt::LeftButton) {
    this->m_pressed = true;
  } else if (event->button() == Qt::RightButton) {
    this->m_pressed = true;
  }
  QLabel::mousePressEvent(event);
}

void MessageWidget::mouseReleaseEvent(QMouseEvent *event) {
  if ((event->button() == Qt::LeftButton) && m_pressed) {
    this->m_pressed = false;
    emit clicked();
  } else if (event->button() == Qt::RightButton) {
    this->m_pressed = false;
    emit right_clicked();
  }
  QLabel::mouseReleaseEvent(event);
}

Message MessageWidget::get_message() const { return m_message; }

void MessageWidget::select_style_message(QLabel *message, Sender sender) {
  if (sender == Sender::HUMAN)
    message->setStyleSheet(
        "background-color: #DCF8C6; font-family: Arial;"
        "font-size: 16pt; border-radius: 10px; border: 1px solid #999999;"
        "color: #0D47A1;");
  else if (sender == Sender::ROBOT)
    message->setStyleSheet(
        "background-color: #E8E8E8; font-family: Arial;"
        "font-size: 16pt; border-radius: 10px; border: 1px solid #999999;"
        "color: #503030;");
  else if (sender == Sender::SYSTEM)
    message->setStyleSheet(
        "background-color: #FFF3C4; font-family: Arial;"
        "font-size: 16pt; border-radius: 10px; border: 1px solid #999999;"
        "color: #503030;");
}
