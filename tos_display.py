 #!/usr/bin/python

# This display module uses Pygame to draw picorder routines to the screen.
# It is built upon the original Picorder UI and is intended to be used for TOS
# styled tricorders.
print("Loading 320x240 Duotronic Interface")
# The following are some necessary modules for the Picorder.
from asyncio import sleep
from pickle import FALSE
import pygame, time, os
import socket

from pathlib import Path
from plars import *
from objects import *
from input import *
from amg8833_pygame import *
from operator import itemgetter


if configure.video:
	from pyvidplayer import Video


if not configure.pc:
	if configure.tr108:
		import os

SAMPLE_SIZE = configure.samples
GRAPH_WIDTH = configure.mode_a_graph_width
GRAPH_HEIGHT = configure.mode_a_graph_height
GRAPH_X = configure.mode_a_x_offset
GRAPH_Y = configure.mode_a_y_offset
GRAPH_X2 = GRAPH_X + GRAPH_WIDTH
GRAPH_Y2 = GRAPH_Y + GRAPH_HEIGHT


os.environ["SDL_VIDEO_CENTERED"] = "1"
os.environ['PYGAME_BLEND_ALPHA_SDL2'] = '1'
# The following commands initiate a pygame environment.
pygame.init()
pygame.mixer.init()
pygame.font.init()
pygame.display.set_caption('PicorderOS')

# The following commands disable the mouse and cursor.
#pygame.event.set_blocked(pygame.MOUSEMOTION)
#pygame.mouse.set_visible(0)

# set the screen configuration
resolution = (320,240)
def_modes = 16
refreshrate = 0

# controls the margins to adjust for adjusting text positioning.
marginright = 16
marginleft = 16

# The following lists are for my colour standards.
red = (255,0,0)
green = (106,255,69)
blue = (99,157,255)
yellow = (255,221,5)
orange = (255,192,2)
black = (0,0,0)
white = (255,255,255)

theme1 = [red,green,yellow]
theme2 = [blue,green,white]
theme3 = [blue, white, red]
themes = [theme1,theme2, theme3]
themenames = ["alpha", "beta", "delta"]


# The following lists/objects are for UI elements.
titleFont = "assets/babs.otf"
blueInsignia = pygame.image.load('assets/icon.png')
pioslogo = pygame.image.load('assets/Med_Picorder_Logo.png')
backplane = pygame.image.load('assets/background.png')
backgraph = pygame.image.load('assets/backgraph.png')
slidera = pygame.image.load('assets/slider.png')
sliderb = pygame.image.load('assets/slider2.png')
videobg = pygame.image.load('assets/videobg.png')
status = "startup"
last_status = "startup"

# sets the icon for the program (will show up in docks/taskbars on PCs)
#pygame.display.set_icon(blueInsignia)



# The following function defines button behaviours and allows the program to
# query the button events and act accordingly. This function is deprecated.
def butswitch():
	configure.eventlist[0] = [False, False, False]
	for event in pygame.event.get():
	#key = pygame.key.get_pressed() 
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RIGHT:
				configure.eventlist[0][2] = True
				configure.eventready[0] = True

			if event.key == pygame.K_DOWN:
				configure.eventlist[0][1] = True
				configure.eventready[0] = True

			if event.key == pygame.K_LEFT:
				configure.eventlist[0][0] = True
				configure.eventready[0] = True

			if event.key == pygame.K_a:
				configure.auto[0] = not configure.auto[0]

			if event.key == pygame.K_q:
				configure.status[0] = "quit"

# the following class defines simple text labels

class Label(object):
	def __init__(self,content = "hello", fontSize = 30, x = 0, y = 0, color = white, font = titleFont):
		self.x = x
		self.y = y
		self.color = color
		self.fontSize = fontSize
		self.myfont = pygame.font.Font(font, self.fontSize)
		self.content = content
		self.size = self.myfont.size(self.content)
		self.scaler = 3

	# Sets the paramaters of the text, used when ready to push the text.
	def update(self, content, fontSize, newx, newy, fontType, color):
		self.x = newx
		self.y = newy
		self.content = content
		self.fontSize = fontSize
		self.myfont = pygame.font.Font(fontType, self.fontSize)
		self.color = color

	def r_align(self,x,y):
		size = self.getrect()
		textposx = x-size[0]
		textposy = y
		self.update(self.content,self.fontSize,textposx,textposy,titleFont,self.color)

	# centers the text within an envelope
	def center(self,w,h,x,y):
		size = self.getrect()
		xmid = x + w/2
		ymid = y + h/2
		textposx = xmid - (size[0]/2)
		textposy = ymid - (size[1]/2) + self.scaler
		self.update(self.content,self.fontSize,textposx,textposy,titleFont,self.color)

	# returns the width and height of the desired text (useful for justifying)
	def getrect(self):
		label = self.myfont.render(self.content, 1, self.color)
		textw = label.get_width()
		texth = label.get_height()
		return textw,texth

	# returns only the width of the text.
	def get_size(self, content):
		width, height = self.myfont.size(content)
		return width

	# finally renders the text and then blits to surface
	def draw(self, surface):
		label = self.myfont.render(self.content, 1, self.color)
		surface.blit(label, (self.x, self.y))

