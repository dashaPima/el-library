from client.ui.profilePage import Ui_ProfileWindow
from PyQt6 import QtWidgets, QtGui
import logging
logger = logging.getLogger(__name__)

# В критических местах
logger.debug("Starting network request...")

class ProfileWindow(QtWidgets.QMainWindow):
    def __init__(self, controller=None,network_client=None):
        super().__init__()
        self.ui = Ui_ProfileWindow()
        self.ui.setupUi(self)
        self.controller = controller
        self.network_client = network_client

        self.ui.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.ui.btnchangeOrSave.clicked.connect(self.handle_change_profile)
        self._edit_mode =False

    def set_data(self,user_id):
        resp = self.network_client.send_request({
            "action": "get_user_profile",
            "user_id": user_id
        })
        if resp.get("status") != "ok":
            QtWidgets.QMessageBox.warning(self, "Ошибка", resp.get("message", ""))
            return

        profile = resp["profile"]
        self.ui.email.setText(profile["email"])
        self.ui.password.setText(profile["password"])
        self.ui.email.setReadOnly(True)
        self.ui.password.setReadOnly(True)
        self.ui.btnchangeOrSave.setText("Изменить")

    def handle_change_profile(self):
        if not self._edit_mode:
            # переключаем в режим редактирования
            self._edit_mode = True
            self.ui.email.setReadOnly(False)
            self.ui.password.setReadOnly(False)
            self.ui.btnchangeOrSave.setText("Сохранить")
        else:
            # собираем новые данные
            new_email = self.ui.email.text().strip()
            new_password = self.ui.password.text().strip()

            if not new_email or not new_password:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Поля не могут быть пустыми")
                return

            # отправляем на сервер
            resp = self.network_client.send_request({
                "action": "edit_user",
                "user_id": self.controller.current_user_id,
                "email": new_email,
                "password": new_password
            })

            if resp.get("status") == "ok":
                QtWidgets.QMessageBox.information(self,
                                                  "Успех", resp.get("message", ""))
                # возвращаем назад «только чтение»
                self.ui.email.setReadOnly(True)
                self.ui.password.setReadOnly(True)
                self.ui.btnchangeOrSave.setText("Изменить")
                self._edit_mode = False
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", resp.get("message", ""))
