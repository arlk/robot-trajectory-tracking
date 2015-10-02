import threading
import time
import sys
from sys import exit
import os
import numpy as np

k = 0
prevtime = time.time()
a = np.array([])
Ts = 2

def printit():
    global k, prevtime, a
    # threading.Timer(0.5, printit).start()
    
    dt = time.time() - prevtime
    prevtime = time.time()
    print("Hello, World!", dt)
    a = np.append(a,dt)
    k += 1
    if k > 8:
        print("YOLOLOLOThread")
        print(np.mean(a))
        print("Err",(np.mean(a) - Ts)*100/Ts)
        os._exit(0)

def main():
    try:
        while True:
            time.sleep(Ts)
            threading.Timer(0,printit).start()
    except:
        print("YOLOLOLO")
        print(np.mean(a))
        print("Err",(np.mean(a) - Ts)*100/Ts)
        os._exit(0)

if __name__ == '__main__':
    main()