# a class to create a simple text list.
# initialize with x/y coordinates
# on update provide list of items to display, and draw object to draw to.
class Label_List(object):

	def __init__(self, x = 0, y = 0, colour = white, font = titleFont, size = 15):

		#initial coordinates
		self.x = x
		self.y = y

		# used in the loop to offset y location of items.
		self.jump = 0

		#adjusts the increase in seperation
		self.spacer = 1

		# holds the items to display
		self.labels = []

		self.font = font

		self.colour = colour

		self.size = size


	# draws the list of items as a text list.
	def draw(self, items, surface):

		# clears label buffer.
		self.labels = []

		# for each item in the list of items to draw
		for index, item in enumerate(items):

			string = str(item)

			# create a text item with the string.
			thislabel = Label(content = string, color = self.colour, x = self.x, y = self.y + self.jump, fontSize = self.size)

			# blit the text		
			thislabel.draw(surface)

			# increase the y position by the height of the last item, plus spacer
			self.jump += (thislabel.myfont.get_height() + self.spacer)

		# when loop is over reset jump counter.
		self.jump = 0

# this class provides functionality for interactive text labels.
class SelectableLabel(Label):

	def __init__(self, oper, special = 0):

		# special determines the behaviour of the label for each type of
		# operator the class is supplied. There may be multiple types of int or
		# boolean based configuration parameters so this variable helps make
		# new options

		self.special = special

		# coordinates
		self.x = 0
		self.y = 0

		# basic graphical parameters
		self.color = white
		self.fontSize = 33
		self.myfont = pygame.font.Font(titleFont, self.fontSize)
		text = "Basic Item"
		self.size = self.myfont.size(text)
		self.scaler = 3
		self.selected = False
		self.indicator = Image()
		self.content = "default"

		#is either 
		self.oper = oper

	def update(self, content, fontSize, nx, ny, fontType, color):
		self.x = nx
		self.y = ny
		self.content = content
		self.fontSize = fontSize
		self.myfont = pygame.font.Font(fontType, self.fontSize)
		self.color = color
		self.indicator.update(sliderb, nx - 23, ny+1)

	# this function is called when the user decides to change a setting.
	def toggle(self):

		# if the parameter supplied is a boolean
		if isinstance(self.oper[0], bool):
			#toggle its state
			self.oper[0] = not self.oper[0]

		#if the parameter supplied is an integer
		elif isinstance(self.oper[0], int):

			# increment the integer.
			self.oper[0] += 1

			# if the integer is larger than the pool of available sensors.
			# this assumes this selectable label is being used to control
			# sensor selection.
			if self.special == 1 and self.oper[0] > (len(configure.sensor_info)-1):
				self.oper[0] = 0

			if self.special == 2 and self.oper[0] > (len(themes) - 1):
				self.oper[0] = 0

		return self.oper[0]

	def draw(self, surface):

		if self.selected:
			self.indicator.draw(surface)

		label = self.myfont.render(self.content, 1, self.color)

		status_text = "dummy"

		if self.special == 0:
			status_text = str(bool(self.oper))
		elif self.special == 1:
			status_text,dev,sym,maxi,mini = configure.sensor_info[self.oper[0]]
		elif self.special == 2:
			status_text = themenames[self.oper[0]]

		pos = resolution[0] - (self.get_size(status_text) + 37)
		state = self.myfont.render(status_text, 1, self.color)


		surface.blit(label, (self.x, self.y))
		surface.blit(state, (pos, self.y))

# the following class is used to display images
class Image(object):
	def __init__(self):
		self.x = 258
		self.y = 66
		self.Img = blueInsignia

	def update(self, image, nx, ny):
		self.x = nx
		self.y = ny
		self.Img = image


	def draw(self, surface):
		surface.blit(self.Img, (self.x,self.y))

# The following class is used to prepare sensordata for display on the graph.
class graphlist(object):

	# the following is constructor code to give each object a list suitable for storing all our graph data, in this case it is 145 spaces.
	def __init__(self):
		self.glist = []
		for i in range(145):
			self.glist.append(110.5)

	# the following function returns the list.
	def grablist(self):
		return self.glist

	# the following appends data to the list.
	def updatelist(self, data):

		#puts a new sensor value at the end
		self.glist.append(data)
		#pop the oldest value off
		self.glist.pop(0)

# the following pairs the list of values with coordinates on the X axis. The supplied variables are the starting X coordinates and spacing between each point.
def graphprep(list):
	linepoint = GRAPH_X
	jump = GRAPH_WIDTH / SAMPLE_SIZE
	newlist = []

	for i in range(SAMPLE_SIZE):
		# if not enough data
		if i > (len(list) - 1):
			# make the data show as 0 scale. (y coord 110)
			item = 110
		else:
			# otherwise just keep plotting the data provided.
			item = list[i]

		newlist.append((linepoint,item))
		linepoint = linepoint + jump

	return newlist

