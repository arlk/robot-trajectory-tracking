import time
from threading import Timer
import sys

# class CustomTimer(_Timer):
#     def __init__(self, interval, function, args=[], kwargs={}):
#         self._original_function = function
#         super(CustomTimer, self).__init__(
#             interval, self._do_execute, args, kwargs)

#     def _do_execute(self, *a, **kw):
#         self.result = self._original_function(*a, **kw)

#     def join(self):
#         super(CustomTimer, self).join()
#         return self.result

def printt(k):
	kk = time.time()
	print("From ", k, time.time())
	dt = time.time() - kk
	print("Stop of ", k, dt)

def times(i):
	global a
	#print(time.time(),i)
	a = Timer(3, printt,(i,))
	a.start()

count = 0

try:
	while(True):
		count += 1
		time.sleep(0.1)
		times(count)

except:
	print("FAIL")