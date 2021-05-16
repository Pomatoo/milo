# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'help_menu.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_HelpDialog(object):
    def setupUi(self, HelpDialog):
        HelpDialog.setObjectName("HelpDialog")
        HelpDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        HelpDialog.resize(426, 241)
        HelpDialog.setMinimumSize(QtCore.QSize(426, 241))
        HelpDialog.setMaximumSize(QtCore.QSize(426, 241))
        self.guide_btn = QtWidgets.QPushButton(HelpDialog)
        self.guide_btn.setGeometry(QtCore.QRect(190, 170, 141, 23))
        self.guide_btn.setObjectName("guide_btn")
        self.ffmpeg_doc_btn = QtWidgets.QPushButton(HelpDialog)
        self.ffmpeg_doc_btn.setGeometry(QtCore.QRect(10, 170, 141, 23))
        self.ffmpeg_doc_btn.setObjectName("ffmpeg_doc_btn")
        self.link_list = QtWidgets.QListWidget(HelpDialog)
        self.link_list.setGeometry(QtCore.QRect(10, 30, 321, 131))
        self.link_list.setObjectName("link_list")
        self.add_btn = QtWidgets.QPushButton(HelpDialog)
        self.add_btn.setGeometry(QtCore.QRect(340, 30, 61, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.add_btn.setFont(font)
        self.add_btn.setObjectName("add_btn")
        self.delete_btn = QtWidgets.QPushButton(HelpDialog)
        self.delete_btn.setGeometry(QtCore.QRect(340, 60, 61, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.delete_btn.setFont(font)
        self.delete_btn.setObjectName("delete_btn")
        self.open_btn = QtWidgets.QPushButton(HelpDialog)
        self.open_btn.setGeometry(QtCore.QRect(340, 140, 61, 23))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.open_btn.setFont(font)
        self.open_btn.setObjectName("open_btn")
        self.links_label = QtWidgets.QLabel(HelpDialog)
        self.links_label.setGeometry(QtCore.QRect(10, 10, 61, 16))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.links_label.setFont(font)
        self.links_label.setObjectName("links_label")
        self.close_btn = QtWidgets.QPushButton(HelpDialog)
        self.close_btn.setGeometry(QtCore.QRect(10, 210, 61, 25))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.close_btn.setFont(font)
        self.close_btn.setObjectName("close_btn")

        self.retranslateUi(HelpDialog)
        self.close_btn.clicked.connect(HelpDialog.close)
        QtCore.QMetaObject.connectSlotsByName(HelpDialog)

    def retranslateUi(self, HelpDialog):
        _translate = QtCore.QCoreApplication.translate
        HelpDialog.setWindowTitle(_translate("HelpDialog", "Help"))
        self.guide_btn.setText(_translate("HelpDialog", "step-by-step guide"))
        self.ffmpeg_doc_btn.setText(_translate("HelpDialog", "FFMPEG documentations"))
        self.add_btn.setText(_translate("HelpDialog", "Add"))
        self.delete_btn.setText(_translate("HelpDialog", "Delete"))
        self.open_btn.setText(_translate("HelpDialog", "Open"))
        self.links_label.setText(_translate("HelpDialog", "Links"))
        self.close_btn.setText(_translate("HelpDialog", "Close"))


