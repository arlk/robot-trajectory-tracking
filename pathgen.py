import socket
import struct

#Room size
room_length = 5.5
room_width = 3.35
scale_img = 120.0

#Robot dimensions
rob_x = int(0.15 * scale_img)
rob_y = int(0.2 * scale_img)

UDP = "localhost"
PORT = 20000
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP,PORT))

print("\n\nPress ctrl + C to exit\n\n")

pix_x = int(room_width*scale_img)
pix_y = int(room_length*scale_img)

color_bot = {1: color(58,116,197),
			 2: color(0,255,30),
			 3: color(220,20,60),
			 4: color(240,255,0)}

data = []

def setup():
	size(pix_x,pix_y)
	colorMode(RGB)
	noStroke()
	frameRate(1)

def draw():
	fill(255,255,255)
	rectMode(CORNER)
	rect(0.0,0.0,width,height)
	udprecv, addr = sock.recvfrom(1024)
	x,y,yaw,rbid,status = struct.unpack('<ddddd',udprecv)
	rbid = int(rbid)
	if status == 1:
		col = [row[3] for row in data]
		if (rbid in col) != 1:
			data.append([x,y,yaw,rbid])
		else:
			data[col.index(rbid)] = [x,y,yaw,rbid]
	for row in data:
		fill(color_bot[row[3]])
		translate(row[0],row[1])
		rotate(row[2])
		rectMode(CENTER)
		rect(0,0,rob_x,rob_y)
		translate(-row[0],-row[1])
		rotate(-row[2])


