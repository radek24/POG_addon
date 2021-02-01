'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
'''


bl_info = {
    "name": "POG",
    "author": "Radovan Stastny <radovan.stastny2004@gmail.com>",
    "version": (1, 3),
    "blender": (2, 85, 0),
    "category": "3D View",
    "doc_url":"https://docs.google.com/document/d/17DsHfqIfumDWSyVnHD1hiJe9GBZ9yfkCH4roNI1Zo4o/edit",
    "location": "View3D > Side Pannel > POG",
    "description": "This addon will help you with your POG expirience",
}

# UI
#-----------------------------------------------------------------------------------------------------------------------#
def menu_func(self, context):
    self.layout.operator(mesh.set_origin_to_selection)
    self.layout.operator(mesh.add_tracked_lamp_plane)

class VIEW3D_PT_POG(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "POG"
    bl_label = "POG"
    def draw(self, context):
        #origin menu
        col = self.layout.column(align=True,)
        col.label(text="Origin:")
        col.scale_y = 1.25
        col.operator('mesh.set_origin_to_selection',icon='OBJECT_ORIGIN')
        #adding lamo to active menu
        col = self.layout.column(align=True, )
        col.label(text="Add lamp to active object:",icon='PIVOT_ACTIVE')
        col.scale_y = 1.25

        props = col.operator('mesh.add_tracked_lamp_plane',text="Add tracked plane lamp", icon='LIGHT')
        props.tracked_to_empty = False

        props = col.operator('mesh.add_tracked_lamp', text="Add tracked lamp", icon='CON_TRACKTO')
        props.tracked_to_empty=False
        #adding lamo to empty menu
        col = self.layout.column(align=True, )
        col.label(text="Add lamp to empty:",icon='EMPTY_AXIS')
        col.scale_y = 1.25

        props = col.operator('mesh.add_tracked_lamp_plane', text="Add tracked plane lamp", icon='LIGHT')
        props.tracked_to_empty = True

        props = col.operator('mesh.add_tracked_lamp', text="Add tracked lamp", icon='CON_TRACKTO')
        props.tracked_to_empty=True


class VIEW3D_PT_POG_bake(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "POG"
    bl_label = "Bake"
    def draw(self, context):
        pass

#Operators
#-----------------------------------------------------------------------------------------------------------------------#
# ASSIGN ORIGIN FUNCTION
class MESH_OT_set_origin_selection(bpy.types.Operator):
    """assign origin to selection"""
    bl_idname = 'mesh.set_origin_to_selection'
    bl_label = "Set Origin to selection"
    bl_options = {'REGISTER', 'UNDO', 'UNDO_GROUPED',}



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
        # tohle je nějaké pohlupave

        bpy.ops.object.mode_set(mode='EDIT')
        # Set 3D cursor back to last position
        bpy.context.scene.cursor.location = original_cursor_location
        return {'FINISHED'}

# ADD TRACKED LAMP PLANE OPERATOR
#-----------------------------------------------------------------------------------------------------------------------#
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

    tracked_to_empty: bpy.props.BoolProperty(
        name="Track to emtpy",
        description="will track to empty instead of active object",
        default=False,
    )

    empty_lamp_position: bpy.props.FloatVectorProperty(
        name="empty position",
        description="position of tracked object",
        default=(0, 0, 0),
        subtype='TRANSLATION',
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

        # Constraint properties
        constraint.show_expanded = True
        constraint.mute = False
        constraint.track_axis = 'TRACK_Z'
        constraint.name ='POG constraint'
        # Get lamp 
        ob = bpy.context.active_object

        #deciding tracking target
        if self.tracked_to_empty == True:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=self.empty_lamp_position)
            constraint.target = bpy.context.active_object
            bpy.context.active_object.name = 'POG_lamp.target'
            bpy.context.active_object.select_set(False)
            ob.select_set(True)
        else:
            constraint.target = tracked_obj
        return {'FINISHED'}




# ADD TRACKED LAMP OPERATOR
#-----------------------------------------------------------------------------------------------------------------------#
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

    tracked_to_empty: bpy.props.BoolProperty(
        name="Track to emtpy",
        description="will track to empty instead of active object",
        default=False,
    )

    empty_lamp_position: bpy.props.FloatVectorProperty(
        name="empty position",
        description="position of tracked object",
        default=(0, 0, 0),
        subtype='TRANSLATION',
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
        bpy.context.active_object.name = 'POG.lamp'
        bpy.context.object.data.energy = self.light_intensity_lamp
        bpy.context.object.data.color = self.color_lamp
        ob = bpy.context.active_object
        print(ob)

        # Constraint creation
        o = bpy.context.object
        constraint = o.constraints.new('TRACK_TO')

        # constraint properties
        constraint.show_expanded = True
        constraint.mute = False
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.name ='POG constraint'

        # deciding tracking target
        if self.tracked_to_empty == True:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=self.empty_lamp_position)
            constraint.target = bpy.context.active_object
            bpy.context.active_object.select_set(False)
            ob.select_set(True)

        else:
            constraint.target = tracked_obj
        return {'FINISHED'}






#-----------------------------------------------------------------------------------------------------------------------#
# BAKING OPERATOR
class MESH_OT_autobaking(bpy.types.Operator):
    """will bake everything automatically, note that bledner will freeze for a moment"""
    bl_idname = 'mesh.autobake'
    bl_label = "Autobake"
    bl_options = {'REGISTER', 'UNDO', 'UNDO_GROUPED',}


    # Checking if it is possible to perform operator
    @classmethod
    def poll(cls, context):
        return True



    def execute(self,context):

        #UV map creation
        bpy.context.object.data.uv_layers.new(name="Bake")
        bpy.ops.object.editmode_toggle()
        bpy.context.object.data.uv_layers["Bake"].active = True

        #Light map pack unwrap
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.lightmap_pack()
        bpy.ops.object.editmode_toggle()

        #Create images and save them to file
        size = 1080                                                                 #Will be variable
        name="mybake"                                                               #Will be variable
        suffixes = "_diffuse","_roughness","_normal"
        type = ".png"
        path = "/tmp/"                                                              #Will be variable

        #def create_image(x):
        for suffix in suffixes:
            bpy.data.images.new("test", width=size, height=size)
            bpy.data.images["test"].filepath_raw = path + name + suffix + type
            bpy.data.images["test"].file_format = 'PNG'
            bpy.data.images["test"].save()


        #create image in all materials and set it to active
        def assing_image(x):
            for mat in bpy.context.object.data.materials.items():
                image_texture_node = mat[1].node_tree.nodes.new('ShaderNodeTexImage')
                image_texture_node.name = "bake image"
                image_texture_node.label = "bake image"
                image_texture_node.image = bpy.data.images.load(path+name+suffixes[x]+type)
                image_texture_node.location = (-150, -200)
                image_texture_node.select = True
                mat[1].node_tree.nodes.active = image_texture_node

        #baking diffuse
        assing_image(0)
        old_samples = bpy.context.scene.cycles.samples
        bpy.context.scene.cycles.samples = 1
        bpy.context.scene.cycles.bake_type = 'DIFFUSE'
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')
        assing_image(1)
        bpy.context.scene.cycles.bake_type = 'ROUGHNESS'
        bpy.ops.object.bake(type='ROUGHNESS', save_mode='EXTERNAL')
        assing_image(2)
        bpy.context.scene.cycles.bake_type = 'NORMAL'
        bpy.ops.object.bake(type='NORMAL', save_mode='EXTERNAL')
        bpy.context.scene.cycles.samples = old_samples
        return {'FINISHED'}


# ----------------------------------------------------------------------------------------------------------------------------------------------------#
# Adds origin function to F3 search
def menu_func_origin(self, context):
    self.layout.operator(MESH_OT_set_origin_selection.bl_idname, icon='OBJECT_ORIGIN')

# Adds add lamp plane function to F3 search
def menu_func_lamp_plane(self, context):
    self.layout.operator(MESH_OT_add_tracked_lamp_plane.bl_idname, icon='LIGHT')

# Adds add lamp function to F3 search
def menu_func_lamp(self, context):
    self.layout.operator(MESH_OT_add_tracked_lamp.bl_idname, icon='CON_TRACKTO')

#----------------------------------------------------------------------------------------------------------------------------------------------------#
# Registration
def registers():
    # UI
    bpy.utils.register_class(VIEW3D_PT_POG)
    bpy.utils.register_class(VIEW3D_PT_POG_bake)

    # operators
    bpy.utils.register_class(MESH_OT_set_origin_selection)
    bpy.utils.register_class(MESH_OT_add_tracked_lamp_plane)
    bpy.utils.register_class(MESH_OT_add_tracked_lamp)
    bpy.utils.register_class(MESH_OT_autobaking)

    # F3 menu
    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func_origin)
    bpy.types.VIEW3D_MT_light_add.append(menu_func_lamp_plane)
    bpy.types.VIEW3D_MT_light_add.append(menu_func_lamp)



    print("I1C jsou borci")

def unregister():
    #UI
    bpy.utils.unregister_class(VIEW3D_PT_POG)
    bpy.utils.unregister_class(VIEW3D_PT_POG_bake)

    #operators
    bpy.utils.unregister_class(MESH_OT_set_origin_selection)
    bpy.utils.unregister_class(MESH_OT_add_tracked_lamp_plane)
    bpy.utils.unregister_class(MESH_OT_add_tracked_lamp)
    bpy.utils.unregister_class(MESH_OT_autobaking)

    #F3 menu
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func_origin)
    bpy.types.VIEW3D_MT_light_add.remove(menu_func_lamp_plane)
    bpy.types.VIEW3D_MT_light_add.remove(menu_func_lamp)

    print("naschle")