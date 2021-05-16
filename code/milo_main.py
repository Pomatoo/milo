# -*- coding: utf-8 -*-
"""
@author: KAIYU
"""


import os
from PyQt5 import QtCore, QtGui, QtWidgets
from milo import Ui_MainWindow
import converter_main
import overlay_main
import splice_main


# This will be shown on UI
date_modified = '30/08/2019'



class MainWindow(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        global date_modified
        _translate = QtCore.QCoreApplication.translate
        self.update_label.setText(_translate("MainWindow", "%s"%date_modified))
        self.setWindowIcon(QtGui.QIcon(r'.\resources\milo.png'))

        # Instantiate 3 dialogs
        self.converter_window = converter_main.ConverterTool()
        self.overlay_window = overlay_main.OverlayTool()
        self.splice_window = splice_main.SpliceTool()
    
        self.converter_btn.clicked.connect(lambda: self.show_sub_window('converter'))
        self.overlay_btn.clicked.connect(lambda: self.show_sub_window('overlay'))
        self.splicing_btn.clicked.connect(lambda: self.show_sub_window('splice'))


    def show_sub_window(self,window_title):
        if window_title == 'converter':
            self.converter_window.preset_dialog.refresh_preset_list(self.converter_window.preset_dialog.read_preset_book())
            self.converter_window.refresh_preset_dropdown(self.converter_window.preset_dialog.read_preset_book())
            self.converter_window.show()
        elif window_title == 'overlay':
            self.overlay_window.preset_dialog.refresh_preset_list(self.overlay_window.preset_dialog.read_preset_book())
            self.overlay_window.refresh_preset_dropdown(self.overlay_window.preset_dialog.read_preset_book())
            self.overlay_window.show()
        elif window_title == 'splice':
            self.splice_window.preset_dialog.refresh_preset_list(self.splice_window.preset_dialog.read_preset_book())
            self.splice_window.refresh_preset_dropdown(self.splice_window.preset_dialog.read_preset_book())
            self.splice_window.show()
        
        self.showMinimized()
        

    def closeEvent(self,event): 
        reply = QtWidgets.QMessageBox.question(self,'Warning','Are you sure to Exit',QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            
            # Close everything, including sub-windows 
            os.sys.exit(0)    
            self.close() 
        else:
            event.ignore()
    




if __name__ == '__main__':
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(os.sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    main_window = MainWindow()
    
    main_window.show()
    app.exec_()     

                        
