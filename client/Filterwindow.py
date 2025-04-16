from client.ui.filterPage import Ui_FilterWindow
from PyQt6 import QtWidgets, QtGui, QtCore
import logging
logger = logging.getLogger(__name__)

class FilterWindow(QtWidgets.QMainWindow):
    # Сигнал для отправки отфильтрованных данных
    filters_applied = QtCore.pyqtSignal(list)

    def __init__(self, controller=None, network_client=None):
        super().__init__()
        self.ui = Ui_FilterWindow()
        self.ui.setupUi(self)
        self.controller = controller
        self.network_client = network_client

        self.ui.applyFilters.clicked.connect(self.apply_filters)

    def apply_filters(self):
        if self.ui.btnTitle.isChecked():
            criterion = "title"
        elif self.ui.btnAuthor.isChecked():
            criterion = "author"
        elif self.ui.btnYear.isChecked():
            criterion = "year"
        elif self.ui.btnGenre.isChecked():
            criterion = "genre"
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите критерий для поиска")
            return

        value = self.ui.inputSearch.text().strip()
        if not value:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите значение для поиска")
            return

        request = {"action": "find_books_by_filter", "criterion": criterion, "value": value}
        response = self.network_client.send_request(request)
        if response and response.get("status") == "ok":
            books = response.get("books", [])
            self.filters_applied.emit(books)
            self.close()
        else:
            QtWidgets.QMessageBox.information(self, "Результат", response.get("message", "Книги не найдены"))
