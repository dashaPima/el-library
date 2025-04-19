import threading
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal, QObject
from client.ui.registratePage import Ui_RegistrateWindow
from .UserWindow import UserWindow


class SignalEmitter(QObject):
    registrationFinished = pyqtSignal(dict)

    def __init__(self):
        super().__init__()


class RegistrateWindow(QtWidgets.QMainWindow):
    def __init__(self, controller=None, network_client=None):
        super().__init__()
        self.ui = Ui_RegistrateWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Регистрация")
        self.controller = controller
        self.network_client = network_client
        #Создание сигнального объекта
        self.signal_emitter = SignalEmitter()

        # Подключение сигнала к слоту
        self.signal_emitter.registrationFinished.connect(self.handle_registration_response)

        self.ui.inputPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.ui.btnToLogInPage.clicked.connect(self.handle_open_login)
        self.ui.btnRegistrate.clicked.connect(self.handle_registrate)

    def handle_open_login(self):
        if self.controller:
            self.controller.show_login()

    def handle_registrate(self):
        email = self.ui.inputEmail.toPlainText().strip()
        password = self.ui.inputPassword.text().strip()
        if not email or not password:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите email и пароль")
            return

        request = {
                "action": "register_user",
                "email": email,
                "password": password
        }
        threading.Thread(target=self.send_registration_request, args=(request,), daemon=True).start()

    def send_registration_request(self, request):
        response = self.network_client.send_request(request)
        print("Ответ получен:", response)
        # Эмитим сигнал в основной поток
        self.signal_emitter.registrationFinished.emit(response)

    def handle_registration_response(self, response):
        print("Обработка ответа:", response)
        if response is None:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Ошибка соединения с сервером")
            return

        if response["status"] == 'ok':
            print("Регистрация прошла успешно")
            if "user_id" in response and self.controller:
                self.controller.current_user_id = response["user_id"]
            QtWidgets.QMessageBox.information(self, "Успех", response.get("message"))
            self.controller.user_window.show()
            self.close()
        else:
            print("Ошибка регистрации:", response.get("message"))
            QtWidgets.QMessageBox.warning(self, "Ошибка", response.get("message"))