# graphit is a quick tool to help prepare graphs by changing their data from
# true values into scaled values for their pixel position on screen.
def graphit(data, auto = True):

	#grabs our databuffer object.
	buffer = data

	prep = []

	for i in data:

		if configure.auto[0]:
			# autoscales the data.
			if len(buffer) > 0:
				data_high = max(buffer)
				data_low = min(buffer)
			else:
				data_high = 0
				data_low = 0
		
			# scales the data on the y axis.
			prep.append(numpy.interp(i, (data_low, data_high), (GRAPH_Y2, GRAPH_Y)))
		else:
			prep.append(numpy.interp(i, (data_low, data_high), (GRAPH_Y2, GRAPH_Y))) # <----need to fix total scale.


	return graphprep(prep)

# the following function runs the startup animation
def startUp(surface):
	#This function draws the opening splash screen for the program that provides the user with basic information.

	#Sets a black screen ready for our UI elements
	surface.fill(black)

	#Instantiates the components of the scene
	insignia = Image()
	secTitle = Label()
	secblurb = Label()

	logoposx = (resolution[0]/2) - (98/2)

	#sets out UI objects with the appropriate data
	insignia.update(pioslogo, logoposx, 37)

	secTitle.update("PicorderOS " + configure.version,19,37,210,titleFont,blue)
	secTitle.center(resolution[0],20,0,190)
	secblurb.update(configure.boot_message,15,37,210,titleFont,blue)
	secblurb.center(resolution[0],20,0,210)

	#writes our objects to the buffer
	insignia.draw(surface)

	#checks time
	timenow = time.time()

	#if (timenow - timeSinceStart) > 1:
	secTitle.draw(surface)
	secblurb.draw(surface)

	pygame.display.flip()
	elapsed = timenow - configure.boot_delay

	#waits for x seconds to elapse before returning the state that will take us to the sensor readout
	if elapsed > configure.boot_delay and configure.sensor_ready[0]:
	 return "graph"
	else:
	 return "startup"

# the following function displays version information about the program
def about(surface):

	#Sets a black screen ready for our UI elements
	surface.fill(black)

	#Instantiates the components of the scene
	insignia = Image()
	mainTitle = Label()
	version = Label()
	secTitle = Label()
	secblurb = Label()

	logoposx = (resolution[0]/2) - (226/2)

	insignia.update(pioslogo, logoposx, 30)
	version.update(configure.version,17,37,210,titleFont,blue)
	version.center(resolution[0],20,0,90)

	secTitle.update(configure.author,17,37,210,titleFont,blue)
	secTitle.center(resolution[0],20,0,110)

	mainTitle.update("Written in Python",17,37,210,titleFont,blue)
	mainTitle.center(resolution[0],20,0,125)
	secblurb.update("Developed By directive0",15,37,210,titleFont,blue)
	secblurb.center(resolution[0],20,0,210)

	#writes our objects to the buffer
	insignia.draw(surface)


	version.draw(surface)
	mainTitle.draw(surface)
	secTitle.draw(surface)
	secblurb.draw(surface)

	pygame.display.flip()

class Settings_Panel(object):

	def __init__(self,surface):

		self.left_margin = 37

		self.index = 0
		self.surface = surface
		self.labelstart = 47
		self.labeljump = 21

		self.titlelabel = Label()
		self.titlelabel.update("Control Panel",25,17,15,titleFont,orange)

		self.option1 = SelectableLabel(configure.sensor1, special = 1)
		self.option1.update("Graph 1: ",20,self.left_margin,47,titleFont,themes[configure.theme[0]][0])

		self.option2 = SelectableLabel(configure.sensor2, special = 1)
		self.option2.update("Graph 2: ", 20, self.left_margin, self.labelstart + self.labeljump, titleFont, themes[configure.theme[0]][1])

		self.option3 = SelectableLabel(configure.sensor3, special = 1)
		self.option3.update("Graph 3: ", 20, self.left_margin, self.labelstart + (self.labeljump*2), titleFont, themes[configure.theme[0]][2])

		self.option4 = SelectableLabel(configure.theme, special = 2)
		self.option4.update("Theme:  ", 20, self.left_margin, self.labelstart + (self.labeljump*3), titleFont, orange)

		self.option5 = SelectableLabel(configure.auto)
		self.option5.update("Auto Range: ", 20, self.left_margin, self.labelstart + (self.labeljump*4), titleFont, orange)

		self.option6 = SelectableLabel(configure.leds)
		self.option6.update("LEDs: ", 20, self.left_margin, self.labelstart + (self.labeljump*5), titleFont, orange)

		self.option7 = SelectableLabel(configure.moire)
		self.option7.update("Moire: ", 20, self.left_margin, self.labelstart + (self.labeljump*6), titleFont, orange)

		self.options = [self.option1, self.option2, self.option3, self.option4, self.option5, self.option6, self.option7]
		
		self.events = Events([1,2,"last"],"settings")

	def colour_update(self):
		self.option1.update("Graph 1: ",20,self.left_margin,47,titleFont,themes[configure.theme[0]][0])
		self.option2.update("Graph 2: ", 20, self.left_margin, 68, titleFont, themes[configure.theme[0]][1])
		self.option3.update("Graph 3: ", 20, self.left_margin, 90, titleFont, themes[configure.theme[0]][2])
		self.option4.update("Theme:  ", 20, self.left_margin, 111, titleFont, orange)
		self.option5.update("Auto Range: ", 20, self.left_margin, 132, titleFont, orange)
		self.option6.update("LEDs: ", 20, self.left_margin, 154, titleFont, orange)
		self.option7.update("Moire: ", 20, self.left_margin, 176, titleFont, orange)

	def frame(self):

		self.surface.fill(black)

		self.titlelabel.draw(self.surface)

		for i in range(len(self.options)):
			if i == self.index:

				self.options[i].selected = True
			else:
				self.options[i].selected = False

			self.options[i].draw(self.surface)

		self.colour_update()

		# draws UI to frame buffer
		pygame.display.flip()

		# Uses the event class to set the status and check for state changes
		result,payload  = self.events.check()

		if payload == 1:
			self.index += 1
			if self.index > (len(self.options) - 1):
				self.index = 0
		elif payload == 2:
			self.options[self.index].toggle()

		return result

