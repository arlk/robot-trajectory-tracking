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
import sched
from threading import Timer
import threading
from datetime import datetime
import os

#Velocity and Gains
V_norm = 0.20
K_gain = 1.5
Ts = 0.01

#Store data
filename = (datetime.now()).strftime("%d%B%Y%I:%M%p")
# est_store = open("state_est/"+filename+"Ts"+str(int(Ts*100))+".csv","w+")


#Comm Setup
UDP = "192.168.1.90"
UDP_SEND = "192.168.1.54"
# UDP = "localhost"
# UDP_SEND = "localhost"
PORT = 11000
PORT_SEND = 3500
socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

#Global variables

pos = np.zeros(6)
prev_pos = np.zeros(6)
stop = 0
untrackcnt = 0
w_est = 0.0
w_cmd = 0.0
v_cmd = 0.0
wp_num = 0.0
eta = 0.0
true_w = 0.0
L1 = K_gain*V_norm
newL1 = K_gain*V_norm
x_prev = np.zeros(2)
R = np.array([[0.02,0.004],[0.004, 0.035]])
# R = R*1e-11
P = 0.5*np.eye(2)
I = np.eye(2)

prevtime = time.time()
nowtime = 0

# Plotting tool
fig, axes = plt.subplots(nrows=2)

axes[0].set_title("Angular Velocity")
axes[0].set_ylim([-3.0,3.0])
axes[1].set_title("Orientation Angle")
axes[1].set_ylim([-3.0,3.0])
axes = np.repeat(axes,2)

styles = ['r-', 'k-', 'r--', 'k--']
data = np.zeros((4, 1000))

# plt.ylim([-3.0,3.0])

def plotsub(ax, style, i):
    return ax.plot(data[i], style, animated=True)[0]

# lines = [plot(ax, style, i) for i, (ax, style) in enumerate(zip(axes, styles))]
lines = [plotsub(axes[i], style, i) for i, style in enumerate(styles)]

fig.show()


# Trajectory file
file = open('/home/arun/sketchbook/pathgen_processing/robot_traj_id:4.csv')
path = np.asarray(list(csv.reader(file))).astype(float)
pathtree = ss.KDTree(np.column_stack((path[:,0],path[:,1])))

# Unpacks Current Position from UDP message
def current_pos():
    global pos, prev_pos, prevtime, nowtime
    nowtime = time.time() - prevtime
    prevtime = time.time()
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind((UDP,PORT))
    udprecv, addr = sock.recvfrom(1024)
    x,y,yaw,rbid,status,dataFrame = struct.unpack('<dddddd',udprecv)
    yaw = yaw*math.pi/180

    pos = np.array([x,y,yaw,rbid,status,dataFrame])
    sock.close()

# Returns distance to next waypoint
def L1_Distance(waypoint):
    dist_vec = path[waypoint] - pos[:2]
    Dist = la.norm(dist_vec)
    return Dist

# Returns Angular difference to next waypoint
def Angle(waypoint):
    global eta
    vec = path[waypoint] - pos[:2]
    angle = math.atan2(vec[1],vec[0])
    eta = pos[2] - angle
    if math.fabs(eta) > math.pi:
        eta -= math.copysign(2*math.pi,eta)

def true_mes():
    global true_w,prev_pos
    true_w = pos[2] - prev_pos[2]
    prev_pos = np.copy(pos)
    if true_w > 3.0:
        true_w -= 2*math.pi
    if true_w < -3.0:
        true_w += 2*math.pi
    #true_w /= Ts
    true_w /= -nowtime

# Returns Waypoint Index and Distance to Waypoint
def waypoint_finder(L1_Dist):
    global pos
    pntarry = pathtree.query_ball_point(pos[:2],L1_Dist, p = 2)
    if not pntarry:
        nL1, waypoint = pathtree.query(pos[:2], k = 1, p = 2)
    else:
        pntarry = np.sort(np.asarray(pntarry))
        pntarry -= wp_num
        waytemp = pntarry[np.where(pntarry>=0)]
        if waytemp.shape[0] == 0:
            waypoint = 0
        else:
            newtemp = np.arange(waytemp[0],waytemp.shape[0]+waytemp[0])
            waypoint = np.amax(np.where(waytemp-newtemp==0))
        waypoint += wp_num
        nL1 = L1_Distance(waypoint) 
    return waypoint, nL1

def animate(i):
    global data, lines
    newdata = np.array([true_w, x_prev[1], pos[2], x_prev[0]])
    if stop != True:
        data = np.append(data, newdata[:,None], axis = 1)
        data = np.delete(data,0,axis = 1)
    for j, line in enumerate(lines):
        line.set_ydata(data[j])
    return lines

