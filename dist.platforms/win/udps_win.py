#!/usr/bin/env python

#Edit however required

import socket
import struct
import math

UDP = "localhost"
PORT = 10000
xs = [1.0, -1.0,  1.0]
ys = [1.0, -1.0, -1.0]
yaw = [1.0, -0.5, -3.141]
status = 1.0
nbots = 3
count = 1

try:
	while True:
		for i in range(0,nbots):
			sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			msg = struct.pack('<dddddd',xs[i],ys[i],yaw[i],i+2,status,count)
			sock.sendto(msg, (UDP,PORT))
			count += 1

except:
	print("\nClosing Ports\n")
	sock.close()