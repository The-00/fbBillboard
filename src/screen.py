from PIL import Image
from threading import Lock
import time

class Screen():
    def __init__(self, socket):
        self.socket = socket
        self.mutex = Lock()
        
        self.size_str = open(f"/sys/class/graphics/{ self.socket.split('/')[-1] }/virtual_size")
        for l in self.size_str:
            self.size = list(map(int,l[:-1].split(',')))
        
        self.blanck = Image.new("RGBA", self.size)
        self.actual_image = self.blanck.copy()

    def clear(self):
        with open(self.socket, "wb") as buf:
            buf.write( self.blanck.tobytes() )
        
    def disp(self, img, position):
        #actual_image = Image.frombuffer("RGB", self.size, open(self.socket, "rb").read(), 'raw', 'RGB', 0, 1)
        
        self.actual_image.paste(img, position)
        
        #self.actual_image.save("/tmp/vision.png")
        with open(self.socket, "wb") as buf:
            buf.write( self.actual_image.tobytes('raw', 'BGRA', 0, 1) )
        

class Zone():
    def __init__(self, screen, size, position, name, border=False):
        self.size = size
        self.screen = screen
        self.position = position
        self.name = name
        self.border = border
        self.clear = Image.new("RGBA", self.size)

    def clear(self):
        try:
            self.screen.mutex.acquire()
            self.screen( self.clear, self.position)
        except Exception as e:
            print("error while displaying:", e)
        finally:
            self.screen.mutex.release()

    def disp(self, img, time_img):
        maxwidth, maxheight = self.size
        back = self.clear.copy()

        ratio = float(img.size[0]) / float(img.size[1])
        newheight = int( maxwidth / ratio )
        newwidth  = int( maxheight * ratio )

        if newwidth < maxwidth:
            img = img.resize( (newwidth, maxheight) )
        else:
            img = img.resize( (maxwidth, newheight) )

        decalX = (maxwidth - img.size[0]) // 2
        decalY = (maxheight - img.size[1]) // 2

        back.paste(img, (decalX,decalY))

        try:
            self.screen.mutex.acquire()
            #back.save("/tmp/"+self.name + ".vision.png")
            self.screen.disp( back, self.position )
        except Exception as e:
            print("error while displaying:", e)
        finally:
            self.screen.mutex.release()
        time.sleep( time_img )
