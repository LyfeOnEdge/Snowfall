from ursina import *
from ursina.color import rgba
from .constants import INVENTORY_WIDTH, INVENTORY_HEIGHT

class Inventory(Entity):
	def __init__(self, ui, items = None, rows = INVENTORY_HEIGHT, columns=INVENTORY_WIDTH, origin = (-0.5,0.5), **kwargs):
		self.ui = ui
		self.width = columns
		self.height= rows
		self.icons = []
		self.start_inventory = None
		Entity.__init__(self,
			parent = camera.ui,
			model='quad',
			origin = origin,
			position = (-0.865,.4765),
			color = rgba(60,60,60,80),
		)

		self.inventory_grid = Entity(
			parent=self,
			model=Grid(self.width, self.height, thickness = 1),
			origin = origin,
			color = rgba(0,0,0,200)
			)

		for key, value in kwargs.items():
			setattr(self, key, value)

		self.z = -0.1

	def find_free_spot(self):
		for y in range(self.height):
			for x in range(self.width):
				grid_positions = [(int(e.x*self.width), int(e.y*self.height)) for e in self.icons]
				if not (x,-y) in grid_positions:
					return x, y

	def append(self, item, count, x=0, y=0):
		print('add item:', item.name)

		if len(self.icons) >= self.width*self.height:
			print('inventory full')
			error_message = Text('<red>Inventory is full!', origin=(0,-1.5), x=-.5, scale=2)
			destroy(error_message, delay=1)
			return

		x, y = self.find_free_spot()

		icon = item(self,count=count)
		name = icon.name
		self.icons.append(icon)

		num = random.random()
		if num < 0.33:
			icon.color = color.gold
			name = '<orange>Rare ' + name
		elif num < 0.66: 		
			icon.color = color.green
			name = '<green>Uncommon ' + name
		else:
			icon.color = color.white
			name = ' Common ' + name		

		icon.tooltip = Tooltip(name)
		icon.tooltip.background.color = color.color(0,0,0,.8)
		icon.drag = lambda:self.drag(icon)
		icon.drop = lambda:self.drop(icon)

	def clear(self):
		for i in self.icons:
			destroy(i)
		self.icons = []

	def drag(self, icon):
		icon.org_pos = (icon.x, icon.y)
		icon.z -= .05   # ensure the dragged item overlaps the rest
		self.start_inventory = icon.parent

	def drop(self, icon):
		hovered = False
		print(mouse.position)
		mouse_x, mouse_y, _ = mouse.position
		x,y = icon.x, icon.y
		for i in self.ui.inventories:
			inv_x, inv_y = i.x, i.y
			width, height, _ = i.bounds
			if mouse_x >= inv_x and mouse_x <= inv_x + width:
				if mouse_y <= inv_y and mouse_y >= inv_y - height:
					hovered = i
					break
		if hovered:
			if hovered == self.start_inventory:
				icon.x = int((icon.x + (icon.scale_x/2)) * hovered.width) / hovered.width
				icon.y = int((icon.y - (icon.scale_y/2)) * hovered.height) / hovered.height
				icon.z += .05
				# if outside, return to original position
				if icon.x < 0 or icon.x >= 1 or icon.y > 0 or icon.y <= -1:
					icon.position = (icon.org_pos)
					return
				# if the spot is taken, swap positions
				for c in hovered.icons:
					if c == icon:
						continue
					if c.x == icon.x and c.y == icon.y:
						c.position = icon.org_pos
			else:
				old_parent = icon.parent
				icon.world_parent = hovered
				old_parent.icons.remove(icon)
				hovered.icons.append(icon)
				icon.x = int((icon.x + (icon.scale_x/2)) * hovered.width) / hovered.width
				icon.y = int((icon.y - (icon.scale_y/2)) * hovered.height) / hovered.height
				icon.z += .01
				# if outside, return to original position
				if icon.x < 0 or icon.x >= 1 or icon.y > 0 or icon.y <= -1:
					icon.world_parent = old_parent
					icon.position = icon.org_pos
					return
				# if the spot is taken, swap positions
				for c in hovered.icons:
					if c == icon:
						continue
					if c.x == icon.x and c.y == icon.y:
						print('swap positions')
						c.world_parent = old_parent
						c.position = icon.org_pos
						hovered.icons.remove(c)
						old_parent.icons.append(c)				
		else:
			icon.position = icon.org_pos
			return

class HotBar(Inventory):
	def __init__(self, ui, items = None, rows = 1, columns=INVENTORY_WIDTH, **kwargs):
		Inventory.__init__(self, ui, items, rows, columns, **kwargs)

class ArmorBar(Inventory):
	def __init__(self, ui, items = None, rows = INVENTORY_HEIGHT + 2, columns=1, **kwargs):
		Inventory.__init__(self, ui, items, rows, columns, **kwargs)