class Master_Systems_Display(object):

	def __init__(self, surface):

		self.surface = surface
		self.events = Events([1,"wifi","settings"],"msd")

		self.list = Label_List()
		
		# grabs the RPI model info
		if not configure.pc:
			text = os.popen("cat /proc/device-tree/model").readline()
			self.model = str(text.rstrip("\x00")).replace("Raspberry Pi","Raspi")
		else:
			self.model = "Unknown CPU"

	def frame(self):

		# Uses the event class to set the status and check for state changes
		status,payload  = self.events.check()

		if payload == 1:
			self.selection += 1
			if self.selection > 3:
				self.selection = 0

		#Sets a black screen ready for our UI elements
		self.surface.fill(black)

		# pulls data from the modulated_em.py
		wifi = "SSID: " + os.popen("iwgetid").readline()

		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		try:
			s.connect(("8.8.8.8", 80))
			IPAddr = s.getsockname()[0]
		except:
			IPAddr = "No IP Found"
		
		ip_str = "IP:  " + IPAddr
		host_str = "Name:  " + socket.gethostname()
		sense_ready = "Sensors Avl:  " + str(len(configure.sensor_info))
		cpu_name = "CPU:  " + self.model
		PLARS_size, PLARS_em_size = plars.get_plars_size()
		db_size = "PLARS Size:  " + str(PLARS_size)
		em_size = "PLARS EM Size:  " + str(PLARS_em_size)

		itemlist = [wifi, ip_str, host_str, sense_ready, cpu_name, db_size, em_size]

		self.list.draw(itemlist,self.surface)

		#draws UI to frame buffer
		pygame.display.update()

		return status

