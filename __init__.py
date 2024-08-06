bl_info = {
    "name": "Surface Pipe Placer",
    "blender": (4, 2, 0),
    "category": "Object",
    "version": (1, 0, 0),
    "location": "Viewport > N-Panel",
    "description": "Place pipes on a surface based on maximum area relative to surface normal",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
}

import bpy
from . import operators, panels, properties

def register():
    panels.register_panels() 
    properties.register_properties()
    operators.register_operators()

def unregister():
    panels.unregister_panels()
    properties.unregister_properties()
    operators.unregister_operators()
    
if __name__ == "__main__":
    register()
