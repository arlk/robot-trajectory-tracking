import numpy as np 
import csv
import matplotlib.pyplot as plt 


filename = 'time_{}.csv'.format(1)
datf = open(filename, 'r+')
data = np.asarray(list(csv.reader(datf)))

data = data.astype(float)
data = data.T

true_w = data[0]
w_cmd = data[1]
yaw = data[2]
nowtime = data[4]
newL1 = data[5]

x_new = np.zeros((data.shape[1],2))


R = np.array([[0.02,0.004],[0.004, 0.035]])
# R = R*1e-11
P = 0.5*np.eye(2)
I = np.eye(2)

for i in range(1,data.shape[1]):
    #Prediction
    A = np.array([[1, nowtime[i-1]],[0, -nowtime[i-1]/newL1[i-1]]])
    x_pred = A.dot(x_new[i-1]) + np.array([0, w_cmd[i-1]])
    
    P_pred = A.dot(P.dot(A.T))

    #Update
    y = np.array([yaw[i],true_w[i]]) - x_pred

    S = P_pred + R
    K = P_pred.dot(np.linalg.inv(S))

    x_new[i] = x_pred + K.dot(y)
    P = (I - K).dot(P_pred)
    #print(x_new[i])

# Plotting tool
# fig, axes = plt.subplots(nrows=2)

# axes[0].set_title("Angular Velocity")
# axes[0].set_ylim([-3.0,3.0])
# axes[1].set_title("Orientation Angle")
# axes[1].set_ylim([-3.0,3.0])
# axes = np.repeat(axes,2)

# styles = ['k-', 'r-', 'k--', 'r--']
# data = np.zeros((4, 1000))

# # plt.ylim([-3.0,3.0])
x_new = x_new.T
print(np.mean(x_new[1,200:]),np.mean(data[0,200:]))
print(np.std(x_new[1,200:]),np.std(data[0,200:]))


# lines0 = axes[0].plot(data[0], styles[0])[0]
# lines1 = axes[0].plot(x_new[1], styles[1])[0]
# lines2 = axes[1].plot(data[2], styles[2])[0]
# lines3 = axes[1].plot(x_new[0], styles[3])[0]

# fig.show()

# input("Ho")
xrang = np.arange(1,1000)
plt.plot(xrang, data[0], 'r--', xrang, x_new[1], 'k-')
# plt.show()