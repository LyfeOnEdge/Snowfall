from ursina import *
from math import atan2,degrees,sin,cos


class enemy(Entity):
	def __init__(self, *arg, **kwargs):
		self.health = 10
		Entity.__init__(self, *arg, **kwargs)

# class Zombie(enemy):
# 	def __init__(self, player, *args, **kwargs):
# 		self.player = player
# 		kwargs.update(model="pointer")
# 		enemy.__init__(self, *args, **kwargs)
# 		self.speed = 8.5

# 	def update(self):
# 		self.angle_to_player = degrees(math.atan2(self.x-self.player.x, self.z-self.player.z)) - 90

# 		self.rotation = (0,self.angle_to_player,0)
# 		print(self.rotation)

class OrbOfDoom(enemy):
	def __init__(self, player, *args, **kwargs):
		self.player = player
		kwargs.update({'model':'eyeball', 'texture':'eyeball_texture', 'scale':1, 'origin':(0,0)})
		enemy.__init__(self, *args, **kwargs)
		self.speed = 8.5
		self.t = 0

	def update(self):
		self.look_at(self.player)
		dx, dz = self.x-self.player.x, self.z-self.player.z
		dxz = math.sqrt(dx*dx + dz*dz)
		self.y_angle_to_player = degrees(math.atan2(dx, dz))
		# self.x_angle_to_player = degrees(math.atan2(self.y-self.player.y, self.z-self.player.z)) #I can't figure out how to get these two in phase
		self.x_angle_to_player = degrees(math.atan2(dxz, self.y-self.player.y)) + 90
		# self.rotation = (sin(self.t/300)*10,self.y_angle_to_player,0)
		__,_,z = self.rotation
		v = sin(self.t/150)/100
		self.rotation = (v + self.x_angle_to_player,self.y_angle_to_player,z)
		self.t += 1
