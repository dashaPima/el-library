from client.ui.userPage import Ui_UserWindow
from PyQt6 import QtWidgets, QtGui
import logging
logger = logging.getLogger(__name__)

# В критических местах
logger.debug("Starting network request...")

class UserWindow(QtWidgets.QMainWindow):
    def __init__(self, controller=None,network_client=None):
        super().__init__()
        self.ui = Ui_UserWindow()
        self.ui.setupUi(self)
        self.controller = controller
        self.network_client = network_client

        self.ui.tableView.clicked.connect(self.book_clicked)
        self.ui.btnWatchAllBooks.clicked.connect(self.load_books)
        self.ui.FindBook.clicked.connect(self.find_book)
        self.ui.FilterSearch.clicked.connect(self.handle_filter)
        self.ui.btnHistory.clicked.connect(self.load_history)
        self.ui.btnSelectedBooks.clicked.connect(self.load_favorites)
        self.ui.btnOpenProfile.clicked.connect(self.controller.show_profile)
        # Подключаем кнопку "Выход"
        self.ui.btnExit.clicked.connect(self.handle_exit)
        self.load_books()

    def load_books(self):
        # Отправляем запрос на сервер с действием "get_books"
        request = {"action": "get_books"}
        response = self.network_client.send_request(request)
        if response and response.get("status") == "ok":
            books = response.get("books", [])
            # Заполняем QTableView
            self.populate_table_books(books)
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось получить данные о книгах")

    def populate_table_books(self, books):
        model = QtGui.QStandardItemModel()
        # Устанавливаем заголовки столбцов
        model.setHorizontalHeaderLabels(["ID","Название", "Автор"])
        for book in books:
            id_title = QtGui.QStandardItem(str(book.get("id", "")))
            title_item = QtGui.QStandardItem(book.get("title", ""))
            author_item = QtGui.QStandardItem(book.get("author", ""))
            model.appendRow([id_title,title_item, author_item])
        self.ui.tableView.setModel(model)
        self.ui.tableView.resizeColumnsToContents()

    def populate_table_history(self,history):
        model = QtGui.QStandardItemModel()
        # Добавляем колонку для даты
        model.setHorizontalHeaderLabels(["ID", "Название", "Автор", "Дата просмотра"])
        for rec in history:
            full = rec.get("view_date", "")
            short = full.rsplit(":", 1)[0] if full else ""
            id_item    = QtGui.QStandardItem(str(rec.get("id", "")))
            title_item = QtGui.QStandardItem(rec.get("title", ""))
            author_item= QtGui.QStandardItem(rec.get("author", ""))
            date_item  = QtGui.QStandardItem(short)
            model.appendRow([id_item, title_item, author_item, date_item])
        self.ui.tableView.setModel(model)
        self.ui.tableView.resizeColumnsToContents()

    def book_clicked(self, index):
        selected_id = self.ui.tableView.model().index(index.row(), 0).data()
        print("Нажата книга с ID:", selected_id)
        self.controller.show_book_details(book_id=selected_id)

    def find_book(self):
        title = self.ui.inputSearch.text().strip().lower()
        if not title:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите название книги")
            return
        request = {"action": "find_book_by_title", "title": title}
        response = self.network_client.send_request(request)
        if response and response.get("status") == "ok":
            book = response["book"]
            self.populate_table_books([book])  # Можно отобразить найденную книгу в таблице
        else:
            QtWidgets.QMessageBox.information(self, "Результат", "Книга не найдена")

    def handle_filter(self):
        if self.controller:
            self.controller.show_filter(self)

    def load_history(self):
        if self.controller.current_user_id is None:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Сначала войдите в систему")
            return
        resp = self.network_client.send_request({
            "action": "get_history",
            "user_id": self.controller.current_user_id
        })
        if resp.get("status") == "ok":
            self.populate_table_history(resp["history"])
        else:
            QtWidgets.QMessageBox.information(self,"История","Нет записей!")

    def load_favorites(self):
        uid = self.controller.current_user_id
        if uid is None:
            return QtWidgets.QMessageBox.warning(self, "Ошибка", "Сначала войдите")
        resp = self.network_client.send_request({
            "action": "get_favorites",
            "user_id": uid
        })
        if resp.get("status") == "ok":
            self.populate_table_books(resp["books"])
        else:
            QtWidgets.QMessageBox.information(self, "Избранное", "Нет книг")

    def handle_exit(self):
        # Если контроллер передан, вызываем его метод для переключения на окно регистрации
        if self.controller:
            self.controller.show_login()
        self.close()

