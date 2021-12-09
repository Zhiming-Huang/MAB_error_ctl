import math
import random


class MAB_Control():
    def __init__(self):
        #self.packetno = 1
        #self.contype = 1 #context type
        self.rtt = 120
        #action 0 for retransmission, 1 for FEC, and 2 for drop
        self.c1_count = [1/2,1/2,0,0]
        self.c2_count = [1/2,1/2,0,0]
        self.c3_count = [1/2,1/2,0,0]
        self.c4_count = [1/2,1/2,0,0]
        self.c5_count = [1/3,1/3,1/3,0,0,0]
        self.c6_count = [1/3,1/3,1/3,0,0,0]
        self.c7_count = [1/3,1/3,1/3,0,0,0]
        self.c8_count = [1/3,1/3,1/3,0,0,0]
        #c9 for where snd_wnd =1, so no fec, 0 for retransmission, 1 for drop
        self.c9_count = [1/2,1/2,0,0]
        self.action = 0
        self.count = []
        self.type = 1
        self.packetno = {1:1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1, 9:1}


    def update_rtt(self,rtt):
        self.rtt = rtt
    
    def update_mxwnd(self,max_wnd):
        self.max_wnd = max_wnd

    def input_context(self,delayReq, packet_imp, seg_buffer,snd_wnd):
        self.delayReq = delayReq
        self.packet_imp = packet_imp
        self.seg_buffer = seg_buffer
        self.snd_wnd = snd_wnd

    def _detcontype(self):
#type 1: delay<1.5 rtt, seg_buffer = 0, packet_importance = 0
#type 2: delay<1.5 rtt, seg_buffer = 0, packet_importance = 1
#type 3: delay<1.5 rtt, seg_buffer > 0, packet_importance = 0
#type 4: delay<1.5 rtt, seg_buffer > 0, packet_importance = 1
#type 5: delay > 1.5 rtt, seg_buffer = 0, packet_importance = 0
#type 6: delay > 1.5 rtt, seg_buffer = 0, packet_importance = 1
#type 7: delay > 1.5 rtt, seg_buffer > 0, packet_importance = 0
#type 8: delay > 1.5 rtt, seg_buffer > 0, packet_importance = 1
        if self.delayReq <= 1.5*self.rtt:
            if self.packet_imp == -1 and self.seg_buffer == 0:
                self.count = self.c1_count
                self.type = 1
            if self.packet_imp == 1 and self.seg_buffer == 0:
                self.count = self.c2_count
                self.type = 2
            if self.packet_imp == -1 and self.seg_buffer >0:
                self.count = self.c5_count
                self.type = 5
            if self.packet_imp == 1 and self.seg_buffer >0:
                self.count = self.c6_count
                self.type = 6
        if self.delayReq > 1.5*self.rtt:
            if self.packet_imp == -1 and self.seg_buffer <= 0:
                self.count = self.c3_count
                self.type = 3
            if self.packet_imp == 1 and self.seg_buffer <= 0:
                self.count = self.c4_count
                self.type = 4
            if self.packet_imp == -1 and self.seg_buffer >0:
                self.count = self.c7_count
                self.type = 7
            if self.snd_wnd <= 1:
                self.count = self.c9_count
                self.type = 9
            if self.packet_imp == 1 and self.seg_buffer >0:
                self.count = self.c8_count
                self.type = 8

    def exp3_action(self):
        self._detcontype()
        num_action = len(self.count)/2
        rndnum = random.uniform(0,1)
        cumsum = 0
        for i in range(num_action):
            cumsum = cumsum + self.count[i]
            if rndnum <= cumsum:
                self.action = i
                return i #0 for retransmission, 1 for FEC, and 2 for drop 


    def exp3_udate(self,reward):
        num_action = len(self.count)/2
        loss_sum = 0
        eta = math.log(num_action)/(num_action*self.packetno[self.type])
        for i in range(num_action):
            if i == self.action:
                self.count[num_action + i] += (1-reward)/(self.count[self.action]+eta/2)
            self.count[i] = math.exp(-eta*self.count[num_action+i])
            loss_sum +=  self.count[i]
        for i in range(num_action):
            self.count[i] = self.count[i]/loss_sum
        self.packetno[self.type] += 1

        


