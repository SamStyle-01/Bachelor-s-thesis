#ifndef SCROLLAREAWITHRESIZE_H
#define SCROLLAREAWITHRESIZE_H

#include <QScrollArea>
#include <QWidget>

// Отвечает за работу прокручиваемой области чата с сообщениями.
class ScrollAreaWithResize : public QScrollArea {
  Q_OBJECT
public:
  explicit ScrollAreaWithResize(QWidget *parent);

protected:
  void resizeEvent(QResizeEvent *event) override;

signals:
  void resized();
};

#endif // SCROLLAREAWITHRESIZE_H
