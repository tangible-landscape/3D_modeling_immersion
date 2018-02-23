bl_info = {
 "name": "Tangible Landscape Addon",
 "author": "Payam Tabrizian (ptabriz)",
 "version": (1, 0),
 "blender": (2, 7, 9),
 "location": "View3D",
 "description": "Real-time 3D modeling with Tangible Landscape",
 "warning": "",
 "wiki_url": "",
 "tracker_url": "",
 "category": "view_3D"}


import bpy
import sys
import os
import math
import datetime
import addon_utils
import bmesh

from bpy.props import *
from . import mesh_helpers
from .settings import getSettings, setSettings

from bpy.props import (
        StringProperty,
        EnumProperty,
        )

import bpy.utils.previews
from bpy.types import WindowManager
from mathutils import Vector

watchName = "Watch"
textureFile = "texture.png"
terrainFile = "terrain.tif"
DEMFile = "elev.tif"
trailFile = "trail.shp"
vantageFile = "vantage.shp"
waterFile = "water.tif"
emptyFile = "empty.txt"
CRS = "EPSG:3358"

class Prefs:
    def __init__(self):
        self.watchFolder =  getSettings()['folder'] + "/" + watchName
        self.scratchFolder =  getSettings()['folder'] + "/" + "scratch"
        self.terrainPath = os.path.join(self.watchFolder, terrainFile)
        self.DEMPath = os.path.join(self.watchFolder, DEMFile)
        self.texturePath = os.path.join(self.watchFolder, textureFile)
        self.trailPath = os.path.join(self.watchFolder, trailFile)
        self.vantagePath = os.path.join(self.watchFolder, vantageFile)
        self.waterPath = os.path.join(self.watchFolder, waterFile)
        self.emptyPath = os.path.join(self.watchFolder, emptyFile)

        self.CRS = "EPSG:" + getSettings()['CRS']
        self.timer = getSettings()['timer']

def addSide(objName,mat):

    ter = bpy.data.objects[objName]
    ter.select=True

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    me = ter.data

    if ter.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(ter.data)
        vertices = bm.verts

    else:
        vertices = ter.data.vertices

    verts = [ter.matrix_world * vert.co for vert in vertices]

    dic={"x":[], "y":[], "z":[]}
    for vert in verts:
        if not math.isnan(vert[0]):
            dic["x"].append(vert[0])
            dic["y"].append(vert[1])
            dic["z"].append(vert[2])

    xmin = min(dic["x"])
    xmax = max(dic["x"])
    ymin = min(dic["y"])
    ymax = max(dic["y"])
    zmin = min(dic["z"])

    tres = 3

    for vert in vertices:
        if vert.co[0] < xmin + tres and vert.co[0] > xmin-tres:
            vert.select = True
            vert.co[2] = -50

        elif vert.co[1] < ymin + tres and vert.co[1] > ymin-tres:
            vert.select = True
            vert.co[2] = -50

        elif vert.co[0] < xmax + tres and vert.co[0] > xmax-tres:
            vert.select = True
            vert.co[2] = -50
        elif vert.co[1] < ymax + tres and vert.co[1] > ymax-tres:
            vert.select = True
            vert.co[2] = -50
    #bpy.ops.transform.translate(value=(0, 0, -100), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SHARP', proportional_size=45.2593)

    bmesh.update_edit_mesh(me, True)

    def NormalInDirection( normal, direction, limit = .5):
        return direction.dot( normal ) > limit

    def GoingUp( normal, limit = .5):
        return NormalInDirection( normal, Vector( (0, 0, 1 ) ), limit )

    def GoingDown( normal, limit = .5 ):
        return NormalInDirection( normal, Vector( (0, 0, -1 ) ), limit )

    def GoingSide( normal, limit = .2 ):
        return ( GoingUp( normal, limit ) == False and
        GoingDown( normal, limit ) == False )

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    #Selects faces going side

    for face in ter.data.polygons:
        face.select = GoingSide(face.normal)

    bpy.ops.object.mode_set(mode='EDIT', toggle=False)


    changeMat(objName,mat,2)
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

