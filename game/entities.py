import random as rdm
from numpy import asarray
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
from .constants import *
from .timer_decorator import timer_dec

def get_chunk_numerals_by_position(position):
	return int(position[0]/TILE_SCALE), int(position[2]/TILE_SCALE)

def get_chunk_id(chunk_x, chunk_z):
	return f"{chunk_x}x{chunk_z}"

class ModelLoader:
	def __init__(self, app):
		self.app = app
		self.models = {
			"exit" : 'exit',
			"branch" : 'branch',
			"portal" : 'snowgate',
			"treeshroom" : 'treeshroom',
			"rock" : "rock3",
			"mushroom" : "mushroom",
			'log' : 'log',
			"mushroomcircle" : "mushroomcircle"
		}
		self.smallmushrooms = []
		for i in range(3): self.smallmushrooms.append(f"smallmushroom{i}")
		self.trees = []
		for i in range(12): self.trees.append(f"tree{i}")
		self.livingtrees = []
		for i in range(3): self.livingtrees.append(f"livingtree{i}")
		self.rocks = []
		for i in range(5): self.rocks.append(f"rock{i}")
		self.sharprocks = []
		for i in range(7): self.sharprocks.append(f"sharprock{i}")
		self.stumps = []
		for i in range(4): self.stumps.append(f"stump{i}")
		self.stickballs = []
		for i in range(5): self.stickballs.append(f"stickball{i}")

		self.models_to_load = [] #Models should be added in order of importance
		self.loaded_models = []

	def get_tree(self):			return rdm.choice(self.trees)
	def get_livingtree(self):	return rdm.choice(self.livingtrees)
	def get_rock(self):			return rdm.choice(self.rocks)
	def get_sharprock(self):	return rdm.choice(self.sharprocks)
	def get_stump(self):		return rdm.choice(self.stumps)
	def get_smallmushroom(self):return rdm.choice(self.smallmushrooms)
	def get_stickball(self):	return rdm.choice(self.stickballs)

	def get(self, name):
		m = self.models.get(name)
		if m: return m
		else: raise ValueError(f"Failed to find model for {name}")
		
	def load_model(self, model, chunk, *args, **kwargs):
		self.models_to_load.append((model, chunk, args, kwargs))

	def update(self):
		while self.models_to_load:
			model, chunk, args, kwargs = self.models_to_load.pop(0)

			if not chunk.active:
				continue

			x,y,z = kwargs.get('position')
			hit_info = None
			escape = False
			current_y = 4
			obj = model(self.app, *args, **kwargs)
			chunk.objects.append(obj)
			self.loaded_models.append(obj)


class baseEntity(Entity):
	def __init__(self, *args, **kwargs):
		kw = {
			'origin_y' : -0.5,
			'origin_x' : -0.5,
			'origin_z' : -0.5,
		}
		kwargs.update(kw)
		Entity.__init__(self, *args, **kwargs)

	def randomize(self):
		s = rdm.uniform(0.7, 1.4)
		self.scale = (s*rdm.uniform(0.8, 1.2),s*rdm.uniform(0.8, 1.2),s*rdm.uniform(0.8, 1.2))
		self.x += rdm.uniform(-0.2, 0.2)
		self.y += rdm.uniform(-0.6, -0.2)
		self.z += rdm.uniform(-0.2, 0.2)
		self.rotation = (rdm.randrange(0,7),rdm.randrange(0,360),rdm.randrange(0,7))

