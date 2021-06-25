import pathlib

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from shaders import ssao
from game.constants import *
from game.terrain_generation import DynamicTerrainLoader, BARREN
from game.entities import ModelLoader
from game.snowmesh import snowcloud
from game.skybox import SkyBox
from game.timer_decorator import timer_dec

window.vsync = False
window.center_on_screen()



class App(Ursina):
	def __init__(self, *args, **kwargs):
		Ursina.__init__(self, *args, **kwargs)
		self.frame = 0 #Frame count
		self.lasttxt = None # Holder for debug text
		self.input_map = {'escape' : self.exit, 'enter' : self.up}


		self.biome = None
		self.render_distance = BARREN_RENDER_RANGE

		self.frame = 0

		self.skybox = SkyBox(self) #Must be inited before terrain loader

		self.player = FirstPersonController(position=(0.5 * TILE_SCALE, 30, 0.5 * TILE_SCALE))
		self.player.speed = 50
		self.player.camera = ssao.ssao_shader
		self.player.add_script(NoclipMode(speed=60))

		self.modelloader = ModelLoader(self)
		self.modelloader.preload_models()

		self.terrainloader = DynamicTerrainLoader(self)
		self.terrainloader.update()
		self.biome = self.terrainloader.biome
		self.snowcloud = snowcloud(self)

		self.screentext = Text(position = (-.89,0.5), color = rgb(0,0,0))

	def up(self): self.player.y += 5
		
	def update(self, dt):
		self.input_task()
		self.terrainloader.update()
		self.biome = self.terrainloader.biome
		self.modelloader.update()
		self.skybox.update(self.terrainloader.current_x, self.terrainloader.current_z)
		if self.frame % 2: self.snowcloud.advance(self.terrainloader.current_x, self.terrainloader.current_z)
		if self.player.y < -300: self.player.y = 5*TILE_SCALE #Reset player position
		x,y,z = self.player.position
		
		if not self.frame % 30:
			screentext = f"X | {x}\nY | {y}\nZ | {z}\n\n Chunk Coordinate\n\t| X {self.terrainloader.current_x}\n\t| Z {self.terrainloader.current_z}"
			screentext += f"\nBiome - {self.terrainloader.biome}"
			screentext += f"\nSnow Rate - {self.snowcloud.rate}"
			screentext += f"\nNum Snow Particles- {len(self.snowcloud.flakelist)}"
			# screentext += f"\nTarget Fog - {self.terrainloader.target_fog_density}"
			# screentext += f"\nCurrent Fog - {scene.fog_density}"
			# screentext += f"\nTarget Fog Color - {self.terrainloader.target_fog_color}"
			# screentext += f"\nCurrent Fog Color - {scene.fog_color}"
			# screentext += f"\nTarget Skybox Color - {self.terrainloader.target_fog_color}"
			# screentext += f"\nCurrent Skybox Color - {self.skybox.color}"
			self.screentext.text = screentext
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