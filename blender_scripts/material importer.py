import bpy
import struct
import mmh3
import os

def murmur_hash_and_flip(string):
    # Compute MurmurHash3 (32-bit) of the string
    hash_value = mmh3.hash(string, signed=False)
    return hash_value

def read_u32(file):
    """Reads a 32-bit unsigned integer from the file."""
    return struct.unpack('<I', file.read(4))[0]

def read_string_table(file, length):
    strings = []
    data_start = file.tell()
    data_end = data_start + length
    print(f"Reading string table from {hex(data_start)} to {hex(data_end)}")
    
    while file.tell() < data_end:
        s = b''
        while True:
            c = file.read(1)
            if c == b'\x00' or c == b'':
                break
            s += c
        decoded_string = s.decode('ascii', errors='ignore')
        hashed_string = murmur_hash_and_flip(decoded_string)
        print(f"String: {decoded_string}, Hashed: {hashed_string:#010x}")
        strings.append((decoded_string, hashed_string))
    return strings

def load_id_mapping(filepath):
    id_mapping = {}
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split("String: ")
            if len(parts) == 2:
                id_part, rest = parts
                id_value = int(id_part.split("ID: ")[1])
                
                # Further split for bitmap lines
                if "Curve:" in rest and "Normalized:" in rest:
                    string_part, curve_part = rest.split(" Curve: ")
                    curve, normalized = curve_part.split(" Normalized: ")
                    id_mapping[id_value] = {
                        "path": string_part,
                        "curve": curve,
                        "normalized": int(normalized)
                    }
                else:
                    id_mapping[id_value] = {"path": rest, "curve": None, "normalized": None}
    return id_mapping

def extract_filename_from_path(file_path):
    # Extract the file name without the extension
    return file_path.split('\\')[-1].split('.')[0]

def create_shader_in_blender(shader_name, parameters):
    """Creates or updates a shader node group in Blender based on the provided parameters."""
    # Ensure the node group exists
    node_group_name = f"H5 material_shader: {shader_name}"
    if node_group_name not in bpy.data.node_groups:
        print(f"Node group '{node_group_name}' not found in Blender.")
        return
    
    node_group = bpy.data.node_groups[node_group_name]
    
    # Get the active material of the selected object
    obj = bpy.context.active_object
    if not obj or not obj.active_material:
        print("No active object with an active material found.")
        return
    
    material = obj.active_material
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Create a UV Map node
    uv_map_node = nodes.new('ShaderNodeUVMap')
    uv_map_node.name = "UV Map"
    uv_map_node.label = "UV Map"
    uv_map_node.uv_map = "UVMap"  # Set to the default UV map or change to the appropriate UV map name
    uv_map_node.location = (-600, 0)

    # Add the node group to the material's node tree
    group_node = nodes.new('ShaderNodeGroup')
    group_node.node_tree = node_group
    group_node.name = shader_name
    group_node.label = shader_name
    group_node.location = (400, 0)  # Move the node group to the right

    print(f"Setting up shader '{shader_name}' with parameters: {parameters}")
    
    # Set the initial positions for nodes
    x_offset = -200
    y_offset = 0
    y_step = -300  # Vertical spacing between nodes
    
    for param_name, param_data in parameters.items():
        print(f"Processing parameter '{param_name}' of type '{param_data['type']}'")

        if param_data['type'] == 'bitmap':
            # Load the image texture
            texture_path = param_data['value']
            print(f"Loading texture from path: {texture_path}")
            image = bpy.data.images.load(texture_path)
            
            # Create or find the texture node
            tex_node = nodes.new('ShaderNodeTexImage')
            tex_node.name = param_name
            tex_node.label = param_name
            tex_node.image = image
            tex_node.location = (x_offset, y_offset)
            y_offset += y_step  # Move down for the next node
            print(f"Texture node '{tex_node.name}' created/updated at location {tex_node.location}.")

            # Set the curve (color space) if provided
            curve = param_data['curve']
            if curve:
                if curve.lower() == "linear":
                    curve = "Linear Rec.709"
                elif curve.lower() == "srgb":
                    curve = "sRGB"
                tex_node.image.colorspace_settings.name = curve
            print(f"Color space set to: {tex_node.image.colorspace_settings.name}")

            # Create a mapping node and set UV scale
            mapping_node = nodes.new('ShaderNodeMapping')
            mapping_node.name = f"{param_name}_Mapping"
            mapping_node.label = f"{param_name}_Mapping"
            mapping_node.location = (x_offset - 300, y_offset + 150)  # Place above and to the left of the texture node
            
            # Set the UV scale for X and Y
            mapping_node.inputs['Scale'].default_value[0] = param_data['uv_scale'][0]  # X
            mapping_node.inputs['Scale'].default_value[1] = param_data['uv_scale'][1]  # Y
            
            # Connect the UV Map node to the Mapping node
            links.new(uv_map_node.outputs['UV'], mapping_node.inputs['Vector'])
            print(f"Connected UV Map node to mapping node.")

            # Connect the mapping node to the texture node
            links.new(mapping_node.outputs['Vector'], tex_node.inputs['Vector'])
            print(f"Connected mapping node to texture node.")

            # Connect the texture node to the appropriate input of the group node
            if param_name in group_node.inputs.keys():
                links.new(tex_node.outputs['Color'], group_node.inputs[param_name])
                print(f"Connected texture node to group node input '{param_name}'.")

        elif param_data['type'] == 'color':
            # Apply color parameter directly without creating a new shader node
            if param_name in group_node.inputs.keys():
                group_node.inputs[param_name].default_value = param_data['value']
                print(f"Set color parameter '{param_name}' to {param_data['value']}")

        elif param_data['type'] == 'real':
            if param_name in group_node.inputs.keys():
                group_node.inputs[param_name].default_value = param_data['value']
                print(f"Set real parameter '{param_name}' to {param_data['value']}")

        elif param_data['type'] == 'boolean':
            if param_name in group_node.inputs.keys():
                group_node.inputs[param_name].default_value = param_data['value']
                print(f"Set boolean parameter '{param_name}' to {param_data['value']}")

        elif param_data['type'] == 'int':
            if param_name in group_node.inputs.keys():
                group_node.inputs[param_name].default_value = param_data['value']
                print(f"Set int parameter '{param_name}' to {param_data['value']}")
    
    # Ensure the Material Output node is present
    material_output = nodes.get('Material Output')
    if not material_output:
        material_output = nodes.new('ShaderNodeOutputMaterial')
        material_output.location = (800, 0)  # Place it to the right of the group node

    # Connect the group node output to the material output
    if group_node.outputs.get('Output'):
        links.new(group_node.outputs['Output'], material_output.inputs['Surface'])
        print(f"Connected group node 'Output' to material output surface.")
                
