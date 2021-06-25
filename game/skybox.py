from ursina import *
from .constants import *

class SkyboxWall(Entity):
	def __init__(self, app, *args, **kwargs):
		kw = {
			'model' : 'quad',
			'origin_y' : 0,
			'origin_x' : 0.5,
			'origin_z' : 0,
			'scale' : (2 * app.render_distance * TILE_SCALE,2 * app.render_distance * TILE_SCALE),
		}
		if not kwargs.get('position'): kw['position'] = (0,0,0)
		kwargs.update(kw)
		Entity.__init__(self, *args, **kwargs)


class SkyBox:
	def __init__(self, app):
		#make initial skybox
		self.app = app
		self.chunk_x = None
		self.chunk_z = None
		self.n_wall = None
		self.e_wall = None
		self.s_wall = None
		self.w_wall = None
		self.ceiling = None
		self.walls = []
		self.first_run = True
		self.color = rgb(200,200,200)
		self.setcolor(self.color)
		self.update(0,0)

	def update(self, chunk_x, chunk_z):
		if not self.chunk_x == chunk_x or not self.chunk_z == chunk_z:
			HALFRENDER = self.app.render_distance/2
			min_x, min_z, max_x, max_z = chunk_x - self.app.render_distance, chunk_z - self.app.render_distance, chunk_x + self.app.render_distance, chunk_z + self.app.render_distance
			if self.first_run:
				self.first_run = False
				self.n_wall = SkyboxWall(self.app, position = (max_x * TILE_SCALE, TILE_SCALE, max_z * TILE_SCALE))
				self.e_wall = SkyboxWall(self.app, position = (max_x * TILE_SCALE, TILE_SCALE, min_z * TILE_SCALE), rotation = (0,90,0))
				self.s_wall = SkyboxWall(self.app, position = (min_x * TILE_SCALE, TILE_SCALE, min_z * TILE_SCALE), rotation = (0,180,0))
				self.w_wall = SkyboxWall(self.app, position = (min_x * TILE_SCALE, TILE_SCALE, max_z * TILE_SCALE), rotation = (0,270,0))
				self.ceiling = SkyboxWall(self.app, position = ((max_x + min_x) * 0.5 * TILE_SCALE + HALFRENDER * TILE_SCALE, 4 * TILE_SCALE, (max_z + min_z) * 0.5 * TILE_SCALE), rotation = (270,0,0))
				self.ceiling.scale = (2 * self.app.render_distance * TILE_SCALE,2 * self.app.render_distance * TILE_SCALE)
				self.walls.extend([self.n_wall, self.e_wall, self.s_wall, self.w_wall, self.ceiling])
			else:
				self.n_wall.position = (max_x * TILE_SCALE, TILE_SCALE, max_z * TILE_SCALE)
				self.e_wall.position = (max_x * TILE_SCALE, TILE_SCALE, min_z * TILE_SCALE)
				self.s_wall.position = (min_x * TILE_SCALE, TILE_SCALE, min_z * TILE_SCALE)
				self.w_wall.position = (min_x * TILE_SCALE, TILE_SCALE, max_z * TILE_SCALE)
				self.ceiling.position = ((max_x + min_x) * 0.5 * TILE_SCALE + HALFRENDER * TILE_SCALE, 4 * TILE_SCALE, (max_z + min_z) * 0.5 * TILE_SCALE)
			self.chunk_x = chunk_x
			self.chunk_z = chunk_z

	def destroy(self):
		if self.walls:[destroy(w) for w in self.walls]

	def setcolor(self, color):
		self.color = color
		for w in self.walls:
			w.color = color