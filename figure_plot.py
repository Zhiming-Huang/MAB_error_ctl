#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 16:43:33 2022

@author: zhiming
"""
import matplotlib.pyplot as plt


pkts_per_frm_perc = R_packets / pkts_per_frm

plt.plot(pkts_per_frm_perc[0:1000])

plt.xlabel("Frames")
plt.ylabel("Frame Completeness")


plt.savefig("frame_averaged_reward.eps", format="eps")


plt.legend(["MAB", "ARQ", "FEC"])
