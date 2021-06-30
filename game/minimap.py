from ursina import *
from .constants import *
from PIL import Image
from numpy import uint8, asarray

class MiniMap(Entity):
	def __init__(self, app):
		self.app = app
		self.image = None
		Entity.__init__(self,
				name='minimap',
				model="quad",
				parent=camera.ui,
				scale=0.25,
				color=color.white,
				position = (0.6125,0.35)
			)
		self.z -=0.1

		self.minimap_frame = Entity(
				name='minimap_frame',
				model="quad",
				texture="map_frame",
				parent=self,
				scale=1,
				color=color.white,
				position = (0,0)
			)
		self.minimap_frame.z -=0.1

		self.minimap_cursor = Entity(
				name='minimap_cursor',
				model="quad",
				texture="minimap_cursor",
				parent=self,
				scale=1,
				origin = (0,0),
				color=color.white,
				position = (0,0)
			)
		self.minimap_cursor.z -=0.1

		self.minimap_needs_update = True
		self.minimap_needs_conversion = False
		self.image_needs_texture = False

	def update_minimap(self):
		self.minimap_cursor.rotation_z = self.app.player.rotation_y
		if self.minimap_needs_update:
			skip = 8
			heightmap, spawnmap, biomemap, secondary_biomemap, affinitymap, chestmap = self.app.terrainloader.get_maps(
					chunk_x=self.app.terrainloader.current_x+0.5,
			 		chunk_z=self.app.terrainloader.current_z+0.5,
			 		radius=5 * self.app.render_distance,
			 		skip = skip, #1 is no skip
			 		divisions = 1,
			 		status_function=None,
			 		make_heightmap=False,
			 		make_spawnmap=False,
			 		make_biomemap=True,
			 		make_secondary_biomemap=True,
			 		make_affinitymap=True,
			 		make_chestmap = False,
		 		)
			biome_map = [[[0,0,0] for i in range(len(biomemap))] for i in range(len(biomemap[0]))]
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
					r,g,b,a = r*255,g*255,b*255,255
					
					val = affinitymap[x][z]
					for k in AFFINITY_MAP.keys():
						if val < k:
							break
					
					if not AFFINITY_MAP[k][0] == (0,0,0):
						r2,g2,b2 = AFFINITY_MAP[k][0]
						r=max(min(r+r2,255),0)
						g=max(min(g+g2,255),0)
						b=max(min(b+b2,255),0)

					biome_map[x][z] = (r,g,b,a)
					current += 0
			self.minimap_needs_update = False
			self.minimap_needs_conversion = True
			self.image = asarray(biome_map)
		elif self.minimap_needs_conversion:
			self.image = Image.fromarray(uint8(self.image))
			self.minimap_needs_conversion = False
			self.image_needs_texture = True
		elif self.image_needs_texture:
			self.texture = Texture(self.image)
			self.image_needs_texture = False

	def disable(self):
		self.visible = False
		for c in self.children:
			c.visible = False

	def enable(self):
		self.visible = True
		for c in self.children:
			c.visible = True