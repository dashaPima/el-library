import sys
import os
from PyQt6 import QtWidgets
from client.LogInWindow import LogInWindow
from client.RegistrationWindow import RegistrateWindow
from client.NetworkClient import NetworkClient
from client.AdminWindow import AdminWindow
from client.Filterwindow import FilterWindow
from client.UserWindow import UserWindow
from client.AddBookWindow import AddBookWindow
from client.OneBookWindow import OneBookWindow
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [CLIENT] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# В критических местах
logger.debug("Starting network request...")

if sys.platform == "win64":
    os.environ["QT_QPA_PLATFORM"] = "windows:dxvulkan=1"

class Controller:
    def __init__(self):
        self.network_client = NetworkClient()
        self.network_client.connect()
        # Создаем экземпляры окон без указания родительского виджета
        self.login_window = LogInWindow(controller=self,network_client=self.network_client)
        self.registrate_window = RegistrateWindow(controller=self,network_client=self.network_client)

        self.admin_window = AdminWindow(controller=self,network_client=self.network_client)
        self.user_window = UserWindow(controller=self,network_client=self.network_client)

        # Подключаем кнопки переключения
        self.login_window.ui.btnToRegistrationPage.clicked.connect(self.show_registration)
        self.registrate_window.ui.btnToLogInPage.clicked.connect(self.show_login)

        # Показываем окно авторизации по умолчанию
        self.show_login()

    def __del__(self):
        self.network_client.close()
        self.login_window.close()
        self.registrate_window.close()
        self.admin_window.close()
        self.user_window.close()

    def show_login(self):
        try:
            self.registrate_window.hide()
            if self.admin_window: self.admin_window.hide()
            if self.user_window: self.user_window.hide()
            self.login_window.show()
            self.login_window.ui.inputEmail.clear()
            self.login_window.ui.inputPassword.clear()
            self.login_window.ui.btnToRegistrationPage.clicked.connect(self.show_registration)
        except Exception as e:
            print("Ошибка при переключении на окно логина:", e)

    def show_filter(self, source):
        # source – окно, которое вызвало фильтр (AdminWindow или UserWindow)
        self.filter_window = FilterWindow(controller=self, network_client=self.network_client)
        self.filter_window.filters_applied.connect(lambda books: source.populate_table_books(books))

        self.filter_window.show()

    def show_registration(self):
        try:
            self.login_window.close()
            self.registrate_window.ui.btnToLogInPage.clicked.connect(self.show_login)
            self.registrate_window.show()
        except Exception as e:
            print("Ошибка при переключении на окно регистрации:", e)

    def show_add_book(self):
        self.add_book_window = AddBookWindow(controller=self, network_client=self.network_client)
        self.add_book_window.show()

    def show_book_details(self, book_id):
        # Запрашиваем данные о книге с сервера
        response = self.network_client.send_request({
            "action": "get_book_details",
            "book_id": book_id
        })
        print("Получен ответ:", response)
        if response["status"] == "ok":
            book_data = response["book"]
            self.book_window = OneBookWindow(controller=self, network_client=self.network_client)
            self.book_window.set_book_data(book_data)
            self.book_window.show()
        else:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Не удалось получить данные книги.")


def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
