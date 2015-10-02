import socket
import struct

#####ROBOT AND LAB INFO####
###########################

#Room size
room_length = 5.5
room_width = 3.35
scale_img = 120.0

#Robot shape and dimensions
rob_scale = 1.2
rob_rect_x = 0.15 * scale_img * rob_scale
rob_rect_y = 0.2 * scale_img * rob_scale
rob_trapz_wid = 0.05 * scale_img * rob_scale
rob_trapz_side = 0.07 * scale_img * rob_scale
rob_wheel_x = 0.04 * scale_img * rob_scale
rob_wheel_y = 0.02 * scale_img * rob_scale
rob_wheel_pos = 2.0/3.0 #Value between 1 and 0

#Robot colors. Add more RGB colors if needed 
#or the program will cycle through the color pallete.
color_robot = [[50,55,100],[49,163,84],[255,50,50],
        [225,204,0],[255,41,0],[253,72,47]]

######UI CUSTOMIZATION#####
###########################

#Grid size
grid_space = 0.5 #Distance between subaxes
dot_space = 0.05 #Distance between dots within the subaxes

#Font size
fntsz = 20

#Curve characteristics
sm = 10 #Fineness of curve
ptdist = 10 #Distance between control points

#########UDP COMMS########
##########################
UDP = "localhost"
PORT = 10000

###########################################################################
###################ONLY DEVELOPERS GO BEYOND THIS LINE#####################
###########################################################################

draw_rbid = 0
store_pt_name =[]
num_draw_rbts = 0
data = []

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP,PORT))

pix_x = int(room_width * scale_img)
pix_y = int(room_length * scale_img)

def setup():
  size(pix_x,pix_y)
  colorMode(RGB)
  frameRate(600)
  noStroke()
  ubuntu_med = loadFont("Ubuntu-Medium-60.vlw")
  textFont(ubuntu_med,fntsz)

def draw():
  global present_id
  global draw_rbid
  global num_draw_rbts
  present_id = []
  strokeWeight(1)
  stroke(255)
  fill(255)
  rectMode(CORNER)
  rect(0.0,0.0,width,height)
  draw_major_axes()
  draw_minor_axes()
  smooth()
  udprecv, addr = sock.recvfrom(1024)
  worldx,worldy,yaw,rbid,status,dataRate = struct.unpack('<dddddd',udprecv)
  x,y = convert_coord(worldx,worldy)
  yaw *= -1  #Reversing direction of rotation
  rbid = int(rbid)
  if status == 1:
    col = [row[3] for row in data]
    if (rbid in col) != 1:
      data.append([x,y,yaw,rbid])
    else:
      data[col.index(rbid)] = [x,y,yaw,rbid]
    present_id = sorted(col)
  for row in data:
    pushMatrix()
    translate(row[0],row[1])
    rotate(row[2]*frameCount/200.0)
    draw_robot(row[3])
    popMatrix()
  drawSpline()
  fill(100)
  stroke(0)
  strokeWeight(2)
  rectMode(CORNER)
  rect(pix_x-60,pix_y-fntsz,100,fntsz)
  fill(255)
  text("Done",pix_x-55,pix_y-0.1*fntsz)
  fill(100)
  rect(pix_x-60,pix_y-2*fntsz,100,fntsz)
  fill(255)
  text("Clear",pix_x-55,pix_y-1.1*fntsz)
  if mouseButton == LEFT:
    if mouseX > pix_x-60 and mouseY > pix_y - 2*fntsz:
      draw_rbid = 0
      num_draw_rbts = 0
    if mouseX > pix_x-60 and mouseY > pix_y - fntsz:
      sys.exit(0)
  if len(present_id) > 0:
    stroke(255)
    strokeWeight(1)
    rectMode(CORNER)
    if mouseButton != LEFT and draw_rbid < len(present_id):
      fill(color_bot([present_id[draw_rbid]][0],255))
      rect(0,0,pix_x,fntsz*1.5)
      circtimeout = frameCount%600
      if circtimeout<300:
        fill(255,0)
        strokeWeight(float(circtimeout%300)/30)
        stroke(color_bot([present_id[draw_rbid]][0],255*(1-float(circtimeout%300)/300)))
        circ = data[col.index(present_id[draw_rbid])]
        ellipse(circ[0],circ[1],float(circtimeout%300)/3,float(circtimeout%300)/3)
      fill(255)
      prompt = "Draw trajectory for Robot:{}".format(present_id[draw_rbid])
      text(prompt,fntsz/3,fntsz)
    if mouseButton == LEFT and draw_rbid <= len(present_id):
      fill(0)
      rect(0,0,pix_x,fntsz*1.5)
      fill(255)
      prompt = "Draw trajectory for Robot:{}".format(present_id[draw_rbid-1])
      text(prompt,fntsz/3,fntsz)
      
