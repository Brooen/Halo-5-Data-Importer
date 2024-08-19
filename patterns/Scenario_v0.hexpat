#pragma pattern_limit 99999999999
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
struct dynblock1header {
u32 block1length;
};

struct dynblock1 {
    if ($-parent.beginBlock >= parent.dynblock1header.block1length)
        break;
    u32 data [16];
};

struct dynblock2 {
    u32 data [28];
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
    padding [header.block8count];
};

struct dynamic {
    dynblock1header dynblock1header;
    u64 beginBlock = $;
    dynblock1 dynblock1[while(true)];
    dynblock2 dynblock2 [443];
    u32 data;
};


static StaticScenarioParams @ 0x00;
dynamic DynamicScenarioParams @ $;