def process_block(file, id_mapping, previous_id, string_table, base_texture_path):
    # Read the raw parameter name (4 bytes)
    parameter_name_bytes = file.read(4)
    parameter_name = struct.unpack('<I', parameter_name_bytes)[0]
    print(f"Parameter Name (hashed): {parameter_name:#010x}, Raw Bytes: {parameter_name_bytes.hex()}")

    # Match the parameter name with the hashed strings in the string table
    matching_string = None
    for string, hashed_string in string_table:
        if hashed_string == parameter_name:
            matching_string = string
            break

    if matching_string:
        print(f"Matched Parameter Name: {matching_string}")
    else:
        print("No matching parameter name found.")

    # Prepare the parameters for the shader node group
    parameters = {}

    # Read the parameter type (u32)
    parameter_type = read_u32(file)
    print(f"Parameter Type: {parameter_type}")

    if parameter_type == 0:  # bitmap
        parameter_index = read_u32(file)
        file.seek(8, 1)  # Skip 8 bytes of padding
        bitmap_tag_type = read_u32(file)
        bitmap_tag_id = read_u32(file)
        file.seek(20, 1)  # Skip 20 bytes of padding
        data = struct.unpack('<4f', file.read(16))
        uv_scale = struct.unpack('<2f', file.read(8))
        other_data = struct.unpack('<9f', file.read(36))
        file.seek(124, 1)  # Skip 124 bytes of padding
        
        # Determine the file path, curve, and normalized value if the bitmap_tag_id matches
        bitmap_info = id_mapping.get(bitmap_tag_id, {"path": "Unknown Filepath", "curve": "Unknown Curve", "normalized": None})
        
        # Validate the file path
        if bitmap_info['path'] == "Unknown Filepath" or not bitmap_info['path'].endswith('.bitmap'):
            print(f"Skipping {matching_string} because the filepath is unknown or invalid.")
        else:
            # Modify the file path to be a full path and replace the extension
            full_texture_path = bitmap_info['path'].replace(".bitmap", ".png")
            full_texture_path = f"{base_texture_path}\\{full_texture_path}"
            
            # Ensure the file actually exists before adding it
            if os.path.exists(full_texture_path):
                parameters[matching_string] = {
                    'type': 'bitmap',
                    'value': full_texture_path,
                    'curve': bitmap_info['curve'],
                    'uv_scale': uv_scale
                }
            else:
                print(f"Texture file does not exist: {full_texture_path}")

    elif parameter_type == 4:  # color
        parameter_index = read_u32(file)
        file.seek(36, 1)  # Skip 8 bytes of padding
        argb = struct.unpack('<4f', file.read(16))
        parameters[matching_string] = {'type': 'color', 'value': argb}
        file.seek(168, 1)  # Skip 124 bytes of padding

    elif parameter_type == 1:  # real
        parameter_index = read_u32(file)
        file.seek(52, 1)  # Skip 8 bytes of padding
        real_value = struct.unpack('<f', file.read(4))[0]
        parameters[matching_string] = {'type': 'real', 'value': real_value}
        file.seek(164, 1)  # Skip 124 bytes of padding

    elif parameter_type == 3:  # boolean
        parameter_index = read_u32(file)
        file.seek(68, 1)  # Skip 8 bytes of padding
        boolean_value = read_u32(file)
        parameters[matching_string] = {'type': 'boolean', 'value': bool(boolean_value)}
        file.seek(148, 1)  # Skip 124 bytes of padding

    elif parameter_type == 2:  # int
        parameter_index = read_u32(file)
        file.seek(68, 1)  # Skip 8 bytes of padding
        int_value = read_u32(file)
        parameters[matching_string] = {'type': 'int', 'value': int_value}
        file.seek(148, 1)  # Skip 124 bytes of padding


    return matching_string, parameters

