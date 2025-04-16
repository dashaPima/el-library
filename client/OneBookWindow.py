from client.ui.bookPage import Ui_BookWindow
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
import logging
import os
logger = logging.getLogger(__name__)

class OneBookWindow(QtWidgets.QMainWindow):
    def __init__(self, controller=None, network_client=None):
        super().__init__()
        self.ui = Ui_BookWindow()
        self.ui.setupUi(self)
        self.controller = controller
        self.network_client = network_client
        self.document = QPdfDocument()

    def set_book_data(self, book_data):
        self.ui.titleBook.setText(book_data.get("title", ""))
        self.ui.authorBook.setText(book_data.get("author", ""))
        self.ui.yearBook.setText(str(book_data.get("year", "")))
        self.ui.genreBook.setText(book_data.get("genre", ""))
        self.ui.pagesBook.setText(str(book_data.get("pages", "")))

        pdf_path = book_data.get("book", "")
        if pdf_path and os.path.exists(pdf_path):
            self.document.load(pdf_path)
            self.ui.widget.setDocument(self.document)

            # Сохраняем путь для открытия
            self.full_pdf_path = pdf_path

            # Добавим обработку клика по PDF — откроет документ внешне
            self.ui.widget.mousePressEvent = self.open_full_pdf
        else:
            logger.warning(f"PDF не найден: {pdf_path}")

    def open_full_pdf(self, event):
        if hasattr(self, "full_pdf_path") and os.path.exists(self.full_pdf_path):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(self.full_pdf_path))
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "PDF-файл не найден.")
