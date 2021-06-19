import random
from ursina import *
from opensimplex import OpenSimplex

from .constants import TILE_SCALE, RENDER_DISTANCE
from .entities import Branch, Tree, Exit, Rock, Mushroom, LivingTree, SmallMushroom, SharpRock, Stump, MushroomCircle, Log, StickBall
from .tools import get_chunk_numerals_by_position, get_chunk_id

TERRAIN_Y_MULT = 1.7
SPAWN_MULT = 2

FB = FOG_BASE = 170

















BARREN = 0.075
BARREN_COLOR = rgb(255,255,103)
BARREN_FOG_DENSITY = (0,50)
BARREN_FOG_COLOR = rgb(FB,FB,FB)
BARREN_FLOOR_COLOR = rgb(255,255,153)
BARREN_MAP = {
	0.004 : StickBall,
	0.016 : SharpRock,
	0.036 : Rock,
	0.085 : Branch,
	0.087 : Tree,
}

SCRUBLAND = 0.1
SCRUB_COLOR = rgb(255,211,0)
SCRUB_FOG_DENSITY = (0,50)
SCRUB_FOG_COLOR = rgb(FB-10,FB-10,FB-10)
SCRUB_FLOOR_COLOR = rgb(254,229,102)
SCRUB_MAP = {
	0.006 : StickBall,
	0.009 : SharpRock,
	0.020 : Log,
	0.021 : SmallMushroom,
	0.020 : Stump,
	0.021 : Log,
	0.025 : Branch,
	0.075 : Tree,
}

LIGHT_FOREST = 0.25
LIGHT_COLOR = rgb(255,170,1)
LIGHT_FOG_DENSITY = (0,50)
LIGHT_FOG_COLOR = rgb(FB-20,FB-20,FB-20)
LIGHT_FLOOR_COLOR = rgb(255,203,101)
LIGHT_MAP = {
	0.004 : StickBall,
	0.014 : Rock,
	0.024 : SharpRock,
	0.036 : Log,
	0.046 : SmallMushroom,
	0.057 : Stump,
	0.072 : Branch,
	0.154 : Tree,
}

HEAVY_FOREST = 0.35
HEAVY_COLOR = rgb(255,115,0)
HEAVY_FOG_DENSITY = (0,50)
HEAVY_FOG_COLOR = rgb(FB-30,FB-30,FB-30)
HEAVY_FLOOR_COLOR = rgb(255,172,102)
HEAVY_MAP = {
	0.006 : StickBall,
	0.014 : Rock,
	0.030 : SharpRock,
	0.045 : Log,
	0.054 : SmallMushroom,
	0.062 : Mushroom,
	0.068 : Stump,
	0.080 : Branch,
	0.176 : Tree,
}

BADLANDS = 0.5
BAD_COLOR = rgb(255,0,0)
BAD_FOG_DENSITY = (0,30)
BAD_FOG_COLOR = rgb(FB-40,FB-40,FB-40)
BAD_FLOOR_COLOR = rgb(255,103,102)
BAD_MAP = {
	0.008 : StickBall,
	0.014 : Rock,
	0.030 : SharpRock,
	0.050 : Log,
	0.056 : SmallMushroom,
	0.064 : Mushroom,
	0.076 : Stump,
	0.083 : Branch,
	0.198 : Tree,
}

MAGIC = 0.6
MAGIC_COLOR = rgb(205,1,116)
MAGIC_FLOOR_COLOR = rgb(226,102,172)
MAGIC_FOG_DENSITY = (0,20)
MAGIC_FOG_COLOR = rgb(FB-50,FB-50,FB-50)
MAGIC_MAP = {
	0.010 : StickBall,
	0.018: Rock,
	0.036 : SharpRock,
	0.054 : Log,
	0.064 : Mushroom,
	0.070 : Stump,
	0.074 : MushroomCircle,
	0.088 : Branch,
	0.170 : Tree,
	0.2 : Exit,
}


BIOME_MAP = {
	BARREN : (BARREN_COLOR, BARREN_MAP),
	SCRUBLAND : (SCRUB_COLOR, SCRUB_MAP),
	LIGHT_FOREST : (LIGHT_COLOR, LIGHT_MAP),
	HEAVY_FOREST : (HEAVY_COLOR, HEAVY_MAP),
	BADLANDS : (BAD_COLOR, BAD_MAP),
	MAGIC : (MAGIC_COLOR, MAGIC_MAP)
}

