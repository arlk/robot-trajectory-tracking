import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import time
from threading import Timer
import threading
x = np.arange(0, 2*np.pi, 0.1)
y = np.sin(x)
prev = time.time()

fig, axes = plt.subplots(nrows=6)

styles = ['r-', 'g-', 'y-', 'm-', 'k-', 'c-']
def plot(ax, style):
    return ax.plot(x, y, style, animated=True)[0]
lines = [plot(ax, style) for ax, style in zip(axes, styles)]

def timep():
    global prev
    times = time.time() - prev
    prev = time.time()
    print(times)
m = threading.Thread(target = timep)
def runtimesa():
    while True:
        time.sleep(0.2)
        pp = Timer(0,timep,())
        print(time.time())
        pp.daemon = True
        pp.start()
t = threading.Thread(target = runtimesa)
t.start()
def animate(i):
    # time.sleep(0.05)
    
    for j, line in enumerate(lines, start=1):
        line.set_ydata(np.sin(j*x + i/100.0))
    return lines

# We'd normally specify a reasonable "interval" here...

ani = animation.FuncAnimation(fig, animate, 
                          interval=0, blit=True)
plt.show()

