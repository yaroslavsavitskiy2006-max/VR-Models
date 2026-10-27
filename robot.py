# -*- coding: utf-8 -*-
"""
Скрипт для создания персонажа "Робот" в Blender
Запуск: Scripting -> New -> вставить код -> Run Script (Alt+P)
"""

import bpy
import math
import os


# ====================== ИНСТРУМЕНТАРИЙ ======================
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials):
        for b in list(coll):
            coll.remove(b)


def make_material(name, color, metallic=0.0, roughness=0.6, emission=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 5.0
    return mat


def add_sphere(name, location, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(material)
    return obj


def add_cube(name, location, scale, material, bevel=0.06):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    m = obj.modifiers.new("Bevel", 'BEVEL')
    m.width = bevel
    m.segments = 3
    obj.modifiers.new("Subdiv", 'SUBSURF').levels = 1
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(material)
    return obj


def add_cylinder(name, location, radius, depth, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rotation
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(material)
    return obj


def add_cone(name, location, radius, depth, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rotation
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(material)
    return obj


def setup_scene(bg_color=(0.75, 0.85, 0.95), cam_location=(0, -8, 2.8), cam_pitch_deg=83):
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.02))
    bpy.context.active_object.data.materials.append(make_material("Ground", (0.8, 0.84, 0.8), roughness=0.9))
    bpy.ops.object.light_add(type='AREA', location=(4, -4, 6))
    bpy.context.active_object.data.energy = 900
    bpy.context.active_object.data.size = 6
    bpy.ops.object.light_add(type='AREA', location=(-5, -3, 3))
    bpy.context.active_object.data.energy = 300
    bpy.context.active_object.data.size = 8
    bpy.ops.object.camera_add(location=cam_location)
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(cam_pitch_deg), 0, 0)
    cam.data.lens = 52
    bpy.context.scene.camera = cam
    world = bpy.data.worlds[0]
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (*bg_color, 1.0)


def render(filepath):
    scene = bpy.context.scene
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)


# ========================== СОЗДАНИЕ ПЕРСОНАЖА ==========================
clear_scene()

# Материалы
METAL = make_material("Metal", (0.6, 0.65, 0.7), roughness=0.4, metallic=0.3)
DARK_METAL = make_material("DarkMetal", (0.35, 0.38, 0.42), roughness=0.4, metallic=0.3)
BLACK = make_material("Black", (0.05, 0.05, 0.05), roughness=0.3)
CYAN = make_material("Cyan", (0.2, 0.6, 0.9), roughness=0.3)
RED = make_material("Red", (0.9, 0.2, 0.2), roughness=0.3)

# Корпус и голова
add_cube("Torso", (0, 0, 0.85), (0.7, 0.4, 0.9), METAL)
add_cube("Head", (0, 0, 1.65), (0.5, 0.4, 0.5), METAL)

# Шея
add_cylinder("Neck", (0, 0, 1.32), 0.12, 0.28, DARK_METAL)

# Антенны
add_cylinder("Antenna", (0, 0, 2.00), 0.02, 0.30, DARK_METAL)
add_sphere("Antenna_Ball", (0, 0, 2.17), (0.06, 0.06, 0.06), RED)

# Руки
add_cube("Arm_L", (-0.44, 0, 1.0), (0.18, 0.18, 0.7), METAL)
add_cube("Arm_R", (0.44, 0, 1.0), (0.18, 0.18, 0.7), METAL)
add_cube("Hand_L", (-0.44, 0, 0.56), (0.22, 0.22, 0.18), DARK_METAL)
add_cube("Hand_R", (0.44, 0, 0.56), (0.22, 0.22, 0.18), DARK_METAL)

# Ноги
add_cube("Leg_L", (-0.22, 0, 0.3), (0.18, 0.18, 0.6), METAL)
add_cube("Leg_R", (0.22, 0, 0.3), (0.18, 0.18, 0.6), METAL)
add_cube("Foot_L", (-0.22, -0.05, 0.08), (0.22, 0.26, 0.16), DARK_METAL)
add_cube("Foot_R", (0.22, -0.05, 0.08), (0.22, 0.26, 0.16), DARK_METAL)

# Детали головы
add_cube("Eye_Panel", (0, -0.21, 1.68), (0.38, 0.02, 0.12), BLACK)
add_sphere("Eye_L", (-0.1, -0.22, 1.68), (0.05, 0.05, 0.05), CYAN)
add_sphere("Eye_R", (0.1, -0.22, 1.68), (0.05, 0.05, 0.05), CYAN)
add_cube("Mouth", (0, -0.21, 1.58), (0.18, 0.02, 0.04), BLACK)

# Кнопки на корпусе
add_cylinder("Button1", (0, -0.21, 0.95), 0.04, 0.03, RED, rotation=(math.radians(90), 0, 0))
add_cylinder("Button2", (0, -0.21, 1.05), 0.04, 0.03, CYAN, rotation=(math.radians(90), 0, 0))

# Рендер
setup_scene(bg_color=(0.62, 0.68, 0.76), cam_location=(0, -4.6, 1.30), cam_pitch_deg=87)
bpy.context.scene.camera.data.lens = 50

# Свет мягче: иначе светлый металл выгорает в чистый белый и теряет форму.
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        obj.data.energy *= 0.40

# Пол темнее фона — робот не сливается с землёй.
ground = bpy.data.materials.get("Ground")
if ground:
    ground.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.58, 0.62, 0.66, 1.0)

# Плоская цветокоррекция вместо AgX — иначе светлый металл выглядит серым.
try:
    bpy.context.scene.view_settings.view_transform = 'Standard'
    bpy.context.scene.view_settings.look = 'None'
except Exception:
    pass

# Картинка сохраняется рядом со скриптом (или в домашнюю папку, если запуск из редактора).
try:
    out_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    out_dir = os.path.expanduser("~")
out_path = os.path.join(out_dir, "Robot.png")

render(out_path)
print("Готово! Робот создан. Объектов:", len([o for o in bpy.data.objects if o.type == 'MESH']))
print("Картинка:", out_path)
