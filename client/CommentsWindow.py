from client.ui.commentsPage import Ui_CommentsWindow
from PyQt6 import QtWidgets, QtGui
import logging
logger = logging.getLogger(__name__)

# В критических местах
logger.debug("Starting network request...")

class CommentsWindow(QtWidgets.QMainWindow):
    def __init__(self, controller=None,network_client=None):
        super().__init__()
        self.ui = Ui_CommentsWindow()
        self.ui.setupUi(self)
        self.controller = controller
        self.network_client = network_client

    def set_book(self,book_id,book_title):
        # подпишем название книги
        self.ui.booktitle.setText(book_title)

        # запросим комментарии с сервера
        resp = self.network_client.send_request({
            "action": "get_comments",
            "book_id": book_id
        })
        if resp.get("status") != "ok":
            QtWidgets.QMessageBox.warning(self, "Ошибка", resp.get("message", "Не удалось получить комментарии"))
            return
        comments = resp["comments"]  # список dict {email,comment,date}
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(["Почта", "Комментарий", "Дата"])
        for c in comments:
            dt = c["date"]
            dt = dt.rsplit(":", 1)[0]
            email_item = QtGui.QStandardItem(c["email"])
            text_item = QtGui.QStandardItem(c["comment"])
            date_item = QtGui.QStandardItem(dt)
            model.appendRow([email_item, text_item, date_item])

        self.ui.tableView.setModel(model)
        self.ui.tableView.resizeColumnsToContents()