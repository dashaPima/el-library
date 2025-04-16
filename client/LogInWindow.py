from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, QTimer, QThread
from client.ui.logInPage import Ui_LogInWindow
import logging
logger = logging.getLogger(__name__)

# В критических местах
logger.debug("Starting network request...")

logging.basicConfig(level=logging.INFO)


class SignalEmitter(QObject):
    loginFinished = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

class LoginThread(QThread):
    finished = pyqtSignal(dict)
    def __init__(self, client, request, parent=None):  # Добавлен parent
        super().__init__(parent)  # Инициализируем QThread
        self.client = client
        self.request = request

    def run(self):
        try:
            response = self.client.send_request(self.request)
            if not isinstance(response, dict):
                raise ValueError("Неверный формат ответа")
            self.finished.emit(response)
        except Exception as e:
            self.finished.emit({
                "status": "error",
                "message": f"Ошибка: {str(e)}"
            })

class LogInWindow(QtWidgets.QMainWindow):
    def __init__(self, controller=None, network_client=None):
        super().__init__()
        self.ui = Ui_LogInWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Авторизация")
        self.controller = controller
        self.network_client = network_client

        # Создаем эмиттер сигналов для безопасного взаимодействия между потоками
        self.signal_emitter = SignalEmitter()
        self.signal_emitter.loginFinished.connect(self.handle_login_response)

        # Настройка интерфейса
        self.ui.inputPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.ui.logIn.clicked.connect(self.handle_login)
        self.ui.btnToRegistrationPage.clicked.connect(self.handle_open_registration)

    @pyqtSlot()
    def handle_login(self):
        email = self.ui.inputEmail.toPlainText().strip()
        password = self.ui.inputPassword.text().strip()
        account_type = self.ui.accountType.currentText()

        if not email or not password:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        # Формируем запрос в зависимости от типа аккаунта
        request = {
            "action": "login_admin" if account_type == "Администратор" else "login_user",
            "email": email,
            "password": password,
            "account_type": account_type  # Сохраняем тип аккаунта в запросе
        }

        # Запускаем отдельный поток для обработки запроса
        self.login_thread = LoginThread(self.network_client, request,parent=self)
        self.login_thread.finished.connect(self.handle_login_response)
        self.login_thread.start()

    def send_login_request(self, request):
        try:
            response = self.network_client.send_request(request)
            print("Ответ получен:", response)
        except Exception as e:
            response = {
                "status": "error",
                "message": f"Connection error: {str(e)}",
                "account_type": request.get("account_type")
            }
            print(f"Ошибка при отправке запроса: {e}")

        # Эмитим сигнал в основной поток
        self.signal_emitter.loginFinished.emit(response or {})

    @QtCore.pyqtSlot(dict)
    def handle_login_response(self, response):
        print("DEBUG: обработка ответа:", response)
        if self.isHidden():  # Если окно уже закрыто, игнорируем ответ
            return

        if response.get("status") == "ok":
            account_type = response.get("account_type", "")
            # Используем задержку, чтобы дать время GUI обработать текущий метод
            QTimer.singleShot(100, lambda: self.open_role_window(account_type))
        else:
            error = response.get("message", "Unknown error")
            QtWidgets.QMessageBox.critical(self, "Ошибка", error)

    def open_role_window(self, role):
        try:
            self.hide()
            # Создаем новое окно
            if role == "Администратор":
                self.controller.admin_window.show()
            else:
                self.controller.user_window.show()

        except Exception as e:
            logging.error(f"Window error: {str(e)}")
            # В случае ошибки показываем сообщение
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось открыть окно: {str(e)}")

    @pyqtSlot()
    def handle_open_registration(self):
        try:
            if self.controller:
                # Показываем окно регистрации
                self.controller.show_registration()
                # Закрываем текущее окно
                self.close()
        except Exception as e:
            logging.error(f"Registration error: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка перехода к регистрации: {str(e)}")
