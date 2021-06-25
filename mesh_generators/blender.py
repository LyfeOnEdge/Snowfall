import bpy
import bmesh
import math

def calc_n_gon(segments, z): #Generate circle verts
    verts = []
    for i in range(segments):
        angle = (math.pi*2) * i / segments
        verts.append((math.cos(angle), math.sin(angle), z))
    return verts

def make_n_gon(name, segments):
    data = {'verts':[],'edges':[],'faces':[]}
    data['verts'].extend(calc_n_gon(segments, 0))
    data['faces'].append([i for i in range(segments)])
    scene = bpy.context.scene
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(data['verts'], data['edges'], data['faces'])
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(state = True)
    bpy.ops.object.mode_set(mode = 'EDIT')
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    #------------------------------------------------------------------
    #This is the line that I thought should give
    #me 12 sides, but I still end up with 6
    bmesh.ops.subdivide_edges(bm, edges = bm.edges, use_grid_fill=True, cuts = 4)
    #------------------------------------------------------------------
    
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update(calc_edges=True)
    mesh.validate(verbose=True)
    return obj

sides = 6
name = f"{sides} - Sided Polygon"
circle_obj = make_n_gon('Cylinder', 6)