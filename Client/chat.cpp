#include "chat.h"

#include "networkmanager.h"

#define TOO_WIDE 1000

// Стиль прокручиваемой области с виджетами сообщений.
QString style_area =
    ("QScrollArea {"
     "   border: none;"
     "   background-color: #fefedf;"
     "}"
     "QScrollArea > QWidget > QWidget {"
     "   background-color: #fefedf;"
     "}"
     "QScrollBar:vertical {"
     "   background: #e8e8e8;"
     "   width: 12px;"
     "   border-radius: 6px;"
     "   margin: 4px 2px 4px 2px;"
     "}"
     "QScrollBar::handle:vertical {"
     "   background: #bdbdbd;"
     "   border-radius: 6px;"
     "   min-height: 40px;"
     "}"
     "QScrollBar::handle:vertical:hover {"
     "   background: #9e9e9e;"
     "}"
     "QScrollBar::handle:vertical:pressed {"
     "   background: #757575;"
     "}"
     "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
     "   border: none;"
     "   background: none;"
     "   height: 0px;"
     "}"
     "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
     "   background: none;"
     "}");

Chat::Chat(QWidget *parent) : QWidget(parent) {
  this->setStyleSheet("background-color: #fefedf;");
  this->m_font = new QFont("Arial", 16);
  this->m_font_metrics = new QFontMetrics(*this->m_font);

  this->m_network_manager = new NetworkManager(this);

  this->m_layout = new QGridLayout();

  this->m_spacer = new QWidget();
  this->m_spacer->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
  this->m_spacer->setStyleSheet("background-color: rgba(0, 0, 0, 0);");

  this->m_area = new ScrollAreaWithResize(this);
  this->m_area->setWidgetResizable(true);
  this->m_area->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
  this->m_area->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);

  // Если область прокрутки, где содержатся виджеты сообщений, не очень широка
  // то сообщения пользователя будут прилегать к правой части экрана. Иначе к
  // левой.
  connect(this->m_area, &ScrollAreaWithResize::resized, this, [this]() {
    if ((m_area->width() > TOO_WIDE) && !this->m_is_wide_area) {
      for (int i = 0; i < this->m_layout->count() - 1; i++) {
        QLayoutItem *item = this->m_layout->itemAt(i);
        MessageWidget *wdg_cast = qobject_cast<MessageWidget *>(item->widget());
        if (wdg_cast->get_message().get_sender() == Sender::HUMAN)
          item->setAlignment(Qt::AlignLeft);
      }
      m_is_wide_area = true;
    } else if ((m_area->width() < TOO_WIDE) && this->m_is_wide_area) {
      for (int i = 0; i < this->m_layout->count() - 1; i++) {
        QLayoutItem *item = this->m_layout->itemAt(i);
        MessageWidget *wdg_cast = qobject_cast<MessageWidget *>(item->widget());
        if (wdg_cast->get_message().get_sender() == Sender::HUMAN)
          item->setAlignment(Qt::AlignRight);
      }
      m_is_wide_area = false;
    }
  });

  this->m_instruction = new QTextEdit(this);
  this->m_instruction->setStyleSheet(
      "background-color: #faf0e1; color: #5c4033; border: 2px solid #d4a574;"
      "border-radius: 10px; padding: 15px; font-family: 'Arial'; line-height: "
      "1.6;"
      "font-size: 18pt;");
  // По умолчанию виджет с инструкцией скрыт.
  this->m_instruction->hide();
  this->m_instruction_on = false;
  // Текст инструкции берётся из файла в ресурсах.
  QFile file(":/items/resources/instruction.txt");
  if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
    QTextStream stream(&file);
    QString content = stream.readAll();
    file.close();

    this->m_instruction->setText(content);
  }
  this->m_instruction->setReadOnly(true);

  this->m_container = new QWidget(m_area);
  this->m_container->setLayout(this->m_layout);

  this->m_area->setWidget(this->m_container);

  // По умолчанию никакие файлы справа не отображаются.
  this->m_second_view = nullptr;
  this->m_second_view_with_code = false;
  this->m_curr_message = nullptr;

  this->m_audio_recorder = new AudioRecorder(this);

  this->m_main_layout = new QGridLayout(this);

  // Подпись сверху чата.
  auto sender = new QLabel("Чат-бот", this);
  sender->setAlignment(Qt::AlignCenter);
  sender->setStyleSheet(
      "background-color: #DAF0FF; font-family: Arial;"
      "font-size: 32px;  border-bottom-left-radius: 20px;"
      "border-bottom-right-radius: 20px; border: 1px solid #999999;"
      "color: #503030;");
  sender->setMinimumHeight(50);
  m_main_layout->setContentsMargins(0, 0, 0, 0);
  m_main_layout->setSpacing(0);

  // Кнопка, открывающая инструкцию.
  auto info_btn = new QPushButton(sender);
  info_btn->setStyleSheet(
      "border-image: url(:/items/resources/info.png) "
      "stretch stretch; border-radius: 0px;");
  info_btn->setFixedSize(42, 42);
  connect(info_btn, &QPushButton::clicked, this, [this]() {
    if (this->m_instruction_on) {
      this->m_area->show();
      this->m_send_wdgt->show();
      this->m_instruction->hide();
    } else {
      this->m_area->hide();
      this->m_send_wdgt->hide();
      this->m_instruction->show();
    }
    this->m_instruction_on = !this->m_instruction_on;
  });
  info_btn->move(20, 5);

  // Кнопка для сохранения открытого PDF-файла на диск.
  auto save_btn = new QPushButton(sender);
  save_btn->setStyleSheet(
      "border-image: url(:/items/resources/save.png) "
      "stretch stretch; border-radius: 0px;");
  save_btn->setFixedSize(42, 42);
  connect(save_btn, &QPushButton::clicked, this, [this]() {
    if (this->m_curr_message == nullptr) {
      message_box(this, QMessageBox::Critical, "Ошибка",
                  "Не было выбрано сообщение.");
    } else {
      QString save_file_name = QFileDialog::getSaveFileName(
          this, "Сохранить файл", QDir::homePath() + "/document.pdf",
          "PDF файлы (*.pdf)");

      if (!save_file_name.isEmpty()) {
        if (!save_file_name.endsWith(".pdf", Qt::CaseInsensitive))
          save_file_name += ".pdf";
        QString name_file = this->m_curr_message->get_message().get_binding();
        if (!this->m_second_view_with_code)
          name_file =
              name_file.left(
                  this->m_curr_message->get_message().get_binding().size() -
                  4) +
              "_2.pdf";
        if (QFile::copy(name_file, save_file_name))
          message_box(this, QMessageBox::Information, "Успех",
                      "Успешно сохранено.");
        else
          message_box(this, QMessageBox::Critical, "Ошибка",
                      "Сохранение не удалось.");
      }
    }
  });
  save_btn->move(75, 5);

  // Кнопка, активирующая/деактивирующая режим аудиоответа от сервера.
  auto sound_btn = new QPushButton(sender);
  sound_btn->setStyleSheet(
      "border-image: url(:/items/resources/mute.png) "
      "stretch stretch; border-radius: 0px;");
  sound_btn->setFixedSize(42, 42);
  connect(sound_btn, &QPushButton::clicked, this, [sound_btn, this]() {
    if (!this->m_speech_on)
      sound_btn->setStyleSheet(
          "border-image: url(:/items/resources/unmute.png) stretch stretch; "
          "border-radius: 0px;");
    else
      sound_btn->setStyleSheet(
          "border-image: url(:/items/resources/mute.png) "
          "stretch stretch; border-radius: 0px;");
    this->m_speech_on = !this->m_speech_on;
  });
  sound_btn->move(125, 5);
  // По умолчанию режим аудиоответа от сервера выключен.
  this->m_speech_on = false;

  this->m_audio_player = new AudioPlayer(this);
  // Как только завершается загрузка аудиоответа с сервера, он воспроизводится.
  connect(this->m_network_manager, &NetworkManager::audio_download_finished,
          this, [this](const QString &audio_path) {
            this->m_audio_player->play_file(audio_path);
          });

  this->m_edit_field = new QTextEdit(this);
  this->m_edit_field->setMaximumHeight(130);
  this->m_edit_field->setStyleSheet(
      "background-color: #DCF8C6; font-family: Arial;"
      "font-size: 16pt; border-radius: 10px;"
      "color: #503030;");
  this->m_edit_field->setPlaceholderText("Введите сообщение...");

  // Кнопка отправки сообщения пользователем.
  this->m_send_btn = new QPushButton(this);
  this->m_send_btn->setStyleSheet(
      "border-image: url(:/items/resources/send_btn.png) stretch stretch;");
  this->m_send_btn->setFixedSize(42, 42);
  connect(m_send_btn, &QPushButton::clicked, this, [this]() {
    auto text = this->m_edit_field->toPlainText();
    auto text2 = text;
    text2.remove(" ").remove("\n").remove("\t");
    if (text2 != "") {
      this->m_send_btn->setEnabled(false);
      this->m_audio_recorder_btn->setEnabled(false);
      this->add_message(Message(Sender::HUMAN, text));
      this->m_edit_field->clear();
    }
  });

  // По умолчанию режим записи аудиозапроса отключен.
  this->m_is_recording_audio = false;
  this->m_audio_recorder_btn = new QPushButton(this);
  this->m_audio_recorder_btn->setStyleSheet(
      "border-image: url(:/items/resources/audio_recorder_btn_not_active.png) "
      "stretch stretch;");
  this->m_audio_recorder_btn->setFixedSize(42, 42);
  connect(m_audio_recorder_btn, &QPushButton::clicked, this, [this]() {
    if (!this->m_is_recording_audio) {
      this->m_audio_recorder_btn->setStyleSheet(
          "border-image: url(:/items/resources/audio_recorder_btn_active.png) "
          "stretch stretch;");
      this->m_audio_recorder->start_recording("audio_to_send/output.wav");
      this->m_send_btn->setEnabled(false);
    } else {
      this->m_audio_recorder_btn->setStyleSheet(
          "border-image: "
          "url(:/items/resources/audio_recorder_btn_not_active.png) stretch "
          "stretch;");
      this->m_audio_recorder->stop_recording();
      this->m_audio_recorder_btn->setEnabled(false);
    }
    this->m_is_recording_audio = !this->m_is_recording_audio;
  });

  // Как только аудиозапрос записан, от отправляется на сервер.
  connect(this->m_audio_recorder, &AudioRecorder::recordingFinished, this,
          [this]() {
            this->m_network_manager->upload_audio("audio_to_send/output.wav",
                                                  this->m_speech_on);
          });

  this->m_send_wdgt = new QWidget(this);
  // Виджет, содержащий кнопки
  auto send_btns_wdgt = new QWidget(m_send_wdgt);
  send_btns_wdgt->setStyleSheet("border: transparent;");
  auto layout_btns = new QVBoxLayout(send_btns_wdgt);

  layout_btns->addWidget(m_send_btn);
  layout_btns->addWidget(m_audio_recorder_btn);

  m_send_wdgt->setStyleSheet(
      "background-color: #EEEECF; font-family: Arial;"
      "font-size: 16pt; border: 1px solid #999999; "
      "border-top-left-radius: 10px;"
      "border-top-right-radius: 10px;"
      "color: #503030;");
  auto send_layout = new QHBoxLayout(m_send_wdgt);
  send_layout->addWidget(m_edit_field);
  send_layout->addWidget(send_btns_wdgt);
  send_layout->setContentsMargins(10, 5, 10, 5);

  this->m_main_layout->addWidget(sender, 0, 0);
  this->m_main_layout->addWidget(this->m_area, 1, 0);
  this->m_main_layout->addWidget(m_send_wdgt, 2, 0);
  this->m_main_layout->addWidget(m_instruction, 1, 0, 2, 1);

  this->m_main_layout->setRowStretch(0, 0);
  this->m_main_layout->setRowStretch(1, 1);
  this->m_main_layout->setRowStretch(2, 0);

  this->m_second_view_frame = new QWidget(this);
  auto second_view_layout = new QHBoxLayout(this->m_second_view_frame);
  second_view_layout->setContentsMargins(1, 0, 0, 0);
  this->m_second_view = new FileViewer(this->m_second_view_frame);
  second_view_layout->addWidget(this->m_second_view);
  this->m_second_view_frame->setStyleSheet("border: 1px solid #333333;");
  this->m_second_view_frame->hide();

  this->m_main_layout->addWidget(this->m_second_view_frame, 0, 2, 3, 1);

  this->setLayout(m_main_layout);

  this->m_area->setStyleSheet(style_area);
  this->m_is_wide_area = this->m_area->width() > TOO_WIDE ? true : false;
}

