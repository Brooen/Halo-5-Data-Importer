import bpy
import os
import importlib.util
from bpy.props import StringProperty, CollectionProperty, BoolProperty, IntProperty
from bpy.types import AddonPreferences, Operator, Panel, PropertyGroup, UIList

bl_info = {
    "name": "Light Importer Addon",
    "blender": (2, 90, 0),
    "category": "Object",
}

# Property Group to store file items with selection
class LightFileItem(PropertyGroup):
    name: StringProperty()
    select: BoolProperty(default=False)

# Addon Preferences (Directory input only here)
class LightImporterAddonPreferences(AddonPreferences):
    bl_idname = __name__

    light_dir: StringProperty(
        name="Light Files Directory",
        subtype='DIR_PATH',
        default="//",
        update=lambda self, context: bpy.ops.file.load_light_files('INVOKE_DEFAULT')
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "light_dir")

# Operator to load files from the directory into the UIList
class FILE_OT_load_light_files(Operator):
    bl_idname = "file.load_light_files"
    bl_label = "Load Light Files"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        directory = prefs.light_dir
        
        context.scene.light_files.clear()

        # Load files from the directory
        if os.path.isdir(directory):
            for file_name in os.listdir(directory):
                if file_name.endswith(".structure_lights"):  # Filter by extension if necessary
                    item = context.scene.light_files.add()
                    item.name = file_name

        return {'FINISHED'}

# Operator to execute the light importing
class FILE_OT_import_lights(Operator):
    bl_idname = "file.import_lights"
    bl_label = "Import Selected Lights"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        directory = prefs.light_dir

        # Gather selected filepaths
        selected_files = [os.path.join(directory, item.name) for item in context.scene.light_files if item.select]

        # Check if any files are selected
        if not selected_files:
            self.report({'WARNING'}, "No files selected")
            return {'CANCELLED'}

        # Import and run the light importer script
        script_path = os.path.join(os.path.dirname(__file__), "light_importer.py")

        if os.path.exists(script_path):
            spec = importlib.util.spec_from_file_location("light_importer", script_path)
            light_importer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(light_importer)
            
            # Run the imported script's function
            light_importer.read_binary_file_and_create_lights(selected_files)
        else:
            self.report({'ERROR'}, "Light importer script not found.")
            return {'CANCELLED'}
        
        self.report({'INFO'}, "Files processed successfully")
        return {'FINISHED'}

# UIList to display the files with checkboxes
class FILE_UL_light_file_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "select", text="")
        layout.label(text=item.name, icon='FILE')

# Panel for the Addon UI in the Viewport Side Panel (N-Panel)
class VIEW3D_PT_light_importer_panel(Panel):
    bl_idname = "VIEW3D_PT_light_importer_panel"
    bl_label = "Light Importer"
    bl_category = "Light Importer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        # File list UI
        layout.template_list("FILE_UL_light_file_list", "", context.scene, "light_files", context.scene, "light_file_index")

        # Import button
        layout.operator("file.import_lights", text="Import Selected Lights")

# Register and Unregister Classes
classes = (
    LightFileItem,
    LightImporterAddonPreferences,
    FILE_OT_load_light_files,
    FILE_OT_import_lights,
    FILE_UL_light_file_list,
    VIEW3D_PT_light_importer_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.light_files = CollectionProperty(type=LightFileItem)
    bpy.types.Scene.light_file_index = IntProperty(default=0)

def unregister():
    for cls in classes:
        bp
