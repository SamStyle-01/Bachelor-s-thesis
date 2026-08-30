#ifndef AUDIOPLAYER_H
#define AUDIOPLAYER_H

#include <QAudioOutput>
#include <QMediaPlayer>
#include <QObject>
#include <QUrl>

// Отвечает за воспроизведение аудиоответа от сервера. Проговаривает полученные
// сообщения, если включена такая функция.
class AudioPlayer : public QObject {
  // Медиаплеер. Управляет воспроизведением аудиозаписи.
  QMediaPlayer *m_player;
  // Воспроизводит аудиозапись через звуковую карту.
  QAudioOutput *m_audio_output;

public:
  explicit AudioPlayer(QWidget *parent = nullptr);
  // Включить аудиоответ от сервера. Воспроизводит голосовое сгенерированное
  // сообщение.
  void play_file(QString path_to_file = "audio/file.mp3");
};

#endif // AUDIOPLAYER_H