def shrinkRaster2Obj(obj, target, method="NEAREST_VERTEX",
                     offset=0, delModifier=True):
    """allows an object to shrink to the surface of another object.
    It moves each vertex of the object being modified to the closest position
    on the surface of the given mesh

    Keyword arguments:
    raster -- is the
    target --
    method -- uses one of the three shrinkwrap methods.(default NEAREST_VERTEX)
    ztranslate -- justifies the produced mesh on the target. It is particulalry
    usefull for pointclouds.(default 0)
    delModifier -- delete exisitng shrinkwrap modifier.
    """

    try:

        rasterObj = bpy.data.objects[obj]
        target = bpy.data.objects[target]
        selectOnly(obj)
        bpy.context.scene.objects.active = rasterObj

        # select only the plane previous modifiers #
        if delModifier and rasterObj.modifiers.get("Shrinkwrap"):
            rasterObj.modifiers.remove(rasterObj.modifiers.get("Shrinkwrap"))

        # apply shrinkwrap Modifier #
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        bpy.context.object.modifiers['Shrinkwrap'].target = target
        bpy.context.object.modifiers["Shrinkwrap"].wrap_method = method
        bpy.context.object.modifiers["Shrinkwrap"].use_keep_above_surface = True
        bpy.context.object.modifiers["Shrinkwrap"].offset = offset
        while rasterObj.modifiers[0] != rasterObj.modifiers["Shrinkwrap"]:
            bpy.ops.object.modifier_move_up(modifier="Shrinkwrap")

    except:
        print ("""Shrinkwrap Unsuccessfull: either the raster or target
              object does not exist""")


def smooth(obj, factor=2, iterations=4):
    """Smooths a mesh by flattening the angles between adjacent faces in it.
    It smooths without subdividing the mesh - the number of vertices remains
    the same.
    Keyword arguments:
    obj -- name of the object
    factor -- The factor to control the smoothing amount. Higher values will
    increase the effect.
    iterations -- number of smoothing iterations, equivalent to executing the
    smooth tool multiple times.
    """

    selectOnly(obj)
    bpy.ops.object.modifier_add(type="SMOOTH")
    modifier = bpy.data.objects[obj].modifiers["Smooth"]
    modifier.factor = factor
    modifier.iterations = iterations


def changeTex(obj, texturePath):
    """Changes the texture of an object based on the passed texturePath
    To maximize performance texture swap is done changing surface material"""

    obj = selectOnly(obj)
    texPath = os.path.expanduser(texturePath)
    # remove previous material from material slot #
    if obj.material_slots:
        # for slot,index in zip(obj.material_slots, range(20)):
        for slot in obj.material_slots:
            bpy.ops.object.material_slot_remove()

    try:
        img = bpy.data.images.load(texPath)

    except:
        raise NameError("Cannot load image [0]".format(texPath))

    # Create image texture from image
    cTex = bpy.data.textures.new("Raster Tec", type="IMAGE")
    cTex.image = img

    # Create material
    mat = bpy.data.materials.new('P')

    # Add texture slot for color texture
    mtex = mat.texture_slots.add()
    mtex.texture = cTex
    mtex.texture_coords = 'UV'
    mtex.use_map_color_diffuse = True
    mtex.use_map_color_emission = True
    mtex.emission_color_factor = 0.5
    mtex.use_map_density = True
    mtex.mapping = 'FLAT'
    me = obj.data
    me.materials.append(mat)


def selectOnly(obj, delete=False):
    """ selects the passed object"""

    if bpy.data.objects.get(obj):
        obj = bpy.data.objects[obj]
        if obj.hide:
            obj.hide = False
        for ob in bpy.context.scene.objects:
            ob.select = False
        obj.select = True
        if delete:
            bpy.ops.object.delete()
            obj.select = True
            bpy.ops.object.delete()
    return obj


def translateLoc(obj, pos, HumanHeight=+1.8):
    """ moves the passed object and returns the new location """

    obj = bpy.data.objects[obj]
    obj.location = [pos[0], pos[1], pos[2] + HumanHeight]
    return obj.location


def getVertexList(obj, precision=0):
    """ returns a dictionary with all the object vertices as keys and
    a list of coordinaltes as walues """

    obj = bpy.data.objects[obj]
    objData = obj.data
    vertDic = {}
    # Looks into the object vertices ##
    for vert in objData.vertices:
        vertX = int((round(vert.co.x, precision)))
        vertY = int((round(vert.co.y, precision)))
        vertZ = int((round(vert.co.z, precision)))
        vertDic[vert.index] = [vertX, vertY, vertZ]
    return vertDic


