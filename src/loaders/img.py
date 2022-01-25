from PIL import Image,ImageEnhance

class Loader():
    def __init__(self):
        pass
    
    def load(self, imgtoload, wheretobuffer, box, full_size, full_time):
        img = Image.open(imgtoload).resize( full_size ).crop( box )
        conf = []
        enhancer = ImageEnhance.Brightness(img)
        
        # fade_time : 1 seconde or 10%of time AND 15fps
        fade_time = min(full_time/10., 1)
        # number of frames at 30FPS
        nb_fade_frames = int(fade_time * 30)
        
        # fade in
        for i in range(nb_fade_frames):
            f_img = enhancer.enhance(i/nb_fade_frames)
            f_img.save( wheretobuffer + '/' + f'{i}.png' )
            conf.append( (f'{i}.png', fade_time/nb_fade_frames) )
        
        img.save( wheretobuffer + '/' + f'{nb_fade_frames}.png' )
        conf.append( (f'{nb_fade_frames}.png', full_time - 2*fade_time) )
        
        # fade out
        for i in range(1,nb_fade_frames+1):
            f_img = enhancer.enhance(1-i/nb_fade_frames)
            f_img.save( wheretobuffer + '/' + f'{i+nb_fade_frames}.png' )
            conf.append( (f'{i+nb_fade_frames}.png', fade_time/nb_fade_frames) )
        
        return conf
    
    def okfor(self):
        return [
            'png','jpg','jpeg','bmp'
        ]