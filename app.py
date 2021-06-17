import pathlib

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders.screenspace_shaders import ssao
from game.constants import *
from game.terrain_generation import DynamicTerrainLoader, BARREN
from game.entities import ModelLoader
from game.snowmesh import SnowLoader
from game.skybox import SkyBox
from game.timer_decorator import timer_dec

window.vsync = False
window.center_on_screen()



class App(Ursina):
	def __init__(self, *args, **kwargs):
		Ursina.__init__(self, *args, **kwargs)
		self.frame = 0 #Frame count
		self.lasttxt = None # Holder for debug text
		self.input_map = {'escape' : self.exit}

		self.skybox = SkyBox() #Must be inited before terrain loader

		self.player = FirstPersonController(position=(0.5 * TILE_SCALE, 30, 0.5 * TILE_SCALE))
		self.player.speed = 40
		# self.player.camera = ssao.ssao_shader

		self.modelloader = ModelLoader(self)
		self.modelloader.preload_models()

		self.terrainloader = DynamicTerrainLoader(self)
		self.terrainloader.update()
		self.terrainloader.update_fog(BARREN)

		self.snowloader = SnowLoader(self)
		
		
	def update(self, dt):
		self.input_task()
		# @timer_dec
		def update_terrain():
			if self.terrainloader.update():
				self.snowloader.update_snowclouds()
		# @timer_dec
		def update_modelloader():
			self.modelloader.update()
		# @timer_dec
		def update_skybox():
			self.skybox.update(self.terrainloader.current_x, self.terrainloader.current_z)
		update_terrain()
		update_modelloader()
		update_skybox()

		if self.player.y < -300: self.player.y = 15*TILE_SCALE #Reset player position
		x,y,z = self.player.position
		if self.lasttxt: destroy(self.lasttxt)
		self.lasttxt = Text(
				text = 	f"X | {x}\nY | {y}\nZ | {z}\n\n Chunk Coordinate\n\t| X {self.terrainloader.current_x}\n\t| Z {self.terrainloader.current_z}\n\nBIOME - {self.terrainloader.biome}",
				position = (0.5,0.5)
			)

		self.snowloader.update()
		self.frame += 1
		sys.stdout.flush() #Make sure stuff gets printed each frame

	def input_task(self):
		for k in self.input_map.keys(): #for keys with a mapped task
			if held_keys[k]: #If held
				self.input_map[k]() #Do task

	def exit(self):
		sys.exit()

if __name__ == '__main__':
	app = App()
	########################################
	#This gets called every loop of app.run despite there being no conspicous code doing so.
	def update(): app.update(time.dt)
	########################################
	sys.stdout.flush()
	app.run()