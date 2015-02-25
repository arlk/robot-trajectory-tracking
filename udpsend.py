#!/usr/bin/env python

import socket
import struct

UDP = "localhost"
PORT = 20000
x = 10.0
y = 20.0
yaw = 0.0
rbid = 1.0
status = 1.0
nbot = 3

try:
	while True:
		for i in range(1,nbot+1):
			sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			xs = x + 100*i
			ys = y + 100*i
			rbid = i
			yaw = i*0.5
			msg = struct.pack('<ddddd',xs,ys,yaw,rbid,status)
			sock.sendto(msg, (UDP,PORT))
except:
	print("\nClosing Ports\n")
	sock.close()