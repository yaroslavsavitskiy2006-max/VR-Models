# -*- coding: utf-8 -*-
"""
КРОЛИК из примитивов Blender (bpy).

Собран на основе шаблона character_task.py — инструментарий внизу не менялся,
переписан только раздел «СОБЕРИТЕ СВОЕГО ПЕРСОНАЖА».

Как запустить (в Blender):
  1) откройте Blender -> вкладка Scripting -> New;
  2) вставьте этот код и нажмите Run Script (или Alt+P);
  3) кролик появится в 3D-вьюпорте, картинка сохранится в вашу папку пользователя.
"""
import bpy
import math
import os


# ====================== ИНСТРУМЕНТАРИЙ (менять не нужно) ======================
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials):
        for b in list(coll):
            coll.remove(b)


def make_material(name, color, metallic=0.0, roughness=0.6, emission=None):
    """Создаёт материал. color/emission — кортеж (r, g, b) в диапазоне 0..1."""
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
    m = obj.modifiers.new("Bevel", 'BEVEL'); m.width = bevel; m.segments = 3
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


def setup_scene(bg_color=(0.75, 0.85, 0.95), cam_location=(0, -7.5, 2.3), cam_pitch_deg=83):
    """Пол, два источника света, камера, фон, настройки рендера."""
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.02))
    bpy.context.active_object.data.materials.append(make_material("Ground", (0.8, 0.84, 0.8), roughness=0.9))
    bpy.ops.object.light_add(type='AREA', location=(4, -4, 6))
    bpy.context.active_object.data.energy = 900; bpy.context.active_object.data.size = 6
    bpy.ops.object.light_add(type='AREA', location=(-5, -3, 3))
    bpy.context.active_object.data.energy = 300; bpy.context.active_object.data.size = 8
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


# =============================================================================
clear_scene()

# ------------------------------- МАТЕРИАЛЫ -----------------------------------
FUR    = make_material("Fur",    (0.93, 0.92, 0.90), roughness=0.85)  # шерсть
PINK   = make_material("Pink",   (0.98, 0.73, 0.80), roughness=0.60)  # уши изнутри
BLUSH  = make_material("Blush",  (0.99, 0.66, 0.75), roughness=0.70)  # щёчки
NOSE   = make_material("Nose",   (0.95, 0.55, 0.68), roughness=0.40)  # носик
BLACK  = make_material("Black",  (0.02, 0.02, 0.02), roughness=0.25)  # глаза
SHINE  = make_material("Shine",  (1.00, 1.00, 1.00), roughness=0.15)  # блики

# ======================= СОБЕРИТЕ СВОЕГО ПЕРСОНАЖА ===========================
# Пропорции «чиби»: большая голова, маленькое тело, длинные уши.
# ВАЖНО: глаза и мордочка сдвинуты вперёд за поверхность головы,
# иначе они окажутся ВНУТРИ шара и на рендере лица не будет видно.

# --- тело (грушевидное) и большая голова ---
add_sphere("Body", (0, 0.05, 0.70), (0.68, 0.64, 0.70), FUR)
add_sphere("Head", (0, -0.10, 1.72), (0.80, 0.76, 0.80), FUR)

# --- мордочка: компактный бугорок, носик на самом кончике ---
add_sphere("Muzzle", (0, -0.86, 1.67), (0.23, 0.14, 0.13), FUR)
add_sphere("Nose",   (0, -1.00, 1.72), (0.060, 0.050, 0.045), NOSE)

# --- глаза (выступают из головы примерно на 0.08) ---
add_sphere("Eye_L", (-0.30, -0.74, 1.88), (0.13, 0.13, 0.13), BLACK)
add_sphere("Eye_R", ( 0.30, -0.74, 1.88), (0.13, 0.13, 0.13), BLACK)

# --- блики в глазах (лежат ровно на сфере глаза) ---
add_sphere("Eye_L_Highlight", (-0.34, -0.855, 1.92), (0.035, 0.035, 0.035), SHINE)
add_sphere("Eye_R_Highlight", ( 0.26, -0.855, 1.92), (0.035, 0.035, 0.035), SHINE)

# --- щёчки (плоские «подушечки» на поверхности головы) ---
add_sphere("Cheek_L", (-0.42, -0.72, 1.62), (0.15, 0.05, 0.10), BLUSH)
add_sphere("Cheek_R", ( 0.42, -0.72, 1.62), (0.15, 0.05, 0.10), BLUSH)

# --- уши: вытянутые эллипсоиды (округлые кончики, без «трубы») ---
for side, sign in (("L", -1), ("R", 1)):
    tilt = math.radians(-8 * sign)                      # наклон наружу
    add_sphere(f"Ear_{side}", (0.26 * sign, 0.00, 2.92), (0.15, 0.10, 0.70), FUR)
    add_sphere(f"Ear_{side}_Inner", (0.26 * sign, -0.070, 2.95), (0.115, 0.06, 0.58), PINK)
    # наклоняем пару «внешняя + внутренняя» вокруг оси Y
    for suffix in ("", "_Inner"):
        ear = bpy.data.objects[f"Ear_{side}{suffix}"]
        ear.rotation_euler = (0, tilt, 0)

# --- лапки: две небольшие передние у самого низа ---
add_sphere("Paw_L", (-0.17, -0.30, 0.16), (0.19, 0.24, 0.17), FUR)
add_sphere("Paw_R", ( 0.17, -0.30, 0.16), (0.19, 0.24, 0.17), FUR)

# --- хвостик ---
add_sphere("Tail", (0, 0.66, 0.55), (0.20, 0.20, 0.20), FUR)

# =============================================================================
# Камера чуть ниже и ближе, чтобы кролик занял кадр целиком (с ушами).
setup_scene(bg_color=(0.62, 0.68, 0.76), cam_location=(0, -6.6, 2.3), cam_pitch_deg=86)
bpy.context.scene.camera.data.lens = 50

# Свет мягче: иначе белый мех выгорает в чистый белый и теряет форму.
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        obj.data.energy *= 0.40

# Пол темнее фона — белый кролик не сливается с землёй.
ground = bpy.data.materials.get("Ground")
if ground:
    ground.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.58, 0.62, 0.66, 1.0)

# Плоская цветокоррекция вместо AgX — иначе белый мех выглядит серым.
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
out_path = os.path.join(out_dir, "Rabbit.png")
render(out_path)
print("Готово. Кролик собран. Объектов в сцене:", len(bpy.data.objects))
print("Картинка:", out_path)
