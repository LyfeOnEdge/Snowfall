import random as rdm
from ursina import *
from .constants import *
from .timer_decorator import timer_dec
from .tools import get_chunk_id

SNOWRENDERDISTANCE = 4.5 * TILE_SCALE

class snowcloud(Entity):
	# __slots__ = ["size", "pos", "rate", "x_drift", "x_drift_radius",\
	# 	"y_drift", "y_drift_radius", "z_drift", "z_drift_radius", 	\
	# 	"positions", "chunk_x", "chunk_z", "cloud_id", "flakelist",	\
	# 	"atomic", "frame", "width", "depth", "height",	\
	# 	"x", "y", "z"
	# 	]
	def __init__(self,
			size : tuple = (SNOWRENDERDISTANCE,TILE_SCALE,SNOWRENDERDISTANCE),
			pos : tuple = (0,0,0),
			# rate : float = .4,
			rate : float = .3,
			x_drift = 5,
			x_drift_radius = 0.3,
			y_drift = 5,
			y_drift_radius = 0.15,
			z_drift = 5,
			z_drift_radius = 0.3,
			positions = None,
			chunk_x = 0,
			chunk_z = 0,
	):
		self.chunk_x, self.chunk_z = chunk_x, chunk_z
		self.width, self.height, self.depth = size
		self.x, self.y, self.z = pos
		self.rate = rate
		self.x_drift, self.y_drift, self.z_drift = x_drift, y_drift, z_drift
		self.x_drift_radius, self.y_drift_radius, self.z_drift_radius = x_drift_radius, y_drift_radius, z_drift_radius
		self.cloud_id = f"{chunk_x}x{chunk_z}"
		self.offset_x = self.chunk_x * TILE_SCALE
		self.offset_z = self.chunk_z * TILE_SCALE
		self.flakelist = []
		if positions: self.spawn_from_positions(positions)
		
		Entity.__init__(self, model=Mesh(mode='point', thickness=6), position = (self.offset_x,0,self.offset_z))

		self.id = get_chunk_id(chunk_x, chunk_z)
		self.vertices = []
		self.objects = []
		self.active = True

	def spawn_from_positions(self, positions):
		for p in positions:
			x, y, z, g = p
			self.flakelist.append([x+self.offset_x,y,z+self.offset_z,g])

	def advance(self, chunk_x, chunk_z):
		X,Y,Z,GRAV = 0,1,2,3
		dx, dz = 0,0
		if not chunk_x == self.chunk_x or not chunk_z == self.chunk_z:
			dx, dz = chunk_x - self.chunk_x, chunk_z - self.chunk_z
		self.chunk_x, self.chunk_z = chunk_x, chunk_z
		self.offset_x = self.chunk_x * TILE_SCALE - 0.5 * SNOWRENDERDISTANCE
		self.offset_z = self.chunk_z * TILE_SCALE - 0.5 * SNOWRENDERDISTANCE
		if self.flakelist:
			for f in list(self.flakelist):
				f[Y] -= f[GRAV]
				if f[Y] < -0.5*self.height: self.flakelist.remove(f)
				if f[X] < self.offset_x: 						f[X] = f[X] + SNOWRENDERDISTANCE
				elif f[X] > self.offset_x + SNOWRENDERDISTANCE: f[X] = f[X] - SNOWRENDERDISTANCE
				if f[Z] < self.offset_z: 						f[Z] = f[Z] + SNOWRENDERDISTANCE
				elif f[Z] > self.offset_z + SNOWRENDERDISTANCE: f[Z] = f[Z] - SNOWRENDERDISTANCE




		#Random Drift
		if self.flakelist:
			for i in range(self.x_drift):
				f = rdm.choice(self.flakelist)
				f[X] += rdm.uniform(-self.x_drift_radius, self.x_drift_radius) * 10

			for i in range(self.y_drift):
				f = rdm.choice(self.flakelist)
				f[Y] += rdm.uniform(-self.y_drift_radius, self.y_drift_radius) * 10

			for i in range(self.z_drift):
				f = rdm.choice(self.flakelist)
				f[Z] += rdm.uniform(-self.z_drift_radius, self.z_drift_radius) * 10

		#Spawn Drops
		spawn = 0
		if self.rate > 1.0:
			spawn = int(self.rate)
			if self.rate - spawn > rdm.uniform(0.0, 1.0): 
				spawn += 1
		else:
			if self.rate > rdm.uniform(0.0, 1.0):
				spawn = 1
		offset_x = self.chunk_x * TILE_SCALE
		offset_z = self.chunk_z * TILE_SCALE
		for _ in range(spawn):
			x = rdm.uniform(0, self.width)
			y = self.height
			z = rdm.uniform(0, self.depth)
			#Snow pieces fall at different rates
			grav = (1 + rdm.uniform(-CONST_GRAVITY_RANDOMNESS, CONST_GRAVITY_RANDOMNESS)) *  CONST_DEFAULT_GRAVITY
			self.flakelist.append([x+offset_x,y,z+offset_z,grav])
		self.model.vertices = [Vec3(x,y,z) for x,y,z,_ in self.flakelist]
		self.model.generate()

	def destroy(self):
		destroy(self)