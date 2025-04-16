from client.ui.addBookPage import Ui_AddBookWindow
from PyQt6 import QtWidgets, QtGui, QtCore
import logging
logger = logging.getLogger(__name__)

class AddBookWindow(QtWidgets.QMainWindow):

    def __init__(self, controller=None, network_client=None):
        super().__init__()
        self.ui = Ui_AddBookWindow()
        self.ui.setupUi(self)
        self.controller = controller
        self.network_client = network_client

        self.ui.btnAddBook.clicked.connect(self.handle_add_book)

    def handle_add_book(self):
        file_path = self.ui.filePathInput.toPlainText().strip()
        title = self.ui.titleInput.toPlainText().strip()
        author = self.ui.authorInput.toPlainText().strip()
        year_text = self.ui.yearInput.toPlainText().strip()
        genre = self.ui.genreInput.toPlainText().strip()
        pages_text = self.ui.pagesInput.toPlainText().strip()

        if not file_path or not title or not author or not year_text or not genre or not pages_text:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return

        try:
            year = int(year_text)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Год издания должен быть числом.")
            return

        try:
            pages = int(pages_text)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Количество страниц должно быть числом.")
            return
        request = {
            "action": "add_book",
            "book_data": file_path,
            "title": title,
            "author": author,
            "pages": pages,
            "genre": genre,
            "year": year
        }
        response = self.network_client.send_request(request)
        if response and response.get("status") == "ok":
            QtWidgets.QMessageBox.information(self, "Успех", response.get("message"))
            # Если у контроллера есть доступ к окну администратора, обновляем список книг
            if self.controller and hasattr(self.controller, "admin_window"):
                self.controller.admin_window.load_books()
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", response.get("message", "Ошибка добавления книги"))

