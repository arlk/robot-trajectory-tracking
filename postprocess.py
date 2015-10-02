import numpy as np
import matplotlib.pyplot as pt
import numpy.linalg as la

spline_name = "robot_traj_id:2.csv"
spline_file = open(spline_name,"r+")
curve = np.array([(linef.rstrip('\n')).split(',') for linef in spline_file], dtype = float)
pt.figure(0)
dx_dt = np.gradient(curve[:,0])[:,None]
dy_dt = np.gradient(curve[:,1])[:,None]
vel = np.hstack((dx_dt,dy_dt))
dy_dx = dy_dt/dx_dt
#print(dy_dx.astype(int))
#velnorm = np.array([la.norm(row) for row in vel])
#pt.plot(velnorm)
#pt.figure(1)
slope = np.arctan(np.abs(dy_dx))
slope_grad = np.gradient(slope.reshape(-1))
pt.scatter(curve[:,0],curve[:,1], s=6*((slope_grad*50).astype(int))**2)
pt.show()