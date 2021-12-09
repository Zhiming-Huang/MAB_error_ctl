# MAB_error_ctl


## Usage
1. python3 receiver.py
2. python3 sender.py IP_address Port_number Required_loss Packet_no

Ip_address: the ip address of where receiver runs
Port_number: the port number is 8888 hardcoded in receiver.py
required_loss: required loss rate
packet_no: how many packets to be sent



Assumption: For each video chunk, the sender will first transmit basic layer and then the enhancement layer
For simplicity, we assume the basic layer requires 1 packet, each enhance layer requires 1 additional layer
There are 3 quality (480p 720p 1080p), i.e., 480p (1 basic layer packet), 720p (1 basic layer packet + 1 enhancement layer), 1080p(1 basic layer packet + 2 enhancement layer) 
Assume the network bandwith can allow 3 packets transmitted at the same time and packets are sent in a back-to-back way
Assume the application always requests
