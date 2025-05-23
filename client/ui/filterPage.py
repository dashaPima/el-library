# Form implementation generated from reading ui file 'filterPage.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_FilterWindow(object):
    def setupUi(self, FilterWindow):
        FilterWindow.setObjectName("FilterWindow")
        FilterWindow.resize(318, 354)
        FilterWindow.setStyleSheet("background-color: rgb(202, 200, 255);\n"
"")
        self.centralwidget = QtWidgets.QWidget(parent=FilterWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_6 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(-30, 20, 171, 31))
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(16)
        font.setBold(False)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.groupBox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(20, 70, 191, 161))
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(11)
        font.setBold(True)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.btnAuthor = QtWidgets.QRadioButton(parent=self.groupBox)
        self.btnAuthor.setGeometry(QtCore.QRect(10, 60, 95, 20))
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(11)
        font.setBold(False)
        self.btnAuthor.setFont(font)
        self.btnAuthor.setObjectName("btnAuthor")
        self.btnYear = QtWidgets.QRadioButton(parent=self.groupBox)
        self.btnYear.setGeometry(QtCore.QRect(10, 90, 151, 20))
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(11)
        self.btnYear.setFont(font)
        self.btnYear.setObjectName("btnYear")
        self.btnGenre = QtWidgets.QRadioButton(parent=self.groupBox)
        self.btnGenre.setGeometry(QtCore.QRect(10, 120, 95, 20))
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(11)
        self.btnGenre.setFont(font)
        self.btnGenre.setObjectName("btnGenre")
        self.btnTitle = QtWidgets.QRadioButton(parent=self.groupBox)
        self.btnTitle.setGeometry(QtCore.QRect(10, 30, 131, 20))
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(10)
        self.btnTitle.setFont(font)
        self.btnTitle.setObjectName("btnTitle")
        self.applyFilters = QtWidgets.QPushButton(parent=self.centralwidget)
        self.applyFilters.setGeometry(QtCore.QRect(12, 260, 291, 41))
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(14)
        self.applyFilters.setFont(font)
        self.applyFilters.setStyleSheet("background-color: rgb(99, 101, 255);\n"
"color: rgb(255, 255, 255);\n"
"border-radius:10%")
        self.applyFilters.setObjectName("applyFilters")
        self.inputSearch = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.inputSearch.setGeometry(QtCore.QRect(110, 20, 191, 41))
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(11)
        self.inputSearch.setFont(font)
        self.inputSearch.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"border-radius:10%")
        self.inputSearch.setObjectName("inputSearch")
        FilterWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=FilterWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 318, 22))
        self.menubar.setObjectName("menubar")
        FilterWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=FilterWindow)
        self.statusbar.setObjectName("statusbar")
        FilterWindow.setStatusBar(self.statusbar)

        self.retranslateUi(FilterWindow)
        QtCore.QMetaObject.connectSlotsByName(FilterWindow)

    def retranslateUi(self, FilterWindow):
        _translate = QtCore.QCoreApplication.translate
        FilterWindow.setWindowTitle(_translate("FilterWindow", "Фильтр поиска"))
        self.label_6.setText(_translate("FilterWindow", "Поиск"))
        self.groupBox.setTitle(_translate("FilterWindow", "Искать по"))
        self.btnAuthor.setText(_translate("FilterWindow", "Автору"))
        self.btnYear.setText(_translate("FilterWindow", "Году издания"))
        self.btnGenre.setText(_translate("FilterWindow", "Жанру"))
        self.btnTitle.setText(_translate("FilterWindow", "Названию"))
        self.applyFilters.setText(_translate("FilterWindow", "Применить"))
        self.inputSearch.setPlaceholderText(_translate("FilterWindow", "ввод данных"))