Chat::~Chat() {
  delete this->m_font;
  delete this->m_font_metrics;
}

Chat::Chat() {}

void Chat::add_message(Message message, bool send_it /*= true*/) {
  this->m_messages.push_back(message);
  auto wdg_message = new MessageWidget(message, this);

  // Определяем необходимый размер сообщения для текста
  int padding = wdg_message->contentsMargins().top() +
                wdg_message->contentsMargins().bottom();
  QRect bounding_rect = this->m_font_metrics->boundingRect(
      QRect(0, 0, 450, 0), Qt::TextWordWrap, message.get_content());

  wdg_message->setFixedHeight(bounding_rect.height() + padding + 25);
  wdg_message->setFixedWidth(fmin(450, bounding_rect.width() * 1.5));

  wdg_message->setAlignment(Qt::AlignVCenter);
  wdg_message->setWordWrap(true);

  if (message.get_sender() == Sender::HUMAN) {
    this->m_layout->addWidget(
        wdg_message, this->m_messages.size() - 1, 0,
        this->m_is_wide_area ? Qt::AlignLeft : Qt::AlignRight);
    // На сервер отправляем сообщение, только если явно указываем это. Нужно для
    // случая, когда приходит расшифровка аудиозапроса, чтобы эту расшифровку не
    // отправлять на сервер повторно и не делать ненужные запросы.
    if (send_it)
      this->m_network_manager->send_message(message, this->m_speech_on);
  } else
    this->m_layout->addWidget(wdg_message, this->m_messages.size() - 1, 0,
                              Qt::AlignLeft);

  if (message.get_binding() != "") {
    // Если у сообщения есть прикреплённый к нему файл, то делаем, чтобы по
    // нажатию на сообщение, этот файл справа отображался.
    connect(wdg_message, &MessageWidget::right_clicked, this,
            [this, wdg_message]() {
              if (wdg_message != this->m_curr_message) {
                // Если уже было выбрано другое сообщение
                if (this->m_curr_message != nullptr)
                  MessageWidget::select_style_message(
                      this->m_curr_message,
                      this->m_curr_message->get_message().get_sender());
                this->m_second_view->load_file(
                    wdg_message->get_message().get_binding());
                // Нажатие на правую кнопку мыши = открытие файла с кодом
                this->m_second_view_with_code = true;
                this->m_second_view_frame->show();
                this->m_main_layout->setColumnMinimumWidth(1, 5);
                this->m_curr_message = wdg_message;
                wdg_message->setStyleSheet(
                    "background-color: #FCA8A6; font-family: Arial;"
                    "font-size: 16pt; border-radius: 10px; border: 1px solid "
                    "#999999;"
                    "color: #503030;");
              } else {
                // Второе нажатие = закрытие файла
                MessageWidget::select_style_message(
                    wdg_message, wdg_message->get_message().get_sender());
                this->hide_second_view();
                this->m_curr_message = nullptr;
              }
            });
    connect(wdg_message, &MessageWidget::clicked, this, [this, wdg_message]() {
      if (wdg_message != this->m_curr_message) {
        // Если уже было выбрано другое сообщение
        if (this->m_curr_message != nullptr)
          MessageWidget::select_style_message(
              this->m_curr_message,
              this->m_curr_message->get_message().get_sender());
        QString name_without_extension =
            wdg_message->get_message().get_binding().left(
                wdg_message->get_message().get_binding().size() - 4);
        this->m_second_view->load_file(name_without_extension + "_2.pdf");
        // Нажатие на левую кнопку мыши = открытие файла без кода
        this->m_second_view_with_code = false;
        this->m_second_view_frame->show();
        this->m_main_layout->setColumnMinimumWidth(1, 5);
        this->m_curr_message = wdg_message;
        wdg_message->setStyleSheet(
            "background-color: #FCA8A6; font-family: Arial;"
            "font-size: 16pt; border-radius: 10px; border: 1px solid #999999;"
            "color: #503030;");
      } else {
        // Второе нажатие = закрытие файла
        MessageWidget::select_style_message(
            wdg_message, wdg_message->get_message().get_sender());
        this->hide_second_view();
        this->m_curr_message = nullptr;
      }
    });
  }
  this->m_layout->addWidget(m_spacer, this->m_messages.size(), 0);
}

