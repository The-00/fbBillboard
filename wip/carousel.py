class Carousel():
    def __init__(self, folder, zone, default_time=10):
        self.folder = folder
        self.zone = zone
        self.default_time = default_time
        self.imgs = {}    # format { name: (hash, [ img [, ...] ], time) }
        self._initialize_()
    
    def _hashFile_(self, path, buf_size=65536):
        md5 = hashlib.md5()

        with open(path, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                md5.update(data)

        return md5.hexdigest()
    
    def _load_(self, path):
        ext = path.split(".")[-1].lower()
        images = []
        opt = { "ext":ext, "type":None }

        try:
            if ext in [ "png", "jpg", "jpeg", "bmp" ]:
                images = [ Image.open(path) ]
                opt["type"] = "image"
            
            elif ext in [ "gif" ]:
                gif = Image.open(path)
                images = [ gif.seek(frame) for frame in range(0, gif.n_frames)]
                opt["type"] = "gif"
                
            elif ext in [ "pdf" ]:
                images = pdf2image.convert_from_path( path )
                opt["type"] = "pdf"

            elif ext in [ "avi", "mp4", "mpv", "webm" ]: 
                capture = cv2.VideoCapture( path )
                while (True):
                    success, frame = capture.read()

                    if success:      images.append( Image.fromarray( cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) ) )
                    else:            break
                capture.release()
                opt["type"] = "video"
                opt["frame_rate"] = capture.get(cv2.CAP_PROP_FPS)
        
            if len(images) == 0:
                raise Exception(f"no image loaded for file {path}") 
            else:
                self._log_( f"load {path} as  {ext}: {len(images)} file{'s' if len(images)>1 else ''} loaded")

        except Exception as e:
            self._log_( f"Error for file {path}: {e}" )
            error_img = Image.new("RGBA", self.zone.size)
            draw = ImageDraw.Draw(error_img)
            draw.text((10, 10), f"Error for file {path} : {e}", fill=(255, 0, 0))
            images = [ error_img ]

        opt["count"] = len(images)
        return images, opt

    def _log_(self, string):
        print( f"[ {self.zone.name} ] :", string)

    def update(self):
        self._initialize_()

    def _initialize_(self):
        # load new image or if change
        actual_files = [f"{self.folder}/{f}" for f in os.listdir(self.folder)]
        for f in actual_files:
            name_img = f
            time_img = int( f.split(".")[-2] ) if len(f.split(".")) > 2 else self.default_time
            hash_img = self._hashFile_( name_img )

            if name_img in self.imgs.keys() and self.imgs[name_img]["hash"] == hash_img: continue     # refresh only if content change or new file

            imgs, opt = self._load_( name_img )

            if opt["type"] in [ "pdf", "gif" ]:
                time_img = time_img / float(opt["count"])                                            # display each page/frame to display full document in time_img 
            if opt["type"] in [ "video" ]:
                time_img = opt["frame_rate"]                                                         # use the video frame rate
            if opt["type"] in [ "url" ]:
                hash_img = None                                                                      # force refresh each time
            
            self._log_( f"add new file {name_img}" )
            self.imgs[ name_img ] = {
                "hash": hash_img,
                "time": time_img,
                "imgs": imgs
            }
        
        # remove old image
        for f in self.imgs:
            if f not in actual_files:
                self._log_( f"remove old file {self.imgs.pop(f)}" )
    
    def stop(self):
        self.running = False
        self._log_("stopping the carousel on zone")
        self.thread.join()

    def start(self):
        self.running = True
        self._log_("start the carousel on zone")
        self.thread = threading.Thread( target= self._run_ )
        self.thread.start()
    
    def _run_(self):
        while self.running:
            for img_name in self.imgs:
                self._log_( f"display {img_name} during {self.imgs[img_name]['time'] * len(self.imgs[img_name]['imgs'])}s" )
                try:
                    for img in self.imgs[img_name]["imgs"]:
                        self.zone.disp( img, self.imgs[img_name]["time"] )
                except Exception as e:
                    self._log_( f"error displaying : {e}" )
