import bpy
import bmesh

from bmesh.types import BMFace as BMFace
from mathutils import Vector, Matrix
from math import radians, sqrt

context = bpy.context

scene = context.scene

mesh = bpy.data.meshes.new("Rings")
obj = bpy.data.objects.new("circle", mesh)

bm = bmesh.new()
bm.from_mesh(mesh)
circle = bmesh.ops.create_circle(bm, radius=1, segments=10, cap_ends=True, calc_uvs=True)
print(circle)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=3)


mesh.update(calc_edges=True)
bm.to_mesh(mesh)
scene.collection.objects.link(obj)