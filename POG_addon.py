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
    "version": (1, 3),
    "blender": (2, 85, 0),
    "category": "General",
    "location": "View3D > Side Pannel > POG",
    "description": "This addon will help you with your POG expirience",
}

# UI
def menu_func(self, context):
    self.layout.operator(mesh.set_origin_to_selection)
    self.layout.operator(mesh.add_tracked_lamp_plane)

class VIEW3D_PT_POG(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "POG"
    bl_label = "POG"
    def draw(self, context):

        col = self.layout.column(align=True,)
        col.label(text="Origin:")
        col.scale_y = 1.25
        col.operator('mesh.set_origin_to_selection',icon='OBJECT_ORIGIN')
        col = self.layout.column(align=True, )
        col.label(text="Add lamp:")
        col.scale_y = 1.25
        col.operator('mesh.add_tracked_lamp_plane',text="Add tracked plane lamp", icon='LIGHT')
        col.operator('mesh.add_tracked_lamp', text="Add tracked lamp", icon='CON_TRACKTO')


# ASSIGN ORIGIN FUNCTION
class MESH_OT_set_origin_selection(bpy.types.Operator):
    """assign origin to selection"""
    bl_idname = 'mesh.set_origin_to_selection'
    bl_label = "Set Origin to selection"
    bl_options = {'REGISTER', 'UNDO', 'UNDO_GROUPED',}

    #properties declaration
    #move_3d_cursor: bpy.props.BoolProperty(
    #    name="move 3d curosor",
    #    description = "move 3d curosor to origin",
    #    default = False,
    #)

    # Checking if it is possible to perform operator
    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        if len(objs) != 0:
            current_mode = bpy.context.object.mode
            return context.area.type == 'VIEW_3D' and current_mode == 'EDIT'
        else: return False


    def execute(self,context):
        # Get cursor location
        original_cursor_location = bpy.context.scene.cursor.location.copy()
        # Set origin
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode='OBJECT')
        #tohle je nějaké pohlupave
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.ops.object.mode_set(mode='EDIT')
        # Set 3D cursor back to last position
        bpy.context.scene.cursor.location = original_cursor_location
        return {'FINISHED'}

# ADD TRACKED LAMP PLANE FUNCTION
class MESH_OT_add_tracked_lamp_plane(bpy.types.Operator):
    """Add lamp with track to constraint to active object"""
    bl_idname = 'mesh.add_tracked_lamp_plane'
    bl_label = "Add tracked plane lamp"
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
        max=100,
        unit='LENGTH',
    )

    position: bpy.props.FloatVectorProperty(
        name="Lamp position",
        description="position of lamp",
        default=(0,0,0),
        subtype='TRANSLATION',
    )

    color: bpy.props.FloatVectorProperty(
        name="Color",
        description="light color",
        subtype='COLOR_GAMMA',
        size=4,
        default=(1,1,1,1),
        min=0,
        max=1,
    )

    # Checking if it is possible to perform operator
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
        emission_node.inputs[0].default_value = self.color
        output_node = material_light.node_tree.nodes["Material Output"]
        output_node.location = (0, 0)
        link(emission_node.outputs[0], output_node.inputs[0])

        #plane creation
        tracked_obj = bpy.context.active_object
        bpy.ops.mesh.primitive_plane_add(
            size=self.scale,
            location=self.position
        )
        bpy.context.active_object.name = 'POG_plane_lamp'
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




# ADD TRACKED LAMP FUNCTION
class MESH_OT_add_tracked_lamp(bpy.types.Operator):
    """Add plane lamp with track to constraint to active object"""
    bl_idname = 'mesh.add_tracked_lamp'
    bl_label = "Add tracked lamp"
    bl_options = {'REGISTER', 'UNDO'}

    # Properties declaration
    light_intensity_lamp: bpy.props.FloatProperty(
        name="Light intensity",
        description="intensity of created lamp",
        default=100,
        min=0,
        soft_max=10000,
        unit='POWER',
        step=10,
    )

    scale_lamp: bpy.props.FloatProperty(
        name="Lamp scale",
        description="uniform scale of lamp",
        default=1,
        min=0,
        unit='LENGTH',
    )

    position_lamp: bpy.props.FloatVectorProperty(
        name="Lamp position",
        description="position of lamp",
        default=(0, 0, 0),
        subtype='TRANSLATION',
    )

    color_lamp: bpy.props.FloatVectorProperty(
        name="Color",
        description="light color",
        subtype='COLOR_GAMMA',
        size=3,
        default=(1, 1, 1),
        min=0,
        max=1,
    )

    # Checking if it is possible to perform operator
    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        if len(objs) != 0:
            current_mode = bpy.context.object.mode
            return context.area.type == 'VIEW_3D' and current_mode == 'OBJECT'
        else:
            return False

    def execute(self, context):
        # light creation
        tracked_obj = bpy.context.active_object
        bpy.ops.object.light_add(type='AREA', radius=self.scale_lamp, location=self.position_lamp,)
        bpy.context.active_object.name = 'POG_lamp'
        bpy.context.object.data.energy = self.light_intensity_lamp
        bpy.context.object.data.color = self.color_lamp

        # Constraint creation
        o = bpy.context.object
        constraint = o.constraints.new('TRACK_TO')

        # constraint properties
        constraint.show_expanded = True
        constraint.mute = False
        constraint.target = tracked_obj
        constraint.track_axis = 'TRACK_NEGATIVE_Z'

        return {'FINISHED'}





# Adds origin function to F3 search
def menu_func_origin(self, context):
    self.layout.operator(MESH_OT_set_origin_selection.bl_idname, icon='OBJECT_ORIGIN')

# Adds add lamp plane function to F3 search
def menu_func_lamp_plane(self, context):
    self.layout.operator(MESH_OT_add_tracked_lamp_plane.bl_idname, icon='LIGHT')

# Adds add lamp function to F3 search
def menu_func_lamp(self, context):
    self.layout.operator(MESH_OT_add_tracked_lamp.bl_idname, icon='CON_TRACKTO')

# Registration
def register():
    bpy.utils.register_class(MESH_OT_set_origin_selection)
    bpy.utils.register_class(VIEW3D_PT_POG)
    bpy.utils.register_class(MESH_OT_add_tracked_lamp_plane)
    bpy.utils.register_class(MESH_OT_add_tracked_lamp)

    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func_origin)
    bpy.types.VIEW3D_MT_light_add.append(menu_func_lamp_plane)
    bpy.types.VIEW3D_MT_light_add.append(menu_func_lamp)
    print("zdar")

def unregister():
    bpy.utils.unregister_class(MESH_OT_set_origin_selection)
    bpy.utils.unregister_class(VIEW3D_PT_POG)
    bpy.utils.unregister_class(MESH_OT_add_tracked_lamp_plane)
    bpy.utils.unregister_class(MESH_OT_add_tracked_lamp)

    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func_origin)
    bpy.types.VIEW3D_MT_light_add.remove(menu_func_lamp_plane)
    bpy.types.VIEW3D_MT_light_add.remove(menu_func_lamp)
    print("naschle")