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
 struct textures { //and shaders
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
 struct block7 {
 u8 stuff5 [1];
 };

 struct block8 {
 u8 stuff5 [1];
 };
 struct textures2 {
 u32 stuff5 [13];
 };
struct block9 {
    u32 stuffs[while($[$]!=0x6d || $[$+1]!=0x74 || $[$+2]!=0x69 || $[$+3]!=0x62)];
    u32 end;
};
struct final {
header header;
textures shader [1];
textures textures [header.texturescount - 1];
block2 block2 [header.block2count];
block3 block3 [header.block3count];
block4 block4 [header.block4count];
block5 block5 [header.block5count];
block6 block6 [header.block6count];

padding [header.block7count];

block8 block8 [header.block8count];
textures2 textures2 [header.texturescount - 1];
block9 block9 [7];;//[header.block9count];
};

final final @ 0x00;