class SmallMushroom(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get_smallmushroom()
		kw = {
			'model' : mesh,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
		}
		if 'color' in kwargs: kw.pop('color')
		kwargs.update(kw)
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()

class MushroomCircle(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get("mushroomcircle")
		kw = {
			'model' : mesh,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
		}
		if 'color' in kwargs: kw.pop('color')
		kwargs.update(kw)
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()

class Mushroom(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get("mushroom")
		kw = {
			'model' : mesh,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
		}
		if 'color' in kwargs: kw.pop('color')
		kwargs.update(kw)
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()


class Branch(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get("branch")
		kw = {
			'model' : mesh,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
		}
		if 'color' in kwargs: kw.pop('color')
		kwargs.update(kw)
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()


class StickBall(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get_stickball()
		kw = {
			'model' : mesh,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
		}
		if 'color' in kwargs: kw.pop('color')
		kwargs.update(kw)
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()


class Stump(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get_stump()
		kw = {
			'model' : mesh,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
		}
		if 'color' in kwargs: kw.pop('color')
		kwargs.update(kw)
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()


class Rock(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get_rock()
		kw = {
			'model' : mesh,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
		}
		if 'color' in kwargs: kw.pop('color')
		kwargs.update(kw)
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()

class SharpRock(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get_sharprock()
		kw = {
			'model' : mesh,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
		}
		if 'color' in kwargs: kw.pop('color')
		kwargs.update(kw)
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()

class Tree(baseEntity):
	def __init__(self, app, *args, **kwargs):
		m = app.modelloader.get_tree()
		kw = {
			'model' : m,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
			'origin_y' : -0.5,
			'origin_x' : 0,
			'origin_z' : 0,
			'scale' : (1,1,1)
		}
		if 'color' in kwargs: kw.pop("color")
		kwargs.update(kw)
		baseEntity.__init__(self, *args, **kwargs)
		self.collider = m
		self.y -= 0.35
		self.randomize()


class LivingTree(baseEntity):
	def __init__(self, app, *args, **kwargs):
		m = app.modelloader.get_livingtree()
		kw = {
			'model' : m,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
			'origin_y' : -0.5,
		}
		if 'color' in kwargs: kw.pop("color")
		kwargs.update(kw)
		baseEntity.__init__(self, *args, **kwargs)
		self.collider = m
		self.y -= 0.35
		self.randomize()


class Log(baseEntity):
	def __init__(self, app, *args, **kwargs):
		m = app.modelloader.get('log')
		kw = {
			'model' : m,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
		}
		if 'color' in kwargs: kw.pop("color")
		kwargs.update(kw)
		baseEntity.__init__(self, *args, **kwargs)
		self.collider = m
		self.randomize()


class Portal:
	def __init__(self, app, *args, **kwargs):
		self.portal = basePortal(app, *args, **kwargs)

	def destroy(self):
		destroy(self)
		self.portal.destroy()

class basePortal:
	def __init__(self, app, *args, **kwargs):
		mesh = app.modelloader.get("portal")
		kw = {
			'model' : mesh,
			'double_sided' : 'True',
			'origin_y' : -0.25,
			'origin_x' : -0.5,
			'origin_z' : -0.5,
			'scale' : (1,1,1),
			'path' : './models',
			'loop' : True,
			'autoplay' : False,
			'fps' : 5
		}
		kwargs.update(kw)
		self.anim = Animation('snowgate.gif', *args, **kwargs)
		self.animator = Animator( animations = {'default' : self.anim})
		self.animator.state = 'default'
		self.anim.enable()

	def destroy(self):
		destroy(self)

class Exit(Entity):
	def __init__(self, app, *args, **kwargs):
		mesh = app.modelloader.get("exit")
		kw = {
			'model' : mesh,
			'texture' : 'brick',
			# 'color' : color.brown,
			# 'color' : rgb(178,166,158),
			'color' : rgb(223,222,221),
			'origin_y' : -0.5,
			'origin_x' : -0.5,
			'origin_z' : -0.5,
			'scale' : (1,1,1)
		}
		kwargs.update(kw)
		Entity.__init__(self, *args, **kwargs)
		self.portal = Portal(app, position = self.position)

	def destroy(self):
		destroy(self)
		self.portal.destroy()

	def randomize(self):
		x = rdm.uniform(0,0.2)
		z = rdm.uniform(0,0.2)

		self.portal.anim.x += x
		self.x += x
		self.portal.anim.z += z
		self.z += z
		rot = (rdm.randrange(0,5),rdm.randrange(0,360),rdm.randrange(0,5))
		self.portal.anim.rotation = rot
		self.rotation = rot