#!/bin/python3
from src.billboard import BillBoard
import argparse
import yaml

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prefix_chars='-')
    parser.add_argument("-c", "--config",
                            type=str,
                            default="config.yaml",
                            help="config file to load"
                        )

    args = parser.parse_args()
    config_file = args.config

    billboard = BillBoard()
    
    with open(config_file) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
        for s in data["screens"]:
            position = (s['position-on-wall']['x'], s['position-on-wall']['y'])
            size = (s['size']['x'], s['size']['y']) if 'size' in s else None
            billboard.register_screen( name=s['name'],
                                       socket=s['socket'],
                                       position=position,
                                       orientation=s['orientation'] if 'orientation'in s else 0,
                                       size = size if 'size' in s else None
                                    )
        
        for z in data["zones"]:
            size = (z['size']['x'], z['size']['y'])
            position = (z['position']['x'], z['position']['y'])
            billboard.register_zone( name=z['name'],
                                       provider=z['provider'],
                                       buffer=z['buffer'],
                                       position=position,
                                       size=size,
                                       options=z['options'] if 'options'in z else {}
                                    )
        
        billboard.run()
        
    