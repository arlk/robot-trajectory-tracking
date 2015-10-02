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

#Velocity and Gains
V_norm = 0.20
K_gain = 1.5

#Store data
filename = (datetime.now()).strftime("%d%B%Y%I:%M%p")
est_store = open(filename+".csv","w+")


#Comm Setup
UDP = "192.168.1.90"
UDP_SEND = "192.168.1.54"
# UDP = "localhost"
# UDP_SEND = "localhost"
PORT = 11000
PORT_SEND = 3500
socksend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

#Global variables
Ts = 0.02
pos = np.zeros(6)
prev_pos = np.zeros(6)
stop = 0
untrackcnt = 0
w_est = 0
w_cmd = 0
v_cmd = 0
wp_num = 0

prevtime = 0
nowtime = 0

# Plotting tool
fig, axes = plt.subplots(nrows=1)
# axes[0].set_title("Velocity")
# axes[1].set_title("Turn Rate")
#axes = np.repeat(axes,2)
styles = ['k-', 'r--']
data = np.zeros((2, 1000))

plt.ylim([-1.5,1.5])

def plot(ax, style, i):
    return ax.plot(data[i], style, animated=True)[0]

# lines = [plot(ax, style, i) for i, (ax, style) in enumerate(zip(axes, styles))]
lines = [plot(axes, style, i) for i, style in enumerate(styles)]

fig.show()


# Trajectory file
file = open('/home/arun/sketchbook/pathgen_processing/robot_traj_id:4.csv')
path = np.asarray(list(csv.reader(file))).astype(float)
pathtree = ss.KDTree(np.column_stack((path[:,0],path[:,1])))

# Unpacks Current Position from UDP message
def current_pos():
    global pos, prev_pos
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind((UDP,PORT))
    udprecv, addr = sock.recvfrom(1024)
    x,y,yaw,rbid,status,dataFrame = struct.unpack('<dddddd',udprecv)
    yaw = yaw*math.pi/180
    prev_pos = np.copy(pos)
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
        print("Yellow")
        eta -= math.copysign(2*math.pi,eta)
    return eta

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
    global data, lines, w_est
    estimate()
    newdata = np.array([w_cmd, w_est])
    datastr = "{},{},{}\n".format(pos[2],pos[5],w_cmd)
    est_store.write(datastr)
    data = np.append(data, newdata[:,None], axis = 1)
    data = np.delete(data,0,axis = 1)
    for j, line in enumerate(lines):
        line.set_ydata(data[j])
    return lines

def L1_control_algo():
    global w_cmd, pos, stop, v_cmd, wp_num, nowtime, prevtime

    # Distance ahead of which the waypoint needs to be tracked
    L1 = K_gain*V_norm

    nowtime = time.time() - prevtime
    prevtime = time.time()
    # Find the waypoint index at that L1 distance
    # and recompute exact L1 distance
    wp_num, newL1 = waypoint_finder(L1)

    #Calculate angle to the waypoint
    eta = Angle(wp_num)
    # print("Angle:",eta)
    print("Waypoint:",wp_num)
    print("Frame:", pos[5])
    print("Time delta:", nowtime)

    #Commands:
    acc_cmd = (math.sin(eta)*V_norm**2)/newL1
    # print("Sin eta", math.sin(eta))
    w_cmd = acc_cmd/V_norm**2
    v_cmd = V_norm

    print("Omega CMD:",w_cmd)


    if newL1<0.1:
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

def estimate():
    global data, w_est
    w_est = pos[2] - prev_pos[2]
    if w_est > 3.0:
        w_est -= 2*math.pi
    if w_est < -3.0:
        w_est += 2*math.pi
    w_est /= -nowtime
    print("Estimate Omega:",w_est)


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
    est_store.close()

def send_udp():
    msg = struct.pack('<dd',v_cmd,w_cmd)
    socksend.sendto(msg, (UDP_SEND,PORT_SEND))

# Animated Plot
def controller():
    while stop != True:


        time.sleep(Ts)

        # Find current pos
        C_POS = Timer(0, current_pos, ())
        C_POS.daemon = True
        C_POS.start()

        # Begin Control Algorithm at Ts = Time Step (1ms)
        L1_ALGO = Timer(0, L1_control_algo, ())
        L1_ALGO.daemon = True
        L1_ALGO.start()

        # Check if robot is being tracked
        TRACKED = Timer(0, track_state, ())
        TRACKED.daemon = True
        TRACKED.start()

        # Send UDP commands
        UDP_SEND = Timer(0, send_udp, ())
        UDP_SEND.daemon = True
        UDP_SEND.start()


    if stop == True:
        stop_udp()

control = threading.Thread(target = controller)
control.daemon = True
control.start()

try:
    ani = animation.FuncAnimation(fig, animate, 
                              interval=Ts*100, blit=True)
    plt.show()
    stop_udp()
except:
    print(sys.exc_info()[0])
    stop_udp()