BIOME_NAME_MAP = {
	BARREN : "Barren",
	SCRUBLAND : "Scrubland",
	LIGHT_FOREST : "Light Forest",
	HEAVY_FOREST : "Heavy Forest",
	BADLANDS : "Badlands",
	MAGIC : "Magic"
}

TERRAIN_COLOR = {
	BARREN : BARREN_FLOOR_COLOR,
	SCRUBLAND : SCRUB_FLOOR_COLOR,
	LIGHT_FOREST : LIGHT_FLOOR_COLOR,
	HEAVY_FOREST : HEAVY_FLOOR_COLOR,
	BADLANDS : BAD_FLOOR_COLOR,
	MAGIC :	MAGIC_FLOOR_COLOR,
}

			# scene.fog_density = (1,40)
		# scene.fog_color = color.rgb(180,180,180)

FOG_LEVELS = {
	BARREN : (BARREN_FOG_DENSITY , BARREN_FOG_COLOR),
	SCRUBLAND : (SCRUB_FOG_DENSITY , SCRUB_FOG_COLOR),
	LIGHT_FOREST : (LIGHT_FOG_DENSITY , LIGHT_FOG_COLOR),
	HEAVY_FOREST : (HEAVY_FOG_DENSITY , HEAVY_FOG_COLOR),
	BADLANDS : (BAD_FOG_DENSITY , BAD_FOG_COLOR),
	MAGIC :	(MAGIC_FOG_DENSITY , MAGIC_FOG_COLOR),
}

from numpy import asarray, linspace
import json

import sys

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

		self.current_x = None
		self.current_z = None
		self.current_chunk_ids = []
		# self.halfrender = int(RENDER_DISTANCE / 2)
		self.halfrender = int(RENDER_DISTANCE / 2)
		self.seed = seed

		self.num_noises = 15
		self.noises = []
		for i in range(self.num_noises):
			self.noises.append(OpenSimplex(seed=self.seed * (i)).noise2d)

		self.spawn_noise = OpenSimplex(seed=self.seed*7*13).noise2d #7 and 13 just magic
		self.biome = None

		self.num_biome_noises = 2
		self.biome_noises = []
		base_biome_val = self.seed*13*17
		for i in range(self.num_biome_noises):
			self.biome_noises.append(OpenSimplex(seed=base_biome_val + i).noise2d)

		self.spawn_noise = OpenSimplex(seed=self.seed*7*13).noise2d #7 and 13 just magic

		self.s = TILE_SCALE

	def update_fog(self, biome = None):
		if not biome:
			i = get_chunk_id(self.current_x, self.current_z)
			for c in self.chunks:
				if i == c.chunk_id:
					self.biome = BIOME_NAME_MAP[c.biome]
					density, color = FOG_LEVELS[c.biome]
					scene.fog_density = density
					scene.fog_color = color
					self.app.skybox.setcolor(color)
		else:
			self.biome = BIOME_NAME_MAP[biome]
			density, color = FOG_LEVELS[biome]
			scene.fog_density = density
			scene.fog_color = color
			self.app.skybox.setcolor(color)

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
				biomerow.append(abs(sum(n((chunk_x + scaled_i)/biomescale, (chunk_z + scaled_j)/biomescale) for n in self.biome_noises)/(self.num_biome_noises)))
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
		# print(f"Loaded Chunk {chunk.chunk_id}")
		# self.current_chunk_ids.append(chunk.chunk_id)

	def update(self):
		ret = False
		if self.update_chunks_rendered():
			self.update_fog()
			ret = True
		if self.chunks_to_load:
			self._load_new_chunk(self.chunks_to_load.pop(0))
		return ret

	def update_chunks_rendered(self, force_load = False):
		last_x, last_z = self.current_x, self.current_z
		self.current_x, self.current_z = get_chunk_numerals_by_position(self.app.player.position)
		if self.current_x == last_x and self.current_z == last_z:
			return False
		else:
			min_x, min_z = self.current_x - self.halfrender, self.current_z - self.halfrender
			max_x, max_z = self.current_x + self.halfrender, self.current_z + self.halfrender
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