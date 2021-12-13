from PIL import Image
from threading import Lock

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
        self.actual_image.paste(img, position)
        with open(self.socket, "wb") as buf:
            buf.write( self.actual_image.tobytes('raw', 'BGRA', 0, 1) )

class VirtualScreen(Screen):
    def __init__(self, size):
        self.size = size
        self.mutex = Lock()
    
    def clear(self):
        print("no display on Virtual Screen")
    
    def disp(self, img, position):
        print("no display on Virtual Screen")