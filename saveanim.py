import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

x = np.arange(0, 2*np.pi, 0.1)
y = np.sin(x)

fig, axes = plt.subplots(nrows=6)

styles = ['r-', 'g-', 'y-', 'm-', 'k-', 'c-']
def plot(ax, style):
    return ax.plot(x, y, style, animated=True)[0]
lines = [plot(ax, style) for ax, style in zip(axes, styles)]

def animate(i):
    for j, line in enumerate(lines, start=1):
        line.set_ydata(np.sin(j*x + i/10.0))
    return lines

#mywriter = FFMPEG
# We'd normally specify a reasonable "interval" here...

ani = animation.FuncAnimation(fig, animate, 
                              interval=50, blit=True)
mywriter = animation.FFMpegWriter()
ani.save('animtrial.mp4',writer=mywriter)
plt.show()