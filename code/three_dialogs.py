# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 10:38:14 2019

@author: KAIYU
"""


from PyQt5 import QtWidgets,QtCore
import os,sys
from help_menu import *
from preset import *
from add_link import *
import subprocess
import webbrowser
from generators import FFMPEGGenerator, read_config, write_config
import json
from time import sleep



################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
class AddLink(QtWidgets.QDialog,Ui_addLinkDialog):
    # create a signal, communicates with HelpMenu Dialog
    # whenever a new link is added, a signal will be emitted
    add_signal = QtCore.pyqtSignal()
    
################################################################################################################################################
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self) 

        # Add an icon to this window
        _translate = QtCore.QCoreApplication.translate
        self.setWindowIcon(QtGui.QIcon(r'.\resources\milo.png'))

        self.clear()
        self.ok_btn.clicked.connect(self.ok_btn_function)

        # Set default type of link to URL
        self.url_radioButton.setChecked(True)

################################################################################################################################################
    def ok_btn_function(self):
        # Get title and path 
        title = self.description_inp.text()
        path = self.path_inp.text()
        
        # Define header according to checked radio buttom
        if self.url_radioButton.isChecked():
            header = 'URL'
        elif self.folder_path_radioButton.isChecked():
            header = 'Folder'
    
        
        if title == '' or path == '':
            QtWidgets.QMessageBox.about(self,' ','Incomplete Information !')   
        else:
            link = {title:'%s,"%s"'%(header,path)}        # Format : {'title':' header,"path" '} 
            self.write_to_linkbook(link)
            QtWidgets.QMessageBox.about(self,' ','Added Successfully !')
            self.add_signal.emit()
            self.clear()  
            
################################################################################################################################################
    def clear(self):
        self.description_inp.clear()
        self.path_inp.clear()
        
################################################################################################################################################
    def write_to_linkbook(self,link):
        config_content = read_config()
        for link_name,path in link.items():
            config_content['link_book'][link_name] = path

        write_config(config_content)

################################################################################################################################################

    
    
    
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
class HelpMenu(QtWidgets.QDialog,Ui_HelpDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        _translate = QtCore.QCoreApplication.translate
        self.setWindowIcon(QtGui.QIcon(r'.\resources\milo.png'))

        self.LINKS = {}
        self.refresh_link_list(self.read_linkbook())


        # Instantiate ADD LINK Dialog
        self.addLink_dialog = AddLink()
        self.add_btn.clicked.connect(lambda: self.addLink_dialog.show())
        self.addLink_dialog.add_signal.connect(lambda: self.refresh_link_list(self.read_linkbook()))
        
        # Connections
        self.delete_btn.clicked.connect(self.delete_link)
        self.open_btn.clicked.connect(self.open_link)
        self.ffmpeg_doc_btn.clicked.connect(self.open_documentation)
        self.guide_btn.clicked.connect(self.open_mannual)

        
################################################################################################################################################
    def delete_link(self):
        # get selected item's name and row
        selected_row = self.link_list.currentRow()
        selected_item = self.link_list.currentItem()  
        
        if not selected_item :
            QtWidgets.QMessageBox.about(self,' ','Please select a link !')   
            
        else:    
            item_name = selected_item.text().split(':')[1]
            
            self.link_list.takeItem(selected_row)
            del self.LINKS[item_name]
            
            print(self.LINKS)
            self.delete_from_linkbook(item_name)
            self.refresh_link_list(self.LINKS)
        
################################################################################################################################################
    def read_linkbook(self):
        config_content = read_config()

        for each_link in config_content['link_book'].keys():
            self.LINKS[each_link] = config_content['link_book'][each_link]

        return self.LINKS
            
    
################################################################################################################################################
    def refresh_link_list(self,LINKS):
        self.link_list.clear()
        if LINKS:
            print(LINKS)
            for key,value in sorted(LINKS.items()):
                header = value.split(',')[0]
                self.link_list.addItem(header + ':' + key)
    
    
################################################################################################################################################
    def write_to_linkbook(self,link):
        config_content = read_config()

        for link_name,path in link.items():
            config_content['link_book'][link_name] = path 

        write_config(config_content)
    

################################################################################################################################################
    def delete_from_linkbook(self,delete_this_item):
        config_content = read_config()
        try:
            del config_content['link_book'][delete_this_item]
        except:
            pass
        else:
            write_config(config_content)


################################################################################################################################################
    def open_link(self):
        selected_item = self.link_list.currentItem()  # the text'Folder:item'
        
        # if user did not select any link , pop out a winddow
        if not selected_item :
            QtWidgets.QMessageBox.about(self,' ','Please select a link !')   
        else:
            
            item_name = selected_item.text().split(':')[1].strip()
            print(item_name)
            header = self.LINKS[item_name].split(',')[0]
            path = self.LINKS[item_name].split(',')[1]
            self.access_link(header,path)


################################################################################################################################################
    def access_link(self,header,path):
        print(path)
        if header == 'URL':
            try:
                webbrowser.open(path)
            except:
                QtWidgets.QMessageBox.about(self,' ERROR ','Cannot open this URL !')
                pass  
            
        elif header == 'Folder':
            try:
                os.system('start explorer %s'%path)
            except:
                QtWidgets.QMessageBox.about(self,' ERROR ','Cannot open this folder !')
                pass   
        else:
            pass


###############################################################################################################################################
    def open_mannual(self):
        # dir is current script or exe directory
        if getattr(sys,'frozen',False):
            # current application is a exe
            dir = os.path.dirname(sys.executable)
        elif __file__ :
            # current application is a script 
            dir = os.path.dirname(__file__)

        manual_path = dir + '\\docs\\milo_manual.pdf'
        docs_folder = dir + '\\docs'

        p = subprocess.call("start %s"%manual_path,shell = True)
        if p != 0 :
            QtWidgets.QMessageBox.about(self,' ','FAILED Please open manually !')   
            subprocess.call('start explorer %s'%docs_folder,shell = True)
    
    
################################################################################################################################################
    def open_documentation(self):
        # dir is current script or exe directory
        if getattr(sys,'frozen',False):
            # current application is a exe
            dir = os.path.dirname(sys.executable)
        elif __file__ :
            # current application is a script 
            dir = os.path.dirname(__file__)

        documentation_path = dir + '\\docs\\milo_documentation.pdf'
        docs_folder = dir + '\\docs'

        p = subprocess.call("start %s"%documentation_path,shell = True)
        if p != 0 :
            QtWidgets.QMessageBox.about(self,' ','FAILED Please open manually !')   
            subprocess.call('start explorer %s'%docs_folder,shell = True)
    
    
################################################################################################################################################
    

    
    
    
    
    
    
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
class PreSet(QtWidgets.QDialog,Ui_PreSetDialog):
    refresh_signal = QtCore.pyqtSignal()
    
    
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.clear_parameters()
        self.refresh_codecs_list()
        self.refresh_crf()

        _translate = QtCore.QCoreApplication.translate
        self.setWindowIcon(QtGui.QIcon(r'.\resources\milo.png'))

        self.PRESETS = {}
        self.refresh_preset_list(self.read_preset_book())
        self.save_btn.clicked.connect(self.save_setting)
        self.delete_btn.clicked.connect(self.delete_preset)
        self.preset_list.itemClicked.connect(lambda: self.show_preset_parameters(self.preset_list.currentItem().text()))
        self.clear_btn.clicked.connect(self.clear_parameters)
        self.crf_dropdown_radioButton.toggled.connect(self.check_radio_btn)
        self.crf_inp_radioButton.toggled.connect(self.check_radio_btn)


    ################################################################################################################################################
    def save_setting(self,save = False):
        set_name =  self.preset_name_inp.text().strip()
        frame_rate = self.frame_rate_inp.text().strip()
        crf = self.get_crf_value()
        audio_bitrate = self.audio_bitrate_inp.text().strip()
        a_codec = self.acodecs_dropdown.currentText().strip()
        v_codec = self.vcodecs_dropdown.currentText().strip()
        
        if set_name == '' or frame_rate == '' or crf =='' or audio_bitrate =='':
            QtWidgets.QMessageBox.about(self,' ','Incomplete Information !')   
        else:
            # Ensure order of magnitude is correct  (UPPER M and lower k)
            audio_bitrate = self.modify_order_of_magnitude(audio_bitrate)
           
            self.PRESETS[set_name] = '%s,%s,%s,%s,%s'%(frame_rate,crf,audio_bitrate,a_codec,v_codec)
            self.preset_list.addItem(set_name)
            self.write_to_preset_book(self.PRESETS)

            self.refresh_preset_list(self.PRESETS)
            self.clear_parameters()
    
    ################################################################################################################################################
    def modify_order_of_magnitude(self,rate):
        if 'm' in rate:
            rate = rate.replace('m','M')
        if 'K' in rate:
            rate = rate.replace('K','k')
        
        return rate 
    

    ################################################################################################################################################
    def refresh_preset_list(self,PRESETS):
        self.preset_list.clear()
        if self.PRESETS.keys():
            for set_name in sorted(PRESETS.keys()):
                self.preset_list.addItem(set_name)
       
    ################################################################################################################################################
    def read_preset_book(self):
        config_content = read_config()
        print('read')

        for set_name in config_content['preset_book'].keys():
            self.PRESETS[set_name] = config_content['preset_book'][set_name]
          
        return self.PRESETS
        

    ################################################################################################################################################
    def delete_preset(self):
        selected_row = self.preset_list.currentRow()
        selected_item = self.preset_list.currentItem()  # the text'Folder:item'
        
        if not selected_item :
            QtWidgets.QMessageBox.about(self,' ','Please select a preset !')   
            
        else:    
            item_name = selected_item.text()
            
            reply = QtWidgets.QMessageBox.question(self,'Warning','Are you sure to delete this preset?',QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            
            if reply == QtWidgets.QMessageBox.Yes:
                self.preset_list.takeItem(selected_row)
                del self.PRESETS[item_name]
                QtWidgets.QMessageBox.about(self,' ','Deleted !')   
                self.delete_from_preset_book(item_name)
                self.refresh_signal.emit()
                self.refresh_preset_list(self.PRESETS)
        self.clear_parameters()        
        
    ################################################################################################################################################
    def write_to_preset_book(self,PRESETS):
    
        config_content = read_config()

        for set_name,settings in PRESETS.items():
            config_content['preset_book'][set_name] = settings

        write_config(config_content)       
        self.refresh_signal.emit()

################################################################################################################################################
    def delete_from_preset_book(self,delete_this_item):
        config_content = read_config()
        try:
            del config_content['preset_book'][delete_this_item]
        except Exception as e:
            print(e)
        else:
            print(config_content['preset_book'])
            write_config(config_content)

    ################################################################################################################################################
    def clear_parameters(self):
        self.preset_name_inp.clear()
        self.frame_rate_inp.clear()
        self.crf_inp.clear()
        self.audio_bitrate_inp.clear()
        self.refresh_codecs_list()

    ################################################################################################################################################
    def show_preset_parameters(self,set_name):
        parameters = self.PRESETS[set_name].split(',')
        
        self.preset_name_inp.setText(set_name)
        self.frame_rate_inp.setText(parameters[0])
        self.parse_crf_value(parameters[1])
        self.audio_bitrate_inp.setText(parameters[2])
        
        self.refresh_codecs_list()
        acodec_index =  self.acodecs_dropdown.findText(parameters[3])  
        self.acodecs_dropdown.setCurrentIndex(acodec_index)
        
        vcodec_index = self.vcodecs_dropdown.findText(parameters[4])
        self.vcodecs_dropdown.setCurrentIndex(vcodec_index)
        
    ################################################################################################################################################
    def refresh_codecs_list(self):
        self.acodecs_dropdown.clear()
        self.vcodecs_dropdown.clear()
        
        self.codec_generator = FFMPEGGenerator()
        codec_list = self.codec_generator.get_codecs()
        
        self.v_codecs_ls,self.a_codecs_ls = self.codec_generator.split_v_a_codecs(codec_list)
                
        self.acodecs_dropdown.addItem('Default')
        for i in self.a_codecs_ls:
            self.acodecs_dropdown.addItem(i[2])
                
        self.vcodecs_dropdown.addItem('Default')
        for i in self.v_codecs_ls:
            self.vcodecs_dropdown.addItem(i[2])
        
    ################################################################################################################################################
    def refresh_crf(self):
        self.crf_dropdown.clear()
        level = ['High','Normal','Low','Proxy']
        for i in level:
            self.crf_dropdown.addItem(i)

    ################################################################################################################################################
    def get_crf_value(self):
        if self.crf_dropdown_radioButton.isChecked():
            text = self.crf_dropdown.currentText().strip().capitalize()
            if text == 'High':
                crf_value = '15'
            elif text == 'Normal':
                crf_value = '23'
            elif text == 'Low':
                crf_value = '30'
            elif text == 'Proxy':
                crf_value = '40'

        elif self.crf_inp_radioButton.isChecked():
            crf_value = self.crf_inp.text().strip()

        return crf_value 

    ################################################################################################################################################
    def parse_crf_value(self,crf):  # variable crf is string variable 
        self.crf_dropdown_radioButton.setChecked(True)
        self.check_radio_btn()
        if crf == '15':
            self.set_selected_crf_dropdown('High')
        elif crf == '23':
            self.set_selected_crf_dropdown('Normal')
        elif crf == '30':
            self.set_selected_crf_dropdown('Low')
        elif crf == '40':
            self.set_selected_crf_dropdown('Proxy')
        else:
            self.crf_inp_radioButton.setChecked(True)
            self.crf_inp.setText(crf)
        self.check_radio_btn()

    ################################################################################################################################################
    def set_selected_crf_dropdown(self,text):
        self.refresh_crf()
        index = self.crf_dropdown.findText(text)
        self.crf_dropdown.setCurrentIndex(index)

    ################################################################################################################################################
    def check_radio_btn(self):
        if self.crf_inp_radioButton.isChecked():
            self.crf_inp.setEnabled(True)
            self.crf_dropdown.setEnabled(False)
        else:
            self.crf_inp.setEnabled(False)
            self.crf_dropdown.setEnabled(True)