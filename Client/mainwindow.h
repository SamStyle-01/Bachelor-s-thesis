#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include "pch.h"

#include <QMainWindow>
#include <QObject>
#include <QWidget>

#include "chat.h"

// Основное окно, в котором отображаются все остальные виджеты.
class CWindow : public QMainWindow {
  Q_OBJECT
  // Открыт ли виджет на весь экран.
  bool m_is_full_screen;
  // Объект чата, содержащий в себе основной интерфейс приложения.
  Chat *m_chat;

public:
  explicit CWindow();

protected:
  void keyPressEvent(QKeyEvent *event) override;
};

#endif // MAINWINDOW_H
