#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 15:25:37 2022

@author: zhiming
"""

import queue
import numpy as np
from SplayTree import *

#read the tracefile
tracefile = open("starwars.frames.old","r+")
traces = tracefile.read().splitlines()
traces = np.array(list(map(int,traces)))
tracefile.close()

def frametype(frm_num):
    # 1 for I, 2 for B, and P for 3
    ret = frm_num % 12
    if ret == 1:
        return 1
    elif 1<ret<4 and 4<ret<7 and 7<ret<10 and 10 < ret <=12:
        return 2
    else:
        return 3



accumu_packets = np.cumsum([int(item/1024) for item in traces])


class packet:
    def __init__(self, pktno):
        self.pktno = pktno

class event:
    def __init__(self, evtype):
        self.evtype = evtype # 0 for packet generation, 1 for packet sent
        

while True:
    # Get imminent 