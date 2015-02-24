#!/usr/bin/env python

import socket
import struct

UDP = "localhost"
PORT = 10000
x = 10
y = 20
yaw = 1
rbid = 1
status = 1
nbot = 3


while True:
	for i in range(1,4):
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		msg = struct.pack('ddddd',x+i*100,y+i*100,yaw+i,rbid+i,status)
		sock.sendto(msg, (UDP,PORT))