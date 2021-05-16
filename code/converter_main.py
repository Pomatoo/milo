# -*- coding: utf-8 -*-
"""
@author: KAIYU
"""

from PyQt5 import QtWidgets,QtCore,QtGui
import os
from converter import *
from three_dialogs import HelpMenu,PreSet
from generators import FFMPEGGenerator,CMDGenerator,OverlayCMDGenerator
from converter_thread import ConvertThread
from myfilebrowser_main import MyFileDialog



# This will be shown on UI
date_modified = '30/08/2019'


################################################################################################################################################
# Customized Erros
class MyError(Exception):
    def __init__(self,message):
        self.message = message
 
################################################################################################################################################
# Define a global method, this will be used in FileList class below
# This function splits a full folder path into folder , file name and extension
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
        self.setGeometry(QtCore.QRect(20, 139, 591, 111))
        self.setColumnCount(2)
        self.resizeRowsToContents()
        self.setHorizontalHeaderLabels(['File Name',' '])
        self.setColumnWidth(0,450)
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

class ConverterTool(QtWidgets.QMainWindow,Ui_converter):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)     

        # Instantiate a ffmpeg generator
        # It can get codec list, resolution of video/image and totoal frame of a video 
        self.ffmpeg_generator = FFMPEGGenerator()
        
        self.refresh_codecs_list()
        self.refresh_resolution_dropdown()

        # Store files and cmds
        self.file_list_dd = {}

        # Update modified date information in UI
        global date_modified
        _translate = QtCore.QCoreApplication.translate
        self.update_label.setText(_translate("MainWindow", "Update: %s"%date_modified))
        self.setWindowIcon(QtGui.QIcon(r'.\resources\milo.png'))

        # Instantiate and overwrite file list box 
        self.file_list = FileList(self)
        self.file_list.refresh_signal.connect(self.refresh_file_list)

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
        self.preset_dropdown.activated[str].connect(lambda: self.apply_selected_preset(self.preset_dropdown.currentText()))
        self.preset_dialog.refresh_signal.connect(lambda:  self.refresh_preset_dropdown(self.preset_dialog.read_preset_book()))
        
        
        # Connections
        self.input_browse.clicked.connect(lambda: self.browse_path(inp = True))
        self.output_browse.clicked.connect(lambda: self.browse_path(out = True))
        self.convert_btn.clicked.connect(self.convert_btn_function)
        self.progressBar.setRange(0,1)
        self.clear_btn.clicked.connect(self.clear)
        self.output_folder_checkbox.stateChanged.connect(self.check_output_folder)
        self.close_btn.clicked.connect(lambda: self.close())
        self.overlay_checkbox.stateChanged.connect(self.use_overlay)


        self.threadpool = QtCore.QThreadPool()


    #############################################################################################################
    def refresh_resolution_dropdown(self):
        for i in range(10,1,-1):
            self.resolution_dropdown.addItem('%s'%(i*10)+'%')

    #############################################################################################################
    # Enable overlay input if 'Use Overlay' is checked
    def use_overlay(self):
        if self.overlay_checkbox.isChecked():
            self.overlay_group.setEnabled(True)
        else:
            self.overlay_group.setEnabled(False)

    ################################################################################################################################################
    # Identities are 'video' and 'image_sequence'
    def get_file_identity(self,file_path,file_name):

        if os.path.isfile(file_path):
            identity = 'video'
        elif os.path.isdir(file_path):
            identity = 'image_sequence'
        else:
            QtWidgets.QMessageBox.about(self,' ',' Unknown File ')   

        print('%s is %s'%(file_path,identity))

        self.file_list_dd[file_name]['identity'] = identity
        print(self.file_list_dd)

    #############################################################################################################
    def refresh_file_list(self):
        print('refresh signal received')

        self.file_list.setRowCount(len(self.file_list_dd.keys()))

        for index,each_file in enumerate(self.file_list_dd.keys()):
            file_name = QtWidgets.QTableWidgetItem(each_file)
            self.file_list.setItem(index,0,file_name)            #Format : (row,col,item)

    #############################################################################################################
    # rewrite closeEvent function, it will pop out a message before exit
    def closeEvent(self,event): 
        reply = QtWidgets.QMessageBox.question(self,'Warning','Are you sure to Exit',QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.clear()
            self.help_menu_dialog.close()
            self.preset_dialog.close()
            self.close() 
    
        else:
            event.ignore()

    ################################################################################################################################################
    # Enable 'browse' button if 'Output to original folder' is unchecked
    def check_output_folder(self):
        if self.output_folder_checkbox.isChecked():
            self.output_dropdown.clear()
            self.output_browse.setEnabled(False)
            self.output_dropdown.setEnabled(False)
        else:
            self.output_browse.setEnabled(True)
            self.output_dropdown.setEnabled(True)

    ################################################################################################################################################
    def clear(self):
        self.time_label.setText('None')
        self.file_list.clearContents()
        self.file_list.setRowCount(1)

        self.file_list_dd = {}

    ################################################################################################################################################
    def refresh_preset_dropdown(self,PRESETS):
        self.preset_dropdown.clear()
        self.preset_dropdown.addItem('None')
        for each_set in sorted(PRESETS.keys()):
            self.preset_dropdown.addItem(each_set)

    ################################################################################################################################################
    def apply_selected_preset(self,set_name):
        if set_name == 'None':
            self.frame_rate_inp.setText('(auto)')
            self.crf_inp.setText('(auto)')
            self.audio_bitrate_inp.setText('(auto)')
            self.refresh_codecs_list()
        
        else:
            parameters = self.PRESETS[set_name].split(',')

            self.frame_rate_inp.setText(parameters[0])
            self.crf_inp.setText(parameters[1])
            self.audio_bitrate_inp.setText(parameters[2])
            
            self.refresh_codecs_list()
            acodec_index =  self.acodecs_dropdown.findText(parameters[3])  
            self.acodecs_dropdown.setCurrentIndex(acodec_index)
            
            vcodec_index = self.vcodecs_dropdown.findText(parameters[4])
            self.vcodecs_dropdown.setCurrentIndex(vcodec_index)

    ################################################################################################################################################
    def estimate_time(self,est_time):
        # est_time is a float number, unit is second
        # If est_time == 0, means convertion finished 
        if est_time == 0:  
            self.time_label.setText('Done')
        
        else:
            # convert second to (xx m xx s)
            mins = int(est_time//60)
            seconds = round(est_time - mins*60,1)
            if mins == 0 and seconds < 20:
                self.time_label.setText('Finishing...')
            else:
                self.time_label.setText('%s m %s s'%(mins,seconds))
        
    ################################################################################################################################################
    def refresh_percentage(self,index,percentage):            
        row = int(index)
        self.file_list.setItem(row,1,QtWidgets.QTableWidgetItem(str(percentage)+'%'))

    ################################################################################################################################################
    def create_a_backend_thread(self):
        self.converter = ConvertThread()
        self.converter.signals.finished.connect(self.finish)
        self.converter.signals.percentage.connect(self.refresh_percentage)
        self.converter.signals.time_info.connect(self.estimate_time)

    ################################################################################################################################################
    # Receive signal from back end thread
    def finish(self,signal):
        if signal == 'done':
            self.progressBar.setRange(0,1)
            self.progressBar.setValue(1)
            self.time_label.setText('None')
            QtWidgets.QMessageBox.about(self,' ','Done !')

            self.clear_btn.setEnabled(True)
            self.clear_btn.clicked.connect(lambda: self.prevent_misclikcing(finish=True))
            
        else:
            row = int(signal)
            self.file_list.setItem(row,1,QtWidgets.QTableWidgetItem('completed'))


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
    # This function prompts user to choose input or output files
    def browse_path(self,inp = False, out = False):
        path = ''
     
        if inp:
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
    # Get codec lists and updated in UI dropdowns
    def refresh_codecs_list(self):
        self.acodecs_dropdown.clear()
        self.vcodecs_dropdown.clear()
         
        codec_list = self.ffmpeg_generator.get_codecs()
        
        self.v_codecs_ls,self.a_codecs_ls = self.ffmpeg_generator.split_v_a_codecs(codec_list)
                
        self.acodecs_dropdown.addItem('Default')
        for i in self.a_codecs_ls:
            self.acodecs_dropdown.addItem(i[2])
                
        self.vcodecs_dropdown.addItem('Default')
        for i in self.v_codecs_ls:
            self.vcodecs_dropdown.addItem(i[2])
 
            
################################################################################################################################################
    def convert_btn_function(self):
        
        if self.check_errors() :

            self.create_a_backend_thread()

            # Pass variables to backend thread 
            self.converter.overlay_flag = self.overlay_checkbox.isChecked()

            project_name = self.project_inp.text()
            author = self.author_inp.text()
            task = self.task_inp.text()
            version = self.version_inp.text()

            self.converter.overlay_info_list = [project_name,author,task,version]


            frame_rate = self.frame_rate_inp.text()
            crf = self.crf_inp.text()
            audio_bitrate = self.audio_bitrate_inp.text()    
            selected_acodec = self.acodecs_dropdown.currentText()
            selected_vcodec = self.vcodecs_dropdown.currentText()

            self.converter.parameter_list = [frame_rate,crf,audio_bitrate,selected_acodec,selected_vcodec]

            self.converter.output_extension = self.extension_inp.text()
            self.converter.extra_cmd = self.extra_cmd()
            self.converter.file_list_dd = self.file_list_dd
            self.converter.use_original_ouput = self.output_folder_checkbox.isChecked()
            self.converter.compress_resolution_ratio = int(self.resolution_dropdown.currentText().strip('%'))/100
            print('passed resolution is %s'%self.converter.compress_resolution_ratio)

            self.prevent_misclikcing()

            self.time_label.setText('Estimating')
            self.progressBar.setRange(0,0)

            if not self.output_folder_checkbox.isChecked():
                self.converter.alt_output_folder = self.output_dropdown.currentText().strip()

            
            self.threadpool.start(self.converter)
            

    ################################################################################################################################################
    def check_errors(self):
        try:
            num_of_files = len(self.file_list_dd.keys()) # count how many items in file list
            if not num_of_files:
                raise MyError(' File list is empty ! ')
            
        except MyError as e:
            QtWidgets.QMessageBox.about(self,' Warning ',e.message)
            
        else:
                
            try:
                # Check valid inputs 
                if self.frame_rate_inp.text().strip() != '(auto)':
                    if not self.frame_rate_inp.text().strip().isdigit():
                        raise MyError(' Invalid Frame Rate. eg. 25 or (auto)')
                
                if self.crf_inp.text().strip() != '(auto)':
                    if not self.crf_inp.text().strip().isdigit():
                        raise MyError(' Invalid CRF value. eg. 23 or (auto)')

                if self.audio_bitrate_inp.text().strip() != '(auto)':
                    error = 1
                    for i in self.audio_bitrate_inp.text().strip():
                        if 'K' in i.upper() or 'M' in i.upper():
                            error = 0
                    if error:
                        raise MyError(' Invalid Audio-Bitrate. eg. 128k, 10M or (auto) ')
                    
            except MyError as e:
                print(e.message)
                QtWidgets.QMessageBox.about(self,' Warning ',e.message)
                
            else:
                return True


    ################################################################################################################################################
    def prevent_misclikcing(self,finish=False):
        self.input_browse.setEnabled(finish)
        self.output_group.setEnabled(finish)
        self.codec_group.setEnabled(finish)
        self.parameter_group.setEnabled(finish)
        self.convert_btn.setEnabled(finish)
        self.clear_btn.setEnabled(finish)
        self.overlay_checkbox.setEnabled(finish)
        


    ################################################################################################################################################
    def extra_cmd(self):
        extra_cmd = ''
        if self.cmd_inp.text() != "(None)":
            cmd = self.cmd_inp.text()
            print(cmd)
        return extra_cmd
    

################################################################################################################################################
def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(os.sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    mainwindow = ConverterTool()
    mainwindow.show()
    app.exec_()



if __name__ == "__main__":
    main()
                


