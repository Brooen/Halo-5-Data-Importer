# Halo 5 Data Importer
 Tool that reads halo 5 tags and imports them to Blender

## Current Tag Support

.material

.structure_lights

## How to Use
First, you need the halo 5 console files, then you need to put all of the .material and .structure_lights files into their own folders. For lights, they all need to be in 1 directory, for materials, they need to keep their file hierarchy.

Then, to import lights, just select the ones you want and import.

To import lights, for the first time you need to install MurMur. Any other time, you just select the models you want to be set up and click set up materials.

For the bitmaps, you need every bitmap, converted to png

## Download Options

[Latest Release](https://github.com/Brooen/Halo-5-Data-Importer/releases/latest "Latest Release")
[Latest Test Build](https://github.com/Brooen/Halo-5-Data-Importer/raw/refs/heads/main/blender_addons/Halo-5-Data-Importer.zip "Latest Test Build")

## Credits
- LordZedd - initial help with how halo 5's tag format works
- Gravemind - help with fixing the light importer
- Chiefster - making most of the shaders
- TacoHombre - helping me test out the shaders and making new ones when needed
- AxCut - helping me with the MurMur code in the material pattern file
- Surasia - new module tool that let me export induvidual tag types instead of everything at once
