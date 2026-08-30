QT       += core gui network pdf pdfwidgets multimedia websockets

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++17 precompile_header

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
    audioplayer.cpp \
    audiorecorder.cpp \
    chat.cpp \
    fileviewer.cpp \
    main.cpp \
    mainwindow.cpp \
    message.cpp \
    messagebox.cpp \
    messagewidget.cpp \
    networkmanager.cpp \
    scrollareawithresize.cpp

HEADERS += \
    audioplayer.h \
    audiorecorder.h \
    chat.h \
    fileviewer.h \
    mainwindow.h \
    message.h \
    messagebox.h \
    messagewidget.h \
    networkmanager.h \
    pch.h \
    scrollareawithresize.h

PRECOMPILED_HEADER = \
    pch.h

win32:RC_FILE = resources.rc

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

RESOURCES += \
    rc.qrc
