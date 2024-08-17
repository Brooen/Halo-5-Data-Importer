struct header {
char magic[5];
padding [3];
u32 stuff [5];
u32 block1count;
u32 block2count;
u32 block3count;
u32 block4count;
u32 block5count;
u32 block6count;
u32 block7count;
u32 block8count;
u32 block9count;
u32 stuff2 [4];
};
 struct block1 {
 u32 stuff3 [6];
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
 u32 stuff5 [1];
 };
 struct block9 {
 u8 stuff5 [8];
 };
struct final {
header header;

block1 block1 [header.block1count];
block2 block2 [header.block2count];
block3 block3 [header.block3count];
block4 block4 [header.block4count];
block5 block5 [header.block5count];
block6 block6 [header.block6count];

block7 block7 [header.block7count];

//block8 block8 [header.block8count];
//block9 block9 [header.block9count];
};

final final @ 0x00;