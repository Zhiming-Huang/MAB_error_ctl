#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 15:25:37 2022

@author: zhiming
"""

import queue
import numpy as np
import logging
#from SplayTree import *

# set logger
logger = logging.getLogger("arq-simulator")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


# read the tracefile
tracefile = open("starwars.frames.old", "r+")
traces = tracefile.read().splitlines()
traces = np.array(list(map(int, traces)))
tracefile.close()


def frametype(frm_num):
    # 1 for I, 2 for B, and P for 3
    ret = frm_num % 12
    if ret == 1:
        return 1
    elif 1 < ret < 4 and 4 < ret < 7 and 7 < ret < 10 and 10 < ret <= 12:
        return 2
    else:
        return 3


class event:
    def __init__(self, evt_time, evt_type, pkt_no=None, pkt_imp=None, pkt_delay_req=None):
        # evt_type 0 for pkt arrival, 1 for timeout, 2 for delivered
        self.time = evt_time
        self.type = evt_type
        self.pkt_no = pkt_no
        self.pkt_imp = pkt_imp
        self.delay_req = pkt_delay_req

    def __lt__(self, other):
        return self.evt_time < other.evt_time

    def set_type(self, evt_type):
        self.type = evt_type

    def set_time(self, evt_time):
        self.time = evt_time


accumu_packets = np.cumsum([int(item/1024) for item in traces])

# Determine the generation time for each frame
num_frms = len(traces)
frame_spawn = np.zeros(num_frms) + 42
frame_spawn[0] = 0
frame_spawn_time = np.cumsum(frame_spawn)

arrival_events = []
for i in range(num_frms):
    # when type = 0, pktno is the frame no.
    arrival_events.append(event(frame_spawn_time[i], 0, i))

snd_wnd = 5
S_base = 0
S_next = 0
drp_rate = 0.01
max_pkt_no = 0
delay_req = 180

t = 0
ind = 0
event_list = queue.PriorityQueue()
event_list.put_nowait(arrival_events[ind])

while True:
    # Get imminent event
    try:
        evnt = event_list.get_nowait()
    except queue.Empty:
        logger.debug("No events any more")
        break
    else:
        if evnt.type == 0:
            # if packts arrive
            t = evnt.time
            max_pkt_no = accumu_packets[evnt.pkt_no]
            # Schedule next arrival event
            ind += 1
            if ind < num_frms:
                event_list.put_nowait(arrival_events[ind])

            # Send packets
            while S_next < S_base + snd_wnd and S_next < max_pkt_no:
                rtt = np.random.uniform(120, 180)

                # determine pkt importance:
                frm_id = np.where(accumu_packets >= S_next)[0][0] + 1
                pkt_imp = frametype(frm_id)

                # determine whether the packet is lost or not
                lost = np.random.binomial(1, drp_rate)
                drp_rate = 0.25 * drp_rate + np.random.uniform(0, 0.05) * 0.75

                if lost:
                    # if packet is lost, an timeout event is generated
                    event_list.put_nowait(
                        event(t + rtt, 1, S_next, pkt_imp, t + delay_req))

                else:
                    # determine the arrival time
                    event_list.put_nowait(
                        event(t + rtt/2, 1, S_next, pkt_imp, t + delay_req))
                S_next += 1
        elif evnt.type == 1:
            # if packet lost and timeout, retransmit packet
            t = evnt.time
            lost = np.random.binomial(1, drp_rate)
            drp_rate = 0.25 * drp_rate + np.random.uniform(0, 0.05) * 0.75
            if lost:
                # if packet is lost, an timeout event is generated
                evnt.set_time = t + rtt
                evnt.set_type = 1
                event_list.put_nowait(evnt)

            else:
                # determine the arrival time
                evnt.set_time = t + rtt/2
                evnt.set_type = 2
                event_list.put_nowait(evnt)

        elif evnt.type == 2:
            # if packet is successfully received
            t = evnt.time
