# Tangible Landscape Immersive Extension

## Abstract
Tangible Landscape is a tangible interface for geographic information systems (GIS). It interactively couples physical and digital models of a landscape so that users can intuitively explore, model, and analyze geospatial data in a collaborative environment. Conceptually Tangible Landscape lets users hold a GIS in their hands so that they can feel the shape of the topography, naturally sculpt new landforms, and interact with simulations like water flow.
Since it only affords a bird's-eye view of the landscape, we coupled it with an immersive virtual environment so that users can virtually walk around the modeled landscape and visualize it at a human-scale. Now as users shape topography, draw trees, define viewpoints, or route a walkthrough they can see the results on the projection-augmented model, rendered on a display, or rendered on a head-mounted display.

## Dependencies
-   Blender (https://www.blender.org/download/)
-   Blender virtual_reality_viewport addon (https://github.com/dfelinto/virtual_reality_viewport)
-   BlenderGIS addon (https://github.com/domlysz/BlenderGIS)

## Installation
Note : Tangible Landscape should be setup and installed before installing the extension.
see https://github.com/tangible-landscape/grass-tangible-landscape/blob/master/README.md

1.  Most recent Blender build 
2.  Install Blender virtual_reality_viewport addon 
3.  Install BlenderGIS addon 
4.  Download the repository into a new folder and run blender
5.  Open immersive_extention.blend in blender 
6.  Activate both of the installed addons in Blender-preferences-addon menu
7.  Load and run the immersive_extension.py in blender scripting environment . You should be able to see the Tangible Landscape gui on the 3d view toolbar 
8.  From the gui click "turn on watch mode"
9.  For testing the functionality copy the point.ply from sample_data folder to the Watch folder. You should be able to see the geometry changed. 

![Immersive extension GUI](https://github.com/tangible-landscape/tangible-landscape-immersive-extension/blob/master/blob/blender_gui_1.PNG)
