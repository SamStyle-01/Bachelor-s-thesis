#ifndef FILEVIEWER_H
#define FILEVIEWER_H

#include "pch.h"

#include <QPdfDocument>
#include <QPdfView>

// Отвечает за отображение PDF-файлов, поступающих с сервера.
class FileViewer : public QPdfView {
  // Виджет отображения PDF-документа.
  QPdfDocument *m_document;
  // Масштаб приближения отображения PDF-файла
  double m_zoom;

public:
  explicit FileViewer(QWidget *parent);
  // Загрузить PDF-файл в m_document.
  void load_file(QString path);
  // Подгоняет отображение PDF-файла по ширине, чтобы поместился
  // в виджет.
  void fit_to_width();
  // Увеличивает масштаб отображения PDF-файла.
  void zoom_plus();
  // Уменьшает масштаб отображения PDF-файла.
  void zoom_minus();
  // Устанавливает масштаб отображения PDF-файла по умолчанию.
  void reset_zoom();

protected:
  void resizeEvent(QResizeEvent *event) override;
};

#endif // FILEVIEWER_H
