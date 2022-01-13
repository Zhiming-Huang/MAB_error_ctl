#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 11:40:32 2022

@author: zhiming
"""
import matplotlib.pyplot as plt
import contex_mab
import numpy as np


drp_rate = 0.05

#RTT =  150 assume one trip time is 75ms, and round trip time is 150ms
num_seg = 100000

RTT =  np.random.uniform(50,70,num_seg)
retrxs = np.random.geometric(1-drp_rate,num_seg)
fecscss = np.random.binomial(2,1-drp_rate,num_seg)
# A basic-layer segment follows by a enhancement-layer segment
packet_imp = 1

delay_req_perseg = 180
# Assume each segment contains 6 frames, i.e., 1 segment per 100 ms
# and the delay requirement for this segment is 150 ms for each segment
# the maximum snd_wnd is 2, i.e., at most two segments can be sent at a time
snd_wnd = 2

mabctl = contex_mab.MAB_Control()

# Initially, we have two segments already generated
seg_buffer = 2

t = 0  #for tracking the time of mab
t1 = 0 #for tracking the time of arq
t2 = 0 #for tracking the time of fec

segment_spawn = np.zeros(num_seg) + 100
segment_spawn[0] = 0
seg_spawn_time = np.cumsum(segment_spawn)
#Context: (delay_req, seg_importance, seg_sndbuffer, seg_bitrate, snd_wnd)


def reward_observed(action,rtt,delayReq,packet_imp,retrxsfori,fecscssfori):
    reward = 0
    delay = 0
    ifdrop = False
    if action == 0: #ARQ
        delay = rtt*retrxsfori
        if delay  > delayReq:
            reward = 0
            ifdrop = True
            delay = delayReq
        else:
            reward = 1
    elif action == 1: #FEC
        delay = rtt
        if fecscssfori == 0:
            reward = 0
            ifdrop = True
        else:
            reward = 1
    else:
        ifdrop = True
        reward = 0
        delay = 0 if packet_imp == 1 else 0
    return reward, delay, ifdrop

actions = np.zeros(num_seg)
delay_packet = np.zeros(num_seg)
reward = np.zeros(num_seg)
reward_arq = np.zeros(num_seg)
reward_fec = np.zeros(num_seg)
packet_receipt = np.zeros(num_seg)


for i in range(num_seg):
    #1 mab process
    #if t > seg_spawn_time[i] + delay_req_perseg:
    #    reward[i] = 0
    #    packet_receipt[i] = 0
    #    continue
    snd_wnd = 2 
    rtt =  RTT[i]
    retrxsfori = retrxs[i]
    fecscssfori = fecscss[i]
    mabctl.update_rtt(rtt)
    #observe context
    seg_buffer = np.where(seg_spawn_time<=t)[0].size - i
    if seg_spawn_time[i] > t: #the seg_buf is empty
        t = seg_spawn_time[i]
    delayReq = seg_spawn_time[i] + delay_req_perseg - t
    if delayReq >= 0:
        mabctl.input_context(delayReq, packet_imp, seg_buffer, snd_wnd)
        action1 = mabctl.exp3_action()
        actions[i] = action1
        reward1, delay1, ifdrop1 = reward_observed(action1,rtt,delayReq,packet_imp,retrxsfori,fecscssfori)
        mabctl.exp3_udate(reward1)
        reward[i] = reward1
        packet_receipt[i] = 1 if not ifdrop1 else 0 #records whether or not packet i is received
        delay_packet[i] = delay1
    else:
        packet_receipt[i] = 0
        reward[i] = 0
    #t = t + delay1 #update the current time
    #2 arq process
    if t1 > seg_spawn_time[i] + delay_req_perseg:
        reward_arq[i] = 0
    else:
        if seg_spawn_time[i] > t1:
            t1 = seg_spawn_time[i]
        delayReq2 = seg_spawn_time[i] + delay_req_perseg - t1
        reward2, delay2, ifdrop2 = reward_observed(0,rtt,delayReq2,packet_imp,retrxsfori,fecscssfori)
        reward_arq[i] = reward2
        t1 = t1 + delay2
        
            
    #3 fec process        
    if t2 > seg_spawn_time[i] + delay_req_perseg:
        reward_fec[i] = 0
    else:
        if seg_spawn_time[i] > t2:
            t2 = seg_spawn_time[i]
        delayReq3 = seg_spawn_time[i] + delay_req_perseg - t2
        reward3, delay3, ifdrop3 = reward_observed(1,rtt,delayReq3,packet_imp,retrxsfori,fecscssfori)
        reward_fec[i] = reward3
        t2 = t2 + delay3



            
reward_cum = np.cumsum(reward)
reward_cum_arq = np.cumsum(reward_arq)
reward_cum_fec = np.cumsum(reward_fec)
for i in range(len(reward_cum)):
    reward_cum[i] = reward_cum[i]/(i+1)
    reward_cum_arq[i] = reward_cum_arq[i]/(i+1)
    reward_cum_fec[i] = reward_cum_fec[i]/(i+1)
plt.ylim([0.99,1])
plt.plot(reward_cum,'r',reward_cum_arq,'b', reward_cum_fec,'g')
