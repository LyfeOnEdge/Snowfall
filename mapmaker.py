import sys
from numpy import asarray, linspace, uint8
from game.constants import *
from PIL import Image
from game.timer_decorator import timer_dec
from threading import Timer

from game.terrain_generation import DynamicTerrainLoader

class app:
	def __init__(self):
		self.terrainloader = DynamicTerrainLoader(self, seed = 9)
		self.message = "Idle"
		self.last_message = None
		Timer(0.1, self._update).start()
		self.make_biome_map()
		self.calculating = True

	def _update(self):
		if not self.message == self.last_message:
			print(self.message)
			self.last_message = self.message
		sys.stdout.flush()
		if self.calculating: 
			Timer(0.1, self._update).start()

	@timer_dec
	def make_biome_map(self):
		self.calculating = True
		print("Getting Maps")
		def set_message(m): self.message = m
		skip = 10
		maps = self.terrainloader.get_maps(
			0,
			0,
			radius=2000,
			status_function = set_message,
			make_heightmap = False,
			make_spawnmap = False,
			make_biomemap = True,
			make_secondary_biomemap = True,
			skip = skip,
			)
		heightmap, spawnmap, biomemap, secondary_biomemap, affinity_biomemap = maps
		biome_map = [[[0,0,0] for i in range(len(biomemap))] for i in range(len(biomemap[0]))]
		print("Making biome color map")
		total = (len(biomemap) * len(biomemap[0])) / (skip * skip)
		current = 0
		for x in range(len(biomemap)):
			for z in range(len(biomemap[0])):
				if secondary_biomemap[x][z] > 0:
					current_map = BIOME_SPAWN_MAP
				else:
					current_map = SECONDARY_BIOME_SPAWN_MAP

				val = biomemap[x][z]
				for k in current_map.keys():
					if val < k:
						break
				r,g,b,a = MAP_COLOR[current_map[k]]
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

app()