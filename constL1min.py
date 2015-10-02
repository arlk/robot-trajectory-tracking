import socket
import struct
import math
import numpy as np
import csv
import numpy.linalg as la

V_norm = 0.4
L1_Damping = 0.75
L1_Period = 20

UDP = "192.168.1.50"
UDP_SEND = "192.168.1.53"
PORT = 11000
PORT_SEND = 3500
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP,PORT))

def Current_Pos():
    rbid = 0
    while rbid != 3:
    	udprecv, addr = sock.recvfrom(1024)
    	x,y,yaw,rbid,status,dataFrame = struct.unpack('<dddddd',udprecv)
    	yaw = yaw*math.pi/180
    	curr_pos = np.array([x,y,yaw,rbid,status])
    	#print(curr_pos)
    return curr_pos

def L1_Distance(waypoint, position):
    dist_vec = waypoint - position[:2]
    Dist = la.norm(dist_vec)
    return Dist

def Angle(wpid, position):
    vec = path[wpid] - position[:2]
    #print(vec)
    #print(path[wpid],position[:2])
    angle = math.atan2(vec[1],vec[0])
    eta = position[2] - angle
    return eta

file = open('/home/arun/sketchbook/pathgen_processing/robot_traj_id:3.csv')
path = np.asarray(list(csv.reader(file))).astype(float)

# w_name = "robot_w"
# w_file = open(w_name,"w+")
# w_file.truncate()

wp_num = 0
pos = Current_Pos()
count = 0
stop = 0
try:
	while stop == 0 and pos[4] > 0:
	    count += 1
	    #print(count)
	    pos = Current_Pos()
	    L1 = 0.75*V_norm
	    #print(pos)
	    #print("L1",L1)
	    for i,wp in enumerate(path[wp_num:,:]):
	        if L1_Distance(wp,pos) > L1:
	            wp_num  += i
	            minimum = 1000
	            minj = 0
	            if L1_Distance(wp,pos) > 2*L1:
		            for j,wpj in enumerate(path[wp_num:,:]):
		            	if L1_Distance(wpj,pos) < minimum:
		            		minimum = L1_Distance(wpj,pos)
		            		minj = j
	            wp_num += minj
	            stop = 0
	            break
	        stop = 1
	    eta = Angle(wp_num,pos)
	    acc_cmd = (math.sin(eta)*V_norm**2)/L1
	    w_turn = acc_cmd/V_norm**2
	    #print(eta,w_turn)
	    print(w_turn)
	    # w_text = "{}\n".format(w_turn)
		# w_file.write(w_text)
	    socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	    msg = struct.pack('<dd',V_norm,w_turn)
	    socksend.sendto(msg, (UDP_SEND,PORT_SEND))
	print("\nClosing Ports\n")
	for i in range(10000):
		socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		msg = struct.pack('<dd',0,0)
		socksend.sendto(msg, (UDP_SEND,PORT_SEND))
	print("Sent terminate command")	
	socksend.close()
except:
	print("\nClosing Ports\n")
	for i in range(10000):
		socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		msg = struct.pack('<dd',0,0)
		socksend.sendto(msg, (UDP_SEND,PORT_SEND))
	print("Sent terminate command")	
	socksend.close()	    
