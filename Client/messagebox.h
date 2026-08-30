#ifndef MESSAGEBOX_H
#define MESSAGEBOX_H

#include <QMessageBox>

// Функция для вызова стилизованного сообщения в виде
// предупреждения/ошибки/информирования.
void message_box(QWidget *parent, QMessageBox::Icon icon, QString title,
                 QString text);

#endif // MESSAGEBOX_H
