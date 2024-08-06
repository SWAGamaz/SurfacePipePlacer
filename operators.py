import bpy
import bmesh
from mathutils import Vector
from math import sqrt
from .utils import find_best_points, find_potential_position, is_intersecting
from .dicom_handler import convert_and_import_dicom

class PlacePipeOnSurfaceOperator(bpy.types.Operator):
    bl_idname = "object.place_additional_pipe"
    bl_label = "Place Additional Pipe"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Ensure an object is selected
        if not context.active_object or context.active_object.type != "MESH":
            self.report({'WARNING'}, "Please select a mesh object!")
            return {'CANCELLED'}

        # Ensure the object is in edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Get the selected object and its first vertex
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()  # Ensure the lookup table is valid
        first_vertex = bm.verts[0]
        vertex_location = obj.matrix_world @ first_vertex.co
        vertex_normal = first_vertex.normal

        # Invert the normal if the property is set to True
        if context.scene.invert_normal:
            vertex_normal = -vertex_normal

        # Create the initial pipe
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.create_pipe_instance()  # Adjust the operator call to match the new class name
        first_pipe = context.active_object

        # Orient and place the first pipe according to the vertex
        first_pipe.location = vertex_location
        aligning_vector = Vector((0, 0, 1))
        rotation_quat = aligning_vector.rotation_difference(vertex_normal)
        first_pipe.rotation_euler = rotation_quat.to_euler()

        # Calculate the potential location for the second pipe
        outer_radius = bpy.context.scene.outer_radius * 0.001

        # Collect global vertices of the object
        global_vertices = [(obj.matrix_world @ v.co, obj.matrix_world @ v.normal) for v in obj.data.vertices]

        # Place the second pipe (similar to the first, but finding the best vertex)
        best_vert = find_potential_position([vertex_location], global_vertices, outer_radius)
        if not best_vert:
            self.report({'WARNING'}, "Couldn't find a suitable location for the second pipe!")
            return {'CANCELLED'}
        bpy.ops.object.create_pipe_instance()
        second_pipe = context.active_object
        second_pipe.location = best_vert
        best_vert_normal = [vert[1] for vert in global_vertices if vert[0] == best_vert][0]
        if context.scene.invert_normal:
            best_vert_normal = -best_vert_normal
        rotation_quat_second = aligning_vector.rotation_difference(best_vert_normal)
        second_pipe.rotation_euler = rotation_quat_second.to_euler()

        # Storing initial pipes and their pairs
        pipe_locations = [first_pipe.location, second_pipe.location]
        checked_pairs = set()

        ideal_distance = outer_radius * 2
        tolerance = 0.01

        # Precollect vertex data in a dictionary for fast access
        vertex_dict = {(vert[0].x, vert[0].y, vert[0].z): vert[1] for vert in global_vertices}

        for _ in range(6):
            new_pipes_added = False

            # Save indices and values instead of recreating the list of potential pairs
            potential_pairs = [(i, j, p1, p2) for i, p1 in enumerate(pipe_locations) for j, p2 in enumerate(pipe_locations)
                               if i < j and (i, j) not in checked_pairs and ideal_distance - tolerance < (p1 - p2).length < ideal_distance + tolerance]

            for i, j, p1, p2 in potential_pairs:
                checked_pairs.add((i, j))

                best_third_position, best_fourth_position = find_best_points(p1, p2, outer_radius, global_vertices)

                for position in [best_third_position, best_fourth_position]:
                    if position and all(not is_intersecting(pipe_pos, position, outer_radius) for pipe_pos in pipe_locations):
                        bpy.ops.object.create_pipe_instance()
                        new_pipe = context.active_object
                        new_pipe.location = position
                        position_normal = vertex_dict[(position.x, position.y, position.z)]
                        if context.scene.invert_normal:
                            position_normal = -position_normal
                        rotation_quat = aligning_vector.rotation_difference(position_normal)
                        new_pipe.rotation_euler = rotation_quat.to_euler()

                        pipe_locations.append(new_pipe.location)
                        new_pipes_added = True

            if not new_pipes_added:
                break

        return {'FINISHED'}

# Оператор для перехода в режим редактирования
class SimpleOperator1(bpy.types.Operator):
    bl_idname = "object.simple_operator1"
    bl_label = "Enter Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not context.active_object or context.active_object.type != "MESH":
            self.report({'WARNING'}, "Please select a mesh object!")
            return {'CANCELLED'}
        
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}


# Оператор для копирования выбранных полигонов
class SimpleOperator2(bpy.types.Operator):
    bl_idname = "object.simple_operator2"
    bl_label = "Copy Selected Polygons"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode != 'EDIT_MESH':
            self.report({'WARNING'}, "Please be in Edit Mode and select polygons!")
            return {'CANCELLED'}
        
        bpy.ops.mesh.duplicate()
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

