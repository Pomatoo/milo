# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 10:09:13 2019

@author: KAIYU
"""
from PyQt5 import QtCore
import subprocess
import os
from time import sleep
from generators import OverlayCMDGenerator,FFMPEGGenerator



################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
# Define some signals
# Note: When using QRunnable, build a sub class for signals as signals inherit from QObject 
# (QThread can directly use signal and slot)
class MySignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(str)
    percentage = QtCore.pyqtSignal(int,float)        # emit completed progress in % 


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
class ConvertThread(QtCore.QRunnable):

    cmd_list = []
    parameter_list = []
    overlay_info_list = []          # [project_name, author, task, version]
    file_list_dd = {}               # [file_name]: file_path
    output_extension = ''


    image_sequence_total_frame = None
    use_original_output = True
    alt_output_folder = ''
    compress_resolution_ratio = 1

    ################################################################################################################################################
    def __init__(self):
        super(ConvertThread,self).__init__()
        self.signals = MySignals()
        self.overlay_cmd_generator = OverlayCMDGenerator()
        self.ffmpeg_generator = FFMPEGGenerator()

    ################################################################################################################################################
    def get_converted_duration(self,line_content):
        ls = line_content.split(' ')
        for i in ls:
            if 'time=' in i:    # i is something like 'time=00:02:01.07' 
                t = i.split('=')[-1]    # t is '00:02:01.07'
                ls = t.split(':')    #  ['00','02','01.07']
                hour = float(ls[0])
                minute = float(ls[1])
                second = float(ls[2])
                converted_duration = second + minute*60 + hour*60*60
                
        return converted_duration
    
    ################################################################################################################################################
    def get_total_duration(self,duration_line):
        t = duration_line.split(',')[0].strip().strip('Duration :').split(':')
        hour = float(t[0])
        minute = float(t[1])
        second = float(t[2])
        duration = second + minute*60 + hour*60*60
        
        return duration     
    
    ################################################################################################################################################
    @QtCore.pyqtSlot()
    def run(self):  

        self.update_cmd_list()
        print('cmd list is %s'%self.cmd_list)

        for index,each_cmd in enumerate(self.cmd_list):  
            print(each_cmd)

            cmd,identity = each_cmd

            if identity == 'still_image':
                pop = subprocess.Popen(cmd, stdout= subprocess.PIPE, stderr = subprocess.STDOUT, shell = True, universal_newlines=True)

            else:
                pop = subprocess.Popen(cmd, stdout= subprocess.PIPE, stderr = subprocess.STDOUT, shell = True, universal_newlines=True)
                count = 0
                count_invalid = 0
                while pop.returncode is None:
                    
                    c = pop.stdout.readline()  # content of each line
                    print(c,end = '')
                    
                    if not c :
                        count_invalid += 1
                        if count_invalid >= 3:
                            print('quit')
                            break
                        else:
                            sleep(2)
                            continue                       
                                             
                    # Grab keywords for image sequence conversion 
                    # % of completion is calculated based on frame
                    if identity == 'image_sequence':
                        if 'frame=' in c:
                            current_frame = int(c.split('frame=')[-1].strip().split(' ')[0])
                            total_frame = self.image_sequence_total_frame
                            
                            percentage = current_frame/total_frame*100
                            self.signals.percentage.emit(index,round(percentage,2))                    
                            
                            if round(percentage,2) >= 99.9:
                                sleep(10)
                                break 

                    # Grab keywords for video conversion
                    # % of completion is calculated based on duration
                    else:           
                        # get duration of original video, unit is second
                        if 'Duration: ' in c and 'start' in c:
                            duration = self.get_total_duration(c) 
                            print(c, end = '')
                            
                        # convertion started     
                        elif 'time=' in c:
                            count += 1
                            converted_duration = self.get_converted_duration(c)                            
                            percentage = converted_duration/duration*100
                            
                            self.signals.percentage.emit(index,round(percentage,2))
                            
                            if converted_duration == duration:
                                break
                            
                            if round(percentage,2) >= 99.9:
                                sleep(10)
                                break                

            pop.terminate()
            #emit index as signal, to show that current file convertion is finsihed
            self.signals.finished.emit(str(index))           
        # emit 'done' when all files have been converted 
        self.signals.finished.emit('done')
        pop.terminate()
    




################################################################################################################################################
    def update_cmd_list(self):
        self.cmd_list = []
        self.check_audio_status()

        logo_file = os.getcwd() + r'\resources\Omens_logo.png'
                
        # Create cmd
        frame_rate = self.parameter_list[0].strip()
        crf = self.parameter_list[1].strip()
        audio_bitrate = self.parameter_list[2].strip()
        selected_acodec = self.parameter_list[3].strip()
        selected_vcodec = self.parameter_list[4].strip()
        
        codec_list = self.ffmpeg_generator.get_codecs()
        v_codecs_ls,a_codecs_ls = self.ffmpeg_generator.split_v_a_codecs(codec_list)
            
        parameter_cmd = self.overlay_cmd_generator.get_parameter_cmd(frame_rate,crf,audio_bitrate)
        codec_cmd = self.overlay_cmd_generator.get_codec_cmd(a_codecs_ls,v_codecs_ls,selected_acodec,selected_vcodec)

        # Information needed to create Text cmd
        project_name,author,task,version = self.overlay_info_list
        
        
        for each_file in self.file_list_dd.keys():
            
            output_extension = '.' + self.output_extension

            identity = self.file_list_dd[each_file]['identity'] 

            audio_status = self.file_list_dd[each_file]['audio']

            if identity == 'image_sequence':

                folder_path = self.file_list_dd[each_file]['file_path']      # for img seq input is a folder

                # Get all the image files and put them in a list, then re-arrange them 
                file_list = os.listdir(folder_path)
                file_list.sort()
            
                # choose the first file(it has the smallest index)
                # when converting an image sequence to a video, a starting index must be specified 
                first_file = file_list[0]
                input_file = folder_path + '\\' + first_file    # Take the first file as an input file for conversion 
                total_frame = len(file_list)  
                self.image_sequence_total_frame = total_frame   # It will be used to calculate % of completion

                # Use the same folder as input file
                if self.use_original_output: 
                    # For image sequence, the input is already a folder, and folder name will be output video name
                    # put the output video at the same same level of the input folder 
                    # eg. input is T:/Image/sequence1/ , output file will be 'T:/Image/sequence1.mp4' and output folder is 'T:/Image/'
                    output_folder = os.path.abspath(os.path.join(folder_path,'../'))
                else:
                    output_folder = self.alt_output_folder

                output_file = output_folder + '\\' + folder_path.split('/')[-1].strip() + '_converted' + output_extension

            # For video and still image conversion ↓
            else :
                input_file = self.file_list_dd[each_file]['file_path'] 
                print('input file is %s '%input_file)

                input_folder,temp_file_name = os.path.split(input_file)
                input_file_name = os.path.splitext(temp_file_name)[0]

                # Use the same folder as input file
                if self.use_original_output : 
                    output_folder = input_folder
                else:
                    output_folder = self.alt_output_folder
                
                # Still image has different input varible values
                if identity == 'still_image':
                    # Still image has only one frame, and no frame rate
                    frame_rate = 'NA'
                    total_frame = '1'
                    
                    # NOTE: parameters and codecs are not allowed in still image convertion
                    parameter_cmd = ''
                    codec_cmd = ''

                    # Extension for still image remains unchanged 
                    output_extension = '.' + input_file.split('.')[-1]
                else:
                    total_frame = self.ffmpeg_generator.get_total_frame(input_file)

                output_file_name = input_file_name + '_converted' + output_extension 
                output_file = output_folder + '/' + output_file_name

            original_resolution = self.ffmpeg_generator.get_resolution(input_file)
            resized_resolution = self.ffmpeg_generator.get_resized_resolution(self.compress_resolution_ratio,input_file)

            text_cmd = self.overlay_cmd_generator.get_text_CMD(each_file,project_name,author,task,version,frame_rate,original_resolution,resized_resolution,total_frame)
            logo_padding_cmd = self.overlay_cmd_generator.get_logo_padding_cmd(resized_resolution)
            
            if audio_status == '1':
                text_cmd += ''

            cmd = self.overlay_cmd_generator.create_cmd(input_file,logo_file,output_file,codec_cmd,parameter_cmd,text_cmd,logo_padding_cmd,identity=='image_sequence')
        
            self.cmd_list.append([cmd,identity])

    #############################################################################################################
    def check_audio_status(self):

        for each_file in self.file_list_dd.keys():
            file_identity = self.file_list_dd[each_file]['identity']
            file_path = self.file_list_dd[each_file]['file_path']
            
            status = '0'
    
            if file_identity == 'video':
                status = self.ffmpeg_generator.get_video_audio_status(file_path)
            
            self.file_list_dd[each_file]['audio'] = status

