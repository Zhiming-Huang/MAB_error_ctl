import math
import random


class MAB_Control():
    def __init__(self):
        self.packetno = 1
        #self.contype = 1 #context type
        self.rtt = 120
        self.c1_count = [1/2,1/2,0,0]
        self.c2_count = [1/2,1/2,0,0]
        self.c3_count = [1/2,1/2,0,0]
        self.c4_count = [1/2,1/2,0,0]
        self.c5_count = [1/3,1/3,1/3,0,0,0]
        self.c6_count = [1/3,1/3,1/3,0,0,0]
        self.c7_count = [1/3,1/3,1/3,0,0,0]
        self.c8_count = [1/3,1/3,1/3,0,0,0]
        self.action = 0
        self.count = []

    def update_rtt(self,rtt):
        self.rtt = rtt

    def input_context(self,delayReq, packet_imp, seg_buffer):
        self.delayReq = delayReq
        self.packet_imp = packet_imp
        self.seg_buffer = seg_buffer

    def _detcontype(self):
        if self.delayReq <= 1.5*self.rtt:
            if self.packet_imp == 0 and self.seg_buffer == 0:
                self.count = self.c1_count
            if self.packet_imp == 1 and self.seg_buffer == 0:
                self.count = self.c2_count
            if self.packet_imp == 0 and self.seg_buffer >0:
                self.count = self.c5_count
            if self.packet_imp == 1 and self.seg_buffer >0:
                self.count = self.c6_count
        if self.delayReq > 1.5*self.rtt:
            if self.packet_imp == 0 and self.seg_buffer == 0:
                self.count = self.c3_count
            if self.packet_imp == 1 and self.seg_buffer == 0:
                self.count = self.c4_count
            if self.packet_imp == 0 and self.seg_buffer >0:
                self.count = self.c7_count
            if self.packet_imp == 1 and self.seg_buffer >0:
                self.count = self.c8_count

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
        eta = math.log(num_action)/(num_action*self.packetno)
        for i in range(num_action):
            if i == self.action:
                self.count[num_action + i] += (1-reward)/(self.count[self.action]+eta/2)
            self.count[i] = math.exp(-eta*self.count[num_action+i])
            loss_sum +=  self.count[i]
        for i in range(num_action):
            self.count[i] = self.count[i]/loss_sum
        self.packetno += 1
        
        


