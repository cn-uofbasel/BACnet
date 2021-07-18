import sys
from gui.main_window import MainWindow
from PyQt5 import QtWidgets as qtw

app = qtw.QApplication(sys.argv)
mainWindow = MainWindow(app)
app.exec()
