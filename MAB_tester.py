import mabctl
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as scio

packetloss = 0.1
mab_instance = mabctl.MAB_Control(packetloss)
exp_independet = 1000
delay = 0.4
total_packet = 10000
actual_packet_loss = np.random.binomial(1, packetloss, size=(exp_independet,total_packet))
packet_delay1 = np.zeros((exp_independet,total_packet))
packet_delay2 = np.zeros((exp_independet,total_packet))

for exp in range(exp_independet):
    for packet in range(total_packet):
        if actual_packet_loss[exp,packet]:# 1 for loss and 0 for no loss
            packet_delay2[exp,packet] = delay * (1+np.random.geometric(packetloss,1))
            p = mab_instance.err_gran(True) # p for retransmit
            if np.random.binomial(1, p):
                packet_delay1[exp,packet] = delay * (1+np.random.geometric(packetloss,1))
        else: #no loss
            mab_instance.err_gran()
            packet_delay1[exp,packet] = delay
            packet_delay2[exp,packet] = delay


packet_delay_mab = np.sum(packet_delay1,0)/exp_independet
packet_delay_arq = np.sum(packet_delay2,0)/exp_independet

newmatfile = 'packetdelay'
scio.savemat(newmatfile,{"mabdelay":packet_delay_mab,"arqdelay":packet_delay_arq})


fig, ax = plt.subplots()
ax.plot(packet_delay_mab)




