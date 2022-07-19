import sys

from PyQt5.QtWidgets import QApplication

from interface.window import Window


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = Window()
    mainWindow.show()
    sys.exit(app.exec_()) 

