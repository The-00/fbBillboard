from PIL import Image
from threading import Lock
from src.loader import Loader
import time


class Zone():
    def __init__(self, provider, buffer, size, screens_parameter, options={}):
        self.size = size
        self.provider = provider
        self.clear = Image.new("RGBA", self.size)
        self.buffer = buffer
        self.screens = [
                            {
                            "screen": sp[0],
                            "box":    sp[1],
                            "pos":    sp[2],
                            "clear":  self.clear.crop( sp[1] )
                            }
                            for sp in screens_parameter
                        ]
        self.loader = Loader(provider=provider, buffer=self.buffer, screens=self.screens)
        # execute loader as Thread tight now

    def clear(self):
        for s in self.screens:
            try:
                s["screen"].mutex.acquire()
                s["screen"].disp( s["clear"], s["pos"] )
            except Exception as e:
                print("error while displaying:", e)
            finally:
                s["screen"].mutex.release()

    def run(self):
        # while true -> list folder in buffer without lock file
        #               get number of frame
        #               for img_frame in range(number of frame) disp( img_name, img_frame )
        pass
    
    
    def disp(img_name, img_frame):
        # find image in '/[BUFFER]/[img_name].[\d+]/[^/]+/[n_frame].[time_in_s]' with regex
        # for s in self.screens: s["screen"].disp( found_img )
        # sleep time_in_s
        pass