# The graph screen object is a self contained screen that is fed the surface
# and the sensor at the current moment and draws a frame when called.
class Graph_Screen(object):

	# Draws three graphs in a grid and three corresponding labels.

	def __init__(self,surface):


		# for long presses
		self.input_timer = timer()
		self.presstime = 5
		self.longpressed = [False, False, False]

		# State variable
		self.status = "graph"
		self.selection = 0

		# An fps controller
		self.drawinterval = timer()

		# Sample rate controller
		self.senseinterval = 0

		# Pygame drawing surface.
		self.surface = surface

		# Draws Background gridplane
		self.graphback = Image()
		self.graphback.update(backgraph, 0, 0)


		# Instantiates 3 labels for our readout
		self.a_label = Label()
		self.b_label = Label()
		self.c_label = Label()
		self.intervallabel = Label()
		self.intervallabelshadow = Label()

		self.focus_label = Label()

		self.slider1 = Image()
		self.slider2 = Image()
		self.slider3 = Image()

		self.data_a = graphlist()
		self.data_b = graphlist()
		self.data_c = graphlist()

		self.graphon1 = True
		self.graphon2 = True
		self.graphon3 = True

		self.visibility = [self.graphon1,self.graphon2,self.graphon3]

		self.events = Events([1,"slider","settings"],"graph")

		self.margin = 16




	def frame(self):

		# Uses the event class to set the status and check for state changes
		status,payload  = self.events.check()

		if payload == 1:
			self.selection += 1
			if self.selection > 3:
				self.selection = 0

		# grabs sensor info from settings for quick reference and display
		sense_info_a = configure.sensor_info[configure.sensors[0][0]]
		sense_info_b = configure.sensor_info[configure.sensors[1][0]]
		sense_info_c = configure.sensor_info[configure.sensors[2][0]]


		#Sets a black screen ready for our UI elements
		self.surface.fill(black)

		#draws Background gridplane
		self.graphback.draw(self.surface)

		# resolves the key items (dsc and dev) for the targeted sensor, for plars to use.
		# creates a "senseslice"; an up to date data fragment for each configured sensor

		senseslice = []
		data_a = []
		data_b = []
		data_c = []
		datas = [data_a,data_b,data_c]

		#gathers the data for all three sensors currently selected for each slot.
		for i in range(3):

			# determines the sensor keys for each of the three main sensors
			this_index = int(configure.sensors[i][0])

			# grabs the sensor metadata for display
			dsc,dev,sym,maxi,mini = configure.sensor_info[this_index]

			# grabs sensor data
			datas[i] = plars.get_recent(dsc,dev,num = SAMPLE_SIZE)[0]


			# if data capture has failed, replace with 47 for diagnostic
			if len(datas[i]) == 0:
				datas[i] = [47]

			item = datas[i]

			senseslice.append([item[-1], dsc, dev, sym, mini, maxi])


		#converts data to float

		a_newest = float(senseslice[0][0])
		b_newest = float(senseslice[1][0])
		c_newest = float(senseslice[2][0])
		newests = [a_newest,b_newest,c_newest]





		a_content = "{:.2f}".format(a_newest)
		a_color = themes[configure.theme[0]][0]
		self.a_label.update(a_content + senseslice[0][3],27,marginleft,205,titleFont,a_color)


		b_content = "{:.2f}".format(b_newest)
		b_color = themes[configure.theme[0]][1]
		self.b_label.update( b_content + senseslice[1][3],27,114,205,titleFont,b_color)
		self.b_label.center(resolution[0],27,0,205)


		c_content = "{:.2f}".format(c_newest)
		c_color = themes[configure.theme[0]][2]

		self.c_label.update(c_content + senseslice[2][3],27,marginright,205,titleFont,c_color)
		self.c_label.r_align(320 - marginright ,205)
		contents = [a_content,b_content,c_content]

		labels = [self.a_label,self.b_label,self.c_label]



		interx= (22)
		intery= (21)


		# updates the data storage object and retrieves a fresh graph ready to store the positions of each segment for the line drawing
		a_cords = graphit(datas[0])
		b_cords = graphit(datas[1])
		c_cords = graphit(datas[2])
		cords = [a_cords,b_cords,c_cords]

		if not configure.auto[0]:

			# map the data from its 
			a_slide = translate(a_newest, senseslice[0][4], senseslice[0][5], GRAPH_Y2, GRAPH_Y)
			b_slide = translate(b_newest, senseslice[1][2], senseslice[1][5], GRAPH_Y2, GRAPH_Y)
			c_slide = translate(c_newest, senseslice[2][2], senseslice[2][5], GRAPH_Y2, GRAPH_Y)

			self.slider1.update(sliderb, 283, a_slide)
			self.slider2.update(sliderb, 283, b_slide)
			self.slider3.update(sliderb, 283, c_slide)
		else:
			# find the most recent coordinates and y for that coord  
			self.slider1.update(sliderb, 283, a_cords[-1][1]-10)
			self.slider2.update(sliderb, 283, b_cords[-1][1]-10)
			self.slider3.update(sliderb, 283, c_cords[-1][1]-10)

		sliders = [self.slider1,self.slider2,self.slider3]

		if self.selection == 0:

			# draw the lines
			pygame.draw.lines(self.surface, c_color, False, c_cords, 2)
			pygame.draw.lines(self.surface, b_color, False, b_cords, 2)
			pygame.draw.lines(self.surface, a_color, False, a_cords, 2)

			# draw the sliders
			self.slider3.draw(self.surface)
			self.slider2.draw(self.surface)
			self.slider1.draw(self.surface)


			# draws the labels
			self.a_label.draw(self.surface)
			self.b_label.draw(self.surface)
			self.c_label.draw(self.surface)



		# this checks if we are viewing a sensor individually and graphing it alone.
		# if individually:
		if self.selection != 0:
			# we make a variable carrying the index of the currently selected item.
			this = self.selection - 1

			# we grab information for it.
			sym, dsc = senseslice[this][3],senseslice[this][1]

			# we collect its default colour based off our theme
			this_color = themes[configure.theme[0]][this]

			focus_cords = cords[this]
			focus_slider = sliders[this]
			pygame.draw.lines(self.surface, this_color, False, focus_cords, 2)
			focus_slider.draw(self.surface)

			self.focus_label.update(dsc,30,283,205,titleFont,this_color)
			self.focus_label.r_align(320 - marginright ,205)
			self.focus_label.draw(self.surface)

			self.a_label.update(contents[this] + sym,30,15,205,titleFont,this_color)
			self.a_label.draw(self.surface)

		# draws the interval label (indicates refresh rate)
		#self.intervallabelshadow.draw(self.surface)
		#self.intervallabel.draw(self.surface)

		#draws UI to frame buffer
		pygame.display.update()


		return status

	def visible(self,item,option):
		self.visibility[item] = option