def findNearVert(coord, targetDic, estimate=2.5):
    """ gets a list of x and y along with a dictionary of object vertices
    and returns the nearest vertex index from the target object dictionary
    estimate --defines    """

    x1 = int(coord[0])
    y1 = int(coord[1])
    distList = []
    distDic = {}

    for vertex in targetDic:
        x2 = targetDic[vertex][0]
        y2 = targetDic[vertex][1]
        # calulates the distance between the object vertices #
        dist = round(math.sqrt(((x2-x1)**2) + ((y2-y1)**2)), 1)
        if dist < estimate:
            distList.append(dist)
            distDic[dist] = targetDic[vertex]
    if distDic:
            nearestVert = (distDic[min(distDic)])
            print ("""Nearest vertex found has distance of {0} meters and
                    coordinates of {1}:".format( min(distDic),
                    distDic[min(distDic)])""")
            return nearestVert
    else:
            return


def calcArea(obj):
    """ Report the surface area of the active mesh """

    obj = bpy.data.objects[obj]
    bm = mesh_helpers.bmesh_copy_from_object(obj, apply_modifiers=True)
    area = mesh_helpers.bmesh_calc_area(bm)*.2
    bm.free()

    return area


def toggleCam(camInitial, multiple=True, adaptGrass=False):
        """ assign the camera scene to the passed camera name"""


        if multiple:
            camList = []
            for obj in bpy.data.objects:
                if camInitial in obj.name:
                    camList.append(obj)

            currentCam = bpy.context.scene.camera

            if camInitial not in currentCam.name:
                camIndex = 0
            else:
                camIndex = camList.index(currentCam)
            if camIndex == len(camList) - 1:
                selectCam = 0
            else:
                selectCam = camIndex + 1

            Camera = camList[selectCam]

        else:
            Camera = bpy.data.objects[camInitial]

        bpy.context.scene.camera = Camera
        bpy.context.scene.objects.active = Camera
        bpy.ops.view3d.object_as_camera()


def getTime(returnType):
    """ Rerturn time related outputs """

    current_time = str(datetime.datetime.now().time())
    seconds = current_time.split(":")[2][:2]
    minutes = current_time.split(":")[1]
    fullTime = current_time.replace(":", "")[:6]
    if returnType == "min":
        return minutes
    elif returnType == "sec":
        return seconds
    elif returnType == "time":
        return fullTime


def makeScratchfile(fPath, fType):
    """ Renames the passed file relative to the current time and puts in
    the scratch path"""
    out_time = getTime("time")
    fName = os.path.basename(fPath).split(".")[0]
    scratchFolder = os.path.normpath(os.path.dirname(fPath) +
                    os.sep + os.pardir) +  "\\scratch"

    scratchName = scratchFolder + "/" + fName + "_" + out_time
    try:

        if fType == "raster":
            outFile = scratchName + ".tif"
            os.rename(fPath, outFile)
        elif fType == "text":
            outFile = scratchName + ".txt"
            os.rename(fPath, outFile)

        if fType == "vector":
            for ext in [".shp", ".shx", ".prj", ".dbf"]:
                fpathNew = fPath[:-4] + ext
                outFile = scratchName + ext
                os.rename(fpathNew, outFile)
    except:
        print("could not rename the {0} file").format(fPath)


def particle(obj, specieType, count, specieSize=.6, rotation=.02,
             rotObj="OB_Y", group=False, vertexGroup=False, particle_name="particle_setting", texture=False):
    """ Get object, specie type, specie count, and specie size
    and apply particle system """
    selectOnly(obj)
<<<<<<< HEAD
=======
    # remove all previously assigned particles systems #
