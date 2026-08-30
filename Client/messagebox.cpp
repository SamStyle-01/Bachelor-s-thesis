#include "messagebox.h"

void message_box(QWidget *parent, QMessageBox::Icon icon, QString title,
                 QString text) {
  auto msg_box = new QMessageBox(parent);
  msg_box->setStyleSheet("color: #551133;");
  msg_box->setText(text);
  msg_box->setWindowTitle(title);
  msg_box->setIcon(icon);
  msg_box->exec();
}
