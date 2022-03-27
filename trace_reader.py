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


fig, ax = plt.subplots()
ax.plot(traces)
ax.set_xlabel('Frame Number')
ax.set_ylabel('Frame Size')