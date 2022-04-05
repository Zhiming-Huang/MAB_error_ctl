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
# logger = logging.getLogger("arq-simulator")
# logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
# create console handler and set level to debug
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)

# create formatter
# formatter = logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
# ch.setFormatter(formatter)

# add ch to logger
# logger.addHandler(ch)


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
    def __init__(self, evt_time, evt_type, pkt_no=None, pkt_imp=None, pkt_delay_req=None, frm_id=None):
        # evt_type 0 for pkt arrival, 1 for timeout, 2 for delivered, 3 for ACK
        self.time = evt_time
        self.type = evt_type
        self.pkt_no = pkt_no
        self.pkt_imp = pkt_imp
        self.delay_req = pkt_delay_req
        self.frm_id = frm_id

    def __lt__(self, other):
        return self.time < other.time

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
    arrival_events.append(event(frame_spawn_time[i], 0, frm_id=i))

# sending window control
snd_wnd = 5
S_base = 0
S_next = 0

R_packets = np.zeros(num_frms)
ACKed_pkts = queue.PriorityQueue()

drp_rate = 0.01
max_pkt_no = 0
delay_req = 180

t = 0
ind = 0
event_list = queue.PriorityQueue()
event_list.put_nowait(arrival_events[ind])

while True:
    # logger.debug(str(event_list.queue))
    # Get imminent event
    try:
        evnt = event_list.get_nowait()
    except queue.Empty:
        logging.debug("No events any more")
        break
    else:
        if evnt.type == 0:
            # if packts arrive
            t = evnt.time
            max_pkt_no = accumu_packets[evnt.frm_id]
            # Schedule next arrival event
            ind += 1
            if ind < num_frms:
                event_list.put_nowait(arrival_events[ind])

            # Send packets
            while S_next < S_base + snd_wnd:
                if S_next >= max_pkt_no:
                    break
                one_trip = np.random.uniform(60, 90)

                # determine pkt importance:
                frm_id = np.where(accumu_packets >= S_next)[0][0] + 1
                pkt_imp = frametype(frm_id)

                # determine whether the packet is lost or not
                lost = np.random.binomial(1, drp_rate)
                drp_rate = 0.25 * drp_rate + np.random.uniform(0, 0.05) * 0.75

                if lost:
                    # if packet is lost, an timeout event is generated
                    event_list.put_nowait(
                        event(t + 2*one_trip, 1, S_next, pkt_imp, t + delay_req, frm_id))

                else:
                    # determine the arrival time
                    event_list.put_nowait(
                        event(t + one_trip, 1, S_next, pkt_imp, t + delay_req, frm_id))
                S_next += 1

        elif evnt.type == 1:
            # if packet lost and timeout, retransmit packet
            t = evnt.time
            lost = np.random.binomial(1, drp_rate)
            one_trip = np.random.uniform(60, 90)
            drp_rate = 0.25 * drp_rate + np.random.uniform(0, 0.05) * 0.75
            if lost:
                # if packet is lost, an timeout event is generated
                evnt.set_time(t + 2*one_trip)
                evnt.set_type(1)
                event_list.put_nowait(evnt)

            else:
                # determine the arrival time
                evnt.set_time(t + one_trip)
                evnt.set_type(2)
                event_list.put_nowait(evnt)

        elif evnt.type == 2:
            # if packet is successfully received
            t = evnt.time
            one_trip = np.random.uniform(60, 90)
            # send ACK
            evnt.set_type(3)
            evnt.set_time(t + one_trip)
            event_list.put_nowait(evnt)

            # receive packets that are not expired
            frm_id = evnt.frm_id
            if t >= evnt.delay_req:
                R_packets[frm_id] += 1

        else:
            # receive an ack
            t = evnt.time
            pkt_no = evnt.pkt_no
            ACKed_pkts.put_nowait(pkt_no)

            while True:
                try:
                    pkt_no = ACKed_pkts.get_nowait()
                except queue.Empty:
                    break

                # uodate S_base if pkt_no == S_base
                if pkt_no == S_base:
                    S_base += 1
                # else put back the pkt_no if pkt_no > S_base
                elif pkt_no > S_base:
                    ACKed_pkts.put_nowait(pkt_no)
                    break
