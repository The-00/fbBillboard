import os, shutil
import yaml
import threading
import time
import src.tools as tools

from src.loaders.img import Loader as Img_Loader

list_loader = [
    Img_Loader()
]

class Loader():
    def __init__(self, provider, buffer, screens, size, default_time):
        self.provider = provider
        self.buffer = buffer
        self.screens = screens
        self.config_lock = threading.Lock()
        self.size = size
        self.default_time = default_time
        self.conf_hash = None
        
        os.system(f"mkdir -p {self.buffer}")
        
        if os.path.exists(f"{self.buffer}/config.yaml"):
            with open(f"{self.buffer}/config.yaml") as f:
                self.config = yaml.load(f, Loader=yaml.SafeLoader)
        else:
            self.config = {
                "provider": self.provider,
                "size"    : list(self.size),
                "buffer"  : self.buffer,
                "screens" : [ [s['screen']['name'], s['box'], s['pos']] for s in self.screens],
                "images"  : {}
            }
            with open(f"{self.buffer}/config.yaml", "w") as f:
                f.write( yaml.dump(self.config) )
 
    def _run_(self):
        while True:
            self.__watch__()
            
            actual_conf_hash = tools.hash(f"{self.buffer}/config.yaml")
            if self.conf_hash != actual_conf_hash:
                with open(f"{self.buffer}/config.yaml", "w") as f:
                    f.write( yaml.dump(self.config) )
                self.conf_hash = actual_conf_hash
            
            time.sleep(1)
    
    def __watch__(self):
        # test if modification in provider folder
        img_to_load = os.listdir(self.provider)
        
        # if new file -> __create__
        for img_name in img_to_load:
            h = tools.hash( f"{self.provider}/{img_name}" )
            if img_name not in self.config["images"] or h != self.config["images"][img_name]["hash"]:
                print('add', img_name, 'from', self.provider)
                self.__create__( img_name )
        
        # if rm  file -> __remove__
        for img_loaded in list(self.config["images"].keys()):
            if img_loaded not in img_to_load:
                print('rem', img_loaded, 'from', self.provider)
                self.__remove__(img_loaded)

    def __select_loader__(self, filename):
        # select loader from list of loader by type
        ext = filename.split(".")[-1].lower()
        for l in list_loader:
            if ext in l.okfor():
                return l
        raise Exception(f"no loader found for '{ext}' file")
    
    def __create__(self, img_name):
        # create the buffer folder with lock and info files and create each frame
        try:
            file_buffer = f"{self.buffer}/{img_name.split('.')[0]}"
            os.makedirs(file_buffer, exist_ok = True)
            
            # lock inside '/[BUFFER]/[img_name]' as 'lock'
            open(f"{file_buffer}/lock", "w").close()
            # info inside '/[BUFFER]/[img_name]' as 'info.yaml'
            open(f"{file_buffer}/info.yaml", "w").close()
            # update_config
            self.config["images"][img_name] = {
                "buffer_path": file_buffer,
                "provider_path": f"{self.provider}/{img_name}",
                "hash": tools.hash( f"{self.provider}/{img_name}" ),
                "total_time_sec": 0,
                "info": {"frames":[], "screens":[], "nb_frames":float("inf")}
            }
            
            specific_loader = self.__select_loader__( f"{self.provider}/{img_name}" )
            
            
            for s in self.screens:
                file_screen_buffer = f"{file_buffer}/{s['screen']['name']}"
                os.makedirs(file_screen_buffer, exist_ok = True)
                
                imgs_conf = specific_loader.load( f"{self.provider}/{img_name}", file_screen_buffer, s['box'], self.size, self.default_time)
                self.config["images"][img_name]["info"]["screens"].append( s['screen']['name'] )
                self.config["images"][img_name]["info"]["nb_frames"] = min(len(imgs_conf), self.config["images"][img_name]["info"]["nb_frames"])
                for ic in imgs_conf:
                    self.config["images"][img_name]["total_time_sec"] += ic[1]
                    self.config["images"][img_name]["info"]["frames"].append( 
                                            {"screen":s['screen']['name'], "name":ic[0], "time":ic[1]}
                                        )
            
            with open(f"{file_buffer}/info.yaml", "w") as f:
                f.write( yaml.dump(self.config["images"][img_name]["info"]) )
            
            os.remove(f"{file_buffer}/lock")
                
        except Exception as error:
            print(error)
        # file format: /[BUFFER]/[img_name]/[SCREENNAME]/[n_frame].png
        
    
    def __remove__(self, img_name):
        file_buffer = f"{self.buffer}/{img_name.split('.')[0]}"
        # put lock file in folder
        open(f"{file_buffer}/lock", "w").close()
        # wait tot_time_in_s
        time.sleep( self.config["images"][img_name]["total_time_sec"] *2)
        # remove the folder
        shutil.rmtree( file_buffer )
        self.config["images"].pop(img_name)
        self.conf_hash = None

        