# Оператор для создания труб
class CreatePipeInstanceOperator(bpy.types.Operator):
    bl_idname = "object.create_pipe_instance"
    bl_label = "Create Pipe Instance"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        inner_radius = context.scene.inner_radius
        outer_radius = context.scene.outer_radius
        length = context.scene.length

        bpy.ops.mesh.primitive_cylinder_add(radius=outer_radius * 0.001, depth=length * 0.001, location=(0, 0, 0))
        outer_cylinder = context.active_object

        bpy.ops.mesh.primitive_cylinder_add(radius=inner_radius * 0.001, depth=length * 0.001 + 0.2, location=(0, 0, 0))
        inner_cylinder = context.active_object

        # Move vertices down
        for cyl in [outer_cylinder, inner_cylinder]:
            bpy.ops.object.select_all(action='DESELECT')
            cyl.select_set(True)
            context.view_layer.objects.active = cyl
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.translate(value=(0, 0, -length * 0.001 / 2))
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')
        outer_cylinder.select_set(True)
        context.view_layer.objects.active = outer_cylinder
        bpy.ops.object.modifier_add(type='BOOLEAN')
        mod = outer_cylinder.modifiers[-1]
        mod.operation = 'DIFFERENCE'
        mod.object = inner_cylinder
        bpy.context.view_layer.objects.active = outer_cylinder  # Ensure the correct context
        bpy.ops.object.modifier_apply(modifier=mod.name)  # Simplified the context
        bpy.ops.object.select_all(action='DESELECT')
        inner_cylinder.select_set(True)
        bpy.ops.object.delete()

        return {'FINISHED'}

class ImportDicomOperator(bpy.types.Operator):
    bl_idname = "import.dicom"
    bl_label = "Import DICOM Directory"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dir_to_import = context.scene.import_directory
        
        if not dir_to_import:
            self.report({'ERROR'}, "No directory specified!")
            return {'CANCELLED'}
        
        # Загрузите серии DICOM
        convert_and_import_dicom(dir_to_import, iso_value=context.scene.threshold_value, center=True, smooth=True, reduction=0.8, remove_small_parts=0.05)

        self.report({'INFO'}, f"DICOM imported from {dir_to_import}")
        return {'FINISHED'}
    
class SurfaceToIsoscelesTrianglesOperator(bpy.types.Operator):
    bl_idname = "object.surface_to_isosceles_triangles"
    bl_label = "Convert Surface to Isosceles Triangles"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Ensure we're in edit mode and have a mesh object
        if context.mode != 'EDIT_MESH' or not context.active_object or context.active_object.type != 'MESH':
            self.report({'WARNING'}, "Please select a mesh object and be in Edit Mode.")
            return {'CANCELLED'}

        # Get the mesh data
        obj = context.active_object
        mesh = bmesh.from_edit_mesh(obj.data)
        
        # Ensure we have selected faces
        selected_faces = [f for f in mesh.faces if f.select]
        if not selected_faces:
            self.report({'WARNING'}, "Please select faces to convert.")
            return {'CANCELLED'}
        
        # Get the edge length from the user
        edge_length = context.scene.edge_length
        
        # Subdivide the selected faces
        bmesh.ops.subdivide_edges(mesh, edges=[e for e in mesh.edges if e.select], cuts=4, use_grid_fill=True)
        
        # Triangulate the faces
        bmesh.ops.triangulate(mesh, faces=selected_faces)
        
        # Convert triangles to isosceles triangles
        self.convert_to_isosceles(mesh, selected_faces, edge_length)
        
        bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}
    
    def convert_to_isosceles(self, mesh, faces, edge_length):
        for face in faces:
            if len(face.verts) == 3:
                v1, v2, v3 = face.verts
                center = (v1.co + v2.co + v3.co) / 3
                
                # Calculate new vertices to form isosceles triangles
                edge1 = (v1.co + v2.co) / 2
                edge2 = (v2.co + v3.co) / 2
                edge3 = (v3.co + v1.co) / 2
                
                # Remove the original face
                bmesh.ops.delete(mesh, geom=[face], context='FACES')
                
                # Create new faces forming isosceles triangles
                new_faces = [
                    (v1.co, edge1, center),
                    (v2.co, edge1, center),
                    (v2.co, edge2, center),
                    (v3.co, edge2, center),
                    (v3.co, edge3, center),
                    (v1.co, edge3, center)
                ]
                
                for verts in new_faces:
                    verts = [mesh.verts.new(v) for v in verts]
                    mesh.faces.new(verts)
        
        mesh.normal_update()
        bmesh.ops.recalc_face_normals(mesh, faces=mesh.faces)
    
def register_operators():
    bpy.utils.register_class(PlacePipeOnSurfaceOperator)
    bpy.utils.register_class(SimpleOperator1)
    bpy.utils.register_class(SimpleOperator2)
    bpy.utils.register_class(CreatePipeInstanceOperator)
    bpy.utils.register_class(ImportDicomOperator)
    bpy.utils.register_class(SurfaceToIsoscelesTrianglesOperator)

def unregister_operators():
    bpy.utils.unregister_class(PlacePipeOnSurfaceOperator)
    bpy.utils.unregister_class(SimpleOperator1)
    bpy.utils.unregister_class(SimpleOperator2)
    bpy.utils.unregister_class(CreatePipeInstanceOperator)
    bpy.utils.unregister_class(ImportDicomOperator)
    bpy.utils.unregister_class(SurfaceToIsoscelesTrianglesOperator)