from PIL import Image, ImageDraw, GifImagePlugin
import pdf2image
import time
import hashlib
import threading
import cv2
import os
import re
from src.screens import Screen, VirtualScreen
from src.zones import Zone


class BillBoard():
    def __init__(self):
        self.screens   = []
        self.zones     = []
        
        self.variables = { }

    def register_screen(self, name, socket, position, orientation=0, size=None):
        s = {
                'name':        name,
                'screen':      None,
                'socket':      socket,
                'size':        size,
                'position':    position,
                'orientation': orientation
        }
        
        if socket == 'virtual':
            s['screen'] = VirtualScreen(size)
        else:
            s['screen'] = Screen(socket)
            
        self.variables[ s['name'] ] = {
            'sx': s['screen'].size[0],
            'sy': s['screen'].size[1],
            'px': s['position'][0],
            'py': s['position'][1]
        }    
        self.screens.append( s )
    
    def register_zone(self, name, provider, buffer, position, size, options={}):
        z = {
                'name':     name,
                'zone':     None,
                'provider': provider,
                'buffer':   buffer,
                'size':     size,
                'position': position,
                'options':  options
        }
        self.variables[ z['name'] ] = {
            'sx': z['size'][0],
            'sy': z['size'][1],
            'px': z['position'][0],
            'py': z['position'][1]
        }
        self.zones.append( z )
    
    def get_variable(self, name, subtype_var):
        value = self.variables[name][subtype_var]
        if type(value) == int :
            return value
        else:
            pattern = '{[^:]+:[^}]+}'
            for token in re.findall(pattern, value):
                token_name, token_subtype = token[1:-1].split(':')
                token_value = self.get_variable(token_name, token_subtype)
                value = value.replace( token, str(token_value))
            self.variables[name][subtype_var] = int( eval( value ) )
            return self.variables[name][subtype_var]
            
    def __apply_variables__(self):
        for s in self.screens:
            s['size'] = ( self.get_variable(s['name'], 'sx'), self.get_variable(s['name'], 'sy')  )
            s['position'] = ( self.get_variable(s['name'], 'px'), self.get_variable(s['name'], 'py')  )
            
        for z in self.zones:
            z['size'] = ( self.get_variable(z['name'], 'sx'), self.get_variable(z['name'], 'sy')  )
            z['position'] = ( self.get_variable(z['name'], 'px'), self.get_variable(z['name'], 'py')  )
    
    def __to_rect__(self, element):
        return [
                    element["position"][0],
                    element["position"][1],
                    element["size"][0],
                    element["size"][1]
                ]
        
    def __overlapp__(self, zone, screen):
        zone_rect = self.__to_rect__(zone)
        screen_rect = self.__to_rect__(screen)
        
        x1,y1,w1,h1=zone_rect
        x2,y2,w2,h2=screen_rect
 
        inter_w=(w1+w2)-(max(x1+w1,x2+w2)-min(x1,x2))
        inter_h=(h1+h2)-(max(y1+h1,y2+h2)-min(y1,y2))
        inter_x=max(x1,x2)
        inter_y=max(y1,y2)
        
        if inter_w <= 0 or inter_h <= 0:
            return None
        else:
            return [inter_x, inter_y, inter_w, inter_h]

    
    def run(self):
        self.__apply_variables__()
        
        for z in self.zones:
            screens_parameter = []
            # describe each screen to compute which part of the image it should display
            for s in self.screens:
                rect = self.__overlapp__(z, s)
                if rect != None:
                    rect_coord_for_zone = [rect[0]-z["position"][0], rect[1]-z["position"][1],
                                           rect[2], rect[3]]
                    rect_position_on_screen = [rect[0]-s["position"][0], rect[1]-s["position"][1]]
                    # (the screen, the part of the image it display, where on the screen)
                    screens_parameter.append( (s, rect_coord_for_zone, rect_position_on_screen) )
            
            z["zone"] = Zone( 
                             provider=z["provider"],
                             buffer=z["buffer"],
                             size=z['size'],
                             options=z["options"],
                             screens_parameter=screens_parameter
                             )
            print(z["name"], ":", z["size"])
            for sp in screens_parameter:
                print("  ", sp[0]["name"], ":", sp[1:])
        
        # Run all Zones in Threads
        time.sleep(10)
        self.zones_threads = []
        for z in self.zones:
            z_thread = threading.Thread( target= z["zone"]._run_)
            z_thread.start()
            self.zones_threads.append( z_thread )
        
        
    
        
