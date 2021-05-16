# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_link.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_addLinkDialog(object):
    def setupUi(self, addLinkDialog):
        addLinkDialog.setObjectName("addLinkDialog")
        addLinkDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        addLinkDialog.resize(392, 120)
        addLinkDialog.setMinimumSize(QtCore.QSize(392, 120))
        addLinkDialog.setMaximumSize(QtCore.QSize(392, 120))
        self.description_label = QtWidgets.QLabel(addLinkDialog)
        self.description_label.setGeometry(QtCore.QRect(10, 10, 91, 16))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.description_label.setFont(font)
        self.description_label.setObjectName("description_label")
        self.url_radioButton = QtWidgets.QRadioButton(addLinkDialog)
        self.url_radioButton.setGeometry(QtCore.QRect(10, 40, 61, 17))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.url_radioButton.setFont(font)
        self.url_radioButton.setObjectName("url_radioButton")
        self.folder_path_radioButton = QtWidgets.QRadioButton(addLinkDialog)
        self.folder_path_radioButton.setGeometry(QtCore.QRect(90, 40, 101, 17))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.folder_path_radioButton.setFont(font)
        self.folder_path_radioButton.setObjectName("folder_path_radioButton")
        self.description_inp = QtWidgets.QLineEdit(addLinkDialog)
        self.description_inp.setGeometry(QtCore.QRect(100, 10, 271, 20))
        self.description_inp.setObjectName("description_inp")
        self.path_inp = QtWidgets.QLineEdit(addLinkDialog)
        self.path_inp.setEnabled(True)
        self.path_inp.setGeometry(QtCore.QRect(10, 60, 371, 20))
        self.path_inp.setObjectName("path_inp")
        self.ok_btn = QtWidgets.QPushButton(addLinkDialog)
        self.ok_btn.setGeometry(QtCore.QRect(320, 90, 61, 25))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.ok_btn.setFont(font)
        self.ok_btn.setObjectName("ok_btn")
        self.close_btn = QtWidgets.QPushButton(addLinkDialog)
        self.close_btn.setGeometry(QtCore.QRect(10, 90, 61, 25))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.close_btn.setFont(font)
        self.close_btn.setObjectName("close_btn")

        self.retranslateUi(addLinkDialog)
        self.close_btn.clicked.connect(addLinkDialog.close)
        QtCore.QMetaObject.connectSlotsByName(addLinkDialog)

    def retranslateUi(self, addLinkDialog):
        _translate = QtCore.QCoreApplication.translate
        addLinkDialog.setWindowTitle(_translate("addLinkDialog", "Add Link"))
        self.description_label.setText(_translate("addLinkDialog", "Description:"))
        self.url_radioButton.setText(_translate("addLinkDialog", "URL"))
        self.folder_path_radioButton.setText(_translate("addLinkDialog", "Folder Path"))
        self.ok_btn.setText(_translate("addLinkDialog", "OK"))
        self.close_btn.setText(_translate("addLinkDialog", "Close"))


