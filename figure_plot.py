#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 16:43:33 2022

@author: zhiming
"""
import matplotlib.pyplot as plt


pkts_per_frm_perc = R_packets / pkts_per_frm

#plt.boxplot(pkts_per_frm_perc[0:1000])
plt.hist(pkts_per_frm_perc)
plt.xlabel("Frame Completeness")
plt.ylabel("Frame Number")


#plt.savefig("frame_averaged_reward.eps", format="eps")


#plt.legend(["MAB", "ARQ", "FEC"])
