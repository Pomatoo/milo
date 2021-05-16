#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   splice_thread.py
@Author  :   Liu Kaiyu 
'''


from PyQt5 import QtCore
import subprocess
import os
import json
import subprocess
from time import sleep
from generators import SpliceCMDGenerator,FFMPEGGenerator,OverlayCMDGenerator,read_config



still_img_extensions = ['tif','tiff','png','jpeg','gif','exr','tga','jpg','jif']


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
# Define some signals
# Note: When using QRunnable, build a sub class for signals as signals inherit from QObject 
# (QThread can directly use signal and slot)
class MySignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(str)


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################

# Converting Thread (run cmd only)
class SpliceThread(QtCore.QRunnable):

    # To receive values from main thread
    output_file = ''
    overlay_flag = False
    overlay_info_list = []
    target_resolution = ''
    sequence_list = []
    file_list_dd = {}
    preset_parameter_list = []


    ################################################################################################################################################
    def __init__(self):
        super(SpliceThread,self).__init__()
        self.splice_cmd_generator = SpliceCMDGenerator()
        self.overlay_cmd_generator = OverlayCMDGenerator()
        self.ffmpeg_tool = FFMPEGGenerator()
        self.signals = MySignals()


    ################################################################################################################################################
    @QtCore.pyqtSlot()
    def run (self):
        print('RUN SPLICE THREAD')
        print(self.file_list_dd)

        # pre check will update audio statuss, original resolutions and scaling
        # and add into file_list_dd  -> eg.{'audio':'1','original_resolution':'200x200','scaling':'increase'}
        self.pre_check()
        print(self.file_list_dd)

        cmd_list = self.splice_cmd_generator.create_cmd(self.output_file,self.preset_parameter_list,self.sequence_list,self.file_list_dd,self.target_resolution)
        
        for i in cmd_list:
            print(i)
            print('\n\n')
            try:
                os.system(i)
            except Exception as e:
                print(e)
                try:
                    os.system(cmd_list[-1])
                except:
                    pass


        if self.overlay_flag:
            overlay_cmd = self.splice_cmd_generator.get_overlay_cmd(self.splice_cmd_generator.get_preset_cmd(self.preset_parameter_list),self.preset_parameter_list,self.overlay_info_list,self.output_file,self.target_resolution)
            print(overlay_cmd)
            try:
                os.system(overlay_cmd)
            except Exception as e:
                print(e)
                pass

            folder_path,file_name = os.path.split(self.output_file)
            rm_temp_overlay_cmd = 'del ' + folder_path + '\\' + 'temp_overlay_' + file_name

            try:
                os.system(rm_temp_overlay_cmd)
            except Exception as e:
                print(e)
                pass


        self.signals.finished.emit('done')


    ################################################################################################################################################
    def pre_check(self):
        for each_file in self.sequence_list:

            # UPDATE ORIGINAL RESOLUTION
            # For image sequence, file path is a folder, pull out a file under the folder 
            if self.file_list_dd[each_file]['identity'] == 'image_sequence' :
                folder_path = self.file_list_dd[each_file]['file_path']
                file_path = folder_path + '\\' + os.listdir(folder_path)[0]
            else:
                file_path = self.file_list_dd[each_file]['file_path']

            original_resolution = self.ffmpeg_tool.get_resolution(file_path)
            self.file_list_dd[each_file]['original_resolution'] = original_resolution


            #UPDATE SCALING 
            scale = self.zoom_in_or_out(self.target_resolution,original_resolution)
            self.file_list_dd[each_file]['scaling'] = scale


            # UPDATE AUDIO STATUS
            # For still image and image sequence, the audio status are always '0'
            if self.file_list_dd[each_file]['identity'] != 'video':
                self.file_list_dd[each_file]['audio'] = '0'
            else:
                file_path = self.file_list_dd[each_file]['file_path']
                status = self.ffmpeg_tool.get_video_audio_status(file_path)
                self.file_list_dd[each_file]['audio'] = status


    ################################################################################################################################################
    def zoom_in_or_out(self,target_resolution,original_resolution):

        print('target resolution is %s'%target_resolution)
        print('original resolution is %s'%original_resolution)

        original_w = original_resolution.split('x')[0].strip()
        original_h = original_resolution.split('x')[-1].strip()

        target_w = target_resolution.split('x')[0].strip()
        target_h = target_resolution.split('x')[-1].strip()


        if int(target_w) >= int(original_w) and int(target_h) >= int(original_h):
            return 'decrease'      # it was supposed to be 'increase', however it may strech the video, use 'decrease' for all cases
        else:
            return 'decrease'
    