def draw_major_axes():
  stroke(0)
  strokeWeight(1)
  line(pix_x/2,0,pix_x/2,pix_y)
  line(0,pix_y/2,pix_x,pix_y/2)

def draw_minor_axes():
  noSmooth()
  for i in range(int(ceil(room_width/(2*grid_space)))):
    for j in range(int(room_length/(2*dot_space))):
      draw_point(convert_coord(i*grid_space,j*dot_space))
      draw_point(convert_coord(-i*grid_space,j*dot_space))
      draw_point(convert_coord(i*grid_space,-j*dot_space))
      draw_point(convert_coord(-i*grid_space,-j*dot_space))
  for j in range(int(ceil(room_length/(2*grid_space)))):
    for i in range(int(room_width/(2*dot_space))):
      draw_point(convert_coord(i*dot_space,j*grid_space))
      draw_point(convert_coord(-i*dot_space,j*grid_space))
      draw_point(convert_coord(i*dot_space,-j*grid_space))
      draw_point(convert_coord(-i*dot_space,-j*grid_space))

def draw_point(pt):
  point(pt[0],pt[1])

def convert_coord(mocapx,mocapy):
  px = pix_x/2 + (mocapx*scale_img)
  py = pix_y/2 - (mocapy*scale_img)
  return (px,py)

def rev_convert_coord(virtx,virty):
  wx = (virtx - pix_x/2)/scale_img
  wy = (pix_y/2 - virty)/scale_img
  return [wx,wy]

def draw_robot(r_id):
  stroke(150)
  strokeWeight(1)
  rectMode(CENTER)
  fill(color_bot([r_id][0],255))
  rect(0.0,0.0,rob_rect_x,rob_rect_y)
  pushMatrix()
  rotate(HALF_PI)
  translate(-fntsz/3.0,fntsz/3.0)
  fill(255)
  text(r_id,0,0)
  popMatrix()
  stroke(50)
  strokeWeight(1)
  fill(255)
  beginShape()
  vertex(rob_rect_x/2.0,rob_rect_y/2.0)
  vertex(rob_rect_x/2.0+rob_trapz_wid,rob_trapz_side/2.0)
  vertex(rob_rect_x/2.0+rob_trapz_wid,-rob_trapz_side/2.0)
  vertex(rob_rect_x/2.0,-rob_rect_y/2.0)
  endShape()
  noStroke()
  draw_wheel(rob_wheel_pos*rob_rect_x/2.0,rob_rect_y/2+rob_wheel_y/2)
  draw_wheel(rob_wheel_pos*rob_rect_x/2.0,-rob_rect_y/2-rob_wheel_y/2)
  draw_wheel(-rob_wheel_pos*rob_rect_x/2.0,rob_rect_y/2+rob_wheel_y/2)
  draw_wheel(-rob_wheel_pos*rob_rect_x/2.0,-rob_rect_y/2-rob_wheel_y/2)

def draw_wheel(wx,wy):
  fill(0)
  rectMode(CENTER)
  rect(wx,wy,rob_wheel_x,rob_wheel_y)

def mousePressed():
  global store_pt_name
  global draw_rbid
  global num_draw_rbts
  draw_rbid += 1
  if draw_rbid <= len(present_id):
    num_draw_rbts = draw_rbid
    store_pt_name.append("temp_store_pt_robot:{}.txt".format(draw_rbid))
    store_pt = open(store_pt_name[draw_rbid-1],"w+")
    store_pt.truncate()
    store_pt.close()
  
def mouseDragged():
  if draw_rbid <= len(present_id):
    store_pt = open(store_pt_name[draw_rbid-1],"a+")
    mousepts = "{},{}\n".format(float(mouseX),float(mouseY))
    store_pt.write(mousepts)
    store_pt.close()

def mouseReleased():
  if len(present_id)>0 and draw_rbid <= len(present_id):
    read_pt = open(store_pt_name[draw_rbid-1],"r")
    curve_pt = [(linef.rstrip('\n')).split(',') for linef in read_pt]
    read_pt.close()
    spline_name = "robot_traj_id:{}.txt".format(present_id[draw_rbid-1])
    spline_file = open(spline_name,"w+")
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
        splinecoord = rev_convert_coord(float(spline_pt[j][0]),float(spline_pt[j][1]))
        splinepts = "{},{}\n".format(splinecoord[0],splinecoord[1])
        spline_file.write(splinepts)
      spline_file.close()

def drawSpline():
  for loop_id in range(num_draw_rbts):
    fill(255,0)
    strokeWeight(3)
    stroke(color_bot([present_id[loop_id]][0],255))
    read_pt = open(store_pt_name[loop_id],"r")
    curve_pt = [(linef.rstrip('\n')).split(',') for linef in read_pt]
    read_pt.close()
    if len(curve_pt) > 2*sm:
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

def color_bot(cid,alpha):
  col_no = cid%len(color_robot) -1
  return color(color_robot[col_no][0],color_robot[col_no][1],color_robot[col_no][2],alpha)
