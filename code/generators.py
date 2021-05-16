# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 10:14:52 2019

@author: KAIYU
"""
import os,sys
import subprocess
import json
from time import sleep



##############################################################################################################################
def write_config(content):
    # dir is current script or exe directory
    if getattr(sys,'frozen',False):
        # current application is a exe
        dir = os.path.dirname(sys.executable)
    elif __file__ :
        # current application is a script 
        dir = os.path.dirname(__file__)

    config_file = dir + '\\milo.config'
    print('config_file is : %s'%config_file)

    try:
        f = open(config_file,'w')
    except PermissionError as e:
        print('\n\n\n\n\n')
        print('No Permission to edit conig file. Find IT people\n\n\n\n\n')
        sleep(3)
        pass
    except Exception as e:
        print(' %s'%e)
        sleep(3)
        pass
    else:
        json.dump(content,f)
        f.close()
        print('written')

##############################################################################################################################
def read_config():
    # dir is current script or exe directory
    if getattr(sys,'frozen',False):
        # current application is a exe
        dir = os.path.dirname(sys.executable)
    elif __file__ :
        # current application is a script 
        dir = os.path.dirname(__file__)

    config_file = dir + '\\milo.config'
    print('config file is %s'%config_file)

    try:
        f = open(config_file,'r')
    except Exception as e:
        print(' %s'%e)
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        sleep(3)
        pass
    else:
        conetnt = json.load(f)
        f.close()
        print('read')
        return conetnt
        
##############################################################################################################################


config_content = read_config()

ffmpeg_folder_path = config_content['ffmpeg_folder_path']

ffmpeg_cmd = ffmpeg_folder_path + '\\ffmpeg.exe'
ffprobe_cmd = ffmpeg_folder_path + '\\ffprobe.exe'
check_codec_cmd = ffmpeg_folder_path + '\\ffmpeg.exe -codecs'
check_fmt_cmd = ffmpeg_folder_path + '\\ffmpeg.exe -formats'
    

##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
class FFMPEGGenerator(object):

    def __init__(self):
        object.__init__(self)      
        
    ##############################################################################################################################
    # Get all codecs 
    def get_codecs(self):
        global check_codec_cmd
        text = os.popen(check_codec_cmd).read().splitlines(True)    
        codec_ls = []        
        for i in text:
            if '=' in i:
                continue
            
            i = i.split(' ')
            while '' in i:
                i.remove('')
            codec = ' '.join(i[2:]).strip()
            each_codec = i[:2] + [codec]
            codec_ls.append(each_codec)
        
        return codec_ls

    ##############################################################################################################################
    # split codecs into audio codecs and video codecs 
    def split_v_a_codecs(self,codec_ls):   
        video_codecs = []
        audio_codecs = []
        
        for each_codec in codec_ls:
            if each_codec[0][1] == 'E':
            
                if each_codec[0][2] == 'V': # video codecs
                    video_codecs.append(each_codec)
                
                elif each_codec[0][2] == 'A':  # audio codecs
                    audio_codecs.append(each_codec)
                
        return video_codecs,audio_codecs

    ##############################################################################################################################
    def get_muxing_supported_fmt(self):
        fmt_ls = self.output_fmt()
        muxing_supported_fmt_ls = []
        for i in fmt_ls:
            if 'E' in i[0]:
                muxing_supported_fmt_ls.append(i[1])
        return muxing_supported_fmt_ls


    ##############################################################################################################################
    # Get all the supported format 
    def output_fmt(self):
        global check_fmt_cmd
        text = os.popen(check_fmt_cmd).read().splitlines(True)[4:]
        fmt_ls = []
        for i in text:
            if '=' in i:
                continue
            
            i = i.split(' ')
            while '' in i:
                i.remove('')
            codec = ' '.join(i[2:]).strip()
            each_codec = i[:2] + [codec]
            fmt_ls.append(each_codec)
        
        return fmt_ls

    ##############################################################################################################################
    def get_resolution(self,file_path):
        global ffprobe_cmd
        resolution_cmd = ffprobe_cmd +' -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "%s"'%file_path
        print('resolution cmd is %s'%resolution_cmd)
        pop = subprocess.Popen(resolution_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
        resolution = pop.stdout.readlines()
        resolution = resolution[-1].decode().strip()
        pop.terminate()

        print('resolution of %s is %s'%(file_path,resolution))
        return resolution
     
    #############################################################################################################
    def get_resized_resolution(self,ratio,file_path):
        # input variable 'ratio' ranges from 0.2-1

        original_resolution = self.get_resolution(file_path)
        original_w,original_h = original_resolution.strip().split('x')

        output_w = round(int(original_w)*ratio/2,)*2
        output_h = round(int(original_h)*ratio/2,)*2

        resized_resolution = '%sx%s'%(output_w,output_h)

        print('resized resolution is %s'%resized_resolution)
        return resized_resolution
 
    ##############################################################################################################################
    def get_total_frame(self,file_path):
        # This function is particularly for videos ONLY
        # total frame for image sequence is the number of imgaes in the folder 
        # total frame for still image is 1
        global ffprobe_cmd
        frame_cmd = ffprobe_cmd + ' -select_streams v -show_streams "%s"'%file_path
        frame = 'NA'
        pop = subprocess.Popen(frame_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
        result = pop.stdout.readlines()
        for i in result:
            try:
                i = i.decode().strip()
            except Exception:
                continue 
            else:
                if 'nb_frames=' in i:
                    frame = i.split('=')[-1].strip()
                    break
                else:
                    continue
        pop.terminate()

        print('total frame of %s is %s'%(file_path,frame))
        return frame

    ##############################################################################################################################
    
    def get_video_audio_status(self,input_video):
        global ffprobe_cmd
        cmd = ffprobe_cmd + ' -i %s'%input_video
        pop = subprocess.Popen(cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
        conetnt = pop.stdout.readlines()

        # 0,1 indicates if a video has audio stream
        status = '0'
        for i in conetnt:
            try:
                if 'Stream #0:1' in i.decode().strip():
                    status = '1'
                    break
            except Exception :
                # May have decode problem, just ignore it :) 
                continue

        print('status is %s'%status)
        return status 

    ##############################################################################################################################
 








##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
class CMDGenerator(object):  
    
    def __init__(self):
        object.__init__(self)

    ################################################################################################################################################
    def get_parameter_cmd(self,frame_rate,crf,audio_bitrate):
        
        frame_rate_cmd = ''
        crf_cmd = ''
        audio_bitrate_cmd = ''
        
        if 'auto' not in frame_rate:
            frame_rate_cmd = '-r ' + frame_rate
        if 'auto' not in crf:
            crf_cmd = ' -crf ' + crf
        if 'auto' not in audio_bitrate:
            audio_bitrate_cmd = ' -ab ' + audio_bitrate
        
        parameter_cmd = frame_rate_cmd + audio_bitrate_cmd + crf_cmd 
        
        return parameter_cmd

           
    ################################################################################################################################################
    def get_codec_cmd(self,audio_codecs_ls,video_codecs_ls,selected_acodec,selected_vcodec):
        
        if selected_acodec != 'Default' :
            for i in audio_codecs_ls:
                if i[2] == selected_acodec.strip():
                    acodec_cmd = '-acodec ' + i[1]
                    print('acodec cmd is %s'%acodec_cmd)
        else:
            acodec_cmd = ''
        
        if selected_vcodec != 'Default' :        
            for i in video_codecs_ls:
                if i[2] == selected_vcodec.strip():
                    vcodec_cmd = '-vcodec ' + i[1]
                    print('v codec cmd is : %s'%vcodec_cmd)
                    
        else:
            vcodec_cmd = ''
          
        codec_cmd = vcodec_cmd + ' ' + acodec_cmd
        print('codec cmd is %s'%codec_cmd)

        return codec_cmd
        
    
    ################################################################################################################################################
    def create_cmd(self,input_file,output_file,codec_cmd,parameter_cmd,extra_cmd,image_sequence,output_resolution=None):

        input_file_cmd = ' -i ' + '"' + input_file + '"'        # '-i' is flag for input file
        output_file_cmd = ' -y ' + '"' + output_file + '"'           # '-y' over write existing files
        codec_cmd = ' ' + codec_cmd
        parameter_cmd = ' ' + parameter_cmd
        
        if output_resolution :
            print('getting resize cmd')
            # output resolution is in the format of 1920:1080
            resize_cmd = ' -vf scale=%s'%output_resolution
        else:
            resize_cmd = ''

        if image_sequence:
            image_cmd = ' -f image2'   # Parameter for image and image sequence convertion 
            file_name = input_file.split('\\')[-1]   #Extract selected file name (with extension)
            extension = file_name.split('.')[-1]     # Extension of file eg. 'exr','png'
            folder_path = '\\'.join(i for i in input_file.split('\\')[:-1]) # Get folder path of the sequence 
            
            # Get starting index 
            # Idea is : assume a file "CVN0070_SH0010_00671.exr", the index is "00671" 
            # first, take only "CVN0070_SH0010_00671"
            # looping and count index backwards ('00671' : 1->7->6->0->0), if character is not digit, break loop.
            i = 1 
            temp = []
            while True:
                
                if os.path.splitext(file_name)[0][-i].isdigit():
                    temp.insert(0,os.path.splitext(file_name)[0][-i])
                    i += 1
                else:
                    break
                
            starting_index = ''.join(i for i in temp)
            file_name = file_name.strip('.%s'%extension)[:-len(starting_index)]  # File name without extension and index 
            
            input_file_cmd = (' -start_number %s'%starting_index +
                        ' -i ' + '"' + folder_path + "/" + file_name + "%" + "0%sd."%len(starting_index) + extension + '"' )
        else:
            image_cmd = ''
        
        global ffmpeg_cmd   
        cmd = ffmpeg_cmd + image_cmd + input_file_cmd + resize_cmd + codec_cmd + parameter_cmd + extra_cmd + ' -pix_fmt yuv420p' + output_file_cmd
        
        return cmd    

    ################################################################################################################################################
    def get_preset_cmd(self,preset_parameter_list):

        if preset_parameter_list == [] :
            preset_cmd = ''

        else:
            frame_rate = preset_parameter_list[0].strip()
            crf = preset_parameter_list[1].strip()
            audio_bitrate = preset_parameter_list[2].strip()
            selected_acodec = preset_parameter_list[3].strip()
            selected_vcodec = preset_parameter_list[4].strip()
            
            parameter_cmd = self.get_parameter_cmd(frame_rate,crf,audio_bitrate)

            ffmpeg_tool = FFMPEGGenerator()
            codec_ls = ffmpeg_tool.get_codecs()
            vcodec_ls,acodec_ls = ffmpeg_tool.split_v_a_codecs(codec_ls)

            codec_cmd = self.get_codec_cmd(acodec_ls,vcodec_ls,selected_acodec,selected_vcodec)
            
            preset_cmd = codec_cmd + ' ' + parameter_cmd

        return preset_cmd

    ################################################################################################################################################



##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
class OverlayCMDGenerator(CMDGenerator):

    image_sequence_flag = False
    still_image_flag = False

    def get_text_CMD(self,file_name,project_name,author_name,task_name,version,frame_rate,original_resolution,resized_resolution,total_frame):
        # Font size is based on resolution of video or image 
        # text size is 2% of length , title size is 3% of length 
        length = int(resized_resolution.split('x')[0])
        text_size = int(length*0.020)
        title_size = int(length*0.030)
        
        author_cmd = 'drawtext="fontfile=./resources/arial.ttf:text=\'%s\':fontcolor=white:fontsize=%s:x=w*0.01:y=h*0.02"'%(author_name,text_size)
        shot_name_cmd = 'drawtext="fontfile=./resources/arial.ttf:text=\'%s\':fontcolor=white:fontsize=%s:x=(w-tw)/2:y=h*0.06"'%(os.path.splitext(file_name)[0],text_size)
        project_title_cmd = 'drawtext="fontfile=./resources/arial.ttf:text=\'%s\':fontcolor=white:fontsize=%s:x=(w-tw)/2:y=h*0.01"'%(project_name,title_size)
        resolution_label_cmd = 'drawtext="fontfile=./resources/arial.ttf:text=\'%s\':fontcolor=white:fontsize=%s:x=(w-tw)/2:y=h*0.9"'%(original_resolution,text_size)
        task_cmd = 'drawtext="fontfile=./resources/arial.ttf:text=\'Task\\: %s\':fontcolor=white:fontsize=%s:x=w*0.01:y=h*0.9"'%(task_name,text_size)
        version_cmd = 'drawtext="fontfile=./resources/arial.ttf:text=\'Version\\:%s\':fontcolor=white:fontsize=%s:x=w*0.01:y=h*0.93"'%(version,text_size)
        frame_cmd = 'drawtext="fontfile=./resources/arial.ttf:text=\'(%s/%s FPS)\':fontcolor=white:fontsize=%s:x=w-tw-10:y=h*0.93"'%(total_frame,frame_rate,text_size)
        current_frame = 'drawtext="fontfile=./resources/arial.ttf:text=\'%{frame_num}\':start_number=1:fontcolor=white:' + 'fontsize=%s:x=w-tw-10:y=h*0.9"'%(text_size)

        text_list = [author_cmd,shot_name_cmd,project_title_cmd,resolution_label_cmd,task_cmd,version_cmd,frame_cmd,current_frame]
        text_cmd = ','.join(text_list)
        
        return text_cmd

    
    def get_logo_padding_cmd(self,resolution):
        
        original_length, original_height = resolution.split('x')

        padded_height = int(original_height)*1.3             # Video height after adding black bars
        padding_thickness = int(original_height)*0.3/2       # Thickness of each black bar 
        logo_length = padding_thickness*0.8                  # Logo is square shape, '0.8' ensures logo does not exceed black bar
            
        # Round these parameters to integer and change to String 
        padded_height = str(round(padded_height,))
        padding_thickness = str(round(padding_thickness,))
        logo_length = str(round(logo_length,))
        
        
        padding_cmd = '"[0:v]scale=%s[resized];[resized]pad=%s:%s:0:%s[padded];[1:v]scale=%s:%s[img];\
                        [padded][img]overlay=main_w-overlay_w-10:10"'\
                        %(resolution,original_length,padded_height,padding_thickness,logo_length,logo_length)
                        
        return padding_cmd
    

    def create_cmd(self,input_file,logo_file,output_file,codec_cmd,parameter_cmd,text_cmd,logo_padding_cmd,image_sequence_flag):
        global ffmpeg_cmd

        image_cmd = ''
        input_file_cmd = ' -i ' + '"' + input_file + '"'        # '-i' is flag for input file
        output_file_cmd = ' -y ' + '"' + output_file + '"'           # '-y' over write existing files
        logo_file_cmd = ' -i ' + '"' + logo_file + '"' 
        codec_cmd = ' ' + codec_cmd
        parameter_cmd = ' ' + parameter_cmd
        
        
        if image_sequence_flag:
            folder_path,temfile_name = os.path.split(input_file)
            folder_path_cmd = ' -i ' + '"' + folder_path 
            
            image_cmd = ' -f image2'   # Parameter for image and image sequence convertion 
            file_name,extension = os.path.splitext(temfile_name)
            
            # Get starting index 
            # Idea is : assume a file "CVN0070_SH0010_00671.exr", the index is "00671" 
            # first, take only "CVN0070_SH0010_00671"
            # looping and count index backwards ('00671' : 1->7->6->0->0), if character is not digit, break loop.
            i = 1 
            temp = []
            while True:
            
                if file_name[-i].isdigit():
                    temp.insert(0,file_name[-i])
                    i += 1
                else:
                    break
            
            starting_index = ''.join(i for i in temp)
            file_name_without_index = file_name[:-len(starting_index)]
            
            input_cmd = '\\' + '%s'%file_name_without_index + '%' + '0%sd'%len(starting_index) + '%s'%extension + '"'
            
            cmd = ffmpeg_cmd + ' -thread_queue_size 200' + image_cmd + ' -start_number %s'%starting_index \
                         + folder_path_cmd + input_cmd + logo_file_cmd + ' -filter_complex ' + logo_padding_cmd + ',' \
                             + text_cmd + ' -pix_fmt yuv420p' + codec_cmd + output_file_cmd
        

        elif self.still_image_flag:
            cmd = ffmpeg_cmd + input_file_cmd + logo_file_cmd + ' -filter_complex ' + logo_padding_cmd + ',' + text_cmd  + output_file_cmd
           
        else:
            cmd = ffmpeg_cmd + input_file_cmd + logo_file_cmd + ' -filter_complex ' + logo_padding_cmd + ',' + text_cmd  \
                         + codec_cmd + ' -pix_fmt yuv420p' + parameter_cmd + output_file_cmd
     
        print('overlay cmd is %s'%cmd)
        return cmd





##############################################################################################################################
##############################################################################################################################
##############################################################################################################################
class SpliceCMDGenerator(CMDGenerator):

    overlay_flag = False

    def __init__(self):
        CMDGenerator.__init__(self)

        self.ffmpeg_tool = FFMPEGGenerator()
        self.overlay_cmd_generator = OverlayCMDGenerator()

    ##############################################################################################################################
    # This function takes in a file path and its file type
    # and return a input cmd 

    def get_input_file_cmd(self,file_path,identity,duration=None):
        if identity == 'video':
            file_cmd = ' -i "%s"'%file_path

        elif identity == 'still_image':
            file_cmd = ' -loop 1 -t %s -i %s'%(duration,file_path)

        elif identity == 'image_sequence':
            # For image sequence, 'file_path' is a folder path 
            file_cmd = self.get_image_sequence_inp_cmd(file_path)


        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('file cmd for file %s is %s'%(file_path,file_cmd))
        return file_cmd
    

    ##############################################################################################################################
    def get_image_sequence_inp_cmd(self,folder_path):

        # Get all the image files and put them in a list, then re-arrange them in order
        file_list = os.listdir(folder_path)
        file_list.sort()
        
        # Choose the first file(it has the smallest index)
        # When converting an image sequence to a video, a starting index must be specified 
        first_file = file_list[0]       # The file is in this form : filename.extension
        print('first file of %s is %s'%(folder_path,first_file))

        folder_path_cmd = ' -i ' + '"' + folder_path 
        
        image_cmd = ' -f image2'   # Parameter for image and image sequence convertion 
        file_name,extension = os.path.splitext(first_file)
        
        # Get starting index 
        # Idea is : assume a file "CVN0070_SH0010_00671.exr", the index is "00671" 
        # first, take only "CVN0070_SH0010_00671"s
        # looping and count index backwards ('00671' : 1->7->6->0->0), if character is not digit, break loop.
        i = 1 
        temp = []
        while True:
        
            if file_name[-i].isdigit():
                temp.insert(0,file_name[-i])
                i += 1
            else:
                break
        
        starting_index = ''.join(i for i in temp)
        file_name_without_index = file_name[:-len(starting_index)]
            
        input_cmd = '/' + '%s'%file_name_without_index + '%' + '0%sd'%len(starting_index) + '%s'%extension + '"'
    
        file_cmd = ' -thread_queue_size 200' + image_cmd + ' -start_number %s'%starting_index + folder_path_cmd + input_cmd 

        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('image sequence file cmd is : %s'%file_cmd)
        return file_cmd


    ##############################################################################################################################
    # This function takes in one string variable and a list
    # and generates frist half part of filter complex cmd 
    # NOTE: first part only takes video stream from all the input sources

    def get_filter_inp_cmd(self,resolution,scaling,index_num,canvas_index):
       
        resize_cmd = '[%s:v]'%index_num + 'scale=%s:force_original_aspect_ratio=%s'%(resolution,scaling) + '[v%s];'%index_num

        canvas_cmd = "[%s][v%s]overlay=x='(W-w)/2':y='(H-h)/2':shortest=1[v%s];"%(canvas_index,index_num,index_num)

        return resize_cmd,canvas_cmd

    ################################################################################################################################################

    def get_filter_output_cmd(self,index_num,audio_status,dummy_audio_index):
        
        if audio_status == '0':
            filter_output_cmd = '[v%s][%s:a]'%(index_num,dummy_audio_index)

        elif audio_status == '1':
            filter_output_cmd = '[v%s][%s:a]'%(index_num,index_num)

        return filter_output_cmd



    ################################################################################################################################################
    def create_combine_cmd(self,temp_folder,preset_cmd,sequence_list,output_file):
        '''
        Combine all the files in Temp folder
        NOTE: must in sequence
        '''
        global ffmpeg_cmd
        cmd = ffmpeg_cmd
        filter_inp_cmd = '"'

        num_of_file = len(sequence_list)

        for index,each_file in enumerate(sequence_list):
            file_path = temp_folder + '\\' + each_file
            
            cmd += ' -i %s '%file_path
            filter_inp_cmd += '[%s:v][%s:a]'%(index,index)

        filter_output_cmd = ' concat=n=%s:v=1:a=1[v][a]" -map "[v]" -map "[a]" '%num_of_file

        cmd += ' -filter_complex ' + filter_inp_cmd + filter_output_cmd + preset_cmd + ' -y ' + output_file

        return cmd


    ################################################################################################################################################
    def create_temp_folder(self,output_file):
        '''
        Create a temp folder
        Assuming output file is '\test\output.mov\', temp folder will be '\test\output_Temp\'
        '''

        folder,full_file_name = os.path.split(output_file)
        file_name,extension = os.path.splitext(full_file_name)

        folder_name = file_name.strip() + '_Temp'

        temp_folder = folder + '\\' + folder_name
        
        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)

        return temp_folder,extension

    ################################################################################################################################################
    def create_cmd(self,output_file,preset_parameter_list,sequence_list,file_list_dd,target_resolution):
        
        '''
        Splicing

        NOTE:
        1. input files are in sequence
        2. resize each input file and add to a canvas, add dummy audio if needed, output resized file to a temp folder. 
            Resized file name is 'temp_' + original file name
            Assume output file is 'out.mp4', the temp folder will be 'out_Temp'
        3. combine all the files in folder 'out_Temp' and output 'out.mp4'
        4. delete 'out_Temp' foder

        * this function handles point 2. only, point 3. combine cmd is done by another function

        '''
        
        cmd_list = []
        temp_folder, output_extension = self.create_temp_folder(output_file)
        input_cmd = ''
        filter_inp_cmd = ' -filter_complex ' + '"'
        resize_cmd = ''
        canvas_cmd = ''
        preset_cmd = self.get_preset_cmd(preset_parameter_list)


        filter_output_cmd = ''

        # [input_file, canvas , dummy audio]
        file_index = 0
        canvas_index = 1
        dummy_audio_index = 2

        for each_file in sequence_list:      

            file_path = file_list_dd[each_file]['file_path']
            identity = file_list_dd[each_file]['identity']
            audio_status = file_list_dd[each_file]['audio']
            scaling =file_list_dd[each_file]['scaling']

            if identity == 'still_image':
                t = file_list_dd[each_file]['duration']
                input_cmd = self.get_input_file_cmd(file_path,identity,duration=t)
            else:
                input_cmd = self.get_input_file_cmd(file_path,identity)

            resize_cmd = self.get_filter_inp_cmd(target_resolution,scaling,file_index,canvas_index)[0]
            canvas_cmd = self.get_filter_inp_cmd(target_resolution,scaling,file_index,canvas_index)[1]

            filter_output_cmd = self.get_filter_output_cmd(file_index,audio_status,dummy_audio_index)

        
            # Add dummy audio cmd and canvas cmd
            # Canvas size is input resolution
            input_cmd += ' -f lavfi -i color=s=%s -f lavfi -t 1 -i anullsrc'%target_resolution      
            print('input cmd is %s'%input_cmd)

            filter_output_cmd += ' concat=n=1:v=1:a=1[v][a]' + '"'

            temp_output_file = temp_folder + '\\' + 'temp_' + os.path.splitext(each_file)[0] + output_extension
            filter_cmd = filter_inp_cmd + resize_cmd + canvas_cmd + filter_output_cmd + ' -map "[v]" -map "[a]" ' 

            print('filter input cmd is : %s'%filter_cmd)

            global ffmpeg_cmd
            cmd = ffmpeg_cmd + input_cmd + filter_cmd + preset_cmd + ' -y %s'%temp_output_file
            cmd_list.append(cmd)

        # UPDATE ORDER LIST
        # eg. original file path is '\Test\input.mp4', change it to '\Test\temp_input.mp4'
        for index,each_file in enumerate(sequence_list):
            new_file = 'temp_' + os.path.splitext(each_file)[0].strip() + output_extension
            sequence_list[index] = new_file 


        combine_cmd = self.create_combine_cmd(temp_folder,preset_cmd,sequence_list,output_file)
        cmd_list.append(combine_cmd)

        rm_temp_cmd = 'rmdir /s/q %s'%temp_folder
        cmd_list.append(rm_temp_cmd)

        return cmd_list


    ################################################################################################################################################
    def get_overlay_cmd(self,preset_cmd,preset_parameter_list,overlay_info_list,output_file,target_resolution):
        '''
        Add overlay to output file
        1. rename 'output.mp4' to 'temp_overlay_output.mp4'
        2. take 'temp_overlay_output.mp4' as input, add overlay, and output 'output.mp4'
        3. delete 'temp_overlay_output.mp4'
        
        '''

        project_name,author,task,version = overlay_info_list
        total_frame = self.ffmpeg_tool.get_total_frame(output_file)
        frame_rate = preset_parameter_list[0].strip()

        # dir is current script or exe directory
        if getattr(sys,'frozen',False):
            # current application is a exe
            dir = os.path.dirname(sys.executable)
        elif __file__ :
            # current application is a script 
            dir = os.path.dirname(__file__)

        logo_file = dir + r'\resources\Omens_logo.png'
        logo_file_cmd = ' -i ' + logo_file
        
        output_folder,out_put_file = os.path.split(output_file)
        temp_overlay_file = output_folder + '\\' + 'temp_overlay_' + out_put_file
        os.rename(output_file,temp_overlay_file)
        input_file_cmd = ' -i ' + '"' + temp_overlay_file + '"'

        file_name = os.path.splitext(out_put_file)[0]
        # For Splicing, resized resolution is the same as original resolution
        text_cmd = self.overlay_cmd_generator.get_text_CMD(file_name,project_name,author,task,version,frame_rate,target_resolution,target_resolution,total_frame)
        logo_padding_cmd = self.overlay_cmd_generator.get_logo_padding_cmd(target_resolution)
        
        global ffmpeg_cmd
        cmd = ffmpeg_cmd + input_file_cmd + logo_file_cmd + ' -filter_complex ' + logo_padding_cmd + ',' + text_cmd + ' ' \
              + preset_cmd + ' -y ' + output_file

        return cmd





if __name__ == '__main__':
    pass
    # a = OverlayCMDGenerator()
    # text_cmd = a.get_text_CMD('TTTT11111','CL','xxx','TEST','001','25','1920x1080')
    # logo_cmd = a.get_logo_padding_cmd('1920x1080')
    # cmd = a.create_cmd('1.avi','logo.png','out.mp4','-vcodec h264',' -f 25 -b 10M',text_cmd,logo_cmd,'')
    # print(cmd)
    
    