# Video screen written by scifi.radio from the mycorder discord
class Video_Playback(object):
	def __init__(self,surface):
		self.status = "video"
		self.surface = surface
		self.videobg = Image()
		self.videobg.update(videobg, 0,0)
		self.running = False
		self.paused = False
		self.clock = pygame.time.Clock()
		self.events = Events([1,2,3],"video")


	def frame(self):
		if not self.running:
			self.running = True	
			self.clip = Video('assets/ekmd.mov')
			self.clip.set_size(resolution)
			pygame.mixer.quit()

		self.clock.tick(60)
		
		self.status = "video"
		# Uses the event class to set the status and check for state changes
		status,payload  = self.events.check()

		if payload == 1:
			self.status =  "video"
			self.clip.toggle_pause()
			if self.paused:
				self.paused = False
				print("Resume")
			else:
				self.paused = True
				print("Paused")
			# We would use this to set mode_d instead of
			# toggling a pause were we to get a mode_d
			configure.eventready[0] = False
			return self.status

		if payload == 2:
			self.status = "msd"
			configure.eventready[0] = False
			self.running = False
			self.clip.close()
			return self.status

		if payload == 3:
			configure.last_status[0] = "video"
			print("Button 3")
			self.status = "settings"
			self.running = False
			configure.eventready[0] = False

		self.clock.tick(60)


		#draws Background gridplane
		self.videobg.draw(self.surface)
		self.clip.draw(self.surface,(0,0), force_draw=FALSE)
		#draws UI to frame buffer
		pygame.display.update()
		if not self.clip.active:
			self.clip.restart()

		return self.status

class Slider_Screen(object):
	def __init__(self, surface):
		# This function draws the main 3-slider interface, modelled after McCoy's tricorder in "Plato's Stepchildren". It displays temperature, humidity and pressure.
		self.surface = surface

		#checks time
		self.timenow = time.time()

		# Slide Coordinates
		self.slider_ylow = 204
		self.slider_yhigh = 15

		# Sets a black screen ready for our UI elements
		self.surface.fill(black)

		# Instantiates the components of the scene
		self.a_label = Label()
		self.b_label = Label()
		self.c_label = Label()
		self.backPlane = Image()

		self.slider1 = Image()
		self.slider2 = Image()
		self.slider3 = Image()
		self.status = "graph"
		self.input = input

		self.events = Events([1,"thermal","settings"],"slider")

	def frame(self):
		
		# Uses the event class to set the status and check for state changes
		status,payload  = self.events.check()
		
		senseslice = []

		for i in range(3):

			# determines the sensor keys for each of the three main sensors
			this_index = int(configure.sensors[i][0])

			dsc,dev,sym,mini,maxi = configure.sensor_info[this_index]

			item = plars.get_recent(dsc,dev,num = 1)[0]

			if len(item) > 0:
				senseslice.append([item[0], sym, mini, maxi])
			else:
				senseslice.append([47, sym, mini, maxi])

		#converts data to float
		a_newest = float(senseslice[0][0])
		b_newest = float(senseslice[1][0])
		c_newest = float(senseslice[2][0])
		newests = [a_newest,b_newest,c_newest]

		# data labels
		a_content = str(int(a_newest))
		self.a_label.update(a_content + senseslice[0][1],19,47,215,titleFont,yellow)
		b_content = str(int(b_newest))
		self.b_label.update(b_content + senseslice[1][1],19,152,215,titleFont,yellow)
		c_content = str(int(c_newest))
		self.c_label.update(c_content + senseslice[2][1],19,254,215,titleFont,yellow)

		# slider data adjustment
		# the routine takes the raw sensor data and converts it to screen coordinates to move the sliders
		# determines the sensor keys for each of the three main sensors
		a_slide = translate(senseslice[0][0], senseslice[0][2], senseslice[0][3], self.slider_ylow, self.slider_yhigh)
		b_slide = translate(senseslice[1][0], senseslice[1][2], senseslice[1][3], self.slider_ylow, self.slider_yhigh)
		c_slide = translate(senseslice[2][0], senseslice[2][2], senseslice[2][3], self.slider_ylow, self.slider_yhigh)

		# Updates our UI objects with data parsed from sensor/weather
		self.backPlane.update(backplane, 0, 0)
		self.slider1.update(slidera, 70, a_slide)
		self.slider2.update(slidera, 172, b_slide)
		self.slider3.update(slidera, 276, c_slide)

		# draws the graphic UI to the buffer
		self.backPlane.draw(self.surface)
		self.slider1.draw(self.surface)
		self.slider2.draw(self.surface)
		self.slider3.draw(self.surface)

		# draws the labels to the buffer
		self.a_label.draw(self.surface)
		self.b_label.draw(self.surface)
		self.c_label.draw(self.surface)

		pygame.display.update()
		# draws UI to frame buffer
		return status

