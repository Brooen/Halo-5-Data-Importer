import os
import struct

def read_u16(file):
    """Read a u16 from the current file position."""
    data = file.read(2)
    if len(data) != 2:
        raise struct.error("Not enough bytes to unpack a u16.")
    return struct.unpack('H', data)[0]

def read_u8(file):
    """Read a u8 from the current file position."""
    data = file.read(1)
    if len(data) != 1:
        raise struct.error("Not enough bytes to unpack a u8.")
    return struct.unpack('B', data)[0]

def read_u32(file):
    """Read a u32 from the current file position."""
    return struct.unpack('I', file.read(4))[0]

def read_string(file, offset):
    """Read a null-terminated string from the file starting at the given offset."""
    file.seek(offset)
    chars = []
    while True:
        char = file.read(1)
        if char == b'\x00':  # Null-terminator
            break
        chars.append(char.decode('utf-8'))
    return ''.join(chars)

def process_bitmap(bitmap_path):
    """Process the .bitmap file to extract normalized and curve information after skipping the required bytes."""
    try:
        with open(bitmap_path, 'rb') as bitmap:
            # Skip the first 28 bytes
            bitmap.seek(28, os.SEEK_CUR)
            
            # Read the 13 u32 values and calculate the total number of bytes to skip
            skip_amount = 0
            multipliers = [24, 16, 32, 20, 16, 8, 1, 1] + [0] * 5  # Multipliers for each u32
            
            for multiplier in multipliers:
                u32_value = read_u32(bitmap)
                skip_amount += u32_value * multiplier
            
            # Skip the calculated number of bytes and 80 more bytes
            bitmap.seek(skip_amount + 80, os.SEEK_CUR)
            
            # Read the u32 for overridecount
            overridecount = read_u32(bitmap)
            
            # Skip 252 bytes and then skip overridecount * 40 bytes
            bitmap.seek(252 + (overridecount * 40), os.SEEK_CUR)
            
            # Read the u16 for normalization
            normalized_value = read_u16(bitmap)
            normalized = 0 if normalized_value == 0x3100 else 1
            
            # Skip 7 bytes to reach the curve value
            bitmap.seek(7, os.SEEK_CUR)
            
            # Read the u8 for the curve type
            curve_value = read_u8(bitmap)
            
            curve_types = {
                0x00: "unknown",
                0x01: "xrgb",
                0x02: "gamma_2",
                0x03: "linear",
                0x04: "offset_log",
                0x05: "srgb",
                0x06: "rec709"
            }
            
            curve = curve_types.get(curve_value, "unknown")
            
            return normalized, curve
    except Exception as e:
        print(f"Error processing {bitmap_path}: {e}")
        return None, None

def process_files(directory, header_file):
    """Process the header, files, and names files in the specified directory."""
    header_path = os.path.join(directory, header_file)
    
    with open(header_path, 'rb') as header:
        header.seek(0x10)
        string_count = read_u32(header)
    
    files_path = os.path.join(directory, "files")
    names_path = os.path.join(directory, "names")
    
    strings_dict = {}
    with open(files_path, 'rb') as files, open(names_path, 'rb') as names:
        for _ in range(string_count):
            # Read offset
            offset = read_u32(files)
            
            # Skip 40 bytes
            files.seek(40, os.SEEK_CUR)
            
            # Read string ID
            string_id = read_u32(files)
            
            # Skip 40 more bytes
            files.seek(40, os.SEEK_CUR)
            
            # Read the string from the names file
            string = read_string(names, offset)
            
            # Initialize placeholders for curve and normalized
            curve = None
            normalized = None
            
            # If the string is a .bitmap file, process it
            if string.endswith('.bitmap'):
                bitmap_path = os.path.join(directory, string.replace('\\', os.sep))
                if os.path.exists(bitmap_path):
                    normalized, curve = process_bitmap(bitmap_path)
            
            # Store the string, curve, and normalized value
            strings_dict[string_id] = (string, curve, normalized)
    
    return strings_dict

def write_to_file(strings_dict, output_file):
    """Write the sorted strings, IDs, and additional data to a text file."""
    with open(output_file, 'w') as f:
        for string_id in sorted(strings_dict.keys()):
            string, curve, normalized = strings_dict[string_id]
            if curve is not None and normalized is not None:
                f.write(f"ID: {string_id} String: {string} Curve: {curve} Normalized: {normalized}\n")
            else:
                f.write(f"ID: {string_id} String: {string}\n")

def main():
    file_paths = [
        # Add paths to directories containing "header" files here
        r"F:\halo models\Raw Files\Halo 5 Campaign\deploy\x1\levels\globals-rtx-1"

    ]
    
    all_strings = {}
    
    for directory in file_paths:
        header_file = "header"  # Name of the header file without extension
        strings = process_files(directory, header_file)
        
        # Merge dictionaries, overriding duplicates
        all_strings.update(strings)
    
    output_file = r"C:\Users\abfer\Downloads\filepaths.txt"
    write_to_file(all_strings, output_file)
    print(f"Strings and IDs written to {output_file}")

if __name__ == "__main__":
    main()
