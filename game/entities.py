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
		# kwargs.update({'shader' : })
		self.models_to_load.append((model, chunk, args, kwargs))

	def preload_models(self): #Gets rid of loading lag
		mdls = [self.models[m] for m in self.models.keys()]
		self.modellists = [self.smallmushrooms, self.trees, self.livingtrees, self.rocks, self.sharprocks, self.stumps, self.stickballs, self.models]
		for ml in self.modellists:
			for m in ml: destroy(Entity(model=m))

	def update(self):
		while self.models_to_load:
			model, chunk, args, kwargs = self.models_to_load.pop(0)
			if not chunk.active: continue
			x,y,z = kwargs.get('position')
			hit_info = None
			escape = False
			current_y = 4
			obj = model(self.app, *args, **kwargs)
			chunk.objects.append(obj)
			self.loaded_models.append(obj)
			break


class baseEntity(Entity):
	def __init__(self, *args, **kwargs):
		kwargs.update({'origin_y':-0.5,'origin_x':-0.5,'origin_z':-0.5,})		 
		Entity.__init__(self, *args, **kwargs)

	def randomize(self):
		s = rdm.uniform(0.7, 1.4)
		self.scale = (s*rdm.uniform(0.8, 1.2),s*rdm.uniform(0.8, 1.2),s*rdm.uniform(0.8, 1.2))
		self.x += rdm.uniform(-0.4, 0.4)
		self.y += rdm.uniform(-0.6, -0.2)
		self.z += rdm.uniform(-0.4, 0.4)
		self.rotation = (rdm.randrange(0,7),rdm.randrange(0,360),rdm.randrange(0,7))

class SmallMushroom(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get_smallmushroom()
		kwargs.update({'model':mesh,'texture':'brick'})		 
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()

class MushroomCircle(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get("mushroomcircle")
		kwargs.update({'model':mesh,'texture':'brick'})
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()

class Mushroom(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get("mushroom")
		kwargs.update({'model':mesh,'texture':'brick'})
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()


class Branch(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get("branch")
		kwargs.update({'model':mesh,'texture':'brick'})
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()


class StickBall(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get_stickball()
		kwargs.update({'model':mesh,'texture':'brick'})
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()


class Stump(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get_stump()
		kwargs.update({'model':mesh,'texture':'brick'})
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()


class Rock(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get_rock()
		kwargs.update({'model':mesh,'texture':'brick'})
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()

class SharpRock(baseEntity):
	def __init__(self, app,  *args, **kwargs):
		mesh = app.modelloader.get_sharprock()
		kwargs.update({'model':mesh,'texture':'brick'})
		baseEntity.__init__(self, *args, **kwargs)
		self.randomize()

class Tree(baseEntity):
	def __init__(self, app, *args, **kwargs):
		m = app.modelloader.get_tree()
		kwargs.update({
			'model' : m,
			'texture' : 'brick',
			'origin_y' : -0.5,
			'origin_x' : 0,
			'origin_z' : 0,
			'scale' : (1,1,1)
		})
		baseEntity.__init__(self, *args, **kwargs)
		self.collider = m
		self.y -= 0.35
		self.randomize()


class LivingTree(baseEntity):
	def __init__(self, app, *args, **kwargs):
		m = app.modelloader.get_livingtree()
		kwargs.update({
			'model' : m,
			'texture' : 'brick',
			'origin_y' : -0.5,
		})
		baseEntity.__init__(self, *args, **kwargs)
		self.collider = m
		self.y -= 0.35
		self.randomize()


class Log(baseEntity):
	def __init__(self, app, *args, **kwargs):
		m = app.modelloader.get('log')
		kwargs.update({'model':m,'texture':'brick'})
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
		kwargs.update({
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
		})
		self.anim = Animation('snowgate.gif', *args, **kwargs)
		self.animator = Animator( animations = {'default' : self.anim})
		self.animator.state = 'default'
		self.anim.enable()

	def destroy(self):
		destroy(self)

class Exit(Entity):
	def __init__(self, app, *args, **kwargs):
		mesh = app.modelloader.get("exit")
		kwargs.update({
			'model' : mesh,
			'texture' : 'brick',
			'color' : rgb(223,222,221),
			'origin_y' : -0.5,
			'origin_x' : -0.5,
			'origin_z' : -0.5,
			'scale' : (1,1,1)
		})
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