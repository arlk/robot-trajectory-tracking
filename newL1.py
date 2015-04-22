import socket
import struct
import math
import numpy as np
import csv
import sys
import time
import numpy.linalg as la
from matplotlib import pyplot as plt
import scipy.spatial as ss

V_norm = 0.2
K_gain = 0.75

UDP = "192.168.1.90"
UDP_SEND = "192.168.1.53"
PORT = 11000
PORT_SEND = 3500
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP,PORT))

# plt.ion()
# wfig = plt.figure()
# wax = plt.axes()
# wdata = [0]*1000
# line, = plt.plot(wdata)
# plt.ylim([-2,2])
# plt.show()

def Current_Pos():
    rbid = 0
    while rbid != 3:
    	udprecv, addr = sock.recvfrom(1024)
    	x,y,yaw,rbid,status,dataFrame = struct.unpack('<dddddd',udprecv)
    	yaw = yaw*math.pi/180
    	curr_pos = np.array([x,y,yaw,rbid,status])
    return curr_pos


def L1_Distance(waypoint, position):
    dist_vec = path[waypoint] - position[:2]
    Dist = la.norm(dist_vec)
    return Dist

def Angle(wpid, position):
    vec = path[wpid] - position[:2]
    angle = math.atan2(vec[1],vec[0])
    eta = position[2] - angle
    return eta

file = open('/home/arun/sketchbook/pathgen_processing/robot_traj_id:3.csv')
path = np.asarray(list(csv.reader(file))).astype(float)
pathtree = ss.KDTree(np.column_stack((path[:,0],path[:,1])))

def waypt(postn, L1_Dist):
	pntarry = pathtree.query_ball_point(postn[:2],L1_Dist, p = 2)
	print(pntarry)
	if not pntarry:
		nL1, waypnt = pathtree.query(postn[:2], k = 1, p = 2)
	else:
		pntarry = np.sort(np.asarray(pntarry))
		pntarry -= wp_num
		# print("A",pntarry)
		# print("B",np.where(pntarry>=0))
		waytemp = pntarry[np.where(pntarry>=0)]
		# print("C",waytemp)
		if waytemp.shape[0] == 0:
			waypnt = 0
		else:
			newtemp = np.arange(waytemp[0],waytemp.shape[0]+waytemp[0])
			# print("D",newtemp)
			# print("E",waytemp-newtemp==0)
			waypnt = np.amax(np.where(waytemp-newtemp==0))
		waypnt += wp_num
		# print("F",waypnt,wp_num)
		nL1 = L1_Distance(waypnt,postn)	
	return waypnt, nL1
wp_num = 0
pos = Current_Pos()

wp_num = 0
stop = 0
untrackcnt = 0
try:
	while stop == 0:
	    V_norm = 0.3
	    pos = Current_Pos()
	    L1 = K_gain*V_norm
	    wp_num,newL1 = waypt(pos,L1)
	    eta = Angle(wp_num,pos)
	    print(wp_num)
	    acc_cmd = (math.sin(eta)*V_norm**2)/newL1
	    w_turn = acc_cmd/V_norm**2
	    if pos[4] > 0:
	        untrackcnt = 0
	    else:
	        untrackcnt += 1
	    if untrackcnt>50:
	    	V_norm = 0
	    	w_turn = 0
	    if newL1<1e-2:
	    	stop = 1
	    # wmin = float(min(wdata)) - 2
	    # wmax = float(max(wdata)) + 2
	    # plt.ylim([wmin,wmax])
	    # w_d = w_turn
	    # wdata.append(w_d)
	    # del wdata[0]
	    # line.set_xdata(np.arange(len(wdata)))
	    # line.set_ydata(wdata)
	    print(newL1)
	    socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	    msg = struct.pack('<dd',V_norm,w_turn)
	    socksend.sendto(msg, (UDP_SEND,PORT_SEND))
	    # plt.draw()
	# time.sleep(0.05)
	print("\nClosing Ports\n")
	for i in range(10000):
	    socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	    msg = struct.pack('<dd',0,0)
	    socksend.sendto(msg, (UDP_SEND,PORT_SEND))
	print("Sent terminate command")	
	print(path.shape[0])
	socksend.close()
except:
    print("\nClosing Ports\n")
    print(sys.exc_info()[0])
    for i in range(10000):
        socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        msg = struct.pack('<dd',0,0)
        socksend.sendto(msg, (UDP_SEND,PORT_SEND))
    print("Sent terminate command")	
    socksend.close()