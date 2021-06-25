import sys, json, random
from ursina import *
from opensimplex import OpenSimplex
from numpy import asarray, linspace, uint8

from .constants import *
from .entities import Branch, Tree, Exit, Rock, Mushroom, LivingTree, SmallMushroom, SharpRock, Stump, MushroomCircle, Log, StickBall
from .tools import get_chunk_numerals_by_position, get_chunk_id





def get_spawn_from_map(m, val):
	for k in m.keys():
		if (val / SPAWN_MULT) < k: return m[k]

def get_biome_from_biomemap_value(val):
	for k in BIOME_MAP.keys():
		if val < k:
			return BIOME_MAP[k], k
	return BIOME_MAP[BARREN], BARREN


class TerrainChunk(Entity):
	def __init__(self, app, seed, chunk_x, chunk_z, heightmap, spawnmap, biomemap):
		self.chunk_x = chunk_x
		self.chunk_z = chunk_z
		self.chunk_id = get_chunk_id(chunk_x, chunk_z)
		self.seed = seed
		self.vertices, self.triangles = list(), list()
		self.uvs = list()
		self.normals = list()
		self.objects = list()
		self.spawnmap = spawnmap
		self.active = True

		lsm = len(spawnmap)
		lsm2 = lsm - 1
		w,h = lsm2, lsm2
		
		centering_offset = Vec2(0, 0)

		min_dim = min(w, h)

		i = 0
		for z in range(lsm):
			for x in range(lsm):
				xow = x/w
				zoh = z/h

				y = heightmap[x][z] * TERRAIN_Y_MULT
				vec = Vec3((x/min_dim)+(centering_offset.x), y, (z/min_dim)+centering_offset.y)
				self.vertices.append(vec)
				self.uvs.append((xow, zoh))

				if x > 0 and z > 0: self.triangles.append((i, i-1, i-w-2, i-w-1))

				# normals
				if x > 0 and z > 0 and x < w-1 and z < h-1:
					rl =  heightmap[x+1][z] - heightmap[x-1][z]
					fb =  heightmap[x][z+1] - heightmap[x][z-1]
					self.normals.append(Vec3(rl, 1, fb).normalized())

				i += 1

				if x < lsm2 and z < lsm2:
					random.seed(self.spawnmap[z][x])
					spawnval = random.uniform(0,1)
					m, b = get_biome_from_biomemap_value(biomemap[z][x])
					spawn = get_spawn_from_map(m[1], spawnval)
					if spawn:
						app.modelloader.load_model(spawn,
							self,
							position = vec * TILE_SCALE + Vec3(chunk_x, 0, chunk_z) * TILE_SCALE - Vec3(0,0.5,0),
							color = BIOME_MAP[b][0]
						)

		self.mesh = Mesh(vertices=self.vertices, triangles=self.triangles, uvs=self.uvs, normals=self.normals)
		self.mesh.height_values = asarray(heightmap) #For ursina terraincasting
		self.mesh.depth = h
		self.mesh.width = w
		mp = int(len(heightmap)/2)
		val = biomemap[mp][mp]
		for k in BIOME_MAP.keys():
			if val < k:
				break
		self.biome = k
		Entity.__init__(self,
			position = (chunk_x * TILE_SCALE, 0, chunk_z * TILE_SCALE),
			model = self.mesh,
			scale = TILE_SCALE,
			texture = 'grass',
			color = TERRAIN_COLOR[k]
		)
		self.collider = self.mesh
		self.spawnmap = spawnmap

	def destroy(self):
		self.active = False
		destroy(self)
		for o in self.objects:
			destroy(o)
		# print(f"Unloaded {self.chunk_id}")


#TODO: EXPERIMENT WITH MOVING EXISTING CLOUDS / CHUNKS / ETC



