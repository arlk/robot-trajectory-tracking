import csv
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import matplotlib.mlab as mlab
import math

data = []

for i in range(11):
    filename = '../Line/{}.csv'.format(i+1)
    datf = open(filename, 'r+')
    datai = list(csv.reader(datf))
    data.extend(datai)

for i in range(5):
    filename = '{}.csv'.format(i+1)
    datf = open(filename, 'r+')
    datai = list(csv.reader(datf))
    data.extend(datai)

data = np.asarray(data)
data = data.astype(float)
data = data.T

true_w = data[0]
w_est = data[1]

err_w = true_w - w_est

#err_w /= np.linalg.norm(err_w)

theta_true = data[2]
theta_est = data[3]

err_theta = theta_true - theta_est
# err_w[err_w>2] = 0
# err_w[err_w<-2] = 0
# err_theta[err_theta>1] = 0
# err_theta[err_theta<-1] = 0

print(np.cov(err_theta, err_w))
# print(stats.normaltest(err_w))

# n, bins, patches = plt.hist(err_w, bins = 200, histtype = 'stepfilled',normed = 1,  color='r', alpha = 0.4, label = 'Error Angular Vel')
# mu = np.mean(err_w)
# sigma = np.std(err_w)
# #plt.plot(bins, mlab.normpdf(bins, mu, sigma))
# # plt.hist(err_theta, bins = 200, histtype = 'stepfilled',normed = 1,  color='y', alpha = 0.4, label = 'Error Orientation')
# #plt.hist(err_theta, bins = 100, histtype = 'stepfilled', normed = True, color='r', alpha = 0.5, label = 'Error Orientation')
# plt.legend()
# plt.show()

# data = np.delete(data,1,1)
# fig, axes = plt.subplots(nrows=1)

# data = data.T
# Ts = 0.01
# theta_1 = 0
# data[0] = -data[0]
# angvel = np.zeros(data[0].shape)
# #Calculating Angular vel
# for i,theta in enumerate(data[0]):
#     if i == data[0].shape[0] - 1:
#         break
#     angvel[i+1] = (data[0,i+1] - theta)/Ts

# data = np.append(data, angvel.reshape(1, data[0].shape[0]), 0)

# lines = [axes.plot(dat) for dat in data]

# fig.show()
# input("Ho")