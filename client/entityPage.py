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
from client.CommentsWindow import CommentsWindow
from client.ProfileWindow import ProfileWindow
from client.ConnectionWindow import ConnectionWindow
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
        self.network_client: NetworkClient | None = None
        self.current_user_id: int | None = None

        # сначала окно подключения
        self.connection_window = ConnectionWindow(controller=self)
        self.connection_window.show()

    def on_connected(self):
        # инициализируем остальные окна, когда соединение ок
        self.login_window = LogInWindow(controller=self, network_client=self.network_client)
        self.registrate_window = RegistrateWindow(controller=self, network_client=self.network_client)
        self.admin_window = AdminWindow(controller=self, network_client=self.network_client)
        self.user_window = UserWindow(controller=self, network_client=self.network_client)

        # связываем переходы
        self.login_window.ui.btnToRegistrationPage.clicked.connect(self.show_registration)
        self.registrate_window.ui.btnToLogInPage.clicked.connect(self.show_login)

        # показываем логин
        self.show_login()

    def __del__(self):
        self.network_client.close()
        self.login_window.close()
        self.registrate_window.close()
        self.admin_window.close()
        self.user_window.close()

    def show_login(self):
        # спрячем все кроме логина
        for w in (self.registrate_window, self.admin_window, self.user_window):
            w.hide()
        self.login_window.ui.inputEmail.clear()
        self.login_window.ui.inputPassword.clear()
        self.login_window.show()

    def show_filter(self, source):
        # source – окно, которое вызвало фильтр (AdminWindow или UserWindow)
        self.filter_window = FilterWindow(controller=self, network_client=self.network_client)
        self.filter_window.filters_applied.connect(lambda books: source.populate_table_books(books))

        self.filter_window.show()

    def show_registration(self):
        self.login_window.hide()
        self.registrate_window.show()

    def show_add_book(self):
        self.add_book_window = AddBookWindow(controller=self, network_client=self.network_client)
        self.add_book_window.show()

    def show_book_details(self, book_id):
        if self.current_user_id is not None:
            self.network_client.send_request({
                "action": "add_history",
                "user_id": self.current_user_id,
                "book_id": book_id
            })
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

    def show_comments(self,book_id, book_title):
        self.comments_window = CommentsWindow(
            controller=self,
            network_client=self.network_client
        )
        self.comments_window.set_book(book_id, book_title)
        self.comments_window.show()

    def show_profile(self):
        self.profile_window = ProfileWindow(
            controller=self,
            network_client=self.network_client
        )
        self.profile_window.set_data(self.current_user_id)
        self.profile_window.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    controller = Controller()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
