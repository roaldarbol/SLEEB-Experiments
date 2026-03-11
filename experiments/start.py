import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import time
import belay
from devices.PicoBonn import PicoBonn

# Initialize device
spec = belay.UsbSpecifier(vid=11914, pid=5, serial_number='70973D3DE68AC915', manufacturer='Microsoft', location='1-8:x.0')
pico = PicoBonn(spec)