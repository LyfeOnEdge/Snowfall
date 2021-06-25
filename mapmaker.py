import sys, json, random
from ursina import *
from opensimplex import OpenSimplex
from numpy import asarray, linspace, uint8
from game.constants import *
from PIL import Image
from game.timer_decorator import timer_dec
from threading import Timer

#Map making object, 


class DynamicTerrainMapMaker:
	def __init__(self, seed = 10, radius = 700, skip = 4):
		self.seed = seed
		self.skip = skip #Number of chunks to skip when drawing map
		if self.seed == 0: raise ValueError("Seed cannot be zero")
		
		self.num_noises = 15
		self.noises = []
		for i in range(self.num_noises):
			self.noises.append(OpenSimplex(seed=self.seed * (i)).noise2d)

		self.spawn_noise = OpenSimplex(seed=self.seed*7*13).noise2d #7 and 13 just magic

		self.biomescale = 120 #How scaled the biomes are
		self.affinity_biomescale = 250
		self.num_biome_noises = 2
		self.biome_noises = []
		base_biome_val = self.seed*13*17
		for i in range(self.num_biome_noises):
			self.biome_noises.append(OpenSimplex(seed=base_biome_val + i).noise2d)

		self.num_affinity_noises = 4
		self.affinity_noises = []
		base_biome_val = self.seed*7*13*17
		for i in range(self.num_affinity_noises):
			self.affinity_noises.append(OpenSimplex(seed=base_biome_val + i).noise2d)

		Timer(0.1, self._update).start()
		self.calculating = True
		self.message = "Idle"
		self.make_biome_map()

	def _update(self):
		print(self.message)
		sys.stdout.flush()
		if self.calculating: 
			Timer(0.1, self._update).start()

	@timer_dec
	def make_biome_map(self):
		self.calculating = True
		print("Getting Maps")
		def set_message(m): self.message = m
		skip = 10
		maps = self.get_maps(
			0,
			0,
			radius=2000,
			status_function = set_message,
			make_heightmap = False,
			make_spawnmap = False,
			make_biomemap = True,
			skip = skip,
			)
		heightmap, spawnmap, biomemap, affinity_biomemap = maps
		biome_map = [[[0,0,0] for i in range(len(biomemap))] for i in range(len(biomemap[0]))]
		print("Making biome color map")
		total = (len(biomemap) * len(biomemap[0])) / (skip * skip)
		current = 0
		for x in range(len(biomemap)):
			for z in range(len(biomemap[0])):
				val = biomemap[x][z]
				for k in BIOME_MAP.keys():
					if val < k:
						break
				r,g,b,a = MAP_COLOR[k]
				r,g,b,a = r*255,g*255,b*255,a*255

				val = affinity_biomemap[x][z]
				for k in AFFINITY_MAP.keys():
					if val < k:
						break
				
				if not AFFINITY_MAP[k][0] == (0,0,0):
					r2,g2,b2 = AFFINITY_MAP[k][0]
					r=max(min(r+r2,255),0)
					g=max(min(g+g2,255),0)
					b=max(min(b+b2,255),0)

				biome_map[x][z] = (r,g,b)
				current += 0
			self.message = f"Drawing Map - {(current/total)*100}%"
		print("Saving image")
		im = Image.fromarray(uint8(asarray(biome_map)))
		im.save("map.png")
		self.calculating = False
		self.message = "Done!"
		
	def get_maps(self,
	 		chunk_x=0,
	 		chunk_z=0,
	 		radius=0,
	 		skip = 1, #1 is no skip
	 		status_function=None,
	 		make_heightmap=True,
	 		make_spawnmap=True,
	 		make_biomemap=True,
	 		make_affinitymap=True):

		scale = 4 #How scaled the noise is
		heightmap, spawnmap, biomemap, affinitymap = [], [], [], []

		x_start = chunk_x - 1 if not radius else chunk_x - radius
		x_end = chunk_x if not radius else chunk_x + radius
		z_start = chunk_z - 1 if not radius else chunk_z - radius
		z_end = chunk_z if not radius else chunk_z + radius

		total = (2*radius)*(2*radius) / (skip * skip)
		current = 0
		diameter = 2 * radius

		for i in linspace(x_start, x_end, num=int(diameter / skip), endpoint=True):
			scaled_i = i/scale
			row, spawnrow, biomerow, affinityrow = [], [], [], []
			for	j in linspace(z_start, z_end, num=int(diameter / skip), endpoint =True):
				scaled_j = j/scale
				if make_heightmap: row.append(sum(n(scaled_i,scaled_j) for n in self.noises)/(self.num_noises))
				if make_spawnmap: spawnrow.append(self.spawn_noise(scaled_i, scaled_j))
				if make_biomemap: biomerow.append(sum(n((chunk_x + scaled_i)/self.biomescale, (chunk_z + scaled_j)/self.biomescale) for n in self.biome_noises)/(self.num_biome_noises))
				if make_affinitymap: affinityrow.append(sum(n((chunk_x + scaled_i)/self.affinity_biomescale, (chunk_z + scaled_j)/self.affinity_biomescale) for n in self.affinity_noises)/(self.num_affinity_noises))
				current += 1
			biomemap.append(biomerow)
			if status_function:
				status_function(f"Calculating Maps - {(current/total)*100}%")
			heightmap.append(row)
			spawnmap.append(spawnrow)
			affinitymap.append(affinityrow)
		return heightmap, spawnmap, biomemap, affinitymap

m = DynamicTerrainMapMaker()