void Chat::hide_second_view() {
  this->m_main_layout->setColumnMinimumWidth(1, 0);
  this->m_second_view_frame->hide();
}

void Chat::resizeEvent(QResizeEvent *event) { QWidget::resizeEvent(event); }

void Chat::zoom_plus() {
  if (this->m_second_view != nullptr) {
    this->m_second_view->zoom_plus();
    this->m_second_view->fit_to_width();
  }
}

void Chat::zoom_minus() {
  if (this->m_second_view != nullptr) {
    this->m_second_view->zoom_minus();
    this->m_second_view->fit_to_width();
  }
}

void Chat::reset_zoom() {
  if (this->m_second_view != nullptr) {
    this->m_second_view->reset_zoom();
    this->m_second_view->fit_to_width();
  }
}

void Chat::start_audio_record() {
  if (!this->m_is_recording_audio) {
    this->m_audio_recorder_btn->setStyleSheet(
        "border-image: url(:/items/resources/audio_recorder_btn_active.png) "
        "stretch stretch;");
    this->m_audio_recorder->start_recording("audio_to_send/output.wav");
    this->m_is_recording_audio = true;
  }
}

void Chat::finish_audio_record() {
  if (this->m_is_recording_audio) {
    m_audio_recorder_btn->setStyleSheet(
        "border-image: "
        "url(:/items/resources/audio_recorder_btn_not_active.png) stretch "
        "stretch;");
    this->m_audio_recorder->stop_recording();
    this->m_is_recording_audio = false;
  }
}

