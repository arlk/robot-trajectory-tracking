import socket
import struct
import math
import numpy as np
import csv
import sys
import time
import numpy.linalg as la
from matplotlib import pyplot as plt

V_norm = 0.3
L1_Damping = 0.75
L1_Period = 20

UDP = "192.168.1.90"
UDP_SEND = "192.168.1.51"
PORT = 11000
PORT_SEND = 3500
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP,PORT))

plt.ion()
wfig = plt.figure()
wax = plt.axes()
wdata = [0]*1000
line, = plt.plot(wdata)
plt.ylim([-2,2])
plt.show()

def Current_Pos():
    rbid = 0
    while rbid != 1:
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

file = open('/home/arun/sketchbook/pathgen_processing/robot_traj_id:1.csv')
path = np.asarray(list(csv.reader(file))).astype(float)
#final_pt = 2*path[-1] - path[-150]
#path = np.append(path,final_pt.reshape(1,2),axis=0)

# w_name = "robot_w"
# w_file = open(w_name,"w+")
# w_file.truncate()
wp_num = 0
pos = Current_Pos()
count = 0
stop = 0
untrackcnt = 0
try:
    while stop == 0:
        V_norm = 0.3
        count += 1
        pos = Current_Pos()
        print(pos)
        L1 = 1.5*V_norm
        if pos[4] > 0:
            for i,wp in enumerate(path[wp_num:,:]):
                if L1_Distance(wp,pos) > L1:
                    wp_num  += i
                    minimum = 1000
                    minj = 0
                    if L1_Distance(wp,pos) > 3*L1:
                        for j,wpj in enumerate(path[wp_num:,:]):
                            if L1_Distance(wpj,pos) < minimum:
                                minimum = L1_Distance(wpj,pos)
                                minj = j
                    wp_num += minj
                    stop = 0
                    break
                else:
                    if wp_num == path.shape[0] - 1 and L1_Distance(path[-1],pos) > 1e-2:
                        L1 = L1_Distance(path[wp_num],pos)
                        stop = 0
                        break
                stop = 1
            eta = Angle(wp_num,pos)
            print(wp_num)
            acc_cmd = (math.sin(eta)*V_norm**2)/L1
            w_turn = acc_cmd/V_norm**2
            untrackcnt = 0
        else:
            untrackcnt += 1
            if untrackcnt>50:
                V_norm = 0
                w_turn = 0

        wmin = float(min(wdata)) - 2
        wmax = float(max(wdata)) + 2
        plt.ylim([wmin,wmax])
        w_d = w_turn
        wdata.append(w_d)
        del wdata[0]
        line.set_xdata(np.arange(len(wdata)))
        line.set_ydata(wdata)
        print(w_turn)
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
    plt.show()
    a = input("hello")
except:
    print("\nClosing Ports\n")
    print(sys.exc_info()[0])
    for i in range(10000):
        socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        msg = struct.pack('<dd',0,0)
        socksend.sendto(msg, (UDP_SEND,PORT_SEND))
    print("Sent terminate command")	
    socksend.close()	    
