#include "mainwindow.h"

CWindow::CWindow() {
  this->setWindowIcon(QIcon(":/items/resources/icon.ico"));
  this->setWindowTitle("Валерий AI");
  this->setStyleSheet("background-color: #fefedf;");

  QScreen *screen = QGuiApplication::primaryScreen();
  QRect geometry = screen->geometry();
  int width = geometry.width();
  int height = geometry.height();

  // Соотношение высоты окна приложения к ширине.
  int height_temp = (height * 6) / 7;
  this->setGeometry(
      QRect(width / 3, height / 12, height_temp * 0.77, height_temp));
  this->setMinimumSize((this->width() * 6) / 7, (this->height() * 3) / 4);

  this->m_chat = new Chat(this);

  this->setCentralWidget(m_chat);

  // По умолчанию программа открывается не на весь экран.
  this->m_is_full_screen = false;
}

void CWindow::keyPressEvent(QKeyEvent *event) {
  if (event->key() == Qt::Key_F11) {
    if (m_is_full_screen)
      showNormal();
    else
      showFullScreen();
    m_is_full_screen = !m_is_full_screen;
  } else if (event->key() == Qt::Key_Plus)
    this->m_chat->zoom_plus();
  else if (event->key() == Qt::Key_Minus)
    this->m_chat->zoom_minus();
  else if (event->key() == Qt::Key_R)
    this->m_chat->reset_zoom();
  QWidget::keyPressEvent(event);
}
