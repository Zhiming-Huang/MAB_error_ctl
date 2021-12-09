#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 13:38:00 2021

@author: zhiming
"""
import matplotlib
from contex_mab import *
import numpy as np


drp_rate = 0.2

#RTT =  150 assume one trip time is 75ms, and round trip time is 150ms
num_seg = 5000

#RTT =  np.random.uniform(140,160,num_seg)
#drp = np.random.binomial(1,drp_rate,num_seg)

# A basic-layer segment follows by a enhancement-layer segment
packet_imp = 1
delay_req_perseg = 120
# Assume every 200ms, two segment (i.e., basic and enhancement) with 200ms content is generated
# and the delay requirement for this segment is 120 ms for each segment
# the maximum snd_wnd is 2, i.e., at most two segments can be sent at a time
snd_wnd = 2

mabctl = MAB_Control()

# Initially, we have two segments already generated
seg_buffer = 2

t = 0

segment_spawn = np.zeros(num_seg) + 200
segment_spawn[0] = 0
seg_buffer = np.cumsum(segment_spawn)
#Context: (delay_req, seg_importance, seg_sndbuffer, seg_bitrate, snd_wnd)


for i in range(num_seg):
    
    rtt =  np.random.uniform(140,160,num_seg)
    mabctl.update_rtt(update_rtt)
    #observe context
    seg_buffer = np.where(seg_buffer<t)[0].size() - i
    delayReq = seq_buffer[i] + delay_req_perseg - t
    mabctl.input_context(delayReq, packet_imp, seg_buffer, snd_wnd)
    packet_imp = -packet_imp
    action1 = mabctl.exp3_action()
    if action1 == 0:
        delay = np.random.geometric(1-drp_rate)
        
