from ursina import *
from .constants import *

class Item(Draggable):
	def __init__(self,
				parent,
				count,
				max_stack = 1,
				recipies = [],
				origin = (-0.5,0.5),
				size = (INVENTORY_WIDTH,INVENTORY_HEIGHT)
			):
		self.parent = parent
		x,y = self.parent.find_free_spot()
		self.width, self.height = size
		self.name = "Item"
		Draggable.__init__(self,
			parent = parent,
			model = 'quad',
			color = color.white,
			origin = origin,
			scale_x = 1/self.width,
			scale_y = 1/self.height,
			x = x * 1/self.width,
			y = -y * 1/self.height,
			z = -.5,
		)
		self.texture = texture
		self.max_stack = max_stack
		self.count = count if count <= max_stack else max_stack
		self.recipies = []

	@property
	def name(self):
		return self.__str__()

	def use(self, app):
		pass

class type_Ammo(Item):
	def __init__(self,parent,count=1):
		Item.__init__(self,parent,count=count)
		self.texture = Texture("models/items/ammo.png")
class type_Weapon(Item):
	def __init__(self,parent,count=1):
		Item.__init__(self,parent,count=count)
		self.texture = Texture("models/items/sword.png")
class type_Sword(type_Weapon):
	def __init__(self,parent,count=1):
		type_Weapon.__init__(self,parent,count=count)
		self.texture = Texture("models/items/sword.png")
class type_Bow(type_Weapon):
	def __init__(self,parent,count=1):
		type_Weapon.__init__(self,parent,count=count)
		self.texture = Texture("models/items/bow.png")
class type_Spell(type_Weapon):
	def __init__(self,parent,count=1):
		type_Weapon.__init__(self,parent,count=count)
		self.texture = Texture("models/items/staff.png")
class type_Consumable(Item):
	def __init__(self,parent,count=1):
		Item.__init__(self,parent,count=count)
		self.texture = Texture("models/items/potion.png")
class type_Potion(type_Consumable):
	def __init__(self,parent,count=1):
		type_Consumable.__init__(self,parent,count=count)
		self.texture = Texture("models/items/potion.png")
class type_Equipable(Item):
	def __init__(self,parent,count=1):
		Item.__init__(self,parent,count=count)
		self.texture = Texture("models/items/helmet.png")
class type_Armor(type_Equipable):
	def __init__(self,parent,count=1):
		type_Equipable.__init__(self,parent,count=count)
		self.texture = Texture("models/items/helmet.png")
class type_Boots(type_Armor):
	def __init__(self,parent,count=1):
		type_Armor.__init__(self,parent,count=count)
		self.texture = Texture("models/items/boots.png")
class type_Legs(type_Armor):
	def __init__(self,parent,count=1):
		type_Armor.__init__(self,parent,count=count)
		self.texture = Texture("models/items/legs.png")
class type_Chest(type_Armor):
	def __init__(self,parent,count=1):
		type_Armor.__init__(self,parent,count=count)
		self.texture = Texture("models/items/chest.png")
class type_Helmet(type_Armor):
	def __init__(self,parent,count=1):
		type_Armor.__init__(self,parent,count=count)
		self.texture = Texture("models/items/helmet.png")
class type_Bauble(type_Equipable):
	def __init__(self,parent,count=1):
		type_Equipable.__init__(self,parent,count=count)
		self.texture = Texture("models/items/necklace.png")
class type_Necklace(type_Bauble):
	def __init__(self,parent,count=1):
		type_Bauble.__init__(self,parent,count=count)
		self.texture = Texture("models/items/necklace.png")
class type_Ring(type_Bauble):
	def __init__(self,parent,count=1):
		type_Bauble.__init__(self,parent,count=count)
		self.texture = Texture("models/items/ring.png")

class item_arrow(type_Ammo):
	def __init__(self,parent,count=1):
		type_Ammo.__init__(self,parent,count=count)

class item_shortsword(type_Weapon):
	def __init__(self,parent,count=1):
		type_Weapon.__init__(self,parent,count=count)

class item_wooden_bow(type_Bow):
	def __init__(self,parent,count=1):
		type_Bow.__init__(self,parent,count=count)

class item_fooserodah(type_Spell):
	def __init__(self,parent,count=1):
		type_Spell.__init__(self,parent,count=count)

class item_health_potion(type_Potion):
	def __init__(self,parent,count=1):
		type_Potion.__init__(self,parent,count=count)

class item_basic_boots(type_Boots):
	def __init__(self,parent,count=1):
		type_Boots.__init__(self,parent,count=count)

class item_basic_chest(type_Chest):
	def __init__(self,parent,count=1):
		type_Chest.__init__(self,parent,count=count)

class item_basic_legs(type_Legs):
	def __init__(self,parent,count=1):
		type_Legs.__init__(self,parent,count=count)

class item_basic_helmet(type_Helmet):
	def __init__(self,parent,count=1):
		type_Helmet.__init__(self,parent,count=count)

class item_basic_necklace(type_Necklace):
	def __init__(self,parent,count=1):
		type_Necklace.__init__(self,parent,count=count)

class item_basic_ring(type_Ring):
	def __init__(self,parent,count=1):
		type_Ring.__init__(self,parent,count=count)


TEST_ITEMS = [
	item_arrow,
	item_shortsword,
	item_wooden_bow,
	item_fooserodah,
	item_health_potion,
	item_basic_boots,
	item_basic_chest,
	item_basic_legs,
	item_basic_helmet,
	item_basic_necklace,
	item_basic_ring,
]