>>>>>>> 3bfcd10fed99120242b8e1fbd8445c6b0d069e80
    Obj = bpy.data.objects[obj]
    bpy.context.scene.objects.active = Obj
    # Create an new particle system #
    bpy.ops.object.particle_system_add()
    psys1 = Obj.particle_systems[-1]
    psys1.name = particle_name
    pset1 = psys1.settings
    pset1.name = 'TreePatch'
    pset1.type = 'EMITTER'
    pset1.physics_type = 'NO'
    pset1.use_even_distribution = False
    pset1.use_emit_random = False
    pset1.use_rotation_dupli = False
    pset1.use_dead = True

    if vertexGroup:
        bpy.context.object.particle_systems["ParticleSystem"].\
            vertex_group_density = "Density"
        bpy.context.object.particle_systems["ParticleSystem"].\
            vertex_group_length = "Height"
    if group:
        pset1.render_type = 'GROUP'
        pset1.dupli_group = bpy.data.groups[specieType]
        pset1.use_group_pick_random = True
    else:
        pset1.render_type = 'OBJECT'
        pset1.dupli_object = bpy.data.objects[specieType]

    if texture:
        Obj.particle_systems[particle_name].settings.\
        active_texture = bpy.data.textures[texture]

    pset1.lifetime_random = 0.0
    pset1.emit_from = 'FACE'
    pset1.distribution = 'JIT'
    pset1.count = count
    pset1.use_render_emitter = True

    pset1.userjit = 70
    pset1.use_modifier_stack = True
    pset1.hair_length = specieSize

    pset1.use_rotations = True
    pset1.rotation_factor_random = rotation

    pset1.use_rotation_dupli = True
    pset1.particle_size = 1
    pset1.size_random = .4
    pset1.rotation_mode = rotObj


def changeMat(obj, mat, slot=1):

    obj = bpy.data.objects[obj]
    mat = bpy.data.materials.get(mat)
    if len(obj.data.materials) >= slot:
    # assign to 1st material slot
        obj.data.materials[slot] = mat
    else:
    # no slots
        obj.data.materials.append(mat)

    if slot > 1:
        obj.active_material_index = slot-1
        bpy.ops.object.material_slot_assign()


def remove(wildCard, all=False):

    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith(wildCard):
            if obj.hide:
                obj.hide=False
            obj.select = True
            bpy.ops.object.delete()

def subdivide(cutNo):

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')
        obj = bpy.context.active_object
        bpy.ops.mesh.subdivide(number_cuts=cutNo, smoothness=0.2)
        bmesh.update_edit_mesh(obj.data, True)
        bpy.ops.object.mode_set(mode='OBJECT')

