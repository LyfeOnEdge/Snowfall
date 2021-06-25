#Generate verticies and normals to make plants etc with Ursina


def generate(seed):



	return vertices, normals, triangles, uvs



if __name__ == '__main__':
	verts = generate(0)

		vertices, triangles = list(), list()
		uvs = list()
		normals = list()
		
		centering_offset = Vec2(0, 0)

		min_dim = min(w, h)

		i = 0
		for z in range(lsm):
			for x in range(lsm):
				xow = x/w
				zoh = z/h

				y = heightmap[x][z] * TERRAIN_Y_MULT
				vec = Vec3((x/min_dim)+(centering_offset.x), y, (z/min_dim)+centering_offset.y)
				vertices.append(vec)
				uvs.append((xow, zoh))

				if x > 0 and z > 0: triangles.append((i, i-1, i-w-2, i-w-1))

				# normals
				if x > 0 and z > 0 and x < w-1 and z < h-1:
					rl =  heightmap[x+1][z] - heightmap[x-1][z]
					fb =  heightmap[x][z+1] - heightmap[x][z-1]
					normals.append(Vec3(rl, 1, fb).normalized())

		mesh = Mesh(vertices=vertices, triangles=triangles, uvs=uvs, normals=normals)
		mesh.height_values = asarray(heightmap) #For ursina terraincasting
		mesh.depth = h
		mesh.width = w
		e = Entity(self,
			position = (chunk_x * TILE_SCALE, 0, chunk_z * TILE_SCALE),
			model = mesh,
			scale = TILE_SCALE,
			texture = 'grass',
			color = TERRAIN_COLOR[k]
		)
		collider = mesh
		spawnmap = spawnmap












class TerrainChunk(Entity):
	def __init__(self, app, seed, chunk_x, chunk_z, heightmap, spawnmap, biomemap):
		self.chunk_x = chunk_x
		self.chunk_z = chunk_z
		self.chunk_id = get_chunk_id(chunk_x, chunk_z)
		self.seed = seed
		self.vertices, self.triangles = list(), list()
		self.uvs = list()
		self.normals = list()
		self.objects = list()
		self.spawnmap = spawnmap
		self.active = True

		lsm = len(spawnmap)
		lsm2 = lsm - 1
		w,h = lsm2, lsm2
		
		centering_offset = Vec2(0, 0)

		min_dim = min(w, h)

		i = 0
		for z in range(lsm):
			for x in range(lsm):
				xow = x/w
				zoh = z/h

				y = heightmap[x][z] * TERRAIN_Y_MULT
				vec = Vec3((x/min_dim)+(centering_offset.x), y, (z/min_dim)+centering_offset.y)
				self.vertices.append(vec)
				self.uvs.append((xow, zoh))

				if x > 0 and z > 0: self.triangles.append((i, i-1, i-w-2, i-w-1))

				# normals
				if x > 0 and z > 0 and x < w-1 and z < h-1:
					rl =  heightmap[x+1][z] - heightmap[x-1][z]
					fb =  heightmap[x][z+1] - heightmap[x][z-1]
					self.normals.append(Vec3(rl, 1, fb).normalized())

				i += 1

				if x < lsm2 and z < lsm2:
					random.seed(self.spawnmap[z][x])
					spawnval = random.uniform(0,1)
					m, b = get_biome_from_biomemap_value(biomemap[z][x])
					spawn = get_spawn_from_map(m[1], spawnval)
					if spawn:
						app.modelloader.load_model(spawn,
							self,
							position = vec * TILE_SCALE + Vec3(chunk_x, 0, chunk_z) * TILE_SCALE - Vec3(0,0.5,0),
							color = BIOME_MAP[b][0]
						)

		self.mesh = Mesh(vertices=self.vertices, triangles=self.triangles, uvs=self.uvs, normals=self.normals)
		self.mesh.height_values = asarray(heightmap) #For ursina terraincasting
		self.mesh.depth = h
		self.mesh.width = w
		mp = int(len(heightmap)/2)
		val = biomemap[mp][mp]
		for k in BIOME_MAP.keys():
			if val < k:
				break
		self.biome = k
		Entity.__init__(self,
			position = (chunk_x * TILE_SCALE, 0, chunk_z * TILE_SCALE),
			model = self.mesh,
			scale = TILE_SCALE,
			texture = 'grass',
			color = TERRAIN_COLOR[k]
		)
		self.collider = self.mesh
		self.spawnmap = spawnmap

	def destroy(self):
		self.active = False
		destroy(self)
		for o in self.objects:
			destroy(o)
		# print(f"Unloaded {self.chunk_id}")


#TODO: EXPERIMENT WITH MOVING EXISTING CLOUDS / CHUNKS / ETC