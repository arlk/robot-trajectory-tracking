import matplotlib.pyplot as plt
import scipy.signal as sg
import numpy as np

x = np.array([[2, 2, 5, 2, 1, 0, 1, 4, 0]])
x = np.tile(x,3)
x = np.append(x, sg.savgol_filter(x,5,2), axis = 0)

coeff = np.array([16, 1, -10, -10, -6, 9])/28
y = np.zeros(x[0].shape)
for i in range(5,x[0].shape[0]):
    y[i] = coeff[::-1].dot(x[0,i-5:i+1])


x = np.append(x, y.reshape(1,x[0].shape[0]), axis = 0)

#print(x)
fig, axes = plt.subplots(nrows = 1)
lines = [axes.plot(dat) for dat in x]

plt.show()