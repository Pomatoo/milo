# -*- coding: utf-8 -*-
"""
@author: Kaiyu
"""
import os
from PyQt5 import QtWidgets,QtGui,QtCore
from overlay import Ui_overlay
from three_dialogs import HelpMenu,PreSet
from generators import FFMPEGGenerator,OverlayCMDGenerator
from overlay_thread import ConvertThread
from myfilebrowser_main import MyFileDialog


# This will be shown on UI
date_modified = '21/08/2019'

still_img_extensions = ['tif','tiff','png','jpeg','gif','exr','tga','jpg','jif']

################################################################################################################################################
# Customized Erros
class MyError(Exception):
    def __init__(self,message):
        self.message = message

################################################################################################################################################
# Define a global method, this will be used in Button class below
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
        self.setGeometry(QtCore.QRect(10, 30, 571, 111))
        self.setColumnCount(2)
        self.resizeRowsToContents()
        self.setHorizontalHeaderLabels(['File Name',' '])

        self.setColumnWidth(0,450)
        self.setColumnWidth(1,100)

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
class OverlayTool(QtWidgets.QMainWindow,Ui_overlay):
    
    userprofile = os.environ['USERPROFILE']

    local_book_path = userprofile + '\\Documents\\ffmpeg\\local_preset_book.txt'
    

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.refresh_local_preset()
        self.refresh_resolution_dropdown()
        
        # Instantiate and overwrite file list box 
        self.file_list = FileList(self)
        self.file_list.refresh_signal.connect(self.refresh_file_list)

        # UI date label
        global date_modified
        _translate = QtCore.QCoreApplication.translate
        self.update_label.setText(_translate("MainWindow", "Update: %s"%date_modified))
        self.setWindowIcon(QtGui.QIcon(r'.\resources\milo.png'))
        
        # Store files and cmds
        self.file_list_dd = {}
        self.cmd_list = []

        # Connections 
        self.input_browse.clicked.connect(lambda: self.browse_path(inp = True))
        self.output_browse.clicked.connect(lambda: self.browse_path(out = True))
        self.clear_btn.clicked.connect(self.clear)
        self.convert_btn.clicked.connect(self.convert_btn_function)
        self.close_btn.clicked.connect(lambda: self.close())
        self.output_folder_checkbox.stateChanged.connect(self.check_output_folder)


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

        # Converter thread
        self.threadpool = QtCore.QThreadPool()

        # Some generators needed 
        self.fmt_generator = FFMPEGGenerator()


    #############################################################################################################
    def refresh_resolution_dropdown(self):
        for i in range(10,1,-1):
            self.resolution_dropdown.addItem('%s'%(i*10)+'%')

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

        print(self.file_list_dd[file_name])
        self.file_list_dd[file_name]['identity'] = identity
        print(self.file_list_dd)


    ################################################################################################################################################
    def refresh_file_list(self):
        print('refresh signal received')

        self.file_list.setRowCount(len(self.file_list_dd.keys()))

        for index,each_file in enumerate(self.file_list_dd.keys()):
            file_name = QtWidgets.QTableWidgetItem(each_file)
            self.file_list.setItem(index,0,file_name)            #Format : (row,col,item)


    ################################################################################################################################################
    def check_output_folder(self):
        if self.output_folder_checkbox.isChecked():
            self.output_dropdown.clear()
            self.output_browse.setEnabled(False)
            self.output_dropdown.setEnabled(False)
        else:
            self.output_browse.setEnabled(True)
            self.output_dropdown.setEnabled(True)


    ################################################################################################################################################
    def refresh_preset_dropdown(self,PRESETS):
        self.preset_dropdown.clear()
        self.preset_dropdown.addItem('None')
        for each_set in sorted(PRESETS.keys()):
            self.preset_dropdown.addItem(each_set)
        print(self.PRESETS)

    ################################################################################################################################################
    # This function prompts user to choose input or output files, and display the file path.

    def browse_path(self,inp = False, out = False):
        path = ''
        if inp :
            file_dialog = MyFileDialog()
            path_list = file_dialog.exec_()
               
            if path_list:
                for path in path_list:
                    print(path)
                    self.add_files_to_list(path)
            
        elif out:
                path = QtWidgets.QFileDialog.getExistingDirectory(self, "Save", "/")
                
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
    def create_a_backend_thread(self):
        self.converter = ConvertThread()
        self.converter.signals.finished.connect(self.finish)
        self.converter.signals.percentage.connect(self.refresh_percentage)


    ################################################################################################################################################
    def clear(self):
        self.file_list.clearContents()
        self.file_list.setRowCount(1)
        self.file_list_dd = {}
       
    ################################################################################################################################################
    # This function checks all the files in file list, if all the files are still images, return True
    def all_still_img(self):
        num_of_files = self.file_list.count()
        still_img_count = 0
        for i in range(num_of_files):
            file_name = self.file_list.item(i).text()  
        
            global still_img_extensions
            if file_name.split('.')[-1] in still_img_extensions:
                still_img_count += 1
        
        return still_img_count == num_of_files 
            
    
    ################################################################################################################################################
    def check_errors(self):
        try:
            num_of_files = len(self.file_list_dd.keys())
            if not num_of_files:
                raise MyError(' File List Is Empty ! ')
            
        except MyError as e:
            QtWidgets.QMessageBox.about(self,' Warning ',e.message)
            
        else:
      
            try:
                    # Check a preset is selected 
                if self.preset_dropdown.currentText().strip() == 'None':
                    raise MyError(' Please select a Pre-Set ')

 
            except MyError as e:
                print(e.message)
                QtWidgets.QMessageBox.about(self,' Warning ',e.message)
                
            else:
                return True


    ################################################################################################################################################
    def prevent_misclikcing(self,finish=False):
        self.input_browse.setEnabled(finish)
        self.output_group.setEnabled(finish)
        self.information_group.setEnabled(finish)
        self.preser_group.setEnabled(finish)
        self.convert_btn.setEnabled(finish)
        self.clear_btn.setEnabled(finish)



    ################################################################################################################################################
    def convert_btn_function(self):
        
        if self.check_errors():

            self.create_a_backend_thread()

            # Pass variables to backend thread

            # PRESET
            selected_preset = self.preset_dropdown.currentText().strip()
            if selected_preset == 'None':
                parameter_list = []
            else:
                parameter_list = self.PRESETS[selected_preset].split(',')
            self.converter.parameter_list = parameter_list

            # OVERLAY 
            project_name = self.project_inp.text().strip()
            author = self.author_inp.text().strip()
            task = self.task_inp.text().strip()
            version = self.version_inp.text().strip()
            self.converter.overlay_info_list = [project_name,author,task,version]

            # OUTPUT EXTENSION
            self.converter.output_extension = self.extension_inp.text().strip()

            self.converter.file_list_dd = self.file_list_dd
            self.converter.use_original_output = self.output_folder_checkbox.isChecked()
            if not self.output_folder_checkbox.isChecked():
                self.converter.alt_output_folder = self.output_dropdown.currentText().strip()
            
            self.converter.compress_resolution_ratio = int(self.resolution_dropdown.currentText().strip('%'))/100
            

            self.progressBar.setRange(0,0)
            self.write_local_preset_book()      # Store author,project,version and title 
            self.prevent_misclikcing()
            self.threadpool.start(self.converter)
        
    ################################################################################################################################################
    def refresh_percentage(self,index,percentage):            
        row = int(index)
        self.file_list.setItem(row,1,QtWidgets.QTableWidgetItem(str(percentage)+'%'))


    ################################################################################################################################################
    def finish(self,signal):
        if signal == 'done':
            self.progressBar.setRange(0,1)
            self.progressBar.setValue(1)
            QtWidgets.QMessageBox.about(self,' ','Done !')

            self.clear_btn.setEnabled(True)
            self.clear_btn.clicked.connect(lambda: self.prevent_misclikcing(finish=True))
        
        else:
            row = int(signal)
            self.file_list.setItem(row,1,QtWidgets.QTableWidgetItem('completed'))


    ################################################################################################################################################
    def refresh_local_preset(self):
        
        if self.read_local_preset_book():
            project_name,author_name,task_name,version = self.read_local_preset_book()
            
            self.project_inp.setText(project_name)
            self.author_inp.setText(author_name)
            self.task_inp.setText(task_name)
            self.version_inp.setText(version)
            

    ################################################################################################################################################
    def read_local_preset_book(self):
        if os.path.exists(self.local_book_path):
            f = open(self.local_book_path,'r')
            content_ls = f.read().strip().split(',')
            f.close()

            project_name = content_ls[0]
            author_name = content_ls[1]
            task_name = content_ls[2]
            version = content_ls[3]
            return project_name,author_name,task_name,version
            
        else:
            return None
            
            
    ################################################################################################################################################
    def write_local_preset_book(self):
        project_name = self.project_inp.text().strip()
        author_name = self.author_inp.text().strip()
        task_name = self.task_inp.text().strip()
        version = self.version_inp.text().strip()
        
        content_ls = [project_name,author_name,task_name,version]
        content = ','.join(content_ls)
        
        if os.path.exists(self.local_book_path):
            f = open(self.local_book_path,'w+')
            f.write(content)
            f.close()
        else:
            os.mkdir(os.path.split(self.local_book_path)[0])
            f = open(self.local_book_path,'w+')
            f.write(content)
            f.close()
    
    #############################################################################################################
    def closeEvent(self,event): 
        reply = QtWidgets.QMessageBox.question(self,'Warning','Are you sure to Exit',QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.help_menu_dialog.close()
            self.preset_dialog.close()
            self.close()
        else:
            event.ignore()



if __name__ == '__main__':
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(os.sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    overlay = OverlayTool()
    overlay.show()
    app.exec_()






