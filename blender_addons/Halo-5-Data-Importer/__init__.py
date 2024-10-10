import bpy
import os
import importlib.util
import subprocess
import sys
from bpy.props import StringProperty, CollectionProperty, BoolProperty, IntProperty
from bpy.types import AddonPreferences, Operator, Panel, PropertyGroup, UIList

bl_info = {
    "name": "Halo 5 Data Importer",
    "author": "Brooen",    
    "blender": (4, 2, 1),
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
        name=".structure_lightmap Files Directory",
        subtype='DIR_PATH',
        default="",
        update=lambda self, context: bpy.ops.file.load_light_files('INVOKE_DEFAULT')
    )

    material_search_folder: StringProperty(
        name=".material Files Directory",
        subtype='DIR_PATH',
        default="",
    )

    base_texture_path: StringProperty(
        name="Converted .bitmap Files Directory",
        subtype='DIR_PATH',
        default="",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "light_dir")
        layout.prop(self, "material_search_folder")
        layout.prop(self, "base_texture_path")

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

# Operator to import selected light files
# Operator to import selected light files using the light_importer.py script
class FILE_OT_import_lights(Operator):
    bl_idname = "file.import_lights"
    bl_label = "Import Selected Lights"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        directory = prefs.light_dir

        selected_files = [os.path.join(directory, item.name) for item in context.scene.light_files if item.select]

        if not selected_files:
            self.report({'WARNING'}, "No light files selected")
            return {'CANCELLED'}

        try:
            # Import the light_importer script and run the read_binary_file_and_create_lights function
            script_path = os.path.join(os.path.dirname(__file__), "light_importer.py")
            if os.path.exists(script_path):
                spec = importlib.util.spec_from_file_location("light_importer", script_path)
                light_importer = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(light_importer)

                # Run the imported script's function with the selected files
                light_importer.read_binary_file_and_create_lights(selected_files)

                self.report({'INFO'}, "Selected lights imported successfully")
            else:
                self.report({'ERROR'}, "light_importer script not found.")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to import lights: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

# Operator to install the mmh3 module
class FILE_OT_install_mmh3(Operator):
    bl_idname = "file.install_mmh3"
    bl_label = "Install MurMur Hash"

    def execute(self, context):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mmh3"])
            self.report({'INFO'}, "Successfully installed mmh3 module.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to install mmh3: {e}")
        return {'FINISHED'}

class FILE_OT_run_material_importer(Operator):
    bl_idname = "file.run_material_importer"
    bl_label = "Run Material Importer"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        addon_directory = os.path.dirname(__file__)  # Define addon_directory here

        # Check if the Shaders node group already exists
        if "Shaders" not in bpy.data.node_groups:
            # Append Shaders nodegroup from Shaders.blend
            shaders_blend = os.path.join(addon_directory, "Shaders.blend")
            if os.path.exists(shaders_blend):
                with bpy.data.libraries.load(shaders_blend, link=False) as (data_from, data_to):
                    if "Shaders" in data_from.node_groups:
                        data_to.node_groups = ["Shaders"]
                        self.report({'INFO'}, "Appended Shaders nodegroup from Shaders.blend.")
                    else:
                        self.report({'WARNING'}, "Shaders nodegroup not found in Shaders.blend.")
            else:
                self.report({'WARNING'}, "Shaders.blend file not found.")
        else:
            self.report({'INFO'}, "Shaders nodegroup already exists in the file.")

        # Import and run the material importer script
        script_path = os.path.join(addon_directory, "material_importer.py")

        if os.path.exists(script_path):
            spec = importlib.util.spec_from_file_location("material_importer", script_path)
            material_importer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(material_importer)

            # Run the imported script's main function with arguments
            material_importer.main(
                search_folder=prefs.material_search_folder,
                base_texture_path=prefs.base_texture_path,
                run_on_selected=True  # Always run on selected objects; checkbox hidden
            )
        else:
            self.report({'ERROR'}, "Material importer script not found.")
            return {'CANCELLED'}
        
        self.report({'INFO'}, "Materials processed successfully")
        return {'FINISHED'}

# Operator to run the material cleaner script
class FILE_OT_run_material_cleaner(Operator):
    bl_idname = "file.run_material_cleaner"
    bl_label = "Run Material Cleaner"

    def execute(self, context):
        # Get the path to the material_cleaner.py script
        script_path = os.path.join(os.path.dirname(__file__), "material_cleaner.py")

        if os.path.exists(script_path):
            # Import and run the material cleaner script
            spec = importlib.util.spec_from_file_location("material_cleaner", script_path)
            material_cleaner = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(material_cleaner)

            # Run the main function in the material_cleaner script
            material_cleaner.main()
        else:
            self.report({'ERROR'}, "Material cleaner script not found.")
            return {'CANCELLED'}

        self.report({'INFO'}, "Material cleaner processed successfully.")
        return {'FINISHED'}
        
# UIList to display the files with checkboxes
class FILE_UL_light_file_list(UIList):
    bl_idname = "FILE_UL_light_file_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "select", text="")
        layout.label(text=item.name, icon='FILE')
        
# Panel for the Addon UI in the Viewport Side Panel (N-Panel)
class VIEW3D_PT_light_importer_panel(Panel):
    bl_idname = "VIEW3D_PT_light_importer_panel"
    bl_label = "Import Menu"
    bl_category = "Halo 5 Data Importer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        # Light Importer Dropdown
        box = layout.box()
        box.label(text="Light Importer")
        box.operator("file.load_light_files", text="Load Light Files")
        box.template_list("FILE_UL_light_file_list", "", context.scene, "light_files", context.scene, "light_file_index")
        box.operator("file.import_lights", text="Import Selected Lights")

        # Material Importer Dropdown
        box = layout.box()
        box.label(text="Material Importer")
        box.operator("file.install_mmh3", text="Install MurMur Hash")
        box.operator("file.run_material_importer", text="Run Material Importer")

        # Other Section
        box = layout.box()
        box.label(text="Other")
        box.operator("file.run_material_cleaner", text="Run Material Cleaner")

# Register and Unregister Classes
classes = (
    LightFileItem,
    LightImporterAddonPreferences,
    FILE_OT_load_light_files,
    FILE_OT_import_lights,
    FILE_OT_install_mmh3,
    FILE_OT_run_material_importer,
    FILE_OT_run_material_cleaner,  # Register the new operator here
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
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.light_files
    del bpy.types.Scene.light_file_index

if __name__ == "__main__":
    register()
