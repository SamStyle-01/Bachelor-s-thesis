#ifndef AUDIORECORDER_H
#define AUDIORECORDER_H

#include <QObject>

#include "messagebox.h"
#include "pch.h"

// Осуществляет аудиозапись голосовых запросов пользователя к серверу.
class AudioRecorder : public QObject {
  Q_OBJECT
  QMediaCaptureSession m_capture_session;
  QAudioInput *m_audio_input;
  QMediaRecorder *m_recorder;

public:
  explicit AudioRecorder(QObject *parent = nullptr);
  ~AudioRecorder();

public slots:
  void start_recording(const QString &filePath);
  void stop_recording();

signals:
  void recordingFinished();
};

#endif // AUDIORECORDER_H