def L1_control_algo():
    global w_cmd, pos, stop, v_cmd, wp_num, nowtime, prevtime, newL1

    # Distance ahead of which the waypoint needs to be tracked
    L1 = K_gain*V_norm

    # Find the waypoint index at that L1 distance
    # and recompute exact L1 distance
    wp_num, newL1 = waypoint_finder(L1)

    #Calculate angle to the waypoint
    Angle(wp_num)
    # print("Angle:",eta)
    # print("Waypoint:",wp_num)
    # print("Frame:", pos[5])
    # print("Time delta:", nowtime)

    #Commands:
    if eta > 0.2:
        acc_cmd = (math.sin(eta)*V_norm**2)/newL1
    else:
        acc_cmd = (eta*V_norm**2)/newL1
    # print("Sin eta", math.sin(eta))
    w_cmd = acc_cmd/V_norm**2
    v_cmd = V_norm

    # print("Omega CMD:",w_cmd)


    if newL1<0.01:

        print("Destination REACHED!!", newL1)
        stop = 1

def track_state():
    global untrackcnt, V_norm, w_cmd, v_cmd
    if pos[4] > 0.2:
        untrackcnt = 0
    else:
        untrackcnt += 1
    if untrackcnt>50:
        print("UNTRACKED! for {} ms".format(untrackcnt))
        v_cmd = 0
        w_cmd = 0

def kalmanfilter():
    global x_prev, P, true_w, nowtime, newL1, R, pos

    true_mes()

    A = np.array([[1, -nowtime],[0,-nowtime/newL1]])
    x_pred = A.dot(x_prev) + np.array([0, w_cmd])

    P_pred = A.dot(P.dot(A.T))

    #Update
    if x_pred[0] - pos[2]  > 3.0:
        x_pred[0] -= 2*math.pi
    if x_pred[0] - pos[2] < -3.0:
        x_pred[0] += 2*math.pi
    y = np.array([pos[2],true_w]) - x_pred

    S = P_pred + R
    K = P_pred.dot(np.linalg.inv(S))

    x_new = x_pred + K.dot(y)
    P = (I - K).dot(P_pred)

    x_prev = x_new


    pos[2] = x_prev[0]

    # print("True Omega:", true_w)
    # print("kalmanfilter Omega:",x_prev[1])
    # print("Angle kalmanfilter:",ang_est)
    # datastr = "{},{},{},{},{}\n".format(true_w, w_cmd, pos[2], nowtime, newL1)
    # est_store.write(datastr)



# def filter():
#     pass

def stop_udp():
    print("\nClosing Ports\n")
    for i in range(10000):
        socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        msg = struct.pack('<dd',0,0)
        socksend.sendto(msg, (UDP_SEND,PORT_SEND))
    print("Sent terminate command")
    socksend.close()
    # est_store.close()

def send_udp():
    msg = struct.pack('<dd',v_cmd,w_cmd)
    socksend.sendto(msg, (UDP_SEND,PORT_SEND))

def start_all():
    current_pos()
    kalmanfilter()
    L1_control_algo()
    track_state()
    send_udp()

def controller():
    try:
        while stop != True:


            time.sleep(Ts)

            # # Find current pos
            # C_POS = Timer(0, current_pos, ())
            # C_POS.daemon = True
            # C_POS.start()

            # # Begin Control Algorithm at Ts = Time Step (1ms)
            # L1_ALGO = Timer(0, L1_control_algo, ())
            # L1_ALGO.daemon = True
            # L1_ALGO.start()

            # # Check if robot is being tracked
            # TRACKED = Timer(0, track_state, ())
            # TRACKED.daemon = True
            # TRACKED.start()

            # # Send UDP commands
            # UDP_SEND = Timer(0, send_udp, ())
            # UDP_SEND.daemon = True
            # UDP_SEND.start()
            start_all()

        if stop == True:
            raise Exception
    
    except:
        print(sys.exc_info()[0])
        print("Destination Reached / Interrupt")
        stop_udp()
        raise Exception


control = threading.Thread(target = controller)
control.daemon = True
control.start()

try:
    ani = animation.FuncAnimation(fig, animate, 
                              interval=Ts*500, blit=True)
    # mywriter = animation.FFMpegWriter()
    # ani.save('test_3.mp4',writer=mywriter)
    plt.show()
    stop_udp()
except:
    print(sys.exc_info()[0])
    stop_udp()