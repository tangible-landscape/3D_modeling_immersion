import bpy
import os
import sys
import bpy
import bmesh

sys.path.insert(0, os.path.dirname(bpy.path.abspath("//")))

from bpy.types import Operator
from bpy.props import (
        StringProperty,
        BoolProperty,
        IntProperty,
        FloatProperty,
        FloatVectorProperty,
        EnumProperty,
        PointerProperty,
        )

import  mesh_helpers

def calcArea(obj):
	"""Report the surface area of the active mesh"""
    selectOnly(obj)
    obj = bpy.data.objects[obj]
    bm = mesh_helpers.bmesh_copy_from_object(obj, apply_modifiers=True)
    area = mesh_helpers.bmesh_calc_area(bm)*.2
	bm.free()
	info = []

	return area


def selectOnly(obj, delete= False):
    
    """ seks all objects and selects the passed object"""
    
    if bpy.data.objects.get(obj):
        obj=bpy.data.objects[obj]
        for ob in bpy.context.scene.objects:
            ob.select=False        
        obj.select=True       
        if delete:
            bpy.ops.object.delete()
    return obj

def particle(obj,specieType,count,specieSize):
    
    """ Get object, specie type, specie count, and specie size and apply particle system """
    selectOnly (obj)
    
    # remove all exsisting particles systems #
    obj=bpy.data.objects[obj]
    for i in obj.modifiers:
        if "ParticleSystem" in i.name :
            obj.modifiers.remove(obj.modifiers.get(i.name))
    
    # Create an new particle system #  

    bpy.ops.object.particle_system_add()
    psys1 = obj.particle_systems[-1]
    pset1 = psys1.settings
    pset1.name = 'TreePatch'
    pset1.type = 'HAIR'
    pset1.use_rotation_dupli=False

    pset1.use_dead=True
    pset1.render_type='OBJECT'
    pset1.dupli_object = bpy.data.objects[specieType]
    
    
    pset1.use_advanced_hair=True
    pset1.use_emit_random=False
    pset1.lifetime_random = 0.0
    pset1.emit_from = 'FACE'
    pset1.use_even_distribution = True
    pset1.distribution = 'JIT'
    pset1.count=count
    pset1.use_render_emitter = True
    #pset1.object_align_factor = (0,0,1)

    pset1.use_emit_random=True
    pset1.userjit=70
    pset1.use_modifier_stack=True
    pset1.hair_length=specieSize
    
    pset1.use_rotations=True
    pset1.use_rotation_dupli=True
    pset1.particle_size=1
    pset1.size_random=0
    pset1.rotation_mode='OB_Y'
  
particle ("patches_3d","TreeType1", calcArea("patches_3D)/500,1.5)






