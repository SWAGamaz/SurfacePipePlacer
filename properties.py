import bpy

# Определения свойств
def register_properties():
    bpy.types.Scene.inner_radius = bpy.props.FloatProperty(name="Inner Radius", default=3, min=1)
    bpy.types.Scene.outer_radius = bpy.props.FloatProperty(name="Outer Radius", default=5, min=1)
    bpy.types.Scene.length = bpy.props.FloatProperty(name="Length", default=20, min=1)
    bpy.types.Scene.import_directory = bpy.props.StringProperty(name="Import Directory", default="", subtype='DIR_PATH')
    bpy.types.Scene.threshold_value = bpy.props.FloatProperty(name="Threshold Value", default=-650, min=-3500, max=5000)
    bpy.types.Scene.invert_normal = bpy.props.BoolProperty(name="Invert Normal", description="Invert the normal direction of the vertex for pipe placement",default=True)

def unregister_properties():
    del bpy.types.Scene.inner_radius
    del bpy.types.Scene.outer_radius
    del bpy.types.Scene.length
    del bpy.types.Scene.import_directory
    del bpy.types.Scene.threshold_value
    del bpy.types.Scene.invert_normal
