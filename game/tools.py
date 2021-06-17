from .constants import *

def get_chunk_numerals_by_position(position):
	return int(position[0]/TILE_SCALE), int(position[2]/TILE_SCALE)

def get_chunk_id(chunk_x, chunk_z):
	return f"{chunk_x}x{chunk_z}"