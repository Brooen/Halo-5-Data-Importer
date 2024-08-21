//created by Brooen
//credit to AxCut for all of the murmur functions
import std.io;
import std.string;
import std.mem;
import type.base;
import std.core;

fn read_block(auto s,auto j) {
    return (((((s[j+3]<<8)+s[j+2])<<8)+s[j+1])<<8)+s[j];
};

fn murmur_32_scramble(u32 k) {
    k *= 0xcc9e2d51;
    k = (k << 15) | (k >> 17);
    k *= 0x1b873593;
    return k;
};

fn murmur3_32(ref auto key, auto seed)
{
    u32 h = seed;
    u32 k;
    u32 j=0;
    u64 len = std::string::length(key)-1;
    /* Read in groups of 4. */
    for (u64 i = len >> 2, i, i-=1) {
        // Here is a source of differing results across endiannesses.
        // A swap here has no effects on hash properties though.
        k = read_block(key,j);
        j += 4;
        h ^= murmur_32_scramble(k);
        h = (h << 13) | (h >> 19);
        h = h * 5 + 0xe6546b64;
    }
    /* Read the rest. */
    k = 0;
    for (u64 i = (len & 3), i, i -= 1 ) {
        k = (k << 8);
        k = k | key[i+j-1];
    }
    // A swap is *not* necessary here because the preceding loop already
    // places the low bytes in the low places according to whatever endianness
    // we use. Swaps only apply when the memory is copied in a chunk.
    h ^= murmur_32_scramble(k);
    /* Finalize. */
    h ^= len;
    h ^= h >> 16;
    h *= 0x85ebca6b;
    h ^= h >> 13;
    h *= 0xc2b2ae35;
    h ^= h >> 16;
    return h;
};


struct Header {
    char magic[5];
    padding[3];
    u32 stuff[5];
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

struct Textures {
    u32 stuff3 [4];
    u32 tagID;
    u32 stuff4;
};

struct Block2 {
    u32 stuff3[4];
};

struct Block3 {
    u32 stuff3[8];
};

struct Block4 {
    u32 stuff3[5];
};

struct Block5 {
    u32 stuff3[4];
};

struct Block6 {
    u32 stuff3[2];
};


u32 stringTableCount;

struct Encode<auto string> {
    u32 v = murmur3_32(string,0)[[hidden]];
};

struct FindAddress<auto encoded> {
  u32 v = std::mem::find_sequence(0, 
    u8(encoded),u8(encoded>>8),u8(encoded>>16),u8(encoded>>24)
  )[[hidden]];
};

struct Marker {
   u32;
   str string = parent.string; 
};

struct StringTable {
  char string[];
  Encode<string>          encoded[[export,format("as_hex_number"),sealed]];
  FindAddress<encoded.v>  address[[export,format("as_hex_number"),sealed]];
  if (address.v != 0xFFFFFFFF)
      Marker marker @ address.v[[format("as_parent_string")]];
  stringTableCount    = std::core::array_index();
  if ($-parent.beginBlock >= parent.header.block7count)
    break;
}[[format("as_string")]];  

fn as_string(auto val) {
    return std::format("{}",val.string);
};

fn as_parent_string(auto val) {
    return std::format("{}",val.string);
};

fn as_hex_number(auto val) {
    return std::format("{:#x}",val.v);
};

struct Textures2Header {
    padding[4];
    u32 globalID;
};
 
struct Textures2 {
    u32 stuff5[13];
};

fn getString(auto key, u32 count) {
    for (u32 i=0, i<count, i+=1) {

        if (static.stringTable[i].encoded.v == key) {
            str temp = static.stringTable[i].string;
            u32 len = std::string::length(temp);
            return std::string::substr(temp,0,len-1);
        }
    }
    return "";
};

//end of static, start of dynamic

struct MaterialParametersHeader { // header for material data and other stuff
    padding[8];
    u32 globalTagID;
    padding[12];
    u32 shaderTagType;
    u32 shaderTagID;
    padding[32];
    u32 materialParametersCount;
    padding[60];
};

enum ParameterType : u32 {
    bitmap,
    real,
    int,     
    boolean, 
    color
};

struct ParamName {
    u32 parameterName;
    str parameterString = getString(parameterName,stringTableCount);
}[[format("param_name_string")]];

fn param_name_string(auto v) {
    return v.parameterString;
};

struct MaterialParameters { //material data
    ParamName parameterName; //have to figure out how to dehash
    ParameterType parameterType;
    if (parameterType == ParameterType::bitmap) {
        u32 ParameterIndex;
        padding[8];
        u32 BitmapTagType;
        u32 BitmapTagID;
        padding[20];
        float Data[4];
        float UVScale[2];
        float otherData[9];
        padding[124];
    }
    if (parameterType == ParameterType::color) {
        u32 parameterIndex;
        padding[36];
        float ARGB[4];
        float otherData[11];
        padding[124];
    }
    if (parameterType == ParameterType::real) {
        u32 parameterIndex;
        padding[52];
        float real;
        float otherData[10];
        padding[124];
    }    
    if (parameterType == ParameterType::boolean) {
        u32 parameterIndex;
        padding[68];
        u32 boolean;
        float otherData[6];
        padding[124];
    }    
    if (parameterType == ParameterType::int) {
        u32 parameterIndex;
        padding[68];
        u32 integer;
        float otherData[6];
        padding[124];
    }    
}[[format("mat_param_sname_str")]];


fn mat_param_sname_str(auto v) {
    return v.parameterName.parameterString;
};

struct Block11 { // unkown, i also dont know how to find how many of these blocks there are
    u32 data[21];
};

struct Block13 { // seems to be additional texture params
    u32 data[14];
};

struct Static {
    Header header;
    Textures shader;
    Textures textures[header.texturescount - 1];
    Block2 block2[header.block2count];
    Block3 block3[header.block3count];
    Block4 block4[header.block4count];
    Block5 block5[header.block5count];
    Block6 block6[header.block6count];
    u64 beginBlock = $;
    StringTable stringTable[while(true)];
    //padding [header.block7count];
    padding[60];
    Textures2Header textures2Header[header.texturescount - 1];
    padding[4];
    Textures2 textures2[header.texturescount - 1];
};

struct Dynamic {
    MaterialParametersHeader materialParametersHeader;
    MaterialParameters materialParameters[materialParametersHeader.materialParametersCount];
    //block11 block11 [1];
    //block13 block13 [header.texturescount - 1];
};


struct StaticAndDynamic {
    Static staticMaterialParams;
    Dynamic dynamicMaterialParams;
};

Static static@0[[hidden]];
StaticAndDynamic sd@0;