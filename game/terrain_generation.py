import sys, json, random
from ursina import *
from ursina.color import rgba
from opensimplex import OpenSimplex
from numpy import asarray, linspace, uint8
from PIL import Image
from .constants import *
from .entities import Branch, Tree, Exit, Rock, Mushroom, LivingTree, SmallMushroom, SharpRock, Stump, MushroomCircle, Log, StickBall
from .tools import get_chunk_numerals_by_position, get_chunk_id





def get_spawn_from_map(m, val):
	for k in m.keys():
		if (val / SPAWN_MULT) < k: return m[k]

class TerrainChunk(Entity):
	def __init__(self, app, seed, chunk_x, chunk_z, heightmap, spawnmap, biomemap, secondary_biomemap, affinitymap, chestmap):
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


		mp = int(len(heightmap)/2)
		if secondary_biomemap[mp][mp] > 0:
			current_map = BIOME_SPAWN_MAP
		else:
			current_map = SECONDARY_BIOME_SPAWN_MAP

		val = biomemap[mp][mp]
		for k in current_map.keys():
			if val < k:
				break
		self.biome = current_map[k]
		r,g,b,a = TERRAIN_COLOR[self.biome]
		r,g,b,a = r*255,g*255,b*255,a*255
		

		val = affinitymap[mp][mp]
		for k in AFFINITY_MAP.keys():
			if val < k:
				break
		
		r2,g2,b2 = 0,0,0
		if not AFFINITY_MAP[k][0] == (0,0,0):
			r2,g2,b2 = AFFINITY_MAP[k][0]
			r=max(min(r+r2,255),0)
			g=max(min(g+g2,255),0)
			b=max(min(b+b2,255),0)



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
					random.seed(self.spawnmap[x][z])
					spawnval = random.uniform(0,1)
					spawn = get_spawn_from_map(BIOME_MAP[self.biome][1], spawnval)
					r,g,b,a = BIOME_MAP[self.biome][0]
					r,g,b = int(r*255),int(g*255),int(b*255)
					r=max(min(r+r2,255),0)
					g=max(min(g+g2,255),0)
					b=max(min(b+b2,255),0)
					if spawn:
						app.modelloader.load_model(spawn,
							self,
							position = vec * TILE_SCALE + Vec3(chunk_x, 0, chunk_z) * TILE_SCALE - Vec3(0,0.5,0),
							color = rgb(r,g,b)
						)
					else:
						random.seed(chestmap[x][z])
						spawnval = random.uniform(0,1)
						if spawnval < 0.02:
							app.modelloader.load_chest(chestmap[x][z], #Loot seed
								self,
								position = vec * TILE_SCALE + Vec3(chunk_x, 0, chunk_z) * TILE_SCALE - Vec3(0,0.5,0),
								color = rgb(r,g,b)
							)
						

		self.mesh = Mesh(vertices=self.vertices, triangles=self.triangles, uvs=self.uvs, normals=self.normals)
		self.mesh.height_values = asarray(heightmap) #For ursina terraincasting
		self.mesh.depth = h
		self.mesh.width = w
		
		Entity.__init__(self,
			position = (chunk_x * TILE_SCALE, 0, chunk_z * TILE_SCALE),
			model = self.mesh,
			scale = TILE_SCALE,
			texture = 'grass',
			color = rgb(r,g,b)
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
	def __init__(self, app, seed = 9, minimap = True):
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
		self.biomescale = BIOMESCALE
		self.biome_noises = []
		base_biome_val = self.seed*13*17
		for i in range(self.num_biome_noises):
			self.biome_noises.append(OpenSimplex(seed=base_biome_val + i).noise2d)

		self.secondary_biomescale = SECONDARY_BIOMESCALE
		self.num_secondary_biome_noises = 2
		self.secondary_biome_noises = []
		base_biome_val = self.seed*3*13*17
		for i in range(self.num_secondary_biome_noises):
			self.secondary_biome_noises.append(OpenSimplex(seed=base_biome_val + i).noise2d)

		self.num_affinity_noises = 4
		self.affinity_biomescale = AFFINITY_BIOMESCALE
		self.affinity_noises = []
		base_biome_val = self.seed*7*13*17
		for i in range(self.num_affinity_noises):
			self.affinity_noises.append(OpenSimplex(seed=base_biome_val + i).noise2d)

		self.spawn_noise = OpenSimplex(seed=self.seed*7*13).noise2d #7 and 13 just magic

		self.chest_noise = OpenSimplex(seed=self.seed*123)

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

	def get_maps(self,
 		chunk_x=0,
 		chunk_z=0,
 		radius=0,
 		skip = 1, #1 is no skip
 		divisions = 1,
 		status_function=None,
 		make_heightmap=True,
 		make_spawnmap=True,
 		make_biomemap=True,
 		make_secondary_biomemap=True,
 		make_affinitymap=True,
 		make_chestmap = True):

		scale = 4 #How scaled the noise is
		heightmap, spawnmap, biomemap, secondary_biomemap, affinitymap, chestmap = [], [], [], [], [], []

		x_start = chunk_x - 1 if not radius else chunk_x - radius
		x_end = chunk_x if not radius else chunk_x + radius
		z_start = chunk_z - 1 if not radius else chunk_z - radius
		z_end = chunk_z if not radius else chunk_z + radius

		total = (2*radius)*(2*radius) / (skip * skip)
		current = 0
		diameter = 2 * radius if radius else 1

		for i in linspace(x_start, x_end, num=int(diameter / skip) * divisions, endpoint=True):
			scaled_i = i/scale
			row, spawnrow, biomerow, secondary_biomerow, affinityrow, chestrow = [], [], [], [], [], []
			for	j in linspace(z_start, z_end, num=int(diameter / skip) * divisions, endpoint =True):
				scaled_j = j/scale
				if make_heightmap: row.append(sum(n(scaled_i,scaled_j) for n in self.noises)/(self.num_noises))
				if make_spawnmap: spawnrow.append(self.spawn_noise(scaled_i, scaled_j))
				if make_biomemap: biomerow.append(sum(list(n((chunk_x + scaled_i)/self.biomescale, (chunk_z + scaled_j)/self.biomescale) for n in self.biome_noises))/(self.num_biome_noises))
				if make_secondary_biomemap: secondary_biomerow.append(sum(n((chunk_x + scaled_i)/self.secondary_biomescale, (chunk_z + scaled_j)/self.secondary_biomescale) for n in self.secondary_biome_noises)/(self.num_secondary_biome_noises))
				if make_affinitymap: affinityrow.append(sum(n((chunk_x + scaled_i)/self.affinity_biomescale, (chunk_z + scaled_j)/self.affinity_biomescale) for n in self.affinity_noises)/(self.num_affinity_noises))
				if make_chestmap: chestrow.append(self.spawn_noise(scaled_i*CHEST_SCALE, scaled_j*CHEST_SCALE))
				current += 1
			heightmap.append(row)
			biomemap.append(biomerow)
			secondary_biomemap.append(secondary_biomerow)
			spawnmap.append(spawnrow)
			affinitymap.append(affinityrow)
			chestmap.append(chestrow)
			if status_function: status_function(f"Calculating Maps - {(current/total)*100}%")
		return heightmap, spawnmap, biomemap, secondary_biomemap, affinitymap, chestmap

	def load_new_chunk(self, chunk_x, chunk_z):
		self.chunks_to_load.append((chunk_x, chunk_z))

	def _load_new_chunk(self, pos):
		chunk_x, chunk_z = pos
		heightmap, spawnmap, biomemap, secondary_biomemap, affinitymap, chestmap = self.get_maps(chunk_x, chunk_z, divisions = 4)
		chunk = TerrainChunk(self.app, self.seed, chunk_x, chunk_z, heightmap, spawnmap, biomemap, secondary_biomemap, affinitymap, chestmap)
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
		elif self.current_x == last_x and self.current_z == last_z:
			pass
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
			self.app.ui.minimap.minimap_needs_update = True
			return True
