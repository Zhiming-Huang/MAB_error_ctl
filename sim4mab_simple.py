#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 13:38:00 2021

@author: zhiming
"""
import matplotlib.pyplot as plt
import contex_mab
import numpy as np


def frametype(frm_num):
    # 1 for I, 2 for B, and P for 3
    ret = frm_num % 12
    if ret == 1:
        return 1
    elif 1<ret<4 and 4<ret<7 and 7<ret<10 and 10 < ret <=12:
        return 2
    else:
        return 3


#RTT =  150 assume one trip time is 75ms, and round trip time is 150ms
num_seg = 171000

drp_rate = np.zeros(num_seg)
drp_rate[0] =  0.01

ind = 10000
for i in range(2,num_seg):
    drp_rate[i] = 0.25*drp_rate[i-1]+np.random.uniform(0,0.05)*0.75

RTT =  np.random.uniform(120,180,num_seg)
retrxs = np.random.geometric(1-drp_rate)
fecscss = np.random.binomial(2,1-drp_rate)
# A basic-layer segment follows by a enhancement-layer segment
packet_imp = 1
delay_req_perseg = 180
# Assume every 200ms, a segment (i.e., basic and enhancement) with 200ms content is generated
# and the delay requirement for this segment is 150 ms for each segment
# the maximum snd_wnd is 2, i.e., at most two segments can be sent at a time
snd_wnd = 2

mabctl = contex_mab.MAB_Control()

# Initially, we have two segments already generated
seg_buffer = 2

t = 0

segment_spawn = np.zeros(num_seg) + 100
segment_spawn[0] = 0
seg_spawn_time = np.cumsum(segment_spawn)
#Context: (delay_req, seg_importance, seg_sndbuffer, seg_bitrate, snd_wnd)


def reward_observed(action,rtt,drp_rate,delayReq,packet_imp,retrxsfori,fecscssfori):
    reward = 0
    delay = 0
    ifdrop = False
    if action == 0: #ARQ
        delay = rtt*retrxsfori - rtt/2
        if delay  > delayReq:
            reward = 0
            ifdrop = True
            #delay = delayReq
        else:
            reward = 1
    elif action == 1: #FEC
        delay = rtt/2
        if fecscssfori == 0:
            reward = 0
            ifdrop = True
        else:
            reward = 1
    else:
        ifdrop = True
        reward = 0 if packet_imp == 1 else 0.1
        delay = 0 
    return reward, delay, ifdrop

# actions = np.zeros(num_seg)
# delay_packet = np.zeros(num_seg)
# reward = np.zeros(num_seg)
# reward_arq = np.zeros(num_seg)
# reward_fec = np.zeros(num_seg)
# packet_receipt = np.zeros(num_seg)

actions = np.zeros(num_seg)
delay_packet = np.zeros(num_seg)
delay_packet1 = np.zeros(num_seg)
delay_packet2 = np.zeros(num_seg)
reward = np.zeros(num_seg)
reward_arq = np.zeros(num_seg)
reward_fec = np.zeros(num_seg)
packet_receipt = np.zeros(num_seg)
packet1_receipt = np.zeros(num_seg)
packet2_receipt = np.zeros(num_seg)



for i in range(num_seg):
    packet_imp = frametype(i+1)
    rtt =  RTT[i]
    retrxsfori = retrxs[i]
    fecscssfori = fecscss[i]
    mabctl.update_rtt(rtt)
    #observe context
    seg_buffer = np.where(seg_spawn_time<t)[0].size - i
    if seg_spawn_time[i] > t:
        t = seg_spawn_time[i]
    delayReq = seg_spawn_time[i] + delay_req_perseg - t
    if delayReq <= 0:
        print("here")
        continue
    mabctl.input_context(delayReq, packet_imp, seg_buffer, snd_wnd)
    action1 = mabctl.exp3_action()
    actions[i] = action1
    reward1, delay1, ifdrop1 = reward_observed(action1,rtt,drp_rate,delayReq,packet_imp,retrxsfori,fecscssfori)
    delay_packet[i] = delay1
    mabctl.exp3_udate(reward1)
    reward[i] = reward1
    packet_receipt[i] = 1 if not ifdrop1 else 0
    t = t + rtt/2

    if action1 == 0:
        reward_arq[i] = reward1
        delay_packet1[i] = delay1
        packet1_receipt[i] = 1 if not ifdrop1 else 0

    else:
        delay = rtt*retrxsfori - rtt/2
        delay_packet1[i] = delay
        if delay > delayReq:
            reward_arq[i] = 0
            
        else:
            reward_arq[i] = 1
            packet1_receipt[i] = 1
            
    if action1 == 1:
        reward_fec[i] = reward1
        delay_packet2[i] = rtt/2
        packet2_receipt[i] = 1 if not ifdrop1 else 0

    else:
        delay_packet2[i] = rtt/2
        if fecscssfori == 0:
            
            reward_fec[i] = 0
        else:
            reward_fec[i] = 1
            packet2_receipt[i] = 1
        
                  
            
reward_cum = np.cumsum(reward)
reward_cum_arq = np.cumsum(reward_arq)
reward_cum_fec = np.cumsum(reward_fec)

delay_cum = np.cumsum(delay_packet)
delay1_cum = np.cumsum(delay_packet1)
delay2_cum = np.cumsum(delay_packet2)

for i in range(len(reward_cum)):
    reward_cum[i] = reward_cum[i]/(i+1)
    reward_cum_arq[i] = reward_cum_arq[i]/(i+1)
    reward_cum_fec[i] = reward_cum_fec[i]/(i+1)
    delay_cum[i] = delay_cum[i]/(i+1)
    delay1_cum[i] = delay1_cum[i]/(i+1)
    delay2_cum[i] = delay2_cum[i]/(i+1)

plt.plot(reward_cum,'r',reward_cum_arq,'b', reward_cum_fec,'g')
plt.legend(["MAB","ARQ","FEC"])
plt.xlabel('Frames')
plt.ylabel('Frame-averaged Reward')
plt.savefig('frame_averaged_reward.eps', format='eps')

# plt.plot(delay_cum,'r', delay1_cum, 'b', delay2_cum, 'g')
# plt.legend(["MAB","ARQ","FEC"])
# plt.xlabel('Frames')
# plt.ylabel('Frame-averaged Delay')
# plt.savefig('frame_averaged_delay.eps', format='eps')
# plt.ylim([60,90])

# data = [np.where(reward == 0)[0].size, np.where(reward_arq == 0)[0].size, np.where(reward_fec == 0)[0].size]
# labels = ['Flec', 'ARQ', 'FEC']
# plt.bar(range(len(data)), data, tick_label=labels)
# plt.ylabel('Lost or Expired Frames')
# plt.xlabel('Algorithms')
# plt.savefig('loss_expired.eps', format='eps')
# plt.plot(drp_rate[0:100])
# plt.xlabel('Frames')
# plt.ylabel('Loss Rate')
# plt.savefig('frame_loss_rate.eps', format='eps')