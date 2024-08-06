import bpy
from .operators import SimpleOperator1, SimpleOperator2, CreatePipeInstanceOperator, PlacePipeOnSurfaceOperator, ImportDicomOperator, SurfaceToIsoscelesTrianglesOperator

class PipePlacer_PT_panel(bpy.types.Panel):
    bl_label = "Pipe Placer"
    bl_idname = "PIPEPLACER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PipePlacer'

    def draw(self, context):
        layout = self.layout

        # Added section
        box = layout.box()
        box.label(text="Загрузка данных:")

        col = box.column(align=True)
        col.prop(context.scene, "import_directory", text="Директория")
        col.prop(context.scene, "threshold_value", text="Threshold")
        col.operator(ImportDicomOperator.bl_idname, text="Создать объект")

        # Remaining code
        layout.operator(SimpleOperator1.bl_idname, text="Выбор области")
        layout.operator(SimpleOperator2.bl_idname, text="Копировать выбранную область")
        layout.operator(PlacePipeOnSurfaceOperator.bl_idname, text="Разместить трубки")
        layout.prop(context.scene, "invert_normal", text="Инвертировать нормаль")
        layout.operator(SurfaceToIsoscelesTrianglesOperator.bl_idname, text="Subdivide")

        box = layout.box()
        box.label(text="Параметры трубки:")

        col = box.column(align=True)
        col.prop(context.scene, "inner_radius", text="Внутренний радиус")
        col.prop(context.scene, "outer_radius", text="Внешний радиус")
        col.prop(context.scene, "length", text="Длина")

def register_panels():
    bpy.utils.register_class(PipePlacer_PT_panel)

def unregister_panels():
    bpy.utils.unregister_class(PipePlacer_PT_panel)
