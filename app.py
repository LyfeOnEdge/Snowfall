import pathlib

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

from game.constants import *
from game.terrain_generation import DynamicTerrainLoader
from game.entities import ModelLoader
from game.snow import SnowLoader
from game.skybox import SkyBox

window.vsync = False
window.center_on_screen()

class App(Ursina):
	def __init__(self, *args, **kwargs):
		Ursina.__init__(self, *args, **kwargs)
		self.player = FirstPersonController(position=(0.5 * TILE_SCALE, 30, 0.5 * TILE_SCALE))
		self.player.speed = 35
		self.frame = 0 #Frame count
		self.lasttxt = None # Holder for debug text
		self.input_map = {'escape' : self.exit}

		self.terrainloader = DynamicTerrainLoader(self)
		self.modelloader = ModelLoader(self)
		self.skybox = SkyBox()
		# self.snowloader = SnowLoader(self)

	def update(self, dt):
		self.input_task()
		self.terrainloader.update()
		self.modelloader.update()
		if self.player.y < -300: self.player.y = 15*TILE_SCALE
		x,y,z = self.player.position
		if self.lasttxt: destroy(self.lasttxt)
		self.lasttxt = Text(
				text = 	f"X | {x}\nY | {y}\nZ | {z}\n\n Chunk Coordinate\n\t| X {self.terrainloader.current_x}\n\t| Z {self.terrainloader.current_z}\n\nBIOME - {self.terrainloader.biome}",
				position = (0.5,0.5)
			)
		self.skybox.update(self.terrainloader.current_x, self.terrainloader.current_z)
		# self.snowloader.update()
		self.frame += 1

	def input_task(self):
		for k in self.input_map.keys(): #for keys with a mapped task
			if held_keys[k]: #If held
				self.input_map[k]() #Do task

	def exit(self): self.application.quit()

if __name__ == '__main__':
	app = App()
	########################################
	#This gets called every loop of app.run despite there being no conspicous code doing so.
	def update(): app.update(time.dt)
	########################################
	sys.stdout.flush()
	app.run()