from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
from client.ui.bookPage import Ui_BookWindow
import os, logging

logger = logging.getLogger(__name__)

class OneBookWindow(QtWidgets.QMainWindow):
    def __init__(self, controller=None, network_client=None):
        super().__init__()
        self.ui = Ui_BookWindow()
        self.ui.setupUi(self)
        self.controller = controller
        self.network_client = network_client

        self.document = QPdfDocument(self)
        self.ui.widget.setDocument(self.document)
        # опционально: чтобы отлавливать реальные ошибки
        self.document.statusChanged.connect(self._on_pdf_status_changed)

        # wire exit button
        self.ui.btnExit.clicked.connect(self.close)

    def set_book_data(self, book_data):
        self.ui.titleBook.setText(book_data["title"])
        self.ui.authorBook.setText(book_data["author"])
        self.ui.yearBook.setText(str(book_data["year"]))
        self.ui.genreBook.setText(book_data["genre"])
        self.ui.pagesBook.setText(str(book_data["pages"]))

        pdf_path = book_data.get("book", "")
        if pdf_path and os.path.exists(pdf_path):
            self.full_pdf_path = pdf_path  # сохраняем путь вручную
            self.document.load(pdf_path)  # просто загружаем PDF, путь не сохраняется внутри QPdfDocument
            # перехватываем клик по виджету
            self.ui.widget.mousePressEvent = self._open_full_pdf
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", f"Файл не найден: {pdf_path}")

    def _on_pdf_status_changed(self, status):
        if status != QPdfDocument.Status.Ready:
            QtWidgets.QMessageBox.critical(self, "Ошибка загрузки", f"Статус PDF: {status.name}")

    def _open_full_pdf(self, event):
        if hasattr(self, "full_pdf_path") and os.path.exists(self.full_pdf_path):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(self.full_pdf_path))
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "PDF-файл не найден.")

