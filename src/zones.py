from PIL import Image
from threading import Lock, Thread
from src.loader import Loader
import os
import yaml
import time
import random as rd

class Zone():
    def __init__(self, provider, buffer, size, screens_parameter, options={}):
        self.size = size
        self.provider = provider
        self.bg = Image.new("RGBA", self.size)
        self.buffer = buffer
        self.options = options
        self.screens = [
                            {
                            "screen": sp[0],
                            "box":    sp[1],
                            "pos":    sp[2],
                            "clear":  self.bg.crop( sp[1] )
                            }
                            for sp in screens_parameter
                        ]
        self.loader = Loader(provider=provider, buffer=self.buffer, screens=self.screens, size=self.size, default_time=rd.random() * 5)
        # execute loader as Thread right now
        self.loader_threads = Thread( target= self.loader._run_)
        self.loader_threads.start()

    def clear(self):
        print(self.screens)
        
        for s in self.screens:
            try:
                s["screen"]["screen"].mutex.acquire()
                s["screen"]["screen"].disp( s["clear"], s["pos"] )
            except Exception as e:
                print("error while displaying:", e)
            finally:
                s["screen"]["screen"].mutex.release()

    def _run_(self):
        self.clear()
        
        while True:
            for folder in os.listdir(self.buffer):
                if folder == "config.yaml" or os.path.exists(f"{self.buffer}/lock"):
                    continue
                    
                with open(f"{self.buffer}/{folder}/info.yaml") as f:
                    info = yaml.load(f, Loader=yaml.SafeLoader)
                    
                for frame in range(info["nb_frames"]):
                    img_time = list(filter( lambda x:x["name"] == f"{frame}.png", info["frames"]))[0]["time"]
                    self.disp(folder, frame, img_time)
                

        # while true -> list folder in buffer without lock file
        #               get number of frame
        #               for img_frame in range(number of frame) disp( img_name, img_frame )
        
    
    
    def disp(self, img_name, img_frame, img_time):
        for s in self.screens:
            s["screen"]["screen"].mutex.acquire()
            image = f"{self.buffer}/{img_name}/{s['screen']['name']}/{img_frame}.png"
            s["screen"]["screen"].disp(Image.open(image), s["pos"])
            s["screen"]["screen"].mutex.release()
        time.sleep( img_time )
        # find image in '/[BUFFER]/[img_name].[\d+]/[^/]+/[n_frame].[time_in_s]' with regex
        # for s in self.screens: s["screen"].disp( found_img )
        # sleep time_in_s