class Adapt:

    def __init__(self):

        self.plane = "terrain"
        self.terrain = bpy.data.objects[self.plane]
        self.treePatch = "TreePatch"
        self.trail = "trail"
        self.indexlist = []
        self.importedlist = []
        self.pointlist = []
        self.texture = "texture.tif"
        self.water = "water"
        self.humanCamera = "Camera"
        self.humanTarg = "HumanCamTarg"

        self.engine = bpy.context.scene.render.engine
        self.world = bpy.context.scene.world.name
        self.realism = self.world.split(".")[1]


        self.vantage = "vantage"
        self.vantagetxt = "vantage.txt"
        self.target = "camtarget"
        self.vantageCam = "VantageCam"
        self.camWalk = "Camwalk"
        self.scene = bpy.context.scene

        self.clouds = bpy.data.objects["Clouds"]
        self.sun = bpy.data.objects["Sun"]


    def changeEngine(self, mode, real):

        # Change materials #
        if mode != self.engine or real != self.realism:

            for obj in bpy.data.objects:

                for index, mat in enumerate(obj.material_slots):
                    if not obj.hide:

                        if (mat.name.split(".")[0] == self.engine[0] and
                                "cube" not in obj.name):

                            if self.realism in mat.name:
                                newMatName = (mode[0] + "." +
                                mat.name.split(".")[1] + "." + real)
                            else:
                                newMatName = (mode[0] + "." +
                                mat.name.split(".")[1])

                            mat = bpy.data.materials.get(newMatName)
                            obj.data.materials[index] = mat

        if mode != self.engine:
                for lamp in bpy.data.lamps:
                    lampInd = lamp.name.split(".")[0]

                    if lampInd == self.engine[0] or lampInd == mode[0]:
                        newLampName = mode[0] + lamp.name[1:]
                        if (newLampName in bpy.data.objects and
                            not bpy.data.objects[newLampName].hide ):
                            newLamp = bpy.data.objects[newLampName]
                            oldLamp = bpy.data.objects[lamp.name]
                            oldLamp.layers[0] = False
                            oldLamp.layers[3] = True
                            newLamp.layers[0] = True

                # Change rendere engine #
                bpy.context.scene.render.engine = mode
                self.engine = mode
                # Change background #

        # Change render mode #
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        if mode == "CYCLES":

                            bpy.context.scene.world.active_texture_index = 0
                            space.viewport_shade = 'MATERIAL'

                        else:
                            bpy.context.scene.world.active_texture_index = 1
                            space.viewport_shade = 'MATERIAL'


    def UpdateWorld(self, engine, realism):

        newWorld = engine + "." + realism
        bpy.context.scene.world = bpy.data.worlds[newWorld]
        self.world= bpy.data.worlds[newWorld]

    def changeRealism(self,mode):

        self.realism = mode
        if self.terrain.particle_systems:
            for particle in self.terrain.particle_systems:
                setting = particle.settings
                if setting.count== 1:
                    newParticle= mode + "_" + particle.name + "_single"
                else:
                    newParticle = mode + "_" + particle.name

                if setting.render_type == 'GROUP':
                    setting.dupli_group = bpy.data.groups[newParticle]
                else:
                    setting.dupli_object = bpy.data.objects[newParticle]

        if mode == "High":
          self.clouds.hide = True
          self.sun.hide = True

        elif mode == "Low":
          self.clouds.hide = False
          self.sun.hide = False

        self.changeEngine(self.engine,mode)

    def terrainChange(self,Path, CRS):

        try:
            if bpy.data.objects.get(self.plane):
                selectOnly(self.plane, delete=True)

            bpy.ops.importgis.georaster(filepath=Path, importMode="DEM",
                                        subdivision="mesh", rastCRS=CRS)
            selectOnly(self.plane)
            bpy.ops.object.convert(target="MESH")
            # smooth(self.plane, 3, 1)
            mat = self.engine[0] + ".Grass" + "." + self.realism
            matSide = self.engine[0] + ".Side" + "." + self.realism
            changeMat(self.plane, mat)
            addSide(self.plane,matSide)

            makeScratchfile(Path, "raster")

            return "finished"
        except:
            print ("Train adaptation unsuccessfull")

    def textureM(self,texturePath):

        try:
            selectOnly(self.plane)
            tex = makeScratchfile(texturePath, "texture")
            changeTex(self.plane, tex)
            return "finished"
        except:
            print ("cannot change texture")

    def waterFill(self,waterPath, CRS):

        if bpy.data.objects.get(self.water, CRS):
            self.scene.objects.unlink(bpy.data.objects[self.water])
            bpy.data.objects.remove(bpy.data.objects[self.water])

        try:
            bpy.ops.importgis.georaster(filepath=waterPath, importMode="DEM",
                                        subdivision="mesh", rastCRS=CRS)
            bpy.ops.object.convert(target='MESH')
            bpy.context.object.show_transparent = True
            mat = self.engine[0] + ".Water"
            changeMat(self.water, mat)

            if (int(getTime("sec"))) % 2 == 0:
                makeScratchfile(waterPath, "raster")

            return "imported"
        except:
            print("water patch drawing failed")

    def vantageShp(self,vantagePath, CRS):

        if bpy.data.objects.get(self.vantage):
            selectOnly(self.vantage, delete=True)

        try:
            bpy.ops.importgis.shapefile(filepath=vantagePath, shpCRS=CRS)

            vanLine = bpy.data.objects[self.vantage]
            cam = bpy.data.objects[self.vantageCam]
            tar = bpy.data.objects[self.target]

            me = vanLine.to_mesh(self.scene, apply_modifiers=True,
                                 settings='PREVIEW')
            me.transform(vanLine.matrix_world)
            cam.location = [me.vertices[0].co.x,
                            me.vertices[0].co.y,
                            me.vertices[0].co.z+12]
            tar.location = [me.vertices[-1].co.x,
                            me.vertices[-1].co.y,
                            me.vertices[0].co.z+16]
            toggleCam(self.vantageCam, adaptGrass=False)
            makeScratchfile(vantagePath, "vector")

        except:
            print ("vantage not imported")

    def trails(self,trailPath, CRS):

        if bpy.data.objects.get(self.trail):
            selectOnly(self.trail, delete=True)
        try:

            bpy.ops.importgis.shapefile(filepath=trailPath, shpCRS=CRS)
            if bpy.ops.object.mode_set.poll():

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.remove_doubles()
                bpy.ops.mesh.select_all(action='SELECT')
                #bpy.ops.mesh.vertices_smooth()
                #bpy.ops.mesh.vertices_smooth()

                bpy.context.space_data.cursor_location = (-440, 29, 34)
                bpy.ops.mesh.sort_elements(type='CURSOR_DISTANCE',
                                           elements={'VERT'})
                bpy.ops.object.mode_set(mode='OBJECT')
                shrinkRaster2Obj(self.trail, self.plane,
                                 method='NEAREST_SURFACEPOINT',
                                 offset=1.5, delModifier=False)

                bpy.ops.object.convert(target='CURVE')
                bpy.context.object.data.bevel_object = \
                    bpy.data.objects["T_profile"]
                bpy.context.object.data.twist_mode = 'Z_UP'
                bpy.context.object.data.twist_smooth = 10
                obj = bpy.data.objects[self.trail]
                obj.location[2]= obj.location[2] + 1

                mat = self.engine[0] + ".boardwalk"
                changeMat(self.trail, mat)
                smooth(self.trail, .18,2)
                makeScratchfile(trailPath, "vector")

                return "imported"
        except:
            print ("Camera trajectory import unsucsessfull")

    def treePatchFill_old(self, patch, watchFolder):

        # import patchShapefile #
        try:
            patchPath = os.path.join(watchFolder, patch)
            bpy.ops.importgis.shapefile(filepath=patchPath,
                                        shpCRS=CRS)

            # get patch type and index #

            objName = bpy.context.scene.objects.active.name
            specieType = self.realism + "_" + objName.split("_")[1]

            # calculate number of species based on density and
            # apply particle system #
            selectOnly(objName)
            mat = self.engine[0] + ".Transparent"
            changeMat(objName, mat)

            area = calcArea(objName)
            if area < 400:
                count = 1
                specieType= specieType + "_single"
            elif area > 400 and area < 900:
                count = 2
            elif area > 900 and area < 1200:
                count = 3
            else:
                count = area/300

            if specieType == "class3":
                particle(objName, specieType,
                         area/100, group=True)
            else:
                particle(objName, specieType, count, group=True)

            makeScratchfile(patchPath, "vector")

            return "imported"

        except:
            print ("tree drawing failed")

    def treePatchFill(self, patch, watchFolder):
        print ("received")

                        # import patchShapefile #
                        #try:
        patchPath = os.path.join(watchFolder, patch)
        patchType = patch.split("_")[1]
        textureName = "particle_" + patchType
        img = bpy.data.images.load(patchPath)
        specieType = self.realism + "_" + patchType

        if patchType == "class3":
            density = 700
        else:
            density = 500

        if textureName not in bpy.data.textures:
            bpy.data.textures.new(textureName, type='IMAGE')
        bpy.data.textures[textureName].image = img
            #self.terrain.particle_systems[0].name = patchType

        if patchType in self.terrain.particle_systems:
            self.terrain.particle_systems[patchType].settings.\
            active_texture = bpy.data.textures[textureName]
        else:
            particle(self.plane, specieType, density, group=True,
            particle_name=patchType, texture=textureName )


            return "imported"

