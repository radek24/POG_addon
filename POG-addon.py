# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
import colorsys


bl_info = {
    "name": "POG",
    "author": "Radovan Stastny <radovan.stastny2004@gmail.com>",
    "version": (2, 1),
    "blender": (2, 85, 0),
    "category": "3D View",
    "doc_url": "https://docs.google.com/document/d/17DsHfqIfumDWSyVnHD1hiJe9GBZ9yfkCH4roNI1Zo4o/edit",
    "location": "View3D > Side Panel > POG",
    "description": "This addon will help you with baking and more (check docs)",
}


# UI
# -----------------------------------------------------------------------------------------------------------------------#


def menu_func(self, context):
    self.layout.operator(mesh.set_origin_to_selection)
    self.layout.operator(mesh.add_tracked_lamp_plane)


class VIEW3D_PT_POG(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_label = "POG"

    def draw(self, context):
        # origin menu
        col = self.layout.column(align=True, )
        col.label(text="Origin:")
        col.operator('mesh.set_origin_to_selection', icon='OBJECT_ORIGIN')
        # Adding lamp to active menu
        col = self.layout.column(align=True, )
        col.label(text="Add lamp to active object:", icon='PIVOT_ACTIVE')

        props = col.operator('mesh.add_tracked_lamp_plane', text="Add tracked plane lamp", icon='LIGHT')
        props.tracked_to_empty = False

        props = col.operator('mesh.add_tracked_lamp', text="Add tracked lamp", icon='CON_TRACKTO')
        props.tracked_to_empty = False
        # Adding lamp to empty menu
        col = self.layout.column(align=True, )
        col.label(text="Add lamp to empty:", icon='EMPTY_AXIS')

        props = col.operator('mesh.add_tracked_lamp_plane', text="Add tracked plane lamp", icon='LIGHT')
        props.tracked_to_empty = True

        props = col.operator('mesh.add_tracked_lamp', text="Add tracked lamp", icon='CON_TRACKTO')
        props.tracked_to_empty = True
        

# Operators
# -----------------------------------------------------------------------------------------------------------------------#
# ASSIGN ORIGIN FUNCTION


class MESH_OT_set_origin_selection(bpy.types.Operator):
    """assign origin to selection"""
    bl_idname = 'mesh.set_origin_to_selection'
    bl_label = "Set Origin to selection"
    bl_options = {'REGISTER', 'UNDO', 'UNDO_GROUPED', }

    # Checking if it is possible to perform operator
    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        if len(objs) != 0:
            current_mode = bpy.context.object.mode
            return context.area.type == 'VIEW_3D' and current_mode == 'EDIT'
        else:
            return False

    def execute(self, context):
        # Get cursor location
        original_cursor_location = bpy.context.scene.cursor.location.copy()
        # Set origin
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode='OBJECT')
        # Tohle je nějaké pohlupave
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        # Tohle je nějaké pohlupave
        bpy.ops.object.mode_set(mode='EDIT')
        # Set 3D cursor back to last position
        bpy.context.scene.cursor.location = original_cursor_location
        return {'FINISHED'}

# INCREMENT HUE VERTEX COLOR
# -----------------------------------------------------------------------------------------------------------------------#

def increase_vertex_paint_hue(x):

    # Get the active object (must be in vertex paint mode)
    obj = bpy.context.active_object

    if obj is not None and obj.type == 'MESH' and obj.mode == 'VERTEX_PAINT':
        brush = bpy.data.brushes["Draw"]
        


        existing_color = brush.color
        if existing_color[0] == existing_color[1] and existing_color[1] == existing_color[2] and existing_color[0] == existing_color[2]:
             brush.color = [1.0,0.0,0.0]
             return
        existing_color = [c / 255.0 for c in existing_color]
        hsv = colorsys.rgb_to_hsv(existing_color[0], existing_color[1], existing_color[2])
        new_hue = (hsv[0] + x) % 1.0
        
        new_rgb = colorsys.hsv_to_rgb(new_hue, hsv[1], hsv[2])
        
        new_color = [c * 255.0 for c in new_rgb]
        
        brush.color = new_color



class MESH_OT_increment_vertex_color_hue(bpy.types.Operator):
    """increment hue of vertex color"""
    bl_idname = 'mesh.increment_vertex_color_hue'
    bl_label = "Increment vertex color hue"
    bl_options = {'REGISTER', 'UNDO', 'UNDO_GROUPED', }

    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        if len(objs) != 0:
            current_mode = bpy.context.object.mode
            return context.area.type == 'VIEW_3D' and current_mode == 'VERTEX_PAINT'
        else:
            return False

    def execute(self, context):
        increase_vertex_paint_hue(0.05)
        return {'FINISHED'}






class MESH_OT_decrement_vertex_color_hue(bpy.types.Operator):
    """Decrement hue of vertex color"""
    bl_idname = 'mesh.decrement_vertex_color_hue'
    bl_label = "Decrement vertex color hue"
    bl_options = {'REGISTER', 'UNDO', 'UNDO_GROUPED', }

    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        if len(objs) != 0:
            current_mode = bpy.context.object.mode
            return context.area.type == 'VIEW_3D' and current_mode == 'VERTEX_PAINT'
        else:
            return False

    def execute(self, context):
        increase_vertex_paint_hue(-0.05)
        return {'FINISHED'}



