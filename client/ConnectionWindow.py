from PyQt6 import QtWidgets, QtGui, QtCore
from client.ui.connectionPage import Ui_ConnectionWindow
from client.NetworkClient import NetworkClient

class ConnectionWindow(QtWidgets.QMainWindow):
    def __init__(self, controller=None):
        super().__init__()
        self.ui = Ui_ConnectionWindow()
        self.ui.setupUi(self)
        self.controller = controller

        #network_client будет создан по нажатию
        self.ui.pushButton.clicked.connect(self.handle_connect)

    def handle_connect(self):
        host = self.ui.lineEdit.text().strip() or '127.0.0.1'
        try:
            port = int(self.ui.lineEdit_2.text().strip())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Порт должен быть числом")
            return

        # создаём и пробуем соединиться
        self.controller.network_client = NetworkClient(host=host, port=port)
        self.controller.network_client.connect()
        if self.controller.network_client.connected:
            self.controller.on_connected()
            self.close()
        else:
            # спросим, пытаться ли с настройками по умолчанию
            reply = QtWidgets.QMessageBox.question(
                self, "Не удалось подключиться",
                f"Не удалось достучаться до {host}:{port}.\n"
                "Попробовать 127.0.0.1:9000?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self.controller.network_client = NetworkClient()  # localhost:9000
                self.controller.network_client.connect()
                if self.controller.network_client.connected:
                    self.controller.on_connected()
                    self.close()
                else:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Не удалось подключиться и по умолчанию")