class ModalTimerOperator(bpy.types.Operator):
        """Operator which interatively runs from a timer"""

        bl_idname = "wm.modal_timer_operator"
        bl_label = "Modal Timer Operator"
        _timer = 0
        _timer_count = 0

        def modal(self, context, event):
            if event.type in {"RIGHTMOUSE", "ESC"}:
                return {"CANCELLED"}

            # this condition encomasses all the actions required for watching
            # the folder and related file/object operations .

            if event.type == "TIMER":

                if self._timer.time_duration != self._timer_count:
                    self._timer_count = self._timer.time_duration
                    fileList = (os.listdir(self.prefs.watchFolder))

                    if terrainFile in fileList:
                        self.adapt.terrainChange(self.prefs.terrainPath,self.prefs.CRS)
                        self.adaptMode = "TERRAIN"

                    if waterFile in fileList:
                        self.adapt.waterFill(self.prefs.waterPath, self.prefs.CRS)
                        self.adaptMode = "WATER"

                    if textureFile in fileList:
                        selectOnly(self.plane)
                        self.adapt.textureM()
                        self.adaptMode = "TEXTURE"

                    if trailFile in fileList:
                        self.adapt.trails(self.prefs.trailPath, self.prefs.CRS)
                        self.adaptMode = "TRAIL"

                    if emptyFile in fileList:
                        if self.terrain.particle_systems:
                                for i in self.terrain.modifiers:
                                    if "Particle" in i.name:
                                        self.terrain.modifiers.remove(i)
                        makeScratchfile(self.prefs.emptyPath, "text")

                    if vantageFile in fileList:
                        self.adapt.vantageShp(self.prefs.vantagePath, self.prefs.CRS)
                        self.adaptMode = "VANTAGE"

                    # Multiple Instance objects #

                    # Tree patches #
                    for fileName in fileList:
                        if(
                            fileName.startswith("patch_") and
                            fileName[-4:] == ".png" and
                            fileName not in bpy.data.images):
                            self.adapt.treePatchFill(fileName, self.prefs.watchFolder)
                            self.adaptMode = "PATCH"


            return {"PASS_THROUGH"}

        def execute(self, context):

            bpy.context.space_data.show_manipulator = False
            wm = context.window_manager
            wm.modal_handler_add(self)

            self.treePatch = "TreePatch"
            self.emptyTree = "empty.txt"
            self.terrain = bpy.data.objects["terrain"]
            self.adaptMode = None
            self.prefs = Prefs()
            self.adapt = Adapt()
            self.adapt.realism = "High"
            self._timer = wm.event_timer_add(self.prefs.timer, context.window)

            for file in os.listdir(self.prefs.watchFolder):
                try:
                    os.remove(os.path.join(self.prefs.watchFolder, file))
                except:
                    print("Could not remove file")

            for img in bpy.data.images:
                if "patch_" in img.name:
                    bpy.data.images.remove(img, do_unlink=True)

            for i in self.terrain.modifiers:
                if "Particle" in i.name:
                    self.terrain.modifiers.remove(i)


            return {"RUNNING_MODAL"}

        def cancel(self, context):
            wm = context.window_manager
            wm.event_timer_remove(self._timer)


