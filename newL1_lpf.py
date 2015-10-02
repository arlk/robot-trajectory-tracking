import socket
import struct
import math
import numpy as np
import csv
import sys
import time
import numpy.linalg as la
from matplotlib import pyplot as plt
from matplotlib import animation
import scipy.spatial as ss
import time

V_norm = 0.5
K_gain = 0.75

UDP = "192.168.1.90"
UDP_SEND = "192.168.1.54"
PORT = 11000
PORT_SEND = 3500
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP,PORT))

plt.ion()
wfig = plt.figure()
wax = plt.axes()
wdata = [0]*1000
line, = plt.plot(wdata)
we_data = [0]*1000
eline, = plt.plot(we_data)
#wfig.eline.set_color('r')
plt.ylim([-2,2])
plt.show()

lpf_weight = np.array([1,2,2,2,1])
moving_posn = np.zeros((5,3))
lpf_var = np.exp(np.arange(0,20,1)[::-1])

moving_var = np.zeros(20)

def Low_Pass(posn):
    global moving_posn
    moving_posn[1:] = moving_posn[:-1]
    moving_posn[0] = posn
    new_elem = np.average(moving_posn, axis = 0, weights = lpf_weight)
    return new_elem

def Low_Pass_Var(var):
    global moving_var
    moving_var[1:] = moving_var[:-1]
    moving_var[0] = var
    avg_elem = np.average(moving_var, weights = lpf_var)
    return avg_elem


def Current_Pos():
    rbid = 0
    while rbid != 4:
    	udprecv, addr = sock.recvfrom(1024)
    	x,y,yaw,rbid,status,dataFrame = struct.unpack('<dddddd',udprecv)
    	yaw = yaw*math.pi/180
    	curr_pos = np.array([x,y,yaw,rbid,status,dataFrame])
    	curr_pos[:3] = Low_Pass(curr_pos[:3])
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

file = open('/home/arun/sketchbook/pathgen_processing/robot_traj_id:4.csv')
path = np.asarray(list(csv.reader(file))).astype(float)
pathtree = ss.KDTree(np.column_stack((path[:,0],path[:,1])))

def waypt(postn, L1_Dist):
	pntarry = pathtree.query_ball_point(postn[:2],L1_Dist, p = 2)
	if not pntarry:
		nL1, waypnt = pathtree.query(postn[:2], k = 1, p = 2)
	else:
		pntarry = np.sort(np.asarray(pntarry))
		pntarry -= wp_num
		waytemp = pntarry[np.where(pntarry>=0)]
		if waytemp.shape[0] == 0:
			waypnt = 0
		else:
			newtemp = np.arange(waytemp[0],waytemp.shape[0]+waytemp[0])
			waypnt = np.amax(np.where(waytemp-newtemp==0))
		waypnt += wp_num
		nL1 = L1_Distance(waypnt,postn)	
	return waypnt, nL1

#def animate:

wp_num = 0
stop = 0
untrackcnt = 0
start_t = -1
w_est = 0

try:
    while stop == 0:
        pos = Current_Pos()
        end_t = time.time()
        if start_t != -1:
            dt = start_t - end_t
            w_est = (pos[2] - pos_1[2])/dt
        print(w_est)
        start_t = time.time()
        pos_1 = np.copy(pos)
        L1 = K_gain*V_norm
        wp_num,newL1 = waypt(pos,L1)
        eta = Angle(wp_num,pos)
        print(wp_num)
        acc_cmd = (math.sin(eta)*V_norm**2)/newL1
        w_turn = acc_cmd/V_norm**2
        if pos[4] > 0.2:
            untrackcnt = 0
        else:
            untrackcnt += 1
        if untrackcnt>50:
            print("UNTRACKED!")
            V_norm = 0
            w_turn = 0
        if newL1<1e-2:
            stop = 1
        #wmin = float(min(wdata)) - 2
        #wmax = float(max(wdata)) + 2
        #plt.ylim([wmin,wmax])
        w_est = Low_Pass_Var(w_est)
        #w_turn = Low_Pass_Var(w_turn)
        wdata.append(w_turn)
        del wdata[0]
        line.set_xdata(np.arange(len(wdata)))
        line.set_ydata(wdata)
        we_data.append(w_est)
        del we_data[0]
        eline.set_xdata(np.arange(len(we_data)))
        eline.set_ydata(we_data)
        print(newL1)
        socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        msg = struct.pack('<dd',V_norm,w_turn)
        socksend.sendto(msg, (UDP_SEND,PORT_SEND))
        if pos[5]%20 == 0:
            plt.draw()
    # time.sleep(0.05)
    print("\nClosing Ports\n")
    for i in range(10000):
        socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        msg = struct.pack('<dd',0,0)
        socksend.sendto(msg, (UDP_SEND,PORT_SEND))
    print("Sent terminate command")	
    print(path.shape[0])
    pause = input("Graph")
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