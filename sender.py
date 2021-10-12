import socket
import mabctl
import sys
import random
import time
#import scipy.io as scio
#import numpy as np
#python3 sender.py receiver_ip receriver_port tolarated_loss packet_number

tolated_loss = float(sys.argv[3])

serverAddressPort   = (sys.argv[1], int(sys.argv[2]))

bufferSize          = 1024

packet_number = int(sys.argv[4])

packet_delay = [0]*packet_number

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

UDPClientSocket.settimeout(0.02)

# initiate the MAB module
MAB_err_ctl = mabctl.MAB_Control(tolated_loss)

for i in range(packet_number):

	initial_time = time.time()

	UDPClientSocket.sendto(str(i).encode(), serverAddressPort)

	while True:


		try:

			UDPClientSocket.recvfrom(bufferSize)
			

		except socket.timeout:

				p_retransmit  = MAB_err_ctl.err_gran(True)

				if random.uniform(0,1) < p:
					UDPClientSocket.sendto(str(i).encode(), serverAddressPort)

				else:
					break

		else:
			ending_time = time.time()
			MAB_err_ctl.err_gran(False)
			elapsed_time = ending_time - initial_time
			packet_delay[i] = elapsed_time
			break
	

	

UDPClientSocket.close()

#scio.savemat(newmatfile,{"mabdelay":packet_delay})
