import random
from ursina import *
from .constants import *
from .inventory import Inventory, HotBar, ArmorBar
from .items import TEST_ITEMS
from .minimap import MiniMap

FIRST_PERSON = 0
FREE = 1

# UI_SCALE = 0.075
UI_SCALE = 0.060
class UI:
	def __init__(self, app):
		self.app = app
		self.inventories = []
		self.minimap = MiniMap(app)
		self.inventory = Inventory(self,
			scale =(UI_SCALE*INVENTORY_WIDTH,UI_SCALE*INVENTORY_HEIGHT),
			position = (-0.5*UI_SCALE*INVENTORY_WIDTH,UI_SCALE*(INVENTORY_HEIGHT+0.5)),
		)
		for i in TEST_ITEMS:
			self.inventory.append(i, 1)
		self.armor_inventory = ArmorBar(self,
			scale =(UI_SCALE,UI_SCALE*(INVENTORY_HEIGHT + 2)),
			position = (0.5*UI_SCALE*INVENTORY_WIDTH + UI_SCALE,UI_SCALE*(INVENTORY_HEIGHT+2.5)),
		)
		self.hotbar = HotBar(self,
				scale =(UI_SCALE*INVENTORY_WIDTH,UI_SCALE),
				position = (-(0.5*UI_SCALE*INVENTORY_WIDTH),UI_SCALE*(INVENTORY_HEIGHT+2.5))
			)

		self.chest_inventory = Inventory(self,
			scale =(UI_SCALE*INVENTORY_WIDTH,UI_SCALE*INVENTORY_HEIGHT),
			position = (-0.5*UI_SCALE*INVENTORY_WIDTH,- 0.5 * UI_SCALE),
		)

		self.inventories.extend([self.inventory, self.armor_inventory, self.hotbar])
		self.inventory_enabled = False
		self.in_chest = False
		self.current_chest = None
		self.exit_chest()
		self.minimap.enable()

	# def show_chest_inventory(self, inv_list):
	# 	self.chest_inventory = Inventory(items=inv_list)
		
	# def hide_chest_inventory(self):

	def show_chest(self, chest):
		self.in_chest = True
		self.current_chest = chest
		chest.disabled = True
		self.show_inventory()
		self.chest_inventory.clear()
		self.chest_inventory.visible = True
		for i in chest.items:
			self.chest_inventory.append(i, 1)

	def exit_chest(self):
		self.in_chest = False
		if self.current_chest:
			self.current_chest.items = []
			for i in self.chest_inventory.icons:
				self.current_chest.items.append(type(i))
			self.current_chest.disabled = False
		self.chest_inventory.clear()
		self.chest_inventory.visible = False
		self.hide_inventory()
		self.current_chest = None

	def show_inventory(self):
		self.in_inventory = True
		self.set_player_locked()
		self.minimap.disable()
		self.inventory_enabled = True
		self.inventory.visible = True
		self.armor_inventory.visible = True

	def hide_inventory(self):
		self.in_inventory = False
		self.set_player_free()
		self.minimap.enable()
		self.inventory_enabled = False
		self.inventory.visible = False
		self.armor_inventory.visible = False

	def toggle_inventory(self):
		if self.inventory_enabled == True:
			if self.in_chest:
				self.exit_chest()
			else:
				self.hide_inventory()
		else:
			self.show_inventory()
			
	def set_player_free(self):
		self.app.player.movement_enabled = True
		mouse.locked = True

	def set_player_locked(self):
		self.app.player.movement_enabled = False
		mouse.locked = False

	def update(self):
		self.minimap.update_minimap()