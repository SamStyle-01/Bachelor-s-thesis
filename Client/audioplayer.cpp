#include "audioplayer.h"

AudioPlayer::AudioPlayer(QWidget *parent /*= nullptr*/) : QObject(parent) {
  this->m_player = new QMediaPlayer();
  this->m_audio_output = new QAudioOutput();

  this->m_player->setAudioOutput(m_audio_output);
}

void AudioPlayer::play_file(QString path_to_file /*= "audio/file.mp3"*/) {
  // Устанавливается абсолютный путь к файлу.
  QString absolutePath = QDir::currentPath() + "/" + path_to_file;
  // Устанавливается источник аудиоплеера для воспроизведения аудиофайла.
  this->m_player->setSource(QUrl::fromLocalFile(absolutePath));

  this->m_player->play();
}
