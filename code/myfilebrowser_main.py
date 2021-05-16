#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   myfilebrowser_main.py
@Author  :   Liu Kaiyu
@Edited  :   Barry Lim @ 23/08/2019
'''
from myfilebrowser import Ui_FileBrowser
from PyQt5 import QtWidgets,QtCore,QtGui
import os



################################################################################################################################################
################################################################################################################################################
################################################################################################################################################


class MyFileDialog(QtWidgets.QDialog,Ui_FileBrowser):

    userprofile = os.environ['USERPROFILE']
    default_directory = [os.getcwd(),os.getenv("SystemDrive"),os.environ['USERPROFILE']]

    ################################################################################################################################################
    def __init__(self):
        QtWidgets.QDialog.__init__(self)

        self.setupUi(self)

        self.refresh_folder_dropdown()

        # Add an icon to this window
        _translate = QtCore.QCoreApplication.translate
        self.setWindowIcon(QtGui.QIcon(r'.\resources\milo.png'))

        # Connections
        self.cancel_btn.clicked.connect(lambda: self.close())
        self.home_btn.clicked.connect(self.show_home_page)
        self.open_btn.clicked.connect(self.open_btn_function)
        self.listView.doubleClicked.connect(self.dblClk)
        self.folder_path.currentTextChanged.connect(self.pathUpdated)

        # File System Model
        self.model = QtWidgets.QFileSystemModel()
        self.model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.AllEntries | QtCore.QDir.NoDot)
        self.show_home_page()

        self.selected_item = []
    
    ################################################################################################################################################
    def pathUpdated(self):
        self.listView.setRootIndex(self.model.setRootPath(self.folder_path.currentText().strip()))

    ################################################################################################################################################
    def dblClk(self, index):
        self.listView.setRootIndex(self.model.setRootPath(self.model.filePath(index)))
        self.folder_path.setCurrentText(os.path.abspath(self.model.filePath(index)))

    ################################################################################################################################################
    def show_home_page(self):
        
        self.listView.reset()

        self.model.setRootPath('/')
        self.listView.setModel(self.model)

        self.folder_path.setCurrentText(os.getcwd())
        self.pathUpdated()

    ################################################################################################################################################
    def open_btn_function(self):
        
        self.selected_item = []

        indexes = self.listView.selectionModel().selectedIndexes()

        if not indexes:
            QtWidgets.QMessageBox.about(self,' ',' Please select an item ')

        else:
            for i in indexes:
                if i.column() == 0:
                    path = self.model.filePath(i)
                    self.selected_item.append('%s'%path)
            
            self.accept()


    ################################################################################################################################################
    def refresh_folder_dropdown(self):
        for path in self.default_directory:
            self.folder_path.addItem(path)

    ################################################################################################################################################
    def exec_(self):
        super(MyFileDialog,self).exec_()

        return self.selected_item


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################


if __name__ == '__main__':

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(os.sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    file_dialog = MyFileDialog()
    file_dialog.show()

    app.exec_()     


