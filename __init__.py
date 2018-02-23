# -*- coding:utf-8 -*-

#  ***** GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****\

bl_info = {
 "name": "Tangible Landscape Addon",
 "author": "Payam Tabrizian (ptabriz)",
 "version": (1, 0),
 "blender": (2, 7, 9),
 "location": "Tools",
 "description": "Real-time 3D modeling with Tangible Landscape",
 "warning": "",
 "wiki_url": "https://github.com/ptabriz/tangible-landscape-immersive-extension/blob/master/README.md",
 "tracker_url": "",
 "category": "view_3D"}

import bpy, os
import addon_utils
from . import prefs
from . import Modeling3D
from .settings import getSettings, setSettings

def register():

    bpy.utils.register_module(__name__) #register all imported operators of the current
    prefs = bpy.context.user_preferences.addons[__package__].preferences

def unregister():

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
