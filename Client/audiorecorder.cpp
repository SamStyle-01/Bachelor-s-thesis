#include "audiorecorder.h"
#include "chat.h"
#include <QDebug>
#include <QDir>
#include <QFileInfo>

AudioRecorder::AudioRecorder(QObject *parent /*= nullptr*/)
    : QObject(parent), m_audio_input(nullptr), m_recorder(nullptr) {
  QAudioDevice defaultDevice = QMediaDevices::defaultAudioInput();

  if (defaultDevice.isNull()) {
    message_box(qobject_cast<QWidget *>(this->parent()), QMessageBox::Critical,
                "Ошибка", "Микрофон не найден.");
    return;
  }

  this->m_audio_input = new QAudioInput(defaultDevice, this);
  this->m_recorder = new QMediaRecorder(this);

  QMediaFormat format;
  format.setFileFormat(QMediaFormat::Wave);
  format.setAudioCodec(QMediaFormat::AudioCodec::Wave);
  this->m_recorder->setMediaFormat(format);

  m_capture_session.setAudioInput(this->m_audio_input);
  m_capture_session.setRecorder(this->m_recorder);

  // Испускается сигнал, если аудиозапись остановилась.
  connect(this->m_recorder, &QMediaRecorder::recorderStateChanged, this,
          [this](QMediaRecorder::RecorderState state) {
            if (state == QMediaRecorder::StoppedState)
              emit recordingFinished();
          });

  connect(this->m_recorder, &QMediaRecorder::errorOccurred, this,
          [this](QMediaRecorder::Error error, const QString &errorString) {
            message_box(qobject_cast<QWidget *>(this->parent()),
                        QMessageBox::Critical, "Ошибка",
                        "Ошибка записи. " + errorString);
          });
}

AudioRecorder::~AudioRecorder() {
  if (this->m_recorder &&
      (this->m_recorder->recorderState() == QMediaRecorder::RecordingState))
    this->m_recorder->stop();
}

void AudioRecorder::start_recording(const QString &filePath) {
  if (!this->m_audio_input || this->m_audio_input->device().isNull()) {
    message_box(qobject_cast<QWidget *>(this->parent()), QMessageBox::Critical,
                "Ошибка",
                "Невозможно начать запись: устройство не инициализировано.");
    return;
  }

  QFileInfo file_info(filePath);
  QString absolutePath = file_info.absoluteFilePath();

  QDir dir = file_info.absoluteDir();
  if (!dir.exists())
    return;

  this->m_recorder->setOutputLocation(QUrl::fromLocalFile(absolutePath));

  this->m_recorder->record();
}

void AudioRecorder::stop_recording() {
  if (this->m_recorder->recorderState() == QMediaRecorder::RecordingState)
    this->m_recorder->stop();
}
