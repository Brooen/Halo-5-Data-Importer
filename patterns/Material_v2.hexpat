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

//static params, kinda useless for material importer

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

//end of static, start of dynamic

struct materialparametersheader { // header for material data and other stuff
    padding [8];
    u32 GlobalTagID [1];
    padding [12];
    u32 ShaderTagType;
    u32 ShaderTagID;
    padding [32];
    u32 materialparameterscount;
    padding [60];
};
enum ParameterType : u32 {
    bitmap = 0x00000001,
    real = 0x00000000,
    //int = 0x03000000, //need an example to know what the number should be
    //boolean = 0x04000000,
    color = 0x00000004
};

struct materialparameters { //material data
    u32 ParameterName; //have to figure out how to dehash
    ParameterType ParameterType;
    u32 ParameterIndex;
    padding [8];
    u32 bitmapTagType;
    u32 bitmapTagID;
    padding [20];
    float ARGB [4];
    float UVScale [2];
    float AllTheRest [9];
    padding [124];
};

struct block11 { // unkown, i also dont know how to find how many of these blocks there are
    u32 data [21];
};

struct block13 { // seems to be additional texture params
    u32 data [14];
};

struct static {
    header header;
    textures shader [1];
    textures textures [header.texturescount - 1];
    block2 block2 [header.block2count];
    block3 block3 [header.block3count];
    block4 block4 [header.block4count];
    block5 block5 [header.block5count];
    block6 block6 [header.block6count];
    u64 beginBlock = $;
    StringTable stringtable[while(true)];
    //padding [header.block7count];
    padding [60];
    textures2header textures2header [header.texturescount - 1];
    padding [4];
    textures2 textures2 [header.texturescount - 1];
};

struct dynamic {
    materialparametersheader MaterialParametersHeader;
    materialparameters MaterialParameters [MaterialParametersHeader.materialparameterscount];
    //block11 block11 [1];
    //block13 block13 [header.texturescount - 1];
};

static StaticMaterialParams @ 0x00;
//dynamic DynamicMaterialParams @$;