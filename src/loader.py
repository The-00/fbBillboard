class Loader():
    def __init__(self, provider, buffer, screens):
        self.provider = provider
        self.buffer = buffer
        self.screens = screens
    
    def run(self):
        # while true -> execute __watch__ + sleep 
        pass
    
    def __watch__(self):
        # test if modification in provider folder
        # if new file -> __create__
        # if rm  file -> __remove__
        pass
    
    def __create__(self, img_name):
        # create the buffer folder with lock file and create each frame
        # lock inside '/[BUFFER]/[img_name].[tot_time_in_s]' as 'lock'
        # file format: /[BUFFER]/[img_name].[tot_time_in_s]/[SCREENNAME]/[n_frame].[time_in_s]
        # when complete : remove lock file
        pass
    
    def __remove__(self, img_name):
        # put lock file in folder
        # wait tot_time_in_s
        # remove the folder
        pass