# ADD CHECKER MATERIAL
# -----------------------------------------------------------------------------------------------------------------------#
class OBJECT_OT_add_checker_material(bpy.types.Operator):
    bl_idname = "object.add_checker_material"
    bl_label = "Add Checker Material"
    bl_options = {'REGISTER', 'UNDO'}

    scale: bpy.props.FloatProperty(
        name="Texture Scale",
        default=256.0,
        min=0.1,
        description="Scale of the checker texture",
    )

    def execute(self, context):
        self.create_material(context)
        return {'FINISHED'}

    def create_material(self, context):
        # Get the active object
        obj = context.active_object
        if obj is not None and obj.type == 'MESH':
            # Set the scale parameter for the checker texture
            mat = bpy.data.materials.new(name="CheckerMaterial")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            principled_node = mat.node_tree.nodes.get('Principled BSDF')
            
            link = mat.node_tree.links.new
            
            # Create nodes for checker texture
            tex_coord_node = nodes.new(type='ShaderNodeTexCoord')
            checker_node = nodes.new(type='ShaderNodeTexChecker')
            
            scale_node = nodes.new(type='ShaderNodeValue')
            
            scale_node.outputs["Value"].default_value = self.scale


            checker_node.location = (-500, 0)
            scale_node.location = (-800, -300)
            tex_coord_node.location = (-800, 0)
            # Link nodes
            link(checker_node.outputs[0], principled_node.inputs[0])
            link(tex_coord_node.outputs['UV'], checker_node.inputs['Vector'])
            link(scale_node.outputs['Value'], checker_node.inputs['Scale'])

            # Assign the material to the active object
            obj.active_material = mat
        else:
            self.report({'ERROR'}, "Please select an active mesh object.")



# ADD TRACKED LAMP OPERATOR
# -----------------------------------------------------------------------------------------------------------------------#


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
        if len(objs) == 1:
            current_mode = bpy.context.object.mode
            return context.area.type == 'VIEW_3D' and current_mode == 'OBJECT'
        else:
            return False

    def execute(self, context):
        # light creation
        tracked_obj = bpy.context.active_object
        bpy.ops.object.light_add(type='AREA', radius=self.scale_lamp, location=self.position_lamp, )
        bpy.context.active_object.name = 'POG.lamp'
        bpy.context.object.data.energy = self.light_intensity_lamp
        bpy.context.object.data.color = self.color_lamp
        ob = bpy.context.active_object

        # Constraint creation4k resolution pixels
        o = bpy.context.object
        constraint = o.constraints.new('TRACK_TO')

        # constraint properties
        constraint.show_expanded = True
        constraint.mute = False
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.name = 'POG constraint'

        # deciding tracking target
        if self.tracked_to_empty:
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=self.empty_lamp_position)
            constraint.target = bpy.context.active_object
            bpy.context.active_object.select_set(False)
            ob.select_set(True)

        else:
            constraint.target = tracked_obj
        return {'FINISHED'}


# ---------------------------------------------------------------------------------------------------------------------#
# Adds origin function to F3 search
def menu_func_origin(self, context):
    self.layout.operator(MESH_OT_set_origin_selection.bl_idname, icon='OBJECT_ORIGIN')


# Adds add lamp function to F3 search


def menu_func_lamp(self, context):
    self.layout.operator(MESH_OT_add_tracked_lamp.bl_idname, icon='CON_TRACKTO')

def menu_func_vertex(self, context):
    self.layout.operator(MESH_OT_increment_vertex_color_hue.bl_idname, icon='TRIA_UP')

def menu_func_vertex_dec(self, context):
    self.layout.operator(MESH_OT_decrement_vertex_color_hue.bl_idname, icon='TRIA_DOWN')
    
def menu_func_add_checker_mat(self, context):
    self.layout.operator(OBJECT_OT_add_checker_material.bl_idname, icon='MATERIAL')

# --------------------------------------------------------------------------------------------------------------------#
# Registration


def register():
    # UI
    bpy.utils.register_class(VIEW3D_PT_POG)

    # operators
    bpy.utils.register_class(MESH_OT_set_origin_selection)
    bpy.utils.register_class(MESH_OT_add_tracked_lamp)
    bpy.utils.register_class(MESH_OT_increment_vertex_color_hue)
    bpy.utils.register_class(MESH_OT_decrement_vertex_color_hue)
    bpy.utils.register_class(OBJECT_OT_add_checker_material)

    # F3 menu
    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func_origin)
    bpy.types.VIEW3D_MT_light_add.append(menu_func_lamp)
    bpy.types.VIEW3D_MT_paint_vertex.append(menu_func_vertex)
    bpy.types.VIEW3D_MT_paint_vertex.append(menu_func_vertex_dec)
    bpy.types.VIEW3D_MT_object.append(menu_func_add_checker_mat)

    print("I4C jsou borci")

def unregister():
    # UI
    bpy.utils.unregister_class(VIEW3D_PT_POG)

    # Operators
    bpy.utils.unregister_class(MESH_OT_set_origin_selection)
    bpy.utils.unregister_class(MESH_OT_add_tracked_lamp)
    bpy.utils.unregister_class(MESH_OT_increment_vertex_color_hue)
    bpy.utils.unregister_class(MESH_OT_decrement_vertex_color_hue)
    bpy.utils.unregister_class(OBJECT_OT_add_checker_material)

    # F3 menu
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func_origin)
    bpy.types.VIEW3D_MT_light_add.remove(menu_func_lamp)
    bpy.types.VIEW3D_MT_paint_vertex.remove(menu_func_vertex)
    bpy.types.VIEW3D_MT_paint_vertex.remove(menu_func_vertex_dec)
    bpy.types.VIEW3D_MT_object.remove(menu_func_add_checker_mat)
    print("naschle")
