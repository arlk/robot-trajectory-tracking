draw_rbid = 0
store_pt_name =[]

def setup():
	size(500,500)
	colorMode(RGB)
	frameRate(60)
	
	
def draw():
	background(255)
	stroke(0)
	fill(255,0)
	drawSpline()

def mousePressed():
	global store_pt_name
	global draw_rbid
	draw_rbid += 1
	store_pt_name.append("store_pt_robot:{}.txt".format(draw_rbid))
	store_pt = open(store_pt_name[draw_rbid-1],"w+")
	store_pt.truncate()
	store_pt.close()
	

def mouseDragged():
	global store_pt_name
	global draw_rbid
	store_pt = open(store_pt_name[draw_rbid-1],"a+")
	mousepts = "{},{}\n".format(float(mouseX),float(mouseY))
	store_pt.write(mousepts)
	store_pt.close()

def mouseReleased():
	spline_name = []
	global draw_rbid
	sm = 20
	ptdist = 5
	for loop_id in range(draw_rbid):
		read_pt = open(store_pt_name[loop_id],"r")
		curve_pt = [(linef.rstrip('\n')).split(',') for linef in read_pt]
		read_pt.close()
		spline_name.append("robot_traj_id:{}.txt".format(draw_rbid))
		spline_file = open(spline_name[loop_id-1],"w+")
		spline_file.truncate()
		if len(curve_pt) >= 2*sm:
			spline_pt = []
			for t in range(sm+1):
				spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[0],curve_pt[0],curve_pt[ptdist],curve_pt[ptdist*2]))
			for i in range(len(curve_pt)-2*ptdist):
				if i%ptdist == 0 and i>=ptdist:
					for t in range(sm+1):
						spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[i-ptdist],curve_pt[i],curve_pt[i+ptdist],curve_pt[i+2*ptdist]))
			for t in range(sm+1):
				spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[i],curve_pt[i+ptdist],curve_pt[i+2*ptdist],curve_pt[i+2*ptdist]))
			for j in range(len(spline_pt)):
				splinepts = "{},{}\n".format(float(spline_pt[j][0]),float(spline_pt[j][1]))
				spline_file.write(splinepts)
			spline_file.close()


def drawSpline():
	global store_pt_name
	global draw_rbid
	sm = 20
	ptdist = 5
	for loop_id in range(draw_rbid):
		read_pt = open(store_pt_name[loop_id-1],"r")
		curve_pt = [(linef.rstrip('\n')).split(',') for linef in read_pt]
		read_pt.close()
		if len(curve_pt) >= 2*sm:
			spline_pt = []
			for t in range(sm+1):
				spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[0],curve_pt[0],curve_pt[ptdist],curve_pt[ptdist*2]))
			for i in range(len(curve_pt)-2*ptdist):
				if i%ptdist == 0 and i>=ptdist:
					for t in range(sm+1):
						spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[i-ptdist],curve_pt[i],curve_pt[i+ptdist],curve_pt[i+2*ptdist]))
			for t in range(sm+1):
				spline_pt.append(interpolateSpline(float(t)/sm,curve_pt[i],curve_pt[i+ptdist],curve_pt[i+2*ptdist],curve_pt[i+2*ptdist]))
			for j in range(len(spline_pt)-1):
				line(spline_pt[j][0],spline_pt[j][1],spline_pt[j+1][0],spline_pt[j+1][1])

def interpolateSpline(t,p1,p2,p3,p4):
	point = [0,0]
	f1 = -0.5*t + t**2 - 0.5*t**3
	f2 = 1 - 2.5*t**2 + 1.5*t**3
	f3 = 0.5*t + 2*t**2 - 1.5*t**3
	f4 = -0.5*t**2 + 0.5*t**3
	point[0] = f1*float(p1[0]) + f2*float(p2[0]) + f3*float(p3[0]) + f4*float(p4[0])
	point[1] = f1*float(p1[1]) + f2*float(p2[1]) + f3*float(p3[1]) + f4*float(p4[1])
	return point