# Real-time 3D modeling and immersion with Tangibles
![abstract](https://github.com/tangible-landscape/tangible-landscape-immersive-extension/documentation/img/Photo_collage.jpg)

## Abstract

We have paired GRASS GIS with Blender, a state-of-the-art 3D modeling
and rendering program, to allow real-time 3D rendering and immersion with Tangible Landscape. Tangible Landscape is a tangible interface for geographic information systems (GIS). It interactively couples physical and digital models of a landscape so that users can intuitively explore, model, and analyze geospatial data in a collaborative environment. Conceptually Tangible Landscape lets users hold a GIS in their hands so that they can feel the shape of the topography, naturally sculpt new landforms, and interact with simulations like water flow. As users manipulate a tangible model with topography and objects, geospatial analyses and simulations are projected onto the tangible model and perspective views are realistically rendered on monitors and head-mounted displays (HMDs) in near real-time. Users can visualize in near real-time the changes they are making with either bird’seye views or perspective views from human vantage points. While geospatial data is typically visualized as maps, axonometric views, or bird’s-eye views, human-scale perspective views help us to understand how people would experience and perceive spaces within the landscape.


#### How it works ####
Blender and GRASS GIS are loosely coupled through file-based communication established via a local wireless or Ethernet connection. GRASS GIS exports the spatial data as a standard raster, a vector, or a text file containing coordinates into a specified directory typically called Watch (Figure setup). The Tangible Landscape Blender plugin (modeling3D.py)—implemented and executed inside Blender— constantly monitors the directory for incoming information. Examples of spatial data include a terrain surface (raster), water bodies (3D polygons or rasters), forest patches
(3D polygons), a camera location (3D polyline, text file), and routes (3D polylines).
Upon receiving this information, the file is imported using the BlenderGIS add-on.
Then the relevant modeling and shading procedures for updating an existing 3D
object or creating a new 3D object are applied. The adaptation procedure applied
depends upon the type of spatial data and is handled by a module called adapt. All
3D elements in the scene (i.e. objects, lights, materials, and cameras) reside in a
Blender file (modeling3D.blend).

![Immersive extension GUI](https://github.com/tangible-landscape/tangible-landscape-immersive-extension/blob/master/blob/blender_gui_1.PNG)


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
  * In the Coordinate reference system field type in the 4 digit EPSG code related to your GIS dataset. The provided examples use 3358.
  * Click on Save User Settings on the bottom left corner of user preferences
#### 2. Installing and setting up Blender virtual_reality_viewport addon
  * Install and activate BlenderGIS addon (for detailed instruction see [BlenderGIS wiki](https://github.com/domlysz/BlenderGIS/wiki/Install-and-usage))
  * Go to Preferences > BlenderGIS preferences > Spatial reference system > add your EPSG 4 digit code and a description  (e.g., 3358 , NAD 1983)
  * From the Import/Export panel deactivate Zoom to mouse and Lock options.
  * Click on Save User Settings on the bottom left corner of user preferences
#### 3. Installing and setting up Blender virtual_reality_viewport addon
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
