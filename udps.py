#!/usr/bin/env python

#Edit however required

import socket
import struct
import math
import time
import threading

UDP = "localhost"
PORT = 11000
PORT2 = 10000
xs = [0.0, -1.0,  1.0]
ys = [0.0, -1.0, -1.0]
yaw = [1.0, 0.0, -0.8]
status = 1.0
nbots = 3
count = 1

try:
    while True:
        time.sleep(0.009)
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        msg = struct.pack('<dddddd',xs[1],ys[1],math.sin(count*math.pi/180)*30,4,status,count)
        sock.sendto(msg, (UDP,PORT))
        sock.sendto(msg, (UDP,PORT2))
        count += 1

except:
	print("\nClosing Ports\n")
	sock.close()