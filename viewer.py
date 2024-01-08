import bpy
import pickle
from pathlib import Path
import os
import sys

WORKDIR = Path(__file__).parents[1]
sys.path.append(str(WORKDIR))
MODEL_PATH = WORKDIR / "data/**.pkl" # Rename here!!

def clear_all_meshes():
    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item)
    
def clear_all_materials():
    for item in bpy.data.materials:
        bpy.data.materials.remove(item)

def set_material(object, material_name, texture_filepath):
    material = bpy.data.materials.new(material_name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    node_shader = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_texture = nodes.new("ShaderNodeTexImage")
    node_texture.image = bpy.data.images.load(texture_filepath)
    node_output = nodes.new(type="ShaderNodeOutputMaterial")
    links = material.node_tree.links
    link = links.new(node_texture.outputs["Color"], node_shader.inputs["Base Color"])
    link = links.new(node_shader.outputs["BSDF"], node_output.inputs["Surface"])
    bpy.context.view_layer.objects.active = object
    bpy.context.object.data.materials.append(material)

def generate_sphere(person, location):
    mat_male = bpy.data.materials.new("male")
    mat_male.diffuse_color = (0, 0, 1, 1)
    mat_female = bpy.data.materials.new("female")
    mat_female.diffuse_color = (1, 0, 0, 1)
    
    bpy.ops.mesh.primitive_uv_sphere_add(location=location, radius=0.2)
    bpy.context.object.name = person.name
    child = bpy.data.objects[person.name]
    texture_path = WORKDIR / Path("texture/{}.png".format(person.name))
    if texture_path.exists():
        # texture_data = bpy.data.images.load(str(texture_path))
        set_material(bpy.data.objects[person.name], person.name, str(texture_path))
        print(str(texture_path), "exists")
    else:
        print(str(texture_path), "doesn't exists")
        if person.male:
            child.data.materials.append(mat_male)
        else:
            child.data.materials.append(mat_female)

def generate_node(node):
    px, py, pz, rx, ry, rz, sx, sy, sz = node
    bpy.ops.mesh.primitive_cylinder_add(location=(px, py, pz), rotation=(rx, ry, rz), scale=(sx, sy, sz))

def main():
    with open(MODEL_PATH, "rb") as f:
        family = pickle.load(f)

    clear_all_meshes()
    clear_all_materials()
    for per, pos in family.person_position.items():
        print(per.name, pos)
        generate_sphere(per, pos)

    for node in family.node_list:
        generate_node(node)

if __name__ == "__main__":
    main()