bool Chat::get_is_recording_audio() const { return m_is_recording_audio; }

// Удержание клавиши S = аудиозапись запроса
void Chat::keyPressEvent(QKeyEvent *event) {
  if (event->key() == Qt::Key_S) {
    if (event->isAutoRepeat()) return;
    if (!this->m_is_recording_audio) {
      this->m_audio_recorder_btn->setStyleSheet(
          "border-image: url(:/items/resources/audio_recorder_btn_active.png) "
          "stretch stretch;");
      this->m_audio_recorder->start_recording("audio_to_send/output.wav");
      this->m_is_recording_audio = true;
      this->m_send_btn->setEnabled(false);
    }
  }
  QWidget::keyPressEvent(event);
}

// Отмена нажатия клавиши S = окончание аудиозаписи запроса. Отправка на сервер.
void Chat::keyReleaseEvent(QKeyEvent *event) {
  if (event->key() == Qt::Key_S) {
    if (event->isAutoRepeat()) return;
    if (this->m_is_recording_audio) {
      m_audio_recorder_btn->setStyleSheet(
          "border-image: "
          "url(:/items/resources/audio_recorder_btn_not_active.png) stretch "
          "stretch;");
      this->m_audio_recorder->stop_recording();
      this->m_is_recording_audio = false;
      this->m_audio_recorder_btn->setEnabled(false);
    }
  }
  QWidget::keyReleaseEvent(event);
}

void Chat::btns_on() {
  this->m_audio_recorder_btn->setEnabled(true);
  this->m_send_btn->setEnabled(true);
}