class BirdCam(bpy.types.Operator):

    """switch to user camera mode and runs animation walkthrough """

    bl_idname = "wm.birdcam"
    bl_label = "toggle_through_Birdviews"

    def execute(self, context):

        toggleCam("Bird_", adaptGrass=False)

        return {'FINISHED'}


class HumanCam(bpy.types.Operator):

    """switch to user camera mode and runs animation walkthrough """

    bl_idname = "wm.humancam"
    bl_label = "toggle_through_Birdviews"

    def execute(self, context):

        toggleCam("Human_", adaptGrass=False)

        return {'FINISHED'}


class RotaryCam(bpy.types.Operator):

    """switch to user camera mode and runs animation walkthrough """

    bl_idname = "wm.rotarycam"
    bl_label = "rotating_bird_view"

    def execute(self, context):

        toggleCam("Rotary_")
        bpy.ops.screen.animation_play()

        return {'FINISHED'}


class VantageCam(bpy.types.Operator):

    """switch to user camera mode and runs animation walkthrough """

    bl_idname = "wm.vantagecam"
    bl_label = "user_defined_views"

    def execute(self, context):

        toggleCam("VantageCam", adaptGrass=True)
        return {'FINISHED'}


class mist(bpy.types.Operator):

    bl_idname = "wm.mist"
    bl_label = "mist_creator"

    def execute(self, context):
        if not bpy.context.scene.world.mist_settings.use_mist:
            bpy.context.scene.world.mist_settings.use_mist = True
            return {'FINISHED'}

        if bpy.context.scene.world.mist_settings.use_mist:
            bpy.context.scene.world.mist_settings.use_mist = False
            return {'FINISHED'}

class Object_operators(bpy.types.Operator):
    bl_idname = "objects.operator"
    bl_label = "Object Operators"
    button = bpy.props.StringProperty()

    def execute(self, context):

        world = bpy.context.scene.world.name
        realism = world.split(".")[1]

        if self.button == "TREES":
            for i in bpy.data.objects["terrain"].modifiers:
                if "Particle" in i.name:
                    bpy.data.objects["terrain"].modifiers.remove(i)

        elif self.button == "TRAIL":
            remove("trail")

        return{'FINISHED'}


