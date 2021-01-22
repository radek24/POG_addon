'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
'''
import bpy

bl_info = {
    "name": "POG",
    "author": "Radovan Stastny <radovan.stastny2004@gmail.com>",
    "version": (1, 2),
    "blender": (2, 85, 0),
    "category": "General",
    "location": "View3D > Side Pannel > POG",
    "description": "This addon will help you with your POG expirience",
}

# UI
def menu_func(self, context):
    self.layout.operator(mesh.set_origin_to_selection)
    self.layout.operator(mesh.add_tracked_lamp)

class VIEW3D_PT_POG(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "POG"
    bl_label = "POG"
    def draw(self, context):
        self.layout.operator('mesh.set_origin_to_selection',icon='OBJECT_ORIGIN')
        self.layout.operator('mesh.add_tracked_lamp',text="add tracked lamp to active obj", icon='LIGHT_AREA')

# ASSIGN ORIGIN FUNCTION
class MESH_OT_set_origin_selection(bpy.types.Operator):
    """assign origin to selection"""
    bl_idname = 'mesh.set_origin_to_selection'
    bl_label = "Set Origin to selection"

    # Checking if is possible to perform operator
    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        if len(objs) != 0:
            current_mode = bpy.context.object.mode
            return context.area.type == 'VIEW_3D' and current_mode == 'EDIT'
        else: return False



    def execute(self,context):
        # Get cursor location
        cursor_location = bpy.context.scene.cursor.location.copy()
        # Set origin
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.ops.object.mode_set(mode='EDIT')
        # Set origin back to last position
        bpy.context.scene.cursor.location = cursor_location
        return {'FINISHED'}

# ADD TRACKED LAMP FUNCTION
class MESH_OT_add_tracked_lamp(bpy.types.Operator):
    """add lamp with track to constraint to scene"""
    bl_idname = 'mesh.add_tracked_lamp'
    bl_label = "Add tracked lamp"
    bl_options = {'REGISTER', 'UNDO'}

    # Properties declaration
    light_intensity: bpy.props.FloatProperty(
        name="Light intensity",
        description="intensity of created lamp",
        default = 2,
        min=0, soft_max = 100,
    )

    scale: bpy.props.FloatProperty(
        name="Lamp scale",
        description="uniform scale of lamp",
        default=2.0,
        min=0,
    )

    position: bpy.props.FloatVectorProperty(
        name="Lamp scale",
        description="uniform scale of lamp",
        default=(0,0,0),
    )

    # Checking if is possible to perform operator
    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        if len(objs) != 0:
            current_mode = bpy.context.object.mode
            return context.area.type == 'VIEW_3D' and current_mode == 'OBJECT'
        else:
            return False

    def execute(self, context):

        # Material creation
        material_light = bpy.data.materials.new(name = "Light")
        material_light.use_nodes = True

        # Define link
        link = material_light.node_tree.links.new

        # Material modification
        principled_node = material_light.node_tree.nodes['Principled BSDF']
        material_light.node_tree.nodes.remove(principled_node)
        emission_node = material_light.node_tree.nodes.new('ShaderNodeEmission')
        emission_node.location = (-150, 0)
        emission_node.inputs[1].default_value = self.light_intensity
        output_node = material_light.node_tree.nodes["Material Output"]
        output_node.location = (0, 0)
        link(emission_node.outputs[0], output_node.inputs[0])

        #plane creation
        tracked_obj = bpy.context.active_object
        bpy.ops.mesh.primitive_plane_add(
            size=self.scale,
            location=self.position
        )
        #adds material to plane
        bpy.context.object.active_material = material_light

        # Constraint creation
        o = bpy.context.object
        constraint = o.constraints.new('TRACK_TO')

        # constraint properties
        constraint.show_expanded = True
        constraint.mute = False
        constraint.target = tracked_obj
        constraint.track_axis = 'TRACK_Z'

        return {'FINISHED'}


# Adds origin function to F3 search
def menu_func_origin(self, context):
    self.layout.operator(MESH_OT_set_origin_selection.bl_idname)

# Adds add lamp function to F3 search
def menu_func_lamp(self, context):
    self.layout.operator(MESH_OT_add_tracked_lamp.bl_idname)

# Registration
def register():
    bpy.utils.register_class(MESH_OT_set_origin_selection)
    bpy.utils.register_class(VIEW3D_PT_POG)
    bpy.utils.register_class(MESH_OT_add_tracked_lamp)

    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func_origin)
    bpy.types.VIEW3D_MT_light_add.append(menu_func_lamp)

def unregister():
    bpy.utils.unregister_class(MESH_OT_set_origin_selection)
    bpy.utils.unregister_class(VIEW3D_PT_POG)
    bpy.utils.unregister_class(MESH_OT_add_tracked_lamp)

    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func_origin)
    bpy.types.VIEW3D_MT_light_add.remove(menu_func_lamp)
