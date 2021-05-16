#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   splice_main.py
@Author  :   Liu Kaiyu 
'''


import os
from PyQt5 import QtWidgets,QtCore,QtGui
from splice import Ui_Splice
from three_dialogs import HelpMenu,PreSet
from generators import FFMPEGGenerator,OverlayCMDGenerator,SpliceCMDGenerator
from splice_thread import SpliceThread
from myfilebrowser_main import MyFileDialog



# This will be shown on UI
date_modified = '30/08/2019'

# Hard code some commonly used image extensions
still_img_extensions = ['tif','tiff','png','jpeg','gif','exr','tga','jpg','jif']

################################################################################################################################################
# Customized Erros
class MyError(Exception):
    def __init__(self,message):
        self.message = message

################################################################################################################################################
# Define a global method, this will be used in FileList class below
def split_folder_file(file_path):
    folder,file_name_with_extension = os.path.split(file_path)
    file_name,extension = os.path.splitext(file_name_with_extension)

    return folder,file_name,extension


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
class FileList(QtWidgets.QTableWidget):

    refresh_signal = QtCore.pyqtSignal()

    def __init__(self,parent):
        super(FileList,self).__init__(parent)
        self.setAcceptDrops(True)

        # Some Settings, copy from UI codes
        # Default has one row, and two columns ("file name" and "duration" )
        self.setGeometry(QtCore.QRect(10, 50, 431, 141))
        self.setColumnCount(2)
        self.setRowCount(1)
        self.resizeRowsToContents()
        self.setHorizontalHeaderLabels(['File Name','Duration'])
        self.setColumnWidth(0,300)
        self.verticalHeader().setDefaultSectionSize(15)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setGridStyle(QtCore.Qt.NoPen)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    ##############################################################################################################
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    ##############################################################################################################
    def dragEnterEvent(self, e):
        m = e.mimeData()
        # File path is considered as URL
        if m.hasUrls():
            e.accept()
        else:
            e.ignore()

    ##############################################################################################################
    def dropEvent(self, e):
        m = e.mimeData()
        if m.hasUrls():
            for file in m.urls():
                file_path = file.toLocalFile() 
                
                file_name = split_folder_file(file_path)[1]
                extension = split_folder_file(file_path)[2]

                self.parent().file_list_dd[file_name + extension] = {'file_path':'%s'%file_path}
                self.parent().get_file_identity(file_path,file_name + extension)
                self.parent().check_valid_image_sequence(file_name + extension)

            self.refresh_signal.emit()
            print('refresh signal emitted')






################################################################################################################################################
################################################################################################################################################
################################################################################################################################################

class SpliceTool(QtWidgets.QMainWindow,Ui_Splice):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        # Re-write drop button
        self.file_list = FileList(self)
        self.file_list.refresh_signal.connect(self.refresh_file_list)

        # Update date label 
        global date_modified
        _translate = QtCore.QCoreApplication.translate
        self.update_label.setText(_translate("MainWindow", "Update: %s"%date_modified))
        self.setWindowIcon(QtGui.QIcon(r'.\resources\milo.png'))   

        # Connections
        self.input_browse.clicked.connect(lambda: self.browse_path(inp = True))
        self.output_browse.clicked.connect(lambda: self.browse_path(out = True))
        self.clear_btn.clicked.connect(self.clear_file_list_box)
        self.up_btn.clicked.connect(lambda: self.move_file('up'))
        self.down_btn.clicked.connect(lambda: self.move_file('down'))
        self.close_btn.clicked.connect(lambda: self.close())
        self.delete_btn.clicked.connect(self.delete_item)
        self.splice_btn.clicked.connect(self.splice_btn_function)
        self.overlay_checkbox.stateChanged.connect(self.use_overlay)
        self.file_list.itemClicked.connect(self.check_is_still_img)
        self.ok_btn.clicked.connect(self.ok_btn_function)
        self.clear_all_btn.clicked.connect(self.clear_all)
       
        # Store files and cmds
        self.file_list_dd = {}
        self.cmd_list = []

        # Initialize tool button menu and setting
        menu = QtWidgets.QMenu(self)
        self.help_Act = QtWidgets.QAction('Help',self)
        self.pre_setting_Act = QtWidgets.QAction('Pre Sets',self)
        
        menu.addAction(self.help_Act)
        menu.addAction(self.pre_setting_Act)
        self.toolButton.setMenu(menu)

        # Connect dialogs to mainwindows 
        self.help_menu_dialog = HelpMenu()
        self.help_Act.triggered.connect(lambda: self.help_menu_dialog.show())
        
        self.preset_dialog = PreSet()
        self.pre_setting_Act.triggered.connect(lambda: self.preset_dialog.show())
        
        self.PRESETS = self.preset_dialog.read_preset_book()
        self.refresh_preset_dropdown(self.PRESETS)
        self.preset_dialog.refresh_signal.connect(lambda:  self.refresh_preset_dropdown(self.preset_dialog.read_preset_book()))

        self.fmt_generator = FFMPEGGenerator()
        self.splice_cmd_generator = SpliceCMDGenerator()

        # Thread
        self.threadpool = QtCore.QThreadPool()


    ################################################################################################################################################
    def create_a_thread(self):
        self.splice_tool = SpliceThread()
        self.splice_tool.signals.finished.connect(self.finish)

    ################################################################################################################################################
    def browse_path(self,inp = False, out = False):
        path = ''
        
        supported_video_fmt = self.fmt_generator.get_muxing_supported_fmt()
        
        formats = ''
        for each_fmt in supported_video_fmt:
            formats += '%s(*.%s);;'%(each_fmt.strip(),each_fmt.strip())   
     
        if inp :
            file_dialog = MyFileDialog()
            path_list = file_dialog.exec_()
                
            if path_list:
                for path in path_list:
                    print(path)
                    self.add_files_to_list(path)
            
        elif out:
                path = QtWidgets.QFileDialog.getSaveFileName(self,'Choose File','.','%s'%formats)[0]
                
                if path != '':
                    path = path.replace('/','\\')
                    self.output_dropdown.clear()
                    self.output_dropdown.addItem(path)

    ################################################################################################################################################
    # Add files to file list box, and store the file path to 'file_list_dd'
    def add_files_to_list(self,file_path):            
        file_name = os.path.split(file_path)[1].strip()
        print(file_name)
    
        self.file_list_dd[file_name] = {'file_path':'%s'%file_path}
        self.get_file_identity(file_path,file_name)

        # Check valid image sequence 
        self.check_valid_image_sequence(file_name)

        self.refresh_file_list()


    ################################################################################################################################################
    def check_valid_image_sequence(self,file_name):

        if self.file_list_dd[file_name]['identity'] == 'image_sequence':
            folder_path = self.file_list_dd[file_name]['file_path']
            name_set = set()
            for each_img in os.listdir(folder_path):
                img_without_extension = os.path.splitext(each_img)[0]
                
                i = 1 
                temp = []
                while True:

                    if i == len(img_without_extension):
                        break

                    if img_without_extension[-i].isdigit():
                        i += 1
                        continue
                    else:
                        temp.insert(0,img_without_extension[:-i])
                        break
                
                image_sequence_name = ''.join(i for i in temp)
                name_set.add(image_sequence_name)
            
            if len(name_set) > 1:
                QtWidgets.QMessageBox.about(self,' Warning ','%s has more than one image sequence'%file_name )
                del self.file_list_dd[file_name]


    ################################################################################################################################################
    def get_file_name_from_list(self,row_content):
        if '|' in row_content:
            file_name = row_content.split('|')[1].strip()
        else:
            file_name = row_content.strip()

        return file_name

    ################################################################################################################################################
    def refresh_file_list(self):
        print('refresh signal received')

        self.file_list.setRowCount(len(self.file_list_dd.keys()))

        for index,each_file in enumerate(self.file_list_dd.keys()):
            file_name = QtWidgets.QTableWidgetItem(each_file)
            self.file_list.setItem(index,0,file_name)            #Format : (row,col,item)
        

            if self.file_list_dd[each_file]['identity'] == 'still_image':
                if 'duration' in self.file_list_dd[each_file]:
                    duration = QtWidgets.QTableWidgetItem(self.file_list_dd[each_file]['duration'])
                else:
                    duration = QtWidgets.QTableWidgetItem('!')
                self.file_list.setItem(index,1,duration)
            
            else:
                NA = QtWidgets.QTableWidgetItem('NA')
                self.file_list.setItem(index,1,NA)

  


    ################################################################################################################################################
    def clear_file_list_box(self):
        self.file_list.clearContents()
        self.file_list.setRowCount(1)
        self.duration_inp.clear()
        self.file_list_dd ={}
        self.cmd_list = []

    ################################################################################################################################################
    def clear_all(self):
        self.clear_file_list_box()
        self.output_dropdown.clear()
        self.progressBar.setValue(0)

    #############################################################################################################
    def use_overlay(self):
        if self.overlay_checkbox.isChecked():
            self.overlay_group.setEnabled(True)
        else:
            self.overlay_group.setEnabled(False)

    ################################################################################################################################################
    def refresh_preset_dropdown(self,PRESETS):
        self.preset_dropdown.clear()
        self.preset_dropdown.addItem('None')
        
        for each_set in sorted(PRESETS.keys()):
            self.preset_dropdown.addItem(each_set)
        print(self.PRESETS)

    ################################################################################################################################################
    def finish(self,signal):
        if signal == 'done':
            self.progressBar.setRange(0,1)
            self.progressBar.setValue(1)
            QtWidgets.QMessageBox.about(self,' ','Done !')
            self.prevent_misclicking(finish=True)
 

    #############################################################################################################
    def closeEvent(self,event): 
        '''
        overwrite closeEvent, pop a comfirmation window before closing 
        '''
        reply = QtWidgets.QMessageBox.question(self,'Warning','Are you sure to Exit',QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.help_menu_dialog.close()
            self.preset_dialog.close()
            self.close()
        else:
            event.ignore()


    #############################################################################################################
    def move_file(self,direction):
        selected_row = self.file_list.currentRow()

        # If no row has been selected, return value is -1 
        if selected_row == -1 :
            QtWidgets.QMessageBox.about(self,' ','Please select a file !')   
        else:
            file_name = self.file_list.item(selected_row,0).text()
            duration = self.file_list.item(selected_row,1).text()

            if direction == 'up' and selected_row != 0:
                self.file_list.insertRow(selected_row-1)
                self.file_list.setItem(selected_row-1,0,QtWidgets.QTableWidgetItem(file_name))
                self.file_list.setItem(selected_row-1,1,QtWidgets.QTableWidgetItem(duration))
                self.file_list.removeRow(selected_row+1)
                self.file_list.setCurrentCell(selected_row-1,0)

            elif direction == 'down' and selected_row != len(self.file_list_dd.keys())-1:
                self.file_list.insertRow(selected_row+2)
                self.file_list.setItem(selected_row+2,0,QtWidgets.QTableWidgetItem(file_name))
                self.file_list.setItem(selected_row+2,1,QtWidgets.QTableWidgetItem(duration))
                self.file_list.removeRow(selected_row)
                self.file_list.setCurrentCell(selected_row+1,0)

            
    ################################################################################################################################################
    def delete_item(self):
        selected_row = self.file_list.currentRow()
        
        if selected_row == -1 :
            QtWidgets.QMessageBox.about(self,' ','Please select a item !')   
            
        else:    
            file_name = self.file_list.item(selected_row,0).text()
            
            reply = QtWidgets.QMessageBox.question(self,'Warning','Are you sure to delete [%s]?'%file_name,QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            
            if reply == QtWidgets.QMessageBox.Yes:
                del self.file_list_dd[file_name]
                self.duration_inp.clear()

                self.file_list.removeRow(selected_row)
                print(self.file_list_dd)


    ################################################################################################################################################
    def get_file_identity(self,file_path,file_name):
        global still_img_extensions
        if os.path.isfile(file_path):
            if file_name.split('.')[-1].strip().lower() in still_img_extensions:
                identity = 'still_image'
            else:
                identity = 'video'
        elif os.path.isdir(file_path):
            identity = 'image_sequence'
        else:
            QtWidgets.QMessageBox.about(self,' ',' Unknown File ')   

        print('%s is %s'%(file_path,identity))

        self.file_list_dd[file_name]['identity'] = identity
        print(self.file_list_dd)


    ################################################################################################################################################
    # Check if a file is a still image
    def check_is_still_img(self):
        global still_img_extensions

        self.duration_inp.clear()
        selected_row = self.file_list.currentRow()
        file_name = self.file_list.item(selected_row,0).text()

        if file_name.split('.')[-1].strip().lower() in still_img_extensions:
            
            self.duration_inp.setEnabled(True)
            self.ok_btn.setEnabled(True)
            
            if 'duration' in self.file_list_dd[file_name].keys():
                self.duration_inp.setText(self.file_list_dd[file_name]['duration'])

        else:
            
            self.duration_inp.setEnabled(False)
            self.ok_btn.setEnabled(False)
    
            
    ################################################################################################################################################
    def ok_btn_function(self):
        if not self.duration_inp.text().strip().isdigit():
            QtWidgets.QMessageBox.about(self,' ERROR ',' Please input a valid duration ')   
        elif self.duration_inp.text().strip() == '0':
            QtWidgets.QMessageBox.about(self,' ERROR ',' Duration must be larger than zero ')   
        else:
            selected_row = self.file_list.currentRow()
            if selected_row == -1:
                QtWidgets.QMessageBox.about(self,' ERROR ',' Please select a file ')   
            else:
                file_name = self.file_list.item(selected_row,0).text()
                self.file_list_dd[file_name]['duration']= self.duration_inp.text().strip()
                for obj in self.file_list.findItems(file_name,QtCore.Qt.MatchExactly):
                    self.file_list.setItem(obj.row(),1,QtWidgets.QTableWidgetItem(self.duration_inp.text().strip()))

                self.duration_inp.clear()
            
            print(self.file_list_dd)

            #self.refresh_file_list()

    ################################################################################################################################################
    def get_resolution(self):
        w = self.w_inp.text().strip()
        h = self.h_inp.text().strip()
        resolution = w + 'x' + h

        return resolution

    ################################################################################################################################################
    def splice_btn_function(self):
        if self.check_errors():

            self.create_a_thread()

            # Create a sequence list
            num_of_files = self.file_list.rowCount()
            sequence_list = []
            for i in range(num_of_files):
                file_name = self.file_list.item(i,0).text()
                sequence_list.append(file_name)
            print('file list in GUI is : \n %s'%sequence_list)
            

            # Get selcected preset parameters
            selected_preset = self.preset_dropdown.currentText()
            parameter_list = self.PRESETS[selected_preset].split(',')


            # Pass values to back end thread 
            
            if self.overlay_checkbox.isChecked():
                print('overlay is checked')
                self.splice_tool.overlay_flag = True

                project_name = self.project_inp.text().strip()
                author = self.author_inp.text().strip()
                task = self.task_inp.text().strip()
                version = self.version_inp.text().strip()  

                self.splice_tool.overlay_info_list = [project_name,author,task,version]

            self.splice_tool.preset_parameter_list = parameter_list
            self.splice_tool.output_file = self.output_dropdown.currentText().strip()
            self.splice_tool.target_resolution = self.get_resolution()
            self.splice_tool.sequence_list = sequence_list
            self.splice_tool.file_list_dd = self.file_list_dd

            self.progressBar.setRange(0,0)
            self.threadpool.start(self.splice_tool)
            self.prevent_misclicking()

    ################################################################################################################################################
    # Disable some buttons when it is in splicing process
    def prevent_misclicking(self,finish=False):
        self.output_group.setEnabled(finish)
        self.input_browse.setEnabled(finish)
        self.preser_group.setEnabled(finish)
        self.file_list.setEnabled(finish)
        self.clear_btn.setEnabled(finish)
        self.delete_btn.setEnabled(finish)
        self.duration_inp.setEnabled(finish)
        self.ok_btn.setEnabled(finish)
        self.overlay_checkbox.setEnabled(finish)
        self.splice_btn.setEnabled(finish)
        self.overlay_group.setEnabled(finish)
        self.clear_all_btn.setEnabled(finish)
        self.use_overlay()

    ################################################################################################################################################
    def check_errors(self):
        
        try:
            num_of_files = len(self.file_list_dd.keys())
            print('%s files in file list'%num_of_files)
            if not num_of_files:
                raise MyError(' File list is empty ! ')
            
        except MyError as e:
            QtWidgets.QMessageBox.about(self,' Warning ',e.message)
            
        else:
            try:
                
                if not self.output_dropdown.currentText().strip():
                    raise MyError(' Please specify output file ')

                if self.preset_dropdown.currentText().strip() == 'None':
                    raise MyError(' Please select a Pre-Set ')
                
                if not self.w_inp.text().strip().isdigit():
                    raise MyError(' Please input a valid resolution Width')

                if not self.h_inp.text().strip().isdigit():
                    raise MyError(' Please input a valid resolution Height')

                for i in range(num_of_files):
                    file_name = self.file_list.item(i,0).text()
                    # Identity is at index 1 {file name:[path,identity]}
                    identity = self.file_list_dd[file_name]['identity']

                    # Specific duration must be assigned to still images
                    if identity == 'still_image':
                        # If still image is not assigned with a duration
                        if 'duration' not in self.file_list_dd[file_name].keys():
                            raise MyError(' Please assign a duration for File %s '%file_name)
                        
                        # Check if duration is a digit 
                        elif not self.file_list_dd[file_name]['duration'].isdigit():
                            raise MyError(' Still image %s has invalid duration '%file_name)

                    else:
                        continue

            except MyError as e:
                print(e.message)
                QtWidgets.QMessageBox.about(self,' Warning ',e.message)
                
            else:
                return True







if __name__ == '__main__':
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(os.sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    splice_tool = SpliceTool()
    splice_tool.show()
    app.exec_()

















