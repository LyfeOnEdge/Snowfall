from constants import *
import random as rdm

class snowflake:
	def __init__(self, pos, color = CONST_DEFAULT_COLOR, gravity = CONST_DEFAULT_GRAVITY):
		self.x, self.y = pos
		self.z = 0
		self.color = CONST_DEFAULT_COLOR
		self.gravity = CONST_DEFAULT_GRAVITY + rdm.uniform(-CONST_GRAVITY_RANDOMNESS, CONST_GRAVITY_RANDOMNESS)
		self.length = CONST_DEFAULT_SNOWFLAKE_LENGTH

	def advance(self):
		self.y -= self.gravity

class snowcloud:
	def __init__(self,
			size : tuple = (50,50),
			rate : int = 4,
			# vector : tuple = (0,1),
			color : tuple = (255,255,255,255),
			# background : tuple = (0,0,0,0),
			h_drift : int = 50,
			h_drift_radius : int = 1,
			wrap_h_drift : int = True,
			v_drift : int = 10,
			v_drift_radius : int = 4,
			wrap_v_drift : bool = False,
	):
		self.width, self.height = size
		self.halfwidth = 0.5 * self.width
		self.halfheight = 0.5 * self.height
		self.rate = rate
		self.color = color
		self.h_drift : int = 50
		self.h_drift_radius : int = 4
		self.wrap_h_drift : int = True
		self.v_drift : int = 10
		self.v_drift_radius : int = 4
		self.wrap_v_drift : bool = False

		self.flakes = []

	def advance(self):
		if self.flakes:
			for f in list(self.flakes):
				f.advance()
				if f.y < 0:
					self.flakes.remove(f)

			for i in range(self.h_drift):
				rdm.choice(self.flakes).x += rdm.uniform(-self.h_drift_radius, self.h_drift_radius)
			for i in range(self.v_drift):
				rdm.choice(self.flakes).y += rdm.uniform(-self.v_drift_radius, self.v_drift_radius)


		# if h_drift: #Make snow randomly drift back and forth
		# 	for _ in range(rdm.randrange(0,h_drift)):
		# 		shift_row_right(array, rdm.randrange(height), rdm.randrange(1, h_drift_radius),
		# 			background = background, wrap = wrap_h_drift)
		# 		shift_row_left(array, rdm.randrange(height), rdm.randrange(1, h_drift_radius),
		# 			background = background, wrap = wrap_h_drift)
		# if v_drift: #Make snow randomly drift up and down
		# 	for _ in range(rdm.randrange(0,int(v_drift))): 
		# 		shift_column_up(array, rdm.randrange(width), rdm.randrange(1, v_drift_radius),
		# 			background = background, wrap = wrap_v_drift)
		# 		shift_column_down(array, rdm.randrange(width), rdm.randrange(1, v_drift_radius),
		# 			background = background, wrap = wrap_v_drift)

		#Spawn Drops
		for _ in range(rdm.randrange(0.0, 2.0*self.rate)):
			s = snowflake((rdm.uniform(-0.5*self.halfwidth, 0.5*self.halfwidth), self.height))
			self.flakes.append(s)