class Wifi_Screen(object):

	def __init__(self, surface):
		self.surface = surface
		self.events = Events([1,"graph","settings"],"wifi")

		self.list = Label_List()

	def frequency_map(self):
		# returns the data necessary for freq_intensity map with EM.
		# displays each SSID as a line segment. Its position along the x is
		# determined by frequency. Its height by its signal strength.

		# value to store visualization envelope
		vizX1 = 20
		vizY1 = 36
		vizX2 = 157
		vizY2 = 77

		ballsize = 6

		focus_freq = 0
		overlapping = []

		# change Background
		#draw.rectangle((0,0,320,240),(0,0,0))
		#draw._image = self.burgerfull	





		#grab EM list
		unsorted_em_list = plars.get_recent_em_list()


		if len(unsorted_em_list) > 0:

			# sort it so strongest is first.
			em_list = sorted(unsorted_em_list, key=itemgetter(1), reverse = True)

			# create a list to hold just the info we need for the screen.
			items_list = []
			strength_list = []

			for ssid in em_list:
				strength = ssid[1]
				strength_list.append(strength)

			#filter info into items_list
			for ssid in em_list:
				name = str(ssid[0])
				strength = ssid[1]
				frequency = ssid[3]
				#frequency = float(frequency.replace(' GHz', ''))

				# determing x coordinate
				screenpos = numpy.interp(frequency,(2.412, 2.462),(vizX1 + ballsize, vizX2 - ballsize))

				# determine y coordinate
				lineheight = numpy.interp(strength, (min(strength_list), max(strength_list)), (vizY2 - ballsize, vizY1 + ballsize))

				# package into list
				this_ssid = (name,screenpos,lineheight,strength,frequency)
				items_list.append(this_ssid)
				


			# draw lines and balls
			#for each item in item_list, in reverse order
			for index, item in reversed(list(enumerate(items_list))):

				# determine dot coordinates.
				cords = ((item[1],vizY2),(item[1],item[2]))
				radius = ballsize/2
				x1 = cords[1][0] - (radius)
				y1 = cords[1][1] - (radius)
				x2 = cords[1][0] + (radius)
				y2 = cords[1][1] + (radius)

				# if this is the strongest signal draw labels and change colour.
				if index == 0:
					pygame.draw.line(self.surface,white,cords[0],cords[1],width = 1)
					pygame.draw.ellipse(self.surface,white,[x1,y1,ballsize,ballsize])


					name = item[0]
					trunc_name = name[:16] + (name[16:] and '..')

					focus_freq = item[4]


					# draw the strongest signals name
					#self.signal_name_sm.push(20,80,draw,string = trunc_name)

					# put strength at lower left
					strength_string = str(item[3]) + " DB"
					#self.signal_strength_sm.push(19,114,draw,string = strength_string)

					# put frequency at lower right
					#self.signal_frequency_sm.string = str(focus_freq) + " GHZ" + ", " + strength_string
					#self.signal_frequency_sm.r_align(155,82,draw)


				# otherwise just draw the line and dot in the usual color
				else:
					pygame.draw.line(self.surface,blue,cords[0],cords[1],width = 1)
					pygame.draw.ellipse(self.surface,blue,[x1,y1,ballsize,ballsize])

		#draw round rect background
		#pygame.draw.rect(self.surface,white,[vizX1,vizY1,vizX2,vizY2])


		label_list = []

		for item in items_list:
			if item[4] == focus_freq:
				overlapping.append(item)




		if len(overlapping) > 1:
			del overlapping[0]
			for ssid in overlapping:
				name = ssid[0]
				strength = ssid[1]
				frequency = ssid[4]

				# package into list
				this_ssid = (name,strength)
				label_list.append(this_ssid)

			#self.overlap_list.colour = lcars_pink
		else:
			thislist = sorted(unsorted_em_list, key=itemgetter(1), reverse = True)
			del thislist[0]
			for ssid in thislist:
				name = ssid[0]
				strength = ssid[1]
				frequency = ssid[4]

				# package into list
				this_ssid = (name,strength)
				label_list.append(this_ssid)
			#$self.overlap_list.colour = lcars_blue

		#self.overlap_list.update(label_list,draw)

	def frame(self):
		# Uses the event class to set the status and check for state changes
		status,payload  = self.events.check()

		if payload == 1:
			self.selection += 1
			if self.selection > 3:
				self.selection = 0
				
		#Sets a black screen ready for our UI elements
		self.surface.fill(black)


		# list to hold the data labels
		list_for_labels = []

		# grab EM list
		em_list = plars.get_recent_em_list()

		if len(em_list) > 0:
			#sort it so strongest is first
			sorted_em_list = sorted(em_list, key=itemgetter(1), reverse = True)

			# prepare a list of the data received for display
			for ssid in sorted_em_list:
				name = str(ssid[0])
				strength = str(ssid[1])

				label = strength + " dB • " + name

				list_for_labels.append(label)

			self.list.draw(list_for_labels,self.surface)
		else:
			self.list.draw(["No SSIDS Detected OR PLARS Error!"],self.surface)
		
		self.frequency_map()

		#draws UI to frame buffer
		pygame.display.update()


		return status

