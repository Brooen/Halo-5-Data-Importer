#pragma pattern_limit 9999999999
struct block {
u32 offset;
padding [40];
u32 globalid;
padding [40];
};

block block [42846] @ 0x00; //number is defined in header file