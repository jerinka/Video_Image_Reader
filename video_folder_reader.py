import cv2
import os
import re
# import pdb;pdb.set_trace()
import base64
import re 

import abc

class FrameReaderInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'setFrame_num') and 
                callable(subclass.setFrame_num) and 
                hasattr(subclass, 'next_frame') and 
                callable(subclass.next_frame) or 
                NotImplemented)

    @abc.abstractmethod
    def setFrame_num(self, frame_num: int):
        """Load in the data set"""
        raise NotImplementedError

    @abc.abstractmethod
    def next_frame(self):
        """Extract text from the data set"""
        raise NotImplementedError


class Video_reader(FrameReaderInterface):
    def __init__(self, video_path='video', decode_mode=False):
    
        self.video_path = video_path
        assert os.path.isfile(video_path), "Video path doesnt exist"
        self.video_name = os.path.splitext(os.path.basename(self.video_path))[0]
        self.cap               = cv2.VideoCapture(video_path)
        self.total_frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_num       = 0
        self.decode_mode = decode_mode

    def setFrame_num(self, frame_num=0):
        # import pdb;pdb.set_trace()
        if frame_num > self.total_frame_count:
            print("*"*50)
            print("{} exceeded total frame count {}".format(frame_num, self.total_frame_count))
            print("*"*50)
        if frame_num > self.total_frame_count or frame_num<0:
            print("Error! frame_num > self.total_frame_count or frame_num<0")
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)        
        self.frame_num = frame_num        
        return True

    def next_frame(self):
        _, frame = self.cap.read()
        if self.decode_mode is False:
            frame_str = cv2.imencode('.jpg', frame)[1].tobytes()
            img_bytes = base64.b64encode(frame_str).decode('ascii')
        
        filename_ = os.path.splitext(os.path.basename(self.video_path))[0]
        filename = '_fn'.join([filename_, str(self.frame_num)])
        self.frame_num+=1
        if self.frame_num<=self.total_frame_count:
            if self.decode_mode is False:
                return img_bytes, self.frame_num - 1, filename
            else:
                return frame, self.frame_num-1, filename
        else:
            return None, None, None
            
class Folder_reader(FrameReaderInterface):
    def __init__(self, folder_path='video', decode_mode=False):
        self.total_frame_count=0
        self.image_names=[]
        self.image_paths=[]
        self.frame_num = 0
        self.folder_path = folder_path
        self.decode_mode = decode_mode
        assert os.path.isdir(folder_path), "folder_path doesnt exist"
        for root, _, files in os.walk(self.folder_path):
            for index,file in enumerate(files):
                if isImageFile(file):
                    self.total_frame_count +=1
                    self.full_p = os.path.join(root, file)
                    self.img_name = os.path.splitext(os.path.basename(self.full_p))[0]
                    self.image_names.append(self.img_name)
                    self.image_paths.append(self.full_p)        
        self.image_paths.sort(key=lambda f: int(re.sub('\D', '', f)))
    
    def setFrame_num(self,frame_num):
        if frame_num > self.total_frame_count:
            print("*"*50)
            print("{} exceeded total frame count {}".format(frame_num, self.total_frame_count))
            print("*"*50)
        if frame_num > self.total_frame_count or frame_num<0:
            print("Error! frame_num > self.total_frame_count or frame_num<0")        
        self.frame_num = frame_num
        return True        


    def next_frame(self):
        self.frame_num+=1
        #print("******************frame_num****************",self.frame_num-1)
        if self.frame_num<=self.total_frame_count:
            imgpath = self.image_paths[self.frame_num-1]
            #import pdb;pdb.set_trace()
            filename = os.path.splitext(os.path.basename(imgpath))[0]
            if self.decode_mode is False:
                img_bytes = open(imgpath,"rb").read()
                img_bytes = base64.b64encode(img_bytes).decode('ascii')
                return img_bytes,self.frame_num-1,filename
            else:
                img_array = cv2.imread(imgpath)
                return img_array,self.frame_num-1,filename
            
        else:
            return None,None,None
        
def get_reader_class(path, video_mode=True, decode_mode=True):
    if video_mode:
        return Video_reader(path, decode_mode)
    else:
        return Folder_reader(path, decode_mode)



if __name__=='__main__':
     
    if 1:
        reader = get_reader_class("videos/19991231_234627_NF.mp4",video_mode=True)
        reader.setFrame_num(3)
        image,framenum,name = reader.next_frame()
        print(f'image shape:{image.shape}, framenum:{framenum}, name:{name}')
        
