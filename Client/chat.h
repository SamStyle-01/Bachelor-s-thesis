#ifndef CHAT_H
#define CHAT_H

#include "pch.h"

#include "audioplayer.h"
#include "audiorecorder.h"
#include "fileviewer.h"
#include "message.h"
#include "messagebox.h"
#include "messagewidget.h"
#include "scrollareawithresize.h"

class NetworkManager;

// Отвечает за интерфейс чата и содержит слоты для обработки
// сигналов, поступающих из чата. Является связующим элементом
// в программе.
class Chat : public QWidget {
  Q_OBJECT
  // Контейнер, содержащий все сообщения (логическую часть.
  QVector<Message> m_messages;
  // Макет, содержащий сообщения в чате.
  QGridLayout *m_layout;

  // Отвечает за шрифт в чате.
  QFont *m_font;
  // Нужен для вычисления, сколько пространства занимает запись.
  // Для выбора ширины и высоты сообщения.
  QFontMetrics *m_font_metrics;
  // Объект пустого пространства. Заставляет виджеты прижиматься
  // друг к другу вместо того, чтобы распространяться по области
  // чата равномерно.
  QWidget *m_spacer;
  // Область прокручивания. Для возможности прокручивания чата вниз.
  ScrollAreaWithResize *m_area;
  // Содержится в области прокручивания. Содержит непосредственно сообщения.
  QWidget *m_container;
  // Текстовое поле ввода для пользователя.
  QTextEdit *m_edit_field;

  // Отвечает за расположение сообщений пользователя:
  // если окно приложения не слишком широко, то
  // сообщения пользователя будут прилегать к правой стороне.
  // Если же слишком широко, то к левой.
  bool m_is_wide_area;

  // Виджет, содержащий виджет для отображения PDF-файла.
  QWidget *m_second_view_frame;
  // Будет открываться версия PDF-файла с кодом или версия без.
  bool m_second_view_with_code;

  // Виджет, непосредственно отвечающий за отображение файла.
  FileViewer *m_second_view;
  // Главный макет чата.
  QGridLayout *m_main_layout;

  // Текущее выделенное сообщение.
  MessageWidget *m_curr_message;
  // Нижняя часть чата, содержащая текстовое поле ввода и кнопки отправить
  // и записать аудиосообщение.
  QWidget *m_send_wdgt;

  // Отвечает за соединение с сервером по сети.
  NetworkManager *m_network_manager;

  // Отображает инструкцию в приложении.
  QTextEdit *m_instruction;
  // Включена ли инструкция.
  bool m_instruction_on;

  // Записывает аудиосообщение.
  AudioRecorder *m_audio_recorder;
  // Кнопка отправки текстового сообщения.
  QPushButton *m_send_btn;
  // Кнопка, по нажатию которой записывается аудиосообщение.
  QPushButton *m_audio_recorder_btn;
  // Записывается ли сейчас аудиосообщение.
  bool m_is_recording_audio;

  // Включена ли функция аудиоответов от сервера.
  bool m_speech_on;
  // Воспроизводит аудиоответы от сервера.
  AudioPlayer *m_audio_player;

public:
  explicit Chat(QWidget *parent);
  Chat();
  virtual ~Chat();
  // Добавить сообщения в чат.
  void add_message(Message message, bool send_it = true);
  // Закрыть отображение PDF-файла (если выделение сообщения
  // было отменено.
  void hide_second_view();

  // Увеличить масштаб отображения PDF-файла.
  void zoom_plus();
  // Уменьшить масштаб отображения PDF-файла.
  void zoom_minus();
  // Установить масштаб отображения PDF-файла по умолчанию.
  void reset_zoom();

  // Начать аудиозапись.
  void start_audio_record();
  // Закончить аудиозапись.
  void finish_audio_record();

  // Возвращает, записывается ли сейчас аудио или нет.
  bool get_is_recording_audio() const;

  // Возвращает кнопки во рабочее положение после поступления ответа от сервера.
  void btns_on();

protected:
  void resizeEvent(QResizeEvent *event) override;
  void keyPressEvent(QKeyEvent *event) override;
  void keyReleaseEvent(QKeyEvent *event) override;
};

#endif // CHAT_H
