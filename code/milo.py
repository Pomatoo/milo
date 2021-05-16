# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'milo.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(380, 177)
        MainWindow.setMinimumSize(QtCore.QSize(380, 177))
        MainWindow.setMaximumSize(QtCore.QSize(380, 177))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.logo_label = QtWidgets.QLabel(self.centralwidget)
        self.logo_label.setGeometry(QtCore.QRect(0, -30, 211, 101))
        self.logo_label.setObjectName("logo_label")
        self.ffmpeg_label = QtWidgets.QLabel(self.centralwidget)
        self.ffmpeg_label.setGeometry(QtCore.QRect(290, 10, 81, 16))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.ffmpeg_label.setFont(font)
        self.ffmpeg_label.setObjectName("ffmpeg_label")
        self.update_label = QtWidgets.QLabel(self.centralwidget)
        self.update_label.setGeometry(QtCore.QRect(290, 30, 71, 16))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.update_label.setFont(font)
        self.update_label.setObjectName("update_label")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 70, 361, 80))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.splicing_btn = QtWidgets.QPushButton(self.groupBox)
        self.splicing_btn.setEnabled(True)
        self.splicing_btn.setGeometry(QtCore.QRect(250, 20, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.splicing_btn.setFont(font)
        self.splicing_btn.setObjectName("splicing_btn")
        self.converter_btn = QtWidgets.QPushButton(self.groupBox)
        self.converter_btn.setGeometry(QtCore.QRect(30, 20, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.converter_btn.setFont(font)
        self.converter_btn.setObjectName("converter_btn")
        self.overlay_btn = QtWidgets.QPushButton(self.groupBox)
        self.overlay_btn.setGeometry(QtCore.QRect(140, 20, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.overlay_btn.setFont(font)
        self.overlay_btn.setObjectName("overlay_btn")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Three In One"))
        self.logo_label.setText(_translate("MainWindow", "<html><head/><body><p><img src=\":/logo_small/logo_small.png\"/></p></body></html>"))
        self.ffmpeg_label.setText(_translate("MainWindow", "FFMPEG TOOL"))
        self.update_label.setText(_translate("MainWindow", "29/07/2019"))
        self.splicing_btn.setText(_translate("MainWindow", "Splicing"))
        self.converter_btn.setText(_translate("MainWindow", "Converter"))
        self.overlay_btn.setText(_translate("MainWindow", "Overlay"))


import logo_small_rc
