import bpy
import os
import subprocess

def convert_and_import_dicom(dicom_directory, iso_value=400, reduction=None, polygon_limit=None, remove_small_parts=None, center=False, smooth=False, output_format='stl'):
    # Абсолютный путь к dicom2mesh.exe
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dicom2mesh_path = os.path.join(script_dir, "dicom2mesh", "dicom2mesh.exe")

    # Определите выходной файл
    output_file = os.path.join(script_dir, "dicom2mesh", "output." + output_format)

    # Создайте команду для dicom2mesh
    cmd = [dicom2mesh_path, "-i", dicom_directory, "-o", output_file, "-t", str(iso_value)]

    if reduction:
        cmd.extend(["-r", str(reduction)])
    
    if polygon_limit:
        cmd.extend(["-p", str(polygon_limit)])

    if remove_small_parts:
        cmd.extend(["-e", str(remove_small_parts)])

    if center:
        cmd.append("-c")

    # Вызовите dicom2mesh
    subprocess.run(cmd)

    # Если smooth включен, загрузите и сгладьте меш в Blender
    if output_format == 'stl':
        bpy.ops.wm.stl_import(filepath=output_file)  # Corrected operator
    elif output_format == 'obj':
        bpy.ops.import_scene.obj(filepath=output_file)
    # и так далее для других форматов...

    # Масштабирование объекта
    obj = bpy.context.active_object
    obj.scale = (0.001, 0.001, 0.001)

    if smooth:
        mod = obj.modifiers.new(name="Smooth", type='SMOOTH')
        mod.factor = 1
        mod.iterations = 2  # можно установить количество итераций или другие параметры здесь

    # Удаление файла после его импорта
    os.remove(output_file)

    return bpy.context.active_object
