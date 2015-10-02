import socket
import struct
import math

UDP = "192.168.1.53"
PORT = 3500
xs = [0.0, -1.0,  1.0]
ys = [0.0, -1.0, -1.0]
yaw = [1.0, 0.0, -0.8]
status = 1.0
nbots = 3
count = 1
vel = 0.1
turn = 0.5

try:
	while True:
		for i in range(0,nbots):
			sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			msg = struct.pack('<dd',vel,turn)
			sock.sendto(msg, (UDP,PORT))
			count += 1
			print(count)

except:
	print("\nClosing Ports\n")
	for i in range(10000):
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		msg = struct.pack('<dd',0,0)
		sock.sendto(msg, (UDP,PORT))
	print("Sent terminate command")
	sock.close()