import socket
import struct
import math
import numpy as np
import csv
import numpy.linalg as la
import sys
import time
import numpy.linalg as la
import scipy.spatial as ss

V_norm = 0.3
K_gain = 0.75

#r_id = input("List the id's of the robots present on your screen seperated by commas: ")
#r_id = raw_input('Enter robots: '.split(','))
#r_id = str(r_id)
r_id = [3,4]
robot_id = np.sort(np.asarray(r_id).astype(int))
UDP = "192.168.1.90"
UDP_SEND = ["192.168.1.5{}".format(rbid) for rbid in robot_id]
PORT = 11000
PORT_SEND = 3500
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP,PORT))

def Current_Pos():
    udprecv, addr = sock.recvfrom(1024)
    x,y,yaw,rbid,status,dataFrame = struct.unpack('<dddddd',udprecv)
    yaw = yaw*math.pi/180
    curr_pos = np.array([x,y,yaw,rbid,status,dataFrame])
    return curr_pos,rbid

def L1_Distance(waypoint, position):
    dist_vec = robotpath[ind][waypoint] - position[:2]
    Dist = la.norm(dist_vec)
    return Dist

def Angle(wpid, position):
    vec = robotpath[ind][wpid] - position[:2]
    angle = math.atan2(vec[1],vec[0])
    eta = position[2] - angle
    return eta

robotfile = [open('/home/arun/sketchbook/pathgen_processing/robot_traj_id:{}.csv'.format(rbid)) for rbid in robot_id]
robotpath = [np.asarray(list(csv.reader(rfile))).astype(float) for rfile in robotfile]
robot_tree = [ss.KDTree(np.column_stack((path[:,0],path[:,1]))) for path in robotpath]

def waypt(postn, L1_Dist, indx):
	pntarry = robot_tree[indx].query_ball_point(postn[:2],L1_Dist, p = 2)
	if not pntarry:
		nL1, waypnt = robot_tree[indx].query(postn[:2], k = 1, p = 2)
	else:
		pntarry = np.sort(np.asarray(pntarry))
		pntarry -= wp_num[indx]
		waytemp = pntarry[np.where(pntarry>=0)]
		if waytemp.shape[0] == 0:
			waypnt = 0
		else:
			newtemp = np.arange(waytemp[0],waytemp.shape[0]+waytemp[0])
			waypnt = np.amax(np.where(waytemp-newtemp==0))
		waypnt += wp_num[indx]
		nL1 = L1_Distance(waypnt,postn)	
	return waypnt, nL1


wp_num = np.zeros(robot_id.shape[0]).astype(int)
stop = np.zeros(robot_id.shape[0]).astype(int)
pos,rbid = Current_Pos()
ind = int(np.where(robot_id==rbid)[0])
untrackcnt = np.zeros(robot_id.shape[0]).astype(int)


try:
	while np.array_equal(stop-1,np.zeros(robot_id.shape[0])) != True:
		while stop[ind] == 0:
		    pos,rbid = Current_Pos()
		    ind = int(np.where(robot_id==rbid)[0])
		    L1 = K_gain*V_norm
		    wp_num[ind],newL1 = waypt(pos,L1,ind)
		    eta = Angle(wp_num[ind],pos)
		    acc_cmd = (math.sin(eta)*V_norm**2)/newL1
		    w_turn = acc_cmd/V_norm**2
		    print(w_turn,robot_id[ind],wp_num[ind])
		    if pos[4] > 0:
		        untrackcnt[ind] = 0
		    else:
		        untrackcnt[ind] += 1
		    if untrackcnt[ind]>50:
		    	V_norm = 0
		    	w_turn = 0
		    if newL1<1e-2:
		    	stop[ind] = 1
		    socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		    msg = struct.pack('<dd',V_norm,w_turn)
		    socksend.sendto(msg, (UDP_SEND[ind],PORT_SEND))
		print("\nClosing Ports\n",robot_id[ind])
		for i in range(10000):
			socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			msg = struct.pack('<dd',0,0)
			socksend.sendto(msg, (UDP_SEND[ind],PORT_SEND))
		print("Sent terminate command")	
		socksend.close()
except:
	print("\nClosing Ports\n")
	for i in range(10000):
		socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		msg = struct.pack('<dd',0,0)
		for i in range(robot_id.shape[0]):
			socksend.sendto(msg, (UDP_SEND[i],PORT_SEND))
	print("Sent terminate command")	
	socksend.close()