# The thermal screen is fed the surface and taking the thermal array  
# draws an interpolated rendering of the data for display
# - shows the thermal output
# - displays the high low and xbar of the field
# - switches the display to full screen and back.
class Thermal_Screen(object):


	def __init__(self,surface):
		
		self.events = Events([1,"video","settings"],"thermal")

		# for long presses
		self.input_timer = timer()
		self.presstime = 5
		self.longpressed = [False, False, False]

		# State variable
		self.selection = 0

		# An fps controller
		self.drawinterval = timer()

		# Sample rate controller

		# Pygame drawing surface.
		self.surface = surface

		# Draws Background gridplane
		self.graphback = Image()
		self.graphback.update(backgraph, 0, 0)


		# Instantiates 3 labels for our readout
		self.high_label = Label()
		self.low_label = Label()
		self.xbar_label = Label()

		self.high = 0
		self.low = 0
		self.average = 0

		self.intervallabel = Label()
		self.intervallabelshadow = Label()

		self.t_grid = ThermalGrid(16,15,270,180)
		self.t_grid_full = ThermalGrid(0,0,320,240)

		self.symbol = "°c"


	def frame(self):

		# Uses the event class to set the status and check for state changes
		status,payload  = self.events.check()

		if payload == 1:
			self.selection += 1
			if self.selection > 1:
				self.selection = 0


		#Sets a black screen ready for our UI elements
		self.surface.fill(black)

		if self.selection == 0:
			self.average,self.high,self.low = self.t_grid.update()
			a_color = themes[configure.theme[0]][0]
			self.high_label.update(str(self.high) + self.symbol, 27,marginleft,205,titleFont,a_color)

			b_color = themes[configure.theme[0]][1]
			self.xbar_label.update(str(self.average) + self.symbol, 27,114,205,titleFont,b_color)
			self.xbar_label.center(resolution[0],27,0,205)

			c_color = themes[configure.theme[0]][2]
			self.low_label.update(str(self.low) + self.symbol,27,marginright,205,titleFont,c_color)
			self.low_label.r_align(320 - marginright ,205)
			
			self.high_label.draw(self.surface)
			self.xbar_label.draw(self.surface)
			self.low_label.draw(self.surface)

		if self.selection == 1:
			self.average,self.high,self.low = self.t_grid_full.update()


		if self.selection == 0:
			self.t_grid.push(self.surface)
		elif self.selection == 1:
			self.t_grid_full.push(self.surface)

		#draws UI to frame buffer
		pygame.display.update()


		return status

	def visible(self,item,option):
		self.visibility[item] = option

# A basic screen object. Is given parameters and displays them on a number of preset panels
class Screen(object):

	def __init__(self):
		screenSize = resolution

		# The following commands initiate a pygame environment.
		pygame.init()
		pygame.font.init()
		pygame.display.set_caption('PicorderOS')

		# I forget, probably colour depth?
		smodes = pygame.display.list_modes(def_modes)

		# instantiate a pygame display with the name "surface",

		if configure.pc:
			#for development use this one (windowed mode)
			self.surface = pygame.display.set_mode(screenSize)
		else:
			# on the picorder use this option (Fullscreen).
			flags = pygame.FULLSCREEN | pygame.SCALED
			self.surface = pygame.display.set_mode(screenSize, flags, display=0)
			pygame.event.set_blocked(pygame.MOUSEMOTION)
			pygame.mouse.set_visible(False)


		self.timed = time.time()
		self.graphscreen = Graph_Screen(self.surface)
		self.videoplayback = Video_Playback(self.surface)
		self.slidescreen = Slider_Screen(self.surface)
		self.settings_screen = Settings_Panel(self.surface)
		self.thermalscreen = Thermal_Screen(self.surface)
		self.msdscreen = Master_Systems_Display(self.surface)
		self.wifiscreen = Wifi_Screen(self.surface)

		# carousel dict to hold the keys and defs for each state
		self.carousel = {"startup":self.startup_screen,
				   "graph":self.graph_screen,
				   "video":self.video_screen,
				   "slider":self.slider_screen,
				   "thermal":self.thermal_screen,
				   "wifi":self.wifi_screen,
				   "msd":self.msd_screen,
				   "settings":self.settings}


	def get_size(self):
		return SAMPLE_SIZE

	def startup_screen(self):
		status = startUp(self.surface)
		return status

	def about_screen(self):
		status = about()
		return status

	def slider_screen(self):
		status = self.slidescreen.frame()
		return status

	def graph_screen(self):
		status = self.graphscreen.frame()
		return status
	
	def thermal_screen(self):
		status = self.thermalscreen.frame()
		return status
	
	def wifi_screen(self):
		status = self.wifiscreen.frame()
		return status
	
	def msd_screen(self):
		status = self.msdscreen.frame()
		return status

	def video_screen(self):
		status = self.videoplayback.frame()
		return status

	def settings(self):
		status = self.settings_screen.frame()
		return status

	def run(self):
		butswitch()
		if configure.status[0] != 'quit':
			configure.status[0] = self.carousel[configure.status[0]]()
		else:
			pygame.quit()