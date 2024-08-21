import struct
import bpy
import os
import mathutils

def create_light(light_type, name, location, rotation_values, color, intensity, area_size=None, spot_cone=None):
    # Multiply location coordinates by 3.048
    location = (location[0] * 3.048, location[1] * 3.048, location[2] * 3.048)
    
    # Determine light type for Blender
    light_data = bpy.data.lights.new(name=name, type=light_type)
    light_data.color = color
    light_data.energy = intensity * 10  # Multiply the light's strength by 10

    if light_type == 'AREA' and area_size:
        light_data.shape = 'RECTANGLE' 
        light_data.size = area_size[0] * 5.5
        light_data.size_y = area_size[1] * 5.5
    
    if light_type == 'SPOT' and spot_cone:
        light_data.spot_size = spot_cone[1]  # Set outer cone angle
        light_data.spot_blend = (spot_cone[1] - spot_cone[0]) / spot_cone[1]  # Blend factor

    light_object = bpy.data.objects.new(name, light_data)
    light_object.location = location
    
    # Create an Euler rotation and apply the rotations
    i, j, k, w = rotation_values  # Extract the rotation values
    rotation = mathutils.Euler()
    rotation.rotate_axis('X', k)
    rotation.rotate_axis('Y', -j)  # Inverting the Y rotation
    rotation.rotate_axis('Z', i)

    light_object.rotation_euler = rotation
    
    return light_object

def read_binary_file_and_create_lights(filepaths):
    for filepath in filepaths:
        # Create a collection named after the file path (using the file name)
        collection_name = os.path.splitext(os.path.basename(filepath))[0]
        light_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(light_collection)

        with open(filepath, 'rb') as file:
            # Part 1: Initial byte skipping and calculating skip amount
            file.seek(28)

            multipliers = [24, 16, 32, 20, 16, 8, 1, 1, 0, 0, 0, 0, 0]
            total_skip = 0
            for i in range(13):
                u32_value = struct.unpack('I', file.read(4))[0]
                total_skip += u32_value * multipliers[i]

            file.seek(total_skip, 1)

            # Part 2: Secondary header and block processing
            file.seek(32, 1)
            block_count = struct.unpack('I', file.read(4))[0]
            print(f"Block count: {block_count}")
            file.seek(12, 1)

            light_type_mapping = {
                0: "POINT",
                1: "SPOT",
                2: "POINT",
                3: "AREA",
                4: "SUN"
            }

            for index in range(block_count):
                composer_id = struct.unpack('I', file.read(4))[0]
                x, y, z = struct.unpack('fff', file.read(12))
                i, j, k, w = struct.unpack('ffff', file.read(16))
                file.seek(4, 1)
                light_type_value = struct.unpack('I', file.read(4))[0]
                light_type = light_type_mapping.get(light_type_value, "POINT")
                r, g, b, intensity = struct.unpack('ffff', file.read(16))
                file.seek(124, 1)
                area_width, area_height, area_radius = struct.unpack('fff', file.read(12))
                spot_inner_cone_angle, spot_outer_cone_area = struct.unpack('ff', file.read(8))
                file.seek(296, 1)

                # Prepare the data to create a light in Blender
                location = (x, y, z)
                rotation_values = (i, j, k, w)  # Pass the rotation as a tuple
                color = (r, g, b)

                # Create the light in Blender
                light_object = create_light(
                    light_type=light_type,
                    name=f"Light_{index + 1}",
                    location=location,
                    rotation_values=rotation_values,  # Use rotation_values instead of rotation
                    color=color,
                    intensity=intensity,
                    area_size=(area_width, area_height) if light_type == 'AREA' else None,
                    spot_cone=(spot_inner_cone_angle, spot_outer_cone_area) if light_type == 'SPOT' else None
                )

                # Link the light directly to the collection (no context collection linking)
                light_collection.objects.link(light_object)

                print(f"Created light {index + 1} of type {light_type} in collection {collection_name}")

# No need for example usage since the addon will handle file paths
