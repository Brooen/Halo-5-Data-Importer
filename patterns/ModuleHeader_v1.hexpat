#pragma pattern_limit 9999999999
struct block {
padding [16];
u32 datacount;
};

block block [1] @ 0x00;