class Engine_buttons(bpy.types.Operator):
    bl_idname = "render.engine"
    bl_label = "Change render Engine"
    engineButton = bpy.props.StringProperty()

    def execute(self, context):

        engine = bpy.context.scene.render.engine
        world = bpy.context.scene.world.name
        realism = world.split(".")[1]

        if self.engineButton == "BLENDER_RENDER":

            if realism == "High" and engine != "BLENDER_RENDER" :
                Adapt().changeEngine("BLENDER_RENDER",real=realism)
                self.mode = "BLENDER_RENDER"
                Adapt().realism = realism
                Adapt().engine = "BLENDER_RENDER"
                Adapt().UpdateWorld("BLENDER_RENDER", "High")

            else:
                bpy.ops.error.message('INVOKE_DEFAULT',
                                      type = "Error",
                                      message = "Blender renderer can be only used in realistic mode")

        elif self.engineButton == 'CYCLES':

            if engine != "CYCLES":

                Adapt().changeEngine("CYCLES", real=realism)
                Adapt().engine= "CYCLES"
                Adapt().realism = realism
                Adapt().UpdateWorld("CYCLES", realism)

        elif self.engineButton == 'Low':

            if engine == "CYCLES":
                Adapt().changeEngine(engine,real = 'Low')
                Adapt().changeRealism("Low")
                Adapt().UpdateWorld("CYCLES",'Low')
            else:
                bpy.ops.error.message('INVOKE_DEFAULT',
                                      type = "Error",
                                      message = "Low poly rendering can be only used in Cycles renderer")

        elif self.engineButton == 'High':

            Adapt().changeEngine(engine,real = 'High')
            Adapt().changeRealism("High")
            Adapt().realism = "High"
            Adapt().UpdateWorld(engine,'High')

        if self.engineButton == "Render":
            bpy.context.space_data.viewport_shade = 'RENDERED'

        return{'FINISHED'}

# Panel
class TLGUI(bpy.types.Panel):
    # Create a Panel in the Tool Shelf
    bl_category = "Tangible Landscape"
    bl_label = "Tangibe Landscape "
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    # Draw
    def draw(self, context):

        layout = self.layout
        wm = context.window_manager
        # scene = context.scene
        box = layout.box()
        box.label('System options')
        row = box.row(align=True)
        row.operator("wm.modal_timer_operator",
                     text="Turn on Watch Mode",
                     icon="GHOST_ENABLED")

        # Camera Options #

        box = layout.box()
        box.alignment = 'CENTER'
        box.label('Camera options', icon="CAMERA_DATA")
        row = box.row(align=True)
        row.operator("wm.vantagecam",
                     text="Tangibly selected views",
                     icon="MAN_TRANS")
        row = box.row(align=True)
        row.operator("wm.humancam", text="Preset Human views", icon="SCENE")
        row = box.row()
        row.operator("wm.birdcam", text="Preset Birdviews", icon="HAIR")
        row = box.row()
        row.operator("wm.rotarycam",
                     text="Orbiting bird view",
                     icon="BORDER_LASSO")

        box = layout.box()
        box.label('Atomospheric adjustments')

        row4 = box.row()
        row4.operator("wm.mist", text="Toggle Mist", icon="FORCE_TURBULENCE")

        box = layout.box()
        box.label('Object operations')

        row1 = box.row()
        row1.operator("objects.operator", text="Remove trees").button = "TREES"
        row2 = box.row()
        row2.operator("objects.operator", text="Trail").button = "TRAIL"
        box = layout.box()

        box.label('Rendering and Realism')
        box.alignment = 'CENTER'
        row4 = box.row()
        row4.operator("render.engine",
                      text="Blender").engineButton = "BLENDER_RENDER"
        row4.operator("render.engine",
                      text="Cycles").engineButton = "CYCLES"
        row4.operator("render.engine",
                      text="Render").engineButton = "Render"

        row5 = box.row()
        row5.label("Realism")
        row6 = box.row()
        row6.operator("render.engine",
                      text="Low poly").engineButton = "Low"
        row6.operator("render.engine",
                      text="Realistic").engineButton = "High"

        layout.row().separator()

class MessageOperator(bpy.types.Operator):
    bl_idname = "error.message"
    bl_label = "Message"
    type = StringProperty()
    message = StringProperty()

    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width= 400, height=1000)

    def draw(self, context):
        self.layout.label(self.message)


def register():

    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

# def register(module):

if __name__ == "__main__":
    # register all Classes
    register()
