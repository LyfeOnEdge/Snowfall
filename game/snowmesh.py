import random as rdm
from ursina import *
from .constants import *
from .timer_decorator import timer_dec
from .tools import get_chunk_id


class SnowLoader:
	def __init__(self, app, render_distance = 2):
		self.app = app
		self.render_distance = render_distance
		self.positions = []
		self.clouds = []
		self.open_clouds = []
		self.new_clouds = []
		self.current_x = None
		self.current_z = None
		self.current_clouds = {}
		self.preload_snowchunk()

	@timer_dec
	def preload_snowchunk(self):
		cloud = snowcloud(size = (TILE_SCALE, SNOW_CEILING, TILE_SCALE), chunk_x = 0, chunk_z = 0)
		destroy(cloud)
		for j in range(3000): cloud.advance() #Let it run a while
		self.positions = copy(cloud.flakelist)
		for x in range(-1, 2):
			for z in range(-1, 2):
				self.load_new_cloud(x,z)

	def load_new_cloud(self, chunk_x, chunk_z):
		cloud = snowcloud(size = (TILE_SCALE, SNOW_CEILING, TILE_SCALE), chunk_x = chunk_x, chunk_z = chunk_z, positions = copy(self.positions))
		print(f"Loaded new cloud at {chunk_x} {chunk_z}")
		self.current_clouds.update({cloud.cloud_id:cloud})
		return cloud

	def update_snowclouds(self):
		self.current_x, self.current_z = self.app.terrainloader.current_x, self.app.terrainloader.current_z
		min_x, min_z = self.current_x - 2, self.current_z - 2
		max_x, max_z = self.current_x + 2, self.current_z + 2
		current_cloud_ids = []
		for x in range(min_x, max_x):
			for z in range(min_z, max_z):
				cid = f"{x}x{z}"
				current_cloud_ids.append(cid)
				if not cid in self.current_clouds.keys():
					self.load_new_cloud(x, z)

		for c in [c for c in self.current_clouds.keys()]:
			if not c in current_cloud_ids:
				self.current_clouds.pop(c).destroy()
		self.current_cloud_ids = current_cloud_ids

	def update(self):
		for c in self.current_clouds.keys():
			self.current_clouds[c].advance()


class snowcloud(Entity):
	# __slots__ = ["size", "pos", "rate", "x_drift", "x_drift_radius",\
	# 	"y_drift", "y_drift_radius", "z_drift", "z_drift_radius", 	\
	# 	"positions", "chunk_x", "chunk_z", "cloud_id", "flakelist",	\
	# 	"atomic", "frame", "width", "depth", "height",	\
	# 	"x", "y", "z"
	# 	]
	def __init__(self,
			size : tuple = (TILE_SCALE,0.5*TILE_SCALE,TILE_SCALE),
			pos : tuple = (0,0,0),
			rate : float = .05,
			x_drift = 5,
			x_drift_radius = 0.1,
			y_drift = 5,
			y_drift_radius = 0.1,
			z_drift = 5,
			z_drift_radius = 0.1,
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
		# self.flakes_a, self.flakes_b = [], [] #To store two sets of flake to alternate rendering between
		self.flakelist = []
		if positions: self.spawn_from_positions(positions)
		

		Entity.__init__(self, model=Mesh(mode='point', thickness=10))

		self.id = get_chunk_id(chunk_x, chunk_z)
		self.vertices = []
		self.objects = []
		self.active = True

	def spawn_from_positions(self, positions):
		offset_x = self.chunk_x * TILE_SCALE
		offset_z = self.chunk_z * TILE_SCALE
		for p in positions:
			x, y, z, g = p
			self.flakelist.append([x+offset_x,y,z+offset_z,g])
			
	def advance(self):
		X,Y,Z,GRAV = 0,1,2,3
		if self.flakelist:
			for f in list(self.flakelist):
				f[Y] -= f[GRAV]
				if f[Y] < -15: self.flakelist.remove(f)
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