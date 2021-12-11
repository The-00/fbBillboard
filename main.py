#!/bin/python3
from billboard import BillBoard
import yaml

if __name__ == "__main__":

    billboard = BillBoard()
    
    with open('config.yaml') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
        
        for z in data["zones"]:
            print(z)
            


    billboard.add_carousel( folder="/home/theau/framebuffer-tests/1", screen=0, position=(  0,  0), size=(0.7,  1) )

    billboard.run()
    # billboard.update(20) # hold