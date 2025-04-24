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
        self.book_id = None
        self.is_fav = False

        self.ui.addToFavorite.clicked.connect(self.toggle_favorite)
        self.document = QPdfDocument(self)
        self.ui.widget.setDocument(self.document)
        self.document.statusChanged.connect(self._on_pdf_status_changed)
        self.ui.addComment.clicked.connect(self.handle_add_comment)
        self.ui.watchComments.clicked.connect(self.open_comments)
        # wire exit button
        self.ui.btnExit.clicked.connect(self.close)

    def set_book_data(self, book_data):
        self.book_id = book_data["id"]
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
        resp = self.network_client.send_request({
            "action": "get_favorites",
            "user_id": self.controller.current_user_id
        })
        fav_ids = [b["id"] for b in resp.get("books", [])]
        self.is_fav = self.book_id in fav_ids
        self.ui.addToFavorite.setText(
            "Удалить из избранного" if self.is_fav else "В избранное"
        )

    def _on_pdf_status_changed(self, status):
        if status != QPdfDocument.Status.Ready:
            QtWidgets.QMessageBox.critical(self, "Ошибка загрузки", f"Статус PDF: {status.name}")

    def _open_full_pdf(self, event):
        if hasattr(self, "full_pdf_path") and os.path.exists(self.full_pdf_path):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(self.full_pdf_path))
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "PDF-файл не найден.")

    def toggle_favorite(self):
        uid, bid = self.controller.current_user_id, self.book_id
        if not uid or not bid:
            return QtWidgets.QMessageBox.warning(self, "Ошибка", "Неизвестный пользователь или книга")
        if not self.is_fav:
            req = {"action": "add_favorite", "user_id": uid, "book_id": bid}
        else:
            req = {"action": "remove_favorite", "user_id": uid, "book_id": bid}
        resp = self.network_client.send_request(req)
        if resp.get("status") == "ok":
            self.is_fav = not self.is_fav
            self.ui.addToFavorite.setText(
                "Удалить из избранного" if self.is_fav else "В избранное"
            )
            QtWidgets.QMessageBox.information(self, "✔", resp.get("message"))
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", resp.get("message"))

    def handle_add_comment(self):
        text = self.ui.commentInput.toPlainText().strip()
        if not text:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Комментарий не может быть пустым")
            return
        req = {
            "action": "add_comment",
            "user_id": self.controller.current_user_id,
            "book_id": self.book_id,
            "comment": text
        }
        resp = self.network_client.send_request(req)
        if resp.get("status") == "ok":
            QtWidgets.QMessageBox.information(self, "Спасибо", resp.get("message"))
            self.ui.commentInput.clear()
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", resp.get("message"))

    def open_comments(self):
        self.controller.show_comments(self.book_id, self.ui.titleBook.toPlainText())