class DynamicTerrainLoader:
	def __init__(self, app, seed = 9):
		self.app = app
		self.chunks = []
		self.chunks_to_load = []
		self.seed = seed
		if self.seed == 0: raise ValueError("Seed cannot be zero")

		self.y_scale = 1

		self.target_fog_density = 0
		self.target_fog_color = rgb(200,200,200)
		self.target_skybox_color = rgb(200,200,255)
		self.current_fog = 0

		self.current_x = None
		self.current_z = None
		self.current_chunk_ids = []
		self.halfrender = int(BARREN_RENDER_RANGE / 2)
		self.seed = seed

		self.num_noises = 15
		self.noises = []
		for i in range(self.num_noises):
			self.noises.append(OpenSimplex(seed=self.seed * (i)).noise2d)

		self.spawn_noise = OpenSimplex(seed=self.seed*7*13).noise2d #7 and 13 just magic
		self.biome = None

		self.num_biome_noises = 3
		self.biome_noises = []
		base_biome_val = self.seed*13*17
		for i in range(self.num_biome_noises):
			self.biome_noises.append(OpenSimplex(seed=base_biome_val + i).noise2d)

		self.spawn_noise = OpenSimplex(seed=self.seed*7*13).noise2d #7 and 13 just magic

		self.s = TILE_SCALE

	# 	self.make_map()

	# def make_map(self):
	# 	from PIL import Image

	# 	chunk_x = 0
	# 	chunk_z = 0
	# 	scale = 4 #How scaled the noise is
	# 	steps = 4
	# 	biomescale = 120 #How scaled the biomes are
	# 	spawnmap, biomemap = [], []
	# 	val = 500
	# 	for i in linspace(-val, val, steps * val,endpoint=True):
	# 		scaled_i = i/scale
	# 		row, spawnrow, biomerow = [], [], []
	# 		for	j in linspace(-val, val, steps * val,endpoint =True):
	# 			scaled_j = j/scale
	# 			# row.append(sum(n(scaled_i,scaled_j) for n in self.noises)/(self.num_noises) * self.y_scale)
	# 			spawnrow.append(self.spawn_noise(scaled_i, scaled_j))
	# 			biomerow.append(abs(sum([n((chunk_x + scaled_i)/biomescale, (chunk_z + scaled_j)/biomescale) for n in self.biome_noises])/(self.num_biome_noises)))
	# 		# heightmap.append(row)
	# 		spawnmap.append(spawnrow)
	# 		biomemap.append(biomerow)

		# def make_biome_map():
		# 	biome_map = [[[0,0,0] for i in range(len(biomemap))] for i in range(len(biomemap[0]))]
			
		# 	for x in range(len(biomemap)):
		# 		for z in range(len(biomemap[0])):
		# 			val = biomemap[x][z]
		# 			for k in BIOME_MAP.keys():
		# 				if val < k:
		# 					break
		# 			color = MAP_COLOR[k]
		# 			biome_map[x][z] = color

		# 	biome_map = asarray(biome_map)
		# 	im = Image.fromarray(uint8(biome_map))
		# 	im.save("map.png")
		
		# make_biome_map()



	def update_fog_and_snow(self):
		i = get_chunk_id(self.current_x, self.current_z)
		for c in self.chunks:
			if i == c.chunk_id:
				self.biome = c.biome
				density, color, snow, render_distance, skybox_color = EFFECT_LEVELS[c.biome]
				self.app.render_distance = render_distance
				self.app.snowcloud.update_biome(c.biome)
				self.target_fog_color = color
				self.target_fog_density = density
				self.target_skybox_color = skybox_color
				break

	def get_maps(self, chunk_x, chunk_z):
		scale = 4 #How scaled the noise is
		steps = 4
		biomescale = 120 #How scaled the biomes are
		heightmap, spawnmap, biomemap = [], [], []
		for i in linspace(chunk_x - 1, chunk_x, steps,endpoint=True):
			scaled_i = i/scale
			row, spawnrow, biomerow = [], [], []
			for	j in linspace(chunk_z - 1, chunk_z, steps,endpoint =True):
				scaled_j = j/scale
				row.append(sum(n(scaled_i,scaled_j) for n in self.noises)/(self.num_noises) * self.y_scale)
				spawnrow.append(self.spawn_noise(scaled_i, scaled_j))
				biomerow.append(sum(n((chunk_x + scaled_i)/biomescale, (chunk_z + scaled_j)/biomescale) for n in self.biome_noises)/(self.num_biome_noises))
			heightmap.append(row)
			spawnmap.append(spawnrow)
			biomemap.append(biomerow)
		return heightmap, spawnmap, biomemap

	def load_new_chunk(self, chunk_x, chunk_z):
		self.chunks_to_load.append((chunk_x, chunk_z))

	def _load_new_chunk(self, pos):
		chunk_x, chunk_z = pos
		heightmap, spawnmap, biomemap = self.get_maps(chunk_x, chunk_z)
		chunk = TerrainChunk(self.app, self.seed, chunk_x, chunk_z, heightmap, spawnmap, biomemap)
		self.chunks.append(chunk)

	def update(self):
		ret = False
		if self.update_chunks_rendered():
			self.update_fog_and_snow()
			ret = True
		if self.chunks_to_load:
			self._load_new_chunk(self.chunks_to_load.pop(0))

		if not self.app.frame % 3: #Every 4th frame update fog
			if not scene.fog_density == self.target_fog_density:
				if isinstance(self.target_fog_density, int):
						if isinstance(scene.fog_density, int):
							if scene.fog_density < self.target_fog_density:
								scene.fog_density = scene.fog_density + 1
							else:
								scene.fog_density -= scene.fog_density - 1
						else:
							if self.target_fog_density == 0:
								a,b = scene.fog_density
								a += 1
								b += 1
								scene.fog_density = (a,b)
								if a > 1000 and b > 1000:
									scene.fog_density = self.target_fog_density
				else: #Target is tuple
					a,b = self.target_fog_density
					if isinstance(scene.fog_density, int):
						scene.fog_density = (500, 800)
					else:
						c,d = scene.fog_density
						if 	 a<c:c-=1
						elif a>c:c+=1
						if 	 b<d:d-=1
						elif b>d:d+=1	
						scene.fog_density = (c,d)

		# scene.fog_color = self.target_fog_color

		r,g,b,a = scene.fog_color
		r2,g2,b2,a2 = self.target_fog_color
		weather_different = False
		for s,t in zip([r,g,b,a],[r2,g2,b2,a2]):
			if not s == t:
				weather_different = True
				break
		if weather_different:		
			if 	 r<r2:r+=0.001
			elif r>r2:r-=0.001
			if 	 g<g2:g+=0.001
			elif g>g2:g-=0.001
			if 	 b<b2:b+=0.001
			elif b>b2:b-=0.001
			if   a<a2:a+=0.001
			elif a>a2:a-=0.001
			if abs(r-r2)<0.001:r=r2
			if abs(g-g2)<0.001:g=g2
			if abs(b-b2)<0.001:b=b2
			c = Vec4(r,g,b,1)
			scene.fog_color = c

		r,g,b,a = self.app.skybox.color
		r2,g2,b2,a2 = self.target_skybox_color
		weather_different = False
		for s,t in zip([r,g,b,a],[r2,g2,b2,a2]):
			if not s == t:
				weather_different = True
				break
		if weather_different:		
			if 	 r<r2:r+=0.001
			elif r>r2:r-=0.001
			if 	 g<g2:g+=0.001
			elif g>g2:g-=0.001
			if 	 b<b2:b+=0.001
			elif b>b2:b-=0.001
			if   a<a2:a+=0.001
			elif a>a2:a-=0.001
			if abs(r-r2)<0.001:r=r2
			if abs(g-g2)<0.001:g=g2
			if abs(b-b2)<0.001:b=b2
			c = Vec4(r,g,b,1)
			self.app.skybox.setcolor(c)

		return ret

	def update_chunks_rendered(self, force_load = False):
		last_x, last_z = self.current_x, self.current_z
		self.current_x, self.current_z = get_chunk_numerals_by_position(self.app.player.position)
		if self.current_x == last_x and self.current_z == last_z and self.biome:
			return False
		else:
			halfrender = int(self.app.render_distance / 2)
			min_x, min_z = self.current_x - halfrender, self.current_z - halfrender
			max_x, max_z = self.current_x + halfrender, self.current_z + halfrender
			current_chunk_ids = []
			for x in range(min_x, max_x):
				for z in range(min_z, max_z):
					cid = f"{x}x{z}"
					current_chunk_ids.append(cid)
					if not cid in self.current_chunk_ids:
						self.load_new_chunk(x, z)
			for c in list(self.chunks):
				if not c.chunk_id in current_chunk_ids:
					self.chunks.remove(c)
					try:
						c.destroy()
					except TypeError:
						pass
			self.current_chunk_ids = current_chunk_ids
			return True