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

#Curve characteristics
sm = 20
ptdist = 5

#UDP comms
UDP = "localhost"
PORT = 20000
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP,PORT))

print("\n\nPress ctrl + C to exit\n\n")

draw_rbid = 0
store_pt_name =[]

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
		rotate(row[2]*frameCount/200.0)
		draw_robot(row[3])
		popMatrix()
	drawSpline()

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

def mousePressed():
	global store_pt_name
	global draw_rbid
	draw_rbid += 1
	store_pt_name.append("store_pt_robot:{}.txt".format(draw_rbid))
	store_pt = open(store_pt_name[draw_rbid-1],"w+")
	store_pt.truncate()
	store_pt.close()
	

def mouseDragged():
	global store_pt_name
	global draw_rbid
	store_pt = open(store_pt_name[draw_rbid-1],"a+")
	mousepts = "{},{}\n".format(float(mouseX),float(mouseY))
	store_pt.write(mousepts)
	store_pt.close()

def mouseReleased():
	spline_name = []
	for loop_id in range(draw_rbid):
		read_pt = open(store_pt_name[loop_id],"r")
		curve_pt = [(linef.rstrip('\n')).split(',') for linef in read_pt]
		read_pt.close()
		spline_name.append("robot_traj_id:{}.txt".format(draw_rbid))
		spline_file = open(spline_name[loop_id-1],"w+")
		spline_file.truncate()
		if len(curve_pt) >= 2*sm:
			spline_pt = []
			for t in range(sm+1):
				spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[0],curve_pt[0],curve_pt[ptdist],curve_pt[ptdist*2]))
			for i in range(len(curve_pt)-2*ptdist):
				if i%ptdist == 0 and i>=ptdist:
					for t in range(sm+1):
						spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[i-ptdist],curve_pt[i],curve_pt[i+ptdist],curve_pt[i+2*ptdist]))
			for t in range(sm+1):
				spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[i],curve_pt[i+ptdist],curve_pt[i+2*ptdist],curve_pt[i+2*ptdist]))
			for j in range(len(spline_pt)):
				splinepts = "{},{}\n".format(float(spline_pt[j][0]),float(spline_pt[j][1]))
				spline_file.write(splinepts)
			spline_file.close()


def drawSpline():
	for loop_id in range(draw_rbid):
		fill(255,0)
		stroke(color_bot[loop_id+1])
		read_pt = open(store_pt_name[loop_id],"r")
		curve_pt = [(linef.rstrip('\n')).split(',') for linef in read_pt]
		read_pt.close()
		if len(curve_pt) >= 2*sm:
			spline_pt = []
			for t in range(sm+1):
				spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[0],curve_pt[0],curve_pt[ptdist],curve_pt[ptdist*2]))
			for i in range(len(curve_pt)-2*ptdist):
				if i%ptdist == 0 and i>=ptdist:
					for t in range(sm+1):
						spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[i-ptdist],curve_pt[i],curve_pt[i+ptdist],curve_pt[i+2*ptdist]))
			for t in range(sm+1):
				spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[i],curve_pt[i+ptdist],curve_pt[i+2*ptdist],curve_pt[i+2*ptdist]))
			for j in range(len(spline_pt)-1):
				line(spline_pt[j][0],spline_pt[j][1],spline_pt[j+1][0],spline_pt[j+1][1])

def interpolateSpline(t,p1,p2,p3,p4):
	point = [0,0]
	f1 = -0.5*t + t**2 - 0.5*t**3
	f2 = 1 - 2.5*t**2 + 1.5*t**3
	f3 = 0.5*t + 2*t**2 - 1.5*t**3
	f4 = -0.5*t**2 + 0.5*t**3
	point[0] = f1*float(p1[0]) + f2*float(p2[0]) + f3*float(p3[0]) + f4*float(p4[0])
	point[1] = f1*float(p1[1]) + f2*float(p2[1]) + f3*float(p3[1]) + f4*float(p4[1])
	return point
