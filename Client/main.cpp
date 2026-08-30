#include <QApplication>

#include "mainwindow.h"

int main(int argc, char *argv[]) {
  QApplication app(argc, argv);

  CWindow window;

  app.setApplicationVersion("1.0");
  app.setOrganizationName("SamStyle-01");

  window.show();

  return app.exec();
}
