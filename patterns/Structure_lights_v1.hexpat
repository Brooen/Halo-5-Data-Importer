#pragma pattern_limit 99999999999
#pragma array_limit 9999999999999
import std.io;

struct header {
    char magic[5];
    padding [3];
    u32 stuff [5];
    u32 texturescount;
    u32 block2count;
    u32 block3count;
    u32 block4count;
    u32 block5count;
    u32 block6count;
    u32 block7count;
    u32 block8count;
    u32 block9count;
    u32 block10count;
    u32 block11count;
    u32 block12count;
    u32 block13count;
};

//static params, kinda useless for light importer

struct textures {
    u32 stuff3 [4];
    u32 tagID [1];
    u32 stuff4 [1];
};

struct block2 {
    u32 stuff3 [4];
};

struct block3 {
    u32 stuff3 [8];
};

struct block4 {
    u32 stuff3 [5];
};

struct block5 {
    u32 stuff3 [4];
};

struct block6 {
    u32 stuff3 [2];
};

struct StringTable {
    if ($-parent.beginBlock >= parent.header.block7count)
        break;
    char string[];
};  
struct textures2header {
    padding [4];
    u32 globalID;
};
 
struct textures2 {
    u32 stuff5 [13];
};

//dynamic

enum lighttype : u32 {
Omni = 0x00000000, //point
Spot = 0x00000001,
Directional = 0x00000002, //spot
Planar = 0x00000003, // area
Sun = 0x00000004
};

struct lightdataheader {
padding [8];
u32 tagID;
padding [20];
u32 lightcount;
padding [12];
};

struct position {
    float x;
    float y;
    float z;
};

struct facing {
    float i;
    float j;
    float k;
    float w;
};

struct color {
    float r;
    float g;
    float b;
}  [[static, color(std::format("{:02X}{:02X}{:02X}", u8(255*r), u8(255*g), u8(255*b)))]];

struct attenuation {
    float near_attenuation;
    float far_attenuation;
};

struct camera_params {
    float near_begin;
    float far_begin;
    float camera_distance_fade_start;
    float camera_distance_fade_end;
    float camera_distance_shadow_fade_start;
    float camera_distance_shadow_fade_end;
    float specular_intensity;
};

struct area_light_params {
    float planar_light_width;
    float planar_light_height;
    float area_light_radius;
};

struct shared_spot_params {
    float inner_cone_angle;
    float outer_cone_angle;
    u32 cone_projection_shape;
};

struct lightdata1 {
    u32 composerID;
    position position;
    facing facing;
    u32 data1;
    lighttype light_type;
    color color;
    float intensity_scalar;
    padding [44];
    attenuation attenuation;
    padding [44];
    camera_params camera_params;
    area_light_params area_light_params;
    shared_spot_params shared_spot_params;
    float data [73];
};

struct lightdata2 {
    u32 data [422];
};

struct static {
    header header;
    textures textures [header.texturescount];
    block2 block2 [header.block2count];
    block3 block3 [header.block3count];
    block4 block4 [header.block4count];
    block5 block5 [header.block5count];
    block6 block6 [header.block6count];
    u64 beginBlock = $;
    StringTable stringtable[while(true)];
    //padding [header.block7count];
    padding [header.block8count];
};

struct dynamic {
    lightdataheader lightdataheader;
    lightdata1 lightdata1[lightdataheader.lightcount];
    lightdata2 lightdata2[lightdataheader.lightcount];
};


static StaticLightParams @ 0x00;
dynamic DynamicLightParams @ $;