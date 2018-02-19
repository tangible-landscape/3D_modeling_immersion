import bpy,json
from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty, FloatVectorProperty
from bpy.types import Operator, Panel, AddonPreferences
import addon_utils
from . import bl_info
from .settings import getSettings, setSettings
PKG = __package__


class TL_PREFS_SHOW(bpy.types.Operator):

    bl_idname = "TL.pref_show"
    bl_description = 'Display Tangible landscape addon preferences'
    bl_label = "Preferences"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        addon_utils.modules_refresh()
        bpy.context.user_preferences.active_section = 'ADDONS'
        bpy.data.window_managers["WinMan"].addon_search = bl_info['name']
        #bpy.ops.wm.addon_expand(module=PKG)
        mod = addon_utils.addons_fake_modules.get(PKG)
        mod.bl_info['show_expanded'] = True
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        return {'FINISHED'}

class TL_PREFS(AddonPreferences):

    bl_idname = PKG
    def updateFolder(self, context):
        prefs = getSettings()
        prefs['folder'] = self.Folder
        setSettings(prefs)

    def updateCRS(self, context):
        prefs = getSettings()
        prefs['CRS'] = self.CRS
        setSettings(prefs)

    def updateTime(self, context):
        prefs = getSettings()
        prefs['timer'] = self.Timer
        setSettings(prefs)

    Folder = StringProperty(
        name = "Cache folder",
        default = getSettings()['folder'],
        description = "Define a folder where the Blender File is located (e.g., Modeling3D.blend)",
        subtype = 'DIR_PATH',
        update = updateCRS
        )

    CRS = StringProperty(
        name = "Coordinate Reference System",
        default = getSettings()['CRS'],
        description = "Type in EPSG code of the file Georeferene system e.g., 4328",
        subtype = 'NONE',
        update = updateTime
        )
    Timer = IntProperty(
        name = "Update speed",
        default = 1,
        description = "Type in number of updates per seconds: This would increase the update rate at the expense of performance",
        subtype = 'NONE',
        update = updateFolder
        )

    fontColor = FloatVectorProperty(
        name="Font color",
        subtype='COLOR',
        min=0, max=1,
        size=4,
        default=(0, 0, 0, 1)
        )

    def draw(self, context):

        layout = self.layout
        #Basemaps
        box = layout.box()
        box.label('Preferences')
        box.prop(self, "Folder")
        box.prop(self, "CRS")
        box.prop(self, "Timer")
