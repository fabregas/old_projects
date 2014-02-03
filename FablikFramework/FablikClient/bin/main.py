#!/usr/bin/python

import sys
from PyQt4 import Qt
from mainWindow import MainWindow


if __name__ == '__main__':
    main_app = Qt.QApplication(sys.argv)

    main_window = MainWindow()

    main_app.setActiveWindow(main_window)


    main_app.exec_()

