import socket
import struct

#Room size
length = 5.5
width = 3.35
scale_img = 20

UDP = "localhost"
PORT = 10000
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP,PORT))

print("\n\nPress ctrl + C to exit")

pix_x = int(width*scale_img)
pix_y = int(length*scale_img)

def setup():
	size(pix_x,pix_y)
	colorMode(HSB)
	noStroke()

def draw():
	data, addr = sock.recvfrom(1024)
	x,y,yaw,rbid,size = struct.unpack('<ddddd',data)
	fill(0x11000000)
	rect(0,0,width,height)
	fill(int(85*rbid),255,255)
	rotate(yaw)
	rect(x,y,20,20)