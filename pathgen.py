import socket
import struct
import math

#Room size
room_length = 5.5
room_width = 3.35
scale_img = 120.0

#Robot dimensions
rob_scale = 1.2
rob_rect_x = 0.15 * scale_img * rob_scale
rob_rect_y = 0.2 * scale_img * rob_scale
rob_trapz_wid = 0.05 * scale_img * rob_scale
rob_trapz_side = 0.07 * scale_img * rob_scale
rob_wheel_x = 0.04 * scale_img * rob_scale
rob_wheel_y = 0.02 * scale_img * rob_scale
rob_wheel_pos = 2.0/3.0 #Value between 1 and 0

#Grid Size
grid_space = 0.5 
dot_space = 0.05 

#Font Size
fntsz = 20

UDP = "localhost"
PORT = 20000
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP,PORT))

print("\n\nPress ctrl + C to exit\n\n")

pix_x = int(room_width * scale_img)
pix_y = int(room_length * scale_img)

color_bot = {1: color(71,82,224),
			 2: color(0,255,30),
			 3: color(255,50,50),
			 4: color(240,255,0)}

data = []

def setup():
	size(pix_x,pix_y)
	colorMode(RGB)
	frameRate(600)
	noStroke()
	ubuntu_med = loadFont("Ubuntu-Medium-60.vlw")
	textFont(ubuntu_med,fntsz)

def draw():
	fill(255,255,255)
	rectMode(CORNER)
	rect(0.0,0.0,width,height)
	draw_major_axes()
	draw_minor_axes()
	udprecv, addr = sock.recvfrom(1024)
	worldx,worldy,yaw,rbid,status,dataRate = struct.unpack('<dddddd',udprecv)
	x,y = convert_coord(worldx,worldy)
	yaw *= -1  #Reversing direction of rotation
	rbid = int(rbid)
	if status == 1:
		col = [row[3] for row in data]
		if (rbid in col) != 1:
			data.append([x,y,yaw,rbid])
		else:
			data[col.index(rbid)] = [x,y,yaw,rbid]
	for row in data:
		pushMatrix()
		translate(row[0],row[1])
		rotate(row[2]*frameCount/200)
		draw_robot(row[3])
		popMatrix()

def draw_major_axes():
	stroke(0)
	line(pix_x/2,0,pix_x/2,pix_y)
	line(0,pix_y/2,pix_x,pix_y/2)

def draw_minor_axes():
	noSmooth()
	for i in range(int(math.ceil(room_width/(2*grid_space)))):
		for j in range(int(room_length/(2*dot_space))):
			draw_point(convert_coord(i*grid_space,j*dot_space))
			draw_point(convert_coord(-i*grid_space,j*dot_space))
			draw_point(convert_coord(i*grid_space,-j*dot_space))
			draw_point(convert_coord(-i*grid_space,-j*dot_space))
	for j in range(int(math.ceil(room_length/(2*grid_space)))):
		for i in range(int(room_width/(2*dot_space))):
			draw_point(convert_coord(i*dot_space,j*grid_space))
			draw_point(convert_coord(-i*dot_space,j*grid_space))
			draw_point(convert_coord(i*dot_space,-j*grid_space))
			draw_point(convert_coord(-i*dot_space,-j*grid_space))

def draw_point(pt):
	point(pt[0],pt[1])

def convert_coord(mocapx,mocapy):
	px = pix_x/2 + (mocapx*scale_img)
	py = pix_y/2 - (mocapy*scale_img)
	return (px,py)

def draw_robot(r_id):
	stroke(150)
	rectMode(CENTER)
	fill(color_bot[r_id])
	rect(0.0,0.0,rob_rect_x,rob_rect_y)
	pushMatrix()
	rotate(HALF_PI)
	translate(-fntsz/3.0,fntsz/3.0)
	fill(255)
	text(r_id,0,0)
	popMatrix()
	stroke(50)
	fill(255)
	beginShape()
	vertex(rob_rect_x/2.0,rob_rect_y/2.0)
	vertex(rob_rect_x/2.0+rob_trapz_wid,rob_trapz_side/2.0)
	vertex(rob_rect_x/2.0+rob_trapz_wid,-rob_trapz_side/2.0)
	vertex(rob_rect_x/2.0,-rob_rect_y/2.0)
	endShape()
	noStroke()
	draw_wheel(rob_wheel_pos*rob_rect_x/2.0,rob_rect_y/2+rob_wheel_y/2)
	draw_wheel(rob_wheel_pos*rob_rect_x/2.0,-rob_rect_y/2-rob_wheel_y/2)
	draw_wheel(-rob_wheel_pos*rob_rect_x/2.0,rob_rect_y/2+rob_wheel_y/2)
	draw_wheel(-rob_wheel_pos*rob_rect_x/2.0,-rob_rect_y/2-rob_wheel_y/2)

def draw_wheel(wx,wy):
	fill(0)
	rectMode(CENTER)
	rect(wx,wy,rob_wheel_x,rob_wheel_y)
