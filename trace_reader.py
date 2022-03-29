#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 17:51:29 2022

@author: zhiming
"""

import matplotlib.pyplot as plt
import numpy as np
import math

tracefile = open("starwars.frames.old","r+")
traces = tracefile.read().splitlines()
traces = np.array(list(map(int,traces)))


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

fig, ax = plt.subplots()
ax.plot(traces)
ax.set_xlabel('Frame Number')
ax.set_ylabel('Frame Size')