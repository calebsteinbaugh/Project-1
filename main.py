import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from proj1_mainwindow import Ui_login_window
from logic import LoginController

def main():
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    ui = Ui_login_window()
    ui.setupUi(window)
    
    
    controller = LoginController(ui, window)
    
    window.show()
    app.exec() 

    
if __name__ == '__main__':
    main()