from client.ui.adminPage import Ui_AdminWindow
from PyQt6 import QtWidgets, QtGui, QtCore
import logging
logger = logging.getLogger(__name__)

# В критических местах
logger.debug("Starting network request...")

class AdminWindow(QtWidgets.QMainWindow):
    def __init__(self, controller=None, network_client=None):
        super().__init__()
        self.ui = Ui_AdminWindow()
        self.ui.setupUi(self)
        self.controller = controller
        self.network_client = network_client

        self.editing_mode = False

        self.ui.showAll.clicked.connect(self.load_books)
        self.ui.showAllAccount.clicked.connect(self.showAllUsers)
        self.ui.deleteBook.clicked.connect(self.handle_delete_book)
        self.ui.deleteAccount.clicked.connect(self.handle_delete_user)
        self.ui.editBook.clicked.connect(self.toggle_edit_mode)
        self.ui.btnSearch.clicked.connect(self.find_book)
        self.ui.filter.clicked.connect(self.handle_filter)
        self.ui.addBook.clicked.connect(self.handle_add_book)
        self.ui.btnExit.clicked.connect(self.handle_exit)

    def load_books(self):
        # Отправляем запрос на сервер с действием "get_books"
        request = {"action": "get_books"}
        response = self.network_client.send_request(request)
        if response and response.get("status") == "ok":
            books = response.get("books", [])
            self.populate_table_books(books)
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось получить данные о книгах")

    def populate_table_books(self, books):
        self.ui.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        model = QtGui.QStandardItemModel()
        # Устанавливаем заголовки столбцов
        model.setHorizontalHeaderLabels(["ID","Название", "Автор","Жанр", "Год","Кол-во страниц"])
        for book in books:
            id_item = QtGui.QStandardItem(str(book.get("id", "")))
            title_item = QtGui.QStandardItem(book.get("title", ""))
            author_item = QtGui.QStandardItem(book.get("author", ""))
            pages_item = QtGui.QStandardItem(str(book.get("pages", "")))
            genre_item = QtGui.QStandardItem(book.get("genre", ""))
            year_item = QtGui.QStandardItem(str(book.get("year", "")))
            model.appendRow([id_item,title_item, author_item,genre_item,year_item,pages_item])
        self.ui.tableView.setModel(model)
        self.ui.tableView.resizeColumnsToContents()

    def showAllUsers(self):
        request = {"action": "get_users"}
        response = self.network_client.send_request(request)
        if response and response.get("status") == "ok":
            users = response.get("users", [])
            # Заполняем QTableView
            self.populate_table_users(users)
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось получить данные о книгах")

    def populate_table_users(self, books):
        model = QtGui.QStandardItemModel()
        # Устанавливаем заголовки столбцов
        model.setHorizontalHeaderLabels(["ID","Почта"])
        for book in books:
            id_item = QtGui.QStandardItem(str(book.get("id", "")))
            email_item = QtGui.QStandardItem(book.get("email", ""))
            model.appendRow([id_item,email_item])
        self.ui.tableView.setModel(model)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def toggle_edit_mode(self):
        if not self.editing_mode:
            QtWidgets.QMessageBox.information(self, "Редактирование",
                                              "Теперь можно редактировать данные о книге. Внесите необходимые изменения, затем нажмите эту кнопку снова для сохранения.")
            # Разрешаем редактирование в таблице (например, по двойному клику)
            self.ui.tableView.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
            self.editing_mode = True
            self.ui.editBook.setText("Сохранить")
        else:
            confirmation = QtWidgets.QMessageBox.question(
                self, "Подтверждение",
                "Вы уверены, что хотите сохранить изменения?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if confirmation == QtWidgets.QMessageBox.Yes:
                # Получаем выбранную строку из QTableView
                selectionModel = self.ui.tableView.selectionModel()
                if not selectionModel.hasSelection():
                    QtWidgets.QMessageBox.warning(self, "Ошибка",
                                                  "Пожалуйста, выберите книгу, которую вы редактировали.")
                    return
                selected_indexes = selectionModel.selectedRows()
                if not selected_indexes:
                    QtWidgets.QMessageBox.warning(self, "Ошибка",
                                                  "Пожалуйста, выберите книгу, которую вы редактировали.")
                    return
                selected_row = selected_indexes[0].row()
                model = self.ui.tableView.model()
                book_id = model.index(selected_row, 0).data()
                title = model.index(selected_row, 1).data()
                author = model.index(selected_row, 2).data()
                genre = model.index(selected_row, 3).data()
                year = model.index(selected_row, 4).data()
                pages = model.index(selected_row, 5).data()
                request = {
                    "action": "edit_book",
                    "book_id": book_id,
                    "title": title,
                    "author": author,
                    "genre": genre,
                    "year": year,
                    "pages": pages
                }
                response = self.network_client.send_request(request)
                if response and response.get("status") == "ok":
                    QtWidgets.QMessageBox.information(self, "Успех", response.get("message"))
                    self.load_books()  # Обновление
                else:
                    QtWidgets.QMessageBox.warning(self, "Ошибка",
                                                  response.get("message", "Ошибка сохранения изменений"))
            self.ui.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            self.editing_mode = False
            self.ui.editBook.setText("Редактировать")

    def handle_delete_book(self):
        selectionModel = self.ui.tableView.selectionModel()
        if not selectionModel.hasSelection():
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите книгу для удаления")
            return
        # Получаем первую выбранную строку
        selected_indexes = selectionModel.selectedRows()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите книгу для удаления")
            return
        selected_row = selected_indexes[0].row()
        model = self.ui.tableView.model()
        # Предполагаем, что первая колонка содержит ID книги
        book_id = model.index(selected_row, 0).data()
        confirmation = QtWidgets.QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить книгу с ID {book_id}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirmation == QtWidgets.QMessageBox.Yes:
            request = {"action": "delete_book", "book_id": book_id}
            response = self.network_client.send_request(request)
            if response and response.get("status") == "ok":
                QtWidgets.QMessageBox.information(self, "Успех", response.get("message"))
                self.load_books()  # Обновление списка книг после удаления
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", response.get("message", "Ошибка удаления книги"))

    def handle_delete_user(self):
        selectionModel = self.ui.tableView.selectionModel()
        if not selectionModel.hasSelection():
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите пользователя для удаления")
            return
        # Получаем первую выбранную строку
        selected_indexes = selectionModel.selectedRows()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите пользователя для удаления")
            return
        selected_row = selected_indexes[0].row()
        model = self.ui.tableView.model()
        # Предполагаем, что первая колонка содержит ID книги
        user_id = model.index(selected_row, 0).data()
        confirmation = QtWidgets.QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить пользователя с ID {user_id}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirmation == QtWidgets.QMessageBox.Yes:
            request = {"action": "delete_user", "user_id": user_id}
            response = self.network_client.send_request(request)
            if response and response.get("status") == "ok":
                QtWidgets.QMessageBox.information(self, "Успех", response.get("message"))
                self.showAllUsers()
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", response.get("message", "Ошибка удаления пользователя"))

    def find_book(self):
        title = self.ui.inputField.text().strip().lower()
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

    def handle_add_book(self):
        if self.controller:
            self.controller.show_add_book()

    def handle_exit(self):
        if self.controller:
            self.controller.show_login()
        self.hide()

