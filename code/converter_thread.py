# -*- coding: utf-8 -*-
"""
@author: KAIYU
"""
from PyQt5 import QtCore
import subprocess
import os
from time import time, sleep
from generators import FFMPEGGenerator,OverlayCMDGenerator,CMDGenerator



# Define some signals
# Note: When using QRunnable, build a sub class for signals as signals inherit from QObject 
# (QThread can directly use signal and slot)
class MySignals(QtCore.QObject):
    finished = QtCore.pyqtSignal(str)
    time_info = QtCore.pyqtSignal(float)             # emit estimated time to complete convertion 
    percentage = QtCore.pyqtSignal(int,float)        # emit completed progress in % 


# Converting Thread (run cmd only)
class ConvertThread(QtCore.QRunnable):
    cmd_list = []

    overlay_flag = False 
    use_original_ouput = True
    alt_output_folder = ''
    image_sequence_total_frame = None

    overlay_info_list = []      # [project_name, author, task, version]
    parameter_list = []         # [frame_rate, crf, audio_bitrate, selected_acodec, selected_vcodec] 
    file_list_dd = {}           # [file_name]: file_path
    output_extension = ''
    extra_cmd = ''
    compress_resolution_ratio = 1
    
    ################################################################################################################################################
    def __init__(self):
        super(ConvertThread,self).__init__()
        self.signals = MySignals()
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
    # Decorator, enable slots 
    @QtCore.pyqtSlot()
    def run(self):  

        self.update_cmd_list()

        for index,each_cmd in enumerate(self.cmd_list):  
            print(each_cmd)

            cmd,image_sequence_flag = each_cmd

            pop = subprocess.Popen(cmd, stdout= subprocess.PIPE, stderr = subprocess.STDOUT, shell = True, universal_newlines=True)
            count = 0
            count_invalid = 0
            while pop.returncode is None:
                
                c = pop.stdout.readline()  # content of each line
                print(c,end = '')

                if not c:
                    count_invalid += 1
                    if count_invalid >= 3:
                        break
                    else:
                        sleep(2)
                        continue

                # Grab keywords for image sequence conversion 
                # % of completion is calculated based on frame
                if image_sequence_flag:
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
    #                    print('total duration is %s seconds'%duration)
                        
                    # convertion started     
                    elif 'time=' in c:
                        count += 1
                        converted_duration = self.get_converted_duration(c)
    #                    print('converted duration is %s'%converted_duration)
                        
                        if converted_duration == duration:
                            print('done !')
                            break
                        
                        # define initial time at count = 1
                        if count == 1:
                            init_time = time()
                            print('Converting ...')
    #                        print('init time is %s'%init_time)
                        
                        else:
                            final_time = time()
                            time_elapsed = final_time - init_time
    #                        print('time elapsed is %s'%time_elapsed)
                        
                        
                        # calculate total time needed at count = 20 
                        if count == 10:
                            estim_t = time_elapsed*duration/converted_duration
                            self.signals.time_info.emit(estim_t)
                            
                        
                        # predict and refresh time left 
                        elif count > 10 :
                            time_left = estim_t - time_elapsed
                            percentage = converted_duration/duration*100
                            self.signals.percentage.emit(index,round(percentage,2))
                        
                            if time_left > 0 :
                                self.signals.time_info.emit(time_left)
                            
                            if round(percentage,2) >= 99.99:
                                sleep(5)
                                break
            pop.terminate()
            #emit index as signal, to show that current file convertion is finsihed
            self.signals.finished.emit(str(index))           
        # emit 'done' when all files have been converted 
        self.signals.finished.emit('done')
        pop.terminate()
        

    #############################################################################################################
    def check_audio_status(self):

        for each_file in self.file_list_dd.keys():
            file_identity = self.file_list_dd[each_file]['identity']
            file_path = self.file_list_dd[each_file]['file_path']
            
            status = '0'
    
            if file_identity == 'video':
                status = self.ffmpeg_generator.get_video_audio_status(file_path)
            
            self.file_list_dd[each_file]['audio'] = status


    #############################################################################################################
    def update_cmd_list(self):
        self.cmd_list = []

        self.check_audio_status()

        # If overlay is activated, use overlay cmd generator 
        if self.overlay_flag:
            self.cmd_generator = OverlayCMDGenerator()

            # Additional information required for overlay
            project_name,author,task,version = self.overlay_info_list
            logo_file = os.getcwd() + r'\resources\Omens_logo.png'

        else:
            self.cmd_generator = CMDGenerator()
                
        # Arguments needed to create cmd 
        extra_cmd = self.extra_cmd

        frame_rate = self.parameter_list[0].strip()
        crf = self.parameter_list[1].strip()
        audio_bitrate = self.parameter_list[2].strip()
        selected_acodec = self.parameter_list[3].strip()
        selected_vcodec = self.parameter_list[4].strip()
        
        codec_list = self.ffmpeg_generator.get_codecs()
        v_codecs_ls,a_codecs_ls = self.ffmpeg_generator.split_v_a_codecs(codec_list)
            
        parameter_cmd = self.cmd_generator.get_parameter_cmd(frame_rate,crf,audio_bitrate)
        codec_cmd = self.cmd_generator.get_codec_cmd(a_codecs_ls,v_codecs_ls,selected_acodec,selected_vcodec)
        
        for each_file in self.file_list_dd.keys():

            # Output extension is specified by user. default is 'mov'
            output_extension = '.' + self.output_extension

            image_sequence_flag = self.file_list_dd[each_file]['identity'] == 'image_sequence'  # Bool
      
            audio_status = self.file_list_dd[each_file]['audio']

            if image_sequence_flag:
                folder_path = self.file_list_dd[each_file]['file_path']   # for img seq input is a folder

                # Get all the image files and put them in a list, then re-arrange them in order
                file_list = os.listdir(folder_path)
                file_list.sort()
                
                # Choose the first file(it has the smallest index)
                # When converting an image sequence to a video, a starting index must be specified 
                first_file = file_list[0]
                input_file = folder_path + '\\' + first_file    # Take the first file as an input file for conversion 
                
                # Total frame of video that converted from image sequence is the number of images in that sequence
                total_frame = len(file_list) 
                # For image sequence conversion, pass total_frame to convertor as it is used to calculate % of completion
                self.image_sequence_total_frame = total_frame
                

                if self.use_original_ouput:  # Use the same folder as input file
                    # For image sequence, the input is already a folder, and folder name will be output video name
                    # put the output video at the same same level of the input folder 
                    # eg. input is T:/Image/sequence1/ , output file will be 'T:/Image/sequence1.mp4' and output folde is 'T:/Image/'
                    output_folder = os.path.abspath(os.path.join(folder_path,'../'))
                else:
                    output_folder = self.alt_output_folder

                output_file = output_folder + '\\' + folder_path.split('/')[-1].strip() + '_converted' + output_extension
               
            # For non image-sequence convertion 
            else:
                input_file = self.file_list_dd[each_file]['file_path']
                
                # Here will be a BUG if path contains 'space' (limitation of os module ???)
                input_folder,temp_file_name = os.path.split(input_file)
                input_file_name = os.path.splitext(temp_file_name)[0]

                if self.use_original_ouput : # Use the same folder as input file
                    output_folder = input_folder
                else:
                    output_folder = self.alt_output_folder
                
                output_file_name = input_file_name + '_converted' + output_extension 
                output_file = output_folder + '/' + output_file_name

            original_resolution = self.ffmpeg_generator.get_resolution(input_file)
            resized_resolution = self.ffmpeg_generator.get_resized_resolution(self.compress_resolution_ratio,input_file)

            if self.overlay_flag:
                # Get total frame for a video
                # If input is imgae sequence, total frame is the number of images files(which is defined above).
                if not image_sequence_flag:
                    total_frame = self.ffmpeg_generator.get_total_frame(input_file)


                
                text_cmd = self.cmd_generator.get_text_CMD(each_file,project_name,author,task,version,frame_rate,original_resolution,resized_resolution,total_frame)
                
                # USE RESIZED RESOLUTION TO CALCULATE OVERLAY SIZE 
                logo_padding_cmd = self.cmd_generator.get_logo_padding_cmd(resized_resolution)
            
                if audio_status == '1':
                    text_cmd += ''

                cmd = self.cmd_generator.create_cmd(input_file,logo_file,output_file,codec_cmd,parameter_cmd,text_cmd,logo_padding_cmd,image_sequence_flag) 

            else:             
                print('input file is %s'%input_file)
                print('output file is %s'%output_file)
                print('codec cmd is %s'%codec_cmd)
                print('parameter cmd is %s'%parameter_cmd)
                print('extra cmd is %s'%extra_cmd)
                
                cmd = self.cmd_generator.create_cmd(input_file,output_file,codec_cmd,parameter_cmd,extra_cmd,image_sequence_flag,output_resolution=resized_resolution)

            self.cmd_list.append([cmd,image_sequence_flag])



################################################################################################################################################

