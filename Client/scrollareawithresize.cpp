#include "scrollareawithresize.h"

ScrollAreaWithResize::ScrollAreaWithResize(QWidget *parent)
    : QScrollArea(parent) {}

void ScrollAreaWithResize::resizeEvent(QResizeEvent *event) {
  emit resized();
  QScrollArea::resizeEvent(event);
}
