#include "fileviewer.h"

FileViewer::FileViewer(QWidget *parent) : QPdfView(parent) {
  this->m_document = new QPdfDocument(this);
  this->setPageMode(QPdfView::PageMode::MultiPage);

  QPalette palette = this->palette();
  palette.setBrush(QPalette::Dark, QColor("#dedeaf"));

  this->setPalette(palette);
  this->m_zoom = 1.0f;
}

void FileViewer::load_file(QString path) {
  this->m_document->load(path);
  this->setDocument(this->m_document);
  this->fit_to_width();
}

void FileViewer::fit_to_width() {
  if (!m_document || m_document->pageCount() == 0)
    return;

  QSizeF page_size = m_document->pagePointSize(0);
  int view_width = viewport()->width() / 1.4 * m_zoom;

  if (page_size.width() == 0)
    return;

  qreal zoom = view_width / page_size.width();

  setZoomMode(QPdfView::ZoomMode::Custom);
  setZoomFactor(zoom);
}

void FileViewer::resizeEvent(QResizeEvent *event) {
  QPdfView::resizeEvent(event);
  fit_to_width();
}

void FileViewer::zoom_plus() {
  if (this->m_zoom < 1.7)
    this->m_zoom += 0.1;
}

void FileViewer::zoom_minus() {
  if (this->m_zoom > 0.6)
    this->m_zoom -= 0.1;
}

void FileViewer::reset_zoom() { this->m_zoom = 1; }