def process_secondary_header(file, id_mapping, string_table, base_texture_path):
    # Skip the first 28 bytes
    file.seek(28, 1)
    
    # Read the shader tag ID (u32)
    shadertagID = read_u32(file)
    print(f"Shader Tag ID: {shadertagID}")
    
    # Lookup the ID in the mapping
    if shadertagID in id_mapping:
        full_path = id_mapping[shadertagID]["path"]
        filename = extract_filename_from_path(full_path)
        print(f"Shader: {filename}")
    else:
        print(f"ID {shadertagID} not found in the mapping.")
    
    # Skip 32 bytes
    file.seek(32, 1)
    
    # Read the material parameters count (u32)
    materialparameterscount = read_u32(file)
    print(f"Material Parameters Count: {materialparameterscount}")
    
    # Skip 60 bytes to the end of the header
    file.seek(60, 1)

    # Process each block based on material parameters count
    shader_name = filename
    all_parameters = {}

    for _ in range(materialparameterscount):
        matching_string, parameters = process_block(file, id_mapping, shadertagID, string_table, base_texture_path)
        if matching_string:
            all_parameters.update(parameters)
    
    # Apply the parameters to the shader in Blender
    create_shader_in_blender(shader_name, all_parameters)

def process_binary_file(material_filepath, id_mapping_filepath, base_texture_path):
    # Load the ID mapping from the file
    id_mapping = load_id_mapping(id_mapping_filepath)
    
    with open(material_filepath, 'rb') as f:
        # Previous steps for skipping and reading initial data
        f.seek(28)
        u32_values = [read_u32(f) for _ in range(13)]
        skip_bytes = (
            u32_values[0] * 24 +
            u32_values[1] * 16 +
            u32_values[2] * 32 +
            u32_values[3] * 20 +
            u32_values[4] * 16 +
            u32_values[5] * 8
        )
        string_table_offset = f.tell() + skip_bytes
        f.seek(string_table_offset)
        string_table_length = u32_values[6]
        string_table = read_string_table(f, string_table_length)

        # Print the string table (for demonstration purposes)
        print("String table:")
        for s, h in string_table:
            print(f"String: {s}, Hashed: {h:#010x}")      
        # Skip the number of bytes equal to u32[7]
        f.seek(u32_values[7], 1)
        
        # Skip the calculated bytes based on u32[0]
        f.seek((u32_values[0] - 1) * 52, 1)
        
        # Now process the secondary header
        process_secondary_header(f, id_mapping, string_table, base_texture_path)

def find_material_file(material_name, folder_path):
    """Search for a .material file that matches the material name in the specified folder."""
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.material') and file.startswith(material_name):
                return os.path.join(root, file)
    return None

def apply_material_from_file(folder_path, id_mapping_filepath, base_texture_path):
    """Find and apply the material from a .material file based on the selected object's material."""
    obj = bpy.context.active_object
    if not obj or not obj.material_slots:
        print("No active object with materials found.")
        return
    
    for material_slot in obj.material_slots:
        material_name = material_slot.material.name
        print(f"Searching for material: {material_name}")
        
        material_filepath = find_material_file(material_name, folder_path)
        
        if not material_filepath:
            print(f"No .material file found for {material_name} in {folder_path}.")
            continue
        
        print(f"Found .material file: {material_filepath}")
        
        # Process the found .material file
        process_binary_file(material_filepath, id_mapping_filepath, base_texture_path)

# Example usage
folder_path = r"F:\halo models\Raw Files\Halo 5 Materials"
id_mapping_filepath = r"C:\Users\abfer\Downloads\filepaths.txt"
base_texture_path = r"F:\halo models\Raw Files\H5 Textures"

apply_material_from_file(folder_path, id_mapping_filepath, base_texture_path)
