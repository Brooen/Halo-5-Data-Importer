import bpy

def rename_and_merge_materials():
    # Dictionary to store materials by their tag_name (file path)
    materials_by_tag = {}

    for mat in bpy.data.materials:
        # Check if the material has both 'tag_name' and 'material_name' custom properties
        if "tag_name" in mat and "material_name" in mat:
            tag_name = mat["tag_name"]  # This is the file path
            material_name = mat["material_name"]  # This is the actual material name
            
            # Check if there's already a material with the same tag_name
            if tag_name in materials_by_tag:
                # Merge the current material into the existing one
                existing_material = materials_by_tag[tag_name]
                
                # If this is not the main material, reassign its users to the existing one
                if mat != existing_material:
                    for obj in bpy.data.objects:
                        if obj.type == 'MESH':
                            for slot in obj.material_slots:
                                if slot.material == mat:
                                    slot.material = existing_material
                                    
                    # Remove the duplicate material after merging
                    bpy.data.materials.remove(mat)
            else:
                # No existing material with the same tag_name, so store this one
                materials_by_tag[tag_name] = mat
                mat.name = material_name  # Ensure the base material has the correct material name

    # Now handle renaming for materials with different tag_names
    name_counter = {}
    
    for mat in bpy.data.materials:
        if "tag_name" in mat and "material_name" in mat:
            base_name = mat["material_name"]
            
            # Check if we already used this base_name, if so increment the count
            if base_name not in name_counter:
                name_counter[base_name] = 1  # Start with base name (no number)
            else:
                # Add a numbered suffix to avoid collisions
                new_mat_name = f"{base_name} {name_counter[base_name]}"
                mat.name = new_mat_name
                name_counter[base_name] += 1  # Increment the counter for this base name

# Run the function
rename_and_merge_materials()
def main():
    rename_and_merge_materials()