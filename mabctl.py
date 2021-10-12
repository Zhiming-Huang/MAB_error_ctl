import math


class MAB_Control():
    def __init__(self,lossrate):
        self.packetno = 1
        self.L = lossrate
        self.losspacketno = 0
        self.q_hat = 0


    def ucb(self):
        return self.q_hat + (2*(1+self.packetno*math.log(self.packetno)**2)/self.packetno)**0.5

    def err_gran(self,loss=False):
        if loss:
            self.losspacketno = self.losspacketno + 1
        self.q_hat = self.losspacketno / self.packetno
        q_ucb = self.ucb()
        self.packetno = self.packetno + 1
        return 1 - self.L/(2*q_ucb)

