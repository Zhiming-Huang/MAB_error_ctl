import math


class MAB_Control():
    def __init__(self,lossrate):
        self.packetno = 1
        self.L = lossrate  #required loss rate
        self.losspacketno = 0   #the number of packets that have lost
        self.q_hat = 0  #the sample mean of loss rate


    def ucb(self):
        #calculate upper confidence bound estimate for the action loss rate
        return self.q_hat + (2*math.log(1+self.packetno*math.log(self.packetno)**2)/(self.packetno-1))**0.5

    def err_gran(self,loss=False):
        if loss:
            #if there is a loss, then add 1 to self.losspacketno
            self.losspacketno = self.losspacketno + 1
        #update the sample mean of loss rate
        self.q_hat = self.losspacketno / self.packetno
        #for the first packet, retransmit with probability 1
        if self.packetno == 1:
            self.packetno = self.packetno + 1
            return 1
        #else, use the ucb estimate to calculate retransmission rate
        q_ucb = self.ucb()
        self.packetno = self.packetno + 1
        print(str(self.L)+":  "+str(q_ucb) + ": "+ str(self.q_hat))
        # denote by p the retransmission probability. p is derived by argmin{|q_ucb * (1-p) - L|}, where L is the required loss rate.
        return 1-self.L/q_ucb

