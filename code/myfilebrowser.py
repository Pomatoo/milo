# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\myfilebrowser.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FileBrowser(object):
    def setupUi(self, FileBrowser):
        FileBrowser.setObjectName("FileBrowser")
        FileBrowser.setWindowModality(QtCore.Qt.ApplicationModal)
        FileBrowser.resize(459, 352)
        FileBrowser.setMinimumSize(QtCore.QSize(459, 352))
        FileBrowser.setMaximumSize(QtCore.QSize(459, 352))
        FileBrowser.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        FileBrowser.setModal(False)
        self.cancel_btn = QtWidgets.QPushButton(FileBrowser)
        self.cancel_btn.setGeometry(QtCore.QRect(370, 320, 75, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.cancel_btn.setFont(font)
        self.cancel_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cancel_btn.setObjectName("cancel_btn")
        self.open_btn = QtWidgets.QPushButton(FileBrowser)
        self.open_btn.setGeometry(QtCore.QRect(270, 320, 75, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.open_btn.setFont(font)
        self.open_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.open_btn.setObjectName("open_btn")
        self.folder_path = QtWidgets.QComboBox(FileBrowser)
        self.folder_path.setGeometry(QtCore.QRect(10, 10, 401, 22))
        self.folder_path.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.folder_path.setEditable(True)
        self.folder_path.setObjectName("folder_path")
        self.home_btn = QtWidgets.QPushButton(FileBrowser)
        self.home_btn.setGeometry(QtCore.QRect(420, 10, 31, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.home_btn.setFont(font)
        self.home_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.home_btn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/home_btn/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(icon)
        self.home_btn.setObjectName("home_btn")
        self.listView = QtWidgets.QListView(FileBrowser)
        self.listView.setGeometry(QtCore.QRect(10, 40, 441, 271))
        self.listView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listView.setObjectName("listView")

        self.retranslateUi(FileBrowser)
        QtCore.QMetaObject.connectSlotsByName(FileBrowser)

    def retranslateUi(self, FileBrowser):
        _translate = QtCore.QCoreApplication.translate
        FileBrowser.setWindowTitle(_translate("FileBrowser", "File browser"))
        self.cancel_btn.setText(_translate("FileBrowser", "Cancel"))
        self.open_btn.setText(_translate("FileBrowser", "Open"))

import home_icon_rc
