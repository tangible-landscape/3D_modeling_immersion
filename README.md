# Tangible Landscape Immersive Extension

## Abstract
Tangible Landscape is a tangible interface for geographic information systems (GIS). It interactively couples physical and digital models of a landscape so that users can intuitively explore, model, and analyze geospatial data in a collaborative environment. Conceptually Tangible Landscape lets users hold a GIS in their hands so that they can feel the shape of the topography, naturally sculpt new landforms, and interact with simulations like water flow.
Since it only affords a bird's-eye view of the landscape, we coupled it with an immersive virtual environment so that users can virtually walk around the modeled landscape and visualize it at a human-scale. Now as users shape topography, draw trees, define viewpoints, or route a walkthrough they can see the results on the projection-augmented model, rendered on a display, or rendered on a head-mounted display.

## Dependencies
-   [Blender](https://www.blender.org/download/)
-   [Blender virtual_reality_viewport addon](https://github.com/dfelinto/virtual_reality_viewport)
-   [BlenderGIS addon](https://github.com/domlysz/BlenderGIS)

## Installation
Note : Tangible Landscape should be setup and installed before installing the extension.
[see](https://github.com/tangible-landscape/grass-tangible-landscape/blob/master/README.md)

#### 1. Installing and setting up Tangible landscape addon in Blender
  * Open Blender user preferences (Alt + Ctrl + U) > Go to add-ons tab > Install from file (bottom center of the panel) > locate TL_addon.zip > press enter
  * Select on the addon to activate it.
  * In the Preferences tab > Coupling folder > browse and locate TL_coupling folder (e.g, D:/TL_coupling)
#### 2. Installing and setting up Blender virtual_reality_viewport addon

  * Install and activate BlenderGIS addon (for detialed instruction see [BlenderGIS wiki](https://github.com/domlysz/BlenderGIS/wiki/Install-and-usage))
  * Go to Preferences > BlenderGIS preferences > Spatial reference system > add your EPSG 4 digit code and a description  (e.g., 3358 , NAD 1983)
  * From the Import/Export panel deactivate Zoom to mouse and Lock options.
  * Click on Save User Settings on the bottom left corner of user preferences
5.
4. Open modelling3D.blend in blender
5. Activate both of the installed addons in Blender-preferences-addon menu
6. Load and run the immersive_extension.py in blender scripting environment You should be able to see the Tangible Landscape gui on the 3d view toolbar
7. From the gui click "turn on watch mode"
8. Go to preferences > blenderGIS
#### Testing the blender component
* Inside the test folder you can find the following examples:
  * Terrain raster (terrain.tif)
  * Water raster (water.tif)
  * Multiple vantage points (vantage.shp)
  * 4 tree patches (patch_class1.png, patch_class2.png, patch_class3.png, patch_class2.png)
  * Trail (trail.shp)
* Run the script (Modeling3D.py)
* From Tangible Landscape panel press watch mode
* Copy the test files in one by one starting with the terrain to the Watch folder. You should be able to see the terrain changes constructed.
### Using your own data

![Immersive extension GUI](https://github.com/tangible-landscape/tangible-landscape-immersive-extension/blob/master/blob/blender_gui_1.PNG)
