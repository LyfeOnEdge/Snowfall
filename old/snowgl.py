import random as rdm
from datetime import datetime

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from constants import *

from snowgen import snowcloud

def rendercloud(cloud):
	cloud.advance()
	glBegin(GL_POINTS)
	glColor3f(1.0, 1.0, 1.0)
	for f in cloud.flakes: glVertex3f(f.x + cloud.x, f.y + cloud.y, f.z + cloud.z)
	glEnd()

def renderplane(plane):
	glBegin(GL_QUADS);
	glVertex3f(plane.x, plane.y, plane.z)
	glVertex3f(plane.x+plane.width, plane.y, plane.z)
	glVertex3f(plane.x+plane.width, plane.y, plane.z+plane.depth)
	glVertex3f(plane.x, plane.y, plane.z + plane.depth)
	glEnd()

class renderer:
	def __init__(self):
		self.snowclouds = []
		self.planes = []

	def rendertask(self):
		self.clear()
		render_grid()
		for c in self.snowclouds: rendercloud(c)
		for p in self.planes: renderplane(p)
		
	def clear(self):
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
	
	def spawn_snowcloud(self):
		cloud = snowcloud()
		self.snowclouds.append(cloud)

	def spawn_plane(self):
		p = plane((-20,0,-20), (40, 40))
		self.planes.append(p)


class plane:
	def __init__(self, pos, size):
		self.x, self.y, self.z = pos
		self.width, self.depth = size

# class angled_plane:
# 	def __init__(self, v1, v2, v3, v4):
# 		self.verticies = (v1,v2,v3,v4)

class snowflake:
	def __init__(self, pos, color = CONST_DEFAULT_COLOR, gravity = CONST_DEFAULT_GRAVITY):
		self.x, self.y, self.z = pos
		self.color = CONST_DEFAULT_COLOR
		self.gravity = CONST_DEFAULT_GRAVITY + rdm.uniform(-CONST_GRAVITY_RANDOMNESS, CONST_GRAVITY_RANDOMNESS)
		self.length = CONST_DEFAULT_SNOWFLAKE_LENGTH

	def advance(self): self.y -= self.gravity

class snowcloud:
	def __init__(self,
			size : tuple = (200,100,200),
			pos : tuple = (0,0,0),
			rate : int = 2,
			x_drift = 15,
			x_drift_radius = 0.25,
			y_drift = 10,
			y_drift_radius = 0.25,
			z_drift = 15,
			z_drift_radius = 0.25,
	):
		self.width, self.height, self.depth = size
		self.x, self.y, self.z = pos
		self.halfwidth = 0.5 * self.width
		self.halfheight = 0.5 * self.height
		self.halfdepth = 0.5 * self.depth
		self.rate = rate
		self.x_drift = x_drift
		self.x_drift_radius= 4
		self.y_drift = y_drift
		self.y_drift_radius = y_drift_radius
		self.z_drift = z_drift
		self.z_drift_radius = z_drift_radius

		self.flakes = []

	def advance(self):
		if self.flakes:
			for f in list(self.flakes):
				f.advance()
				if f.y < 0:
					self.flakes.remove(f)

			#Random Drift
			for i in range(self.x_drift): rdm.choice(self.flakes).x += rdm.uniform(-self.x_drift_radius, self.x_drift_radius)
			for i in range(self.y_drift): rdm.choice(self.flakes).y += rdm.uniform(-self.y_drift_radius, self.y_drift_radius)
			for i in range(self.z_drift): rdm.choice(self.flakes).z += rdm.uniform(-self.z_drift_radius, self.z_drift_radius)

		#Spawn Drops
		for _ in range(rdm.randrange(0.0, 2.0*self.rate)):
			x = rdm.uniform(-self.halfwidth, self.halfwidth)
			y = self.height
			z = rdm.uniform(-self.halfdepth, self.halfdepth)
			s = snowflake((x,y,z))
			self.flakes.append(s)

def render_grid():
	glBegin(GL_LINES)
	#Grid length
	gridlen = 100
	
	#Draw X
	for i in range(-gridlen, gridlen):
		if i < 0:
			glColor3f(0.5, 0.0, 0.0)
		else:	
			glColor3f(1.0, 0.0, 0.0)
		glVertex3f(0.0,0.0,0.0)
		glVertex3f(float(i),0.0,0.0)

	#Draw Y
	for i in range(-gridlen, gridlen):
		if i < 0:
			glColor3f(0.0, 0.5, 0.0)
		else:	
			glColor3f(0.0, 1.0, 0.0)
		glVertex3f(0.0,0.0,0.0)
		glVertex3f(0.0,float(i),0.0)

	#Draw Z
	for i in range(-gridlen, gridlen):
		if i < 0:
			glColor3f(0.0, 0.0, 0.5)
		else:	
			glColor3f(0.0, 0.0, 1.0)
		glVertex3f(0.0,0.0,0.0)
		glVertex3f(0.0,0.0,float(i))

	glEnd()
	


def main():
	tstart = datetime.now()

	pygame.init()
	display = (500,500)
	pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

	# cloud = snowcloud()

	glEnable(GL_POINT_SMOOTH)

	gluPerspective(45, (display[0]/display[1]), 5, 500)

	glTranslatef(1, -20, -300) #Move scene back 
	glPointSize(0.25)

	ren = renderer()
	ren.spawn_snowcloud()
	ren.spawn_plane()

	clock = pygame.time.Clock()
	frame = 0
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

		# dt = (datetime.now() - tstart).total_seconds() #Calc delta since start
		if frame > 300 and frame < 480: glTranslatef(0,0,-1) #Slow zoom out 5-7.5 seconds in
		if frame > 480 and frame < 570: glRotatef(0.5, 0.1, 0.0, 0.0)
		if frame > 600: glRotatef(0.5, 0.0, 0.1, 0.0) #Final rotation pattern seconds
		

		

		ren.clear()
		ren.rendertask()
		pygame.display.flip()

		# clock.tick(60)
		frame += 1

main()