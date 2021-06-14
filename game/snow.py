import random as rdm
from ursina import *
from .constants import *
from .timer_decorator import timer_dec

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
		self.current_cloud_ids = []
		self.preload_snowchunk()

	@timer_dec
	def preload_snowchunk(self):
		self.load_new_cloud(0,0)
		cloud = self.clouds[0]
		for j in range(2200): cloud.advance()
		positions = []
		for f in cloud.flakes_a:
			x,y,z = f.position
			positions.append((x,y,z))
		for f in cloud.flakes_b:
			x,y,z = f.position
			positions.append((x,y,z))
		self.positions = positions
		cloud.destroy()
		self.clouds = []
		current_cloud_ids = []
		for x in range(-1, 2):
			for z in range(-1, 2):
				self.load_new_cloud(x,z)

	def load_new_cloud(self, chunk_x, chunk_z):
		cloud = snowcloud(size = (TILE_SCALE, SNOW_CEILING, TILE_SCALE), chunk_x = chunk_x, chunk_z = chunk_z, positions = self.positions)
		self.clouds.append(cloud)
		print(f"Loaded new cloud at {cloud.cloud_id}")
		self.current_cloud_ids.append(cloud.cloud_id)

	def update_snowclouds(self):
		self.current_x, self.current_z = self.app.terrainloader.current_x, self.app.terrainloader.current_z
		min_x, min_z = self.current_x - 1, self.current_z - 1
		max_x, max_z = self.current_x + 2, self.current_z + 2
		current_cloud_ids = []
		for x in range(min_x, max_x):
			for z in range(min_z, max_z):
				cid = f"{x}x{z}"
				current_cloud_ids.append(cid)
				if not cid in self.current_cloud_ids:
					self.new_clouds.append((x,z))
		for c in list(self.clouds):
			if not c.cloud_id in current_cloud_ids:
				self.clouds.remove(c)
				self.open_clouds.append(c)
		self.current_cloud_ids = current_cloud_ids
		sys.stdout.flush()

		for c in self.open_clouds:
			print(len(self.open_clouds), len(self.new_clouds))
			x,z = self.new_clouds.pop()
			c.move(x,z)
			self.clouds.append(c)
		self.open_clouds = []

		return True

	def update(self):
		for c in self.clouds: c.advance()

class Snowflake(Entity):
	def __init__(self, *args, **kwargs):
		kw = {
			'model' : 'quad',
			# 'texture' : 'brick',
			'origin_y' : 0,
			'origin_x' : -0.5,
			'origin_z' : -0.5,
			'scale' : (0.1,0.1),
			'billboard' : True
		}
		kwargs.update(kw)
		Entity.__init__(self,*args, **kwargs)

		self.gravity = (1 + rdm.uniform(-CONST_GRAVITY_RANDOMNESS, CONST_GRAVITY_RANDOMNESS)) *  CONST_DEFAULT_GRAVITY

	def advance(self):
		self.y -= self.gravity

	def destroy(self):
		destroy(self)

class snowcloud:
	__slots__ = ["size", "pos", "rate", "x_drift", "x_drift_radius",\
		"y_drift", "y_drift_radius", "z_drift", "z_drift_radius", 	\
		"positions", "chunk_x", "chunk_z", "cloud_id", "flakes_a", 	\
		"flakes_b", "atomic", "frame", "width", "depth", "height",	\
		"x", "y", "z"
		]
	def __init__(self,
			size : tuple = (30,15,30),
			pos : tuple = (0,0,0),
			rate : float = 0.005,
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
		self.flakes_a, self.flakes_b = [], [] #To store two sets of flake to alternate rendering between
		self.atomic = 0 #For dividing the snow into two groups to reduce load
		self.frame = 0 #For counting which frame to advance, can be split into more groups in the future etc
		if positions: self.spawn_from_positions(positions)

	def spawn_from_positions(self, positions):
		offset_x = self.chunk_x * TILE_SCALE
		offset_z = self.chunk_z * TILE_SCALE
		for p in positions:
			x, y, z = p
			x += offset_x
			z += offset_z
			self.spawn_snowflake((x,y,z))
			
	def spawn_snowflake(self, p):
		s = Snowflake(position = p)
		if self.atomic % 2: self.flakes_a.append(s)
		else: self.flakes_b.append(s)
		self.atomic += 1

	def advance(self):
		if self.frame % 2:
			flakelist = self.flakes_a
		else:
			flakelist = self.flakes_b

		self.frame += 1
		if flakelist:
			for f in list(flakelist):
				f.advance()
				if f.y < 0:
					f.destroy()
					flakelist.remove(f)

		if flakelist: #Random Drift
			for i in range(self.x_drift): rdm.choice(flakelist).x += rdm.uniform(-self.x_drift_radius, self.x_drift_radius)
			for i in range(self.y_drift): rdm.choice(flakelist).y += rdm.uniform(-self.y_drift_radius, self.y_drift_radius)
			for i in range(self.z_drift): rdm.choice(flakelist).z += rdm.uniform(-self.z_drift_radius, self.z_drift_radius)

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
			self.spawn_snowflake((x + offset_x,y,z + offset_z))

	def destroy(self):
		for f in self.flakes_a: destroy(f)
		for f in self.flakes_b: destroy(f)

	def move(self, end_x, end_z):
		dx, dz = (end_x - self.chunk_x) * TILE_SCALE, (end_z - self.chunk_z) * TILE_SCALE
		for f in self.flakes_a:
			f.x += dx
			f.z += dz
		for f in self.flakes_b:
			f.x += dx
			f.z += dz
		self.chunk_x, self.chunk_x = end_x, end_z
		self.x, self.z = end_x * TILE_SCALE, end_z * TILE_SCALE
		self.cloud_id = f"{self.chunk_x}x{self.chunk_z}"