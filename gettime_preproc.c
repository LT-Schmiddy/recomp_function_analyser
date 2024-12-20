# 1 "mm/src/libultra/os/gettime.c"
# 1 "<built-in>" 1
# 1 "<built-in>" 3
# 374 "<built-in>" 3
# 1 "<command line>" 1
# 1 "<built-in>" 2
# 1 "mm/src/libultra/os/gettime.c" 2
# 1 "mm/include\\ultra64.h" 1



# 1 "mm/include\\PR/ultratypes.h" 1



typedef signed char s8;
typedef unsigned char u8;
typedef signed short int s16;
typedef unsigned short int u16;
typedef signed long s32;
typedef unsigned long u32;
typedef signed long long int s64;
typedef unsigned long long int u64;

typedef volatile u8 vu8;
typedef volatile u16 vu16;
typedef volatile u32 vu32;
typedef volatile u64 vu64;
typedef volatile s8 vs8;
typedef volatile s16 vs16;
typedef volatile s32 vs32;
typedef volatile s64 vs64;

typedef float f32;
typedef double f64;






typedef unsigned int size_t;
# 39 "mm/include\\PR/ultratypes.h"
typedef void* TexturePtr;
# 5 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/gbi.h" 1
# 1 "mm/include\\PR\\mbi.h" 1
# 61 "mm/include\\PR\\mbi.h"
# 1 "mm/include\\PR/gbi.h" 1
# 1 "mm/include\\PR\\mbi.h" 1
# 2 "mm/include\\PR/gbi.h" 2
# 62 "mm/include\\PR\\mbi.h" 2







# 1 "mm/include\\PR/abi.h" 1
# 71 "mm/include\\PR/abi.h"
typedef struct
{
    unsigned int cmd : 8;
    unsigned int flags : 8;
    unsigned int gain : 16;
    unsigned int addr;
} Aadpcm;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int flags : 8;
    unsigned int gain : 16;
    unsigned int addr;
} Apolef;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int flags : 8;
    unsigned int pad1 : 16;
    unsigned int addr;
} Aenvelope;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int pad1 : 8;
    unsigned int dmem : 16;
    unsigned int pad2 : 16;
    unsigned int count : 16;
} Aclearbuff;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int pad1 : 8;
    unsigned int pad2 : 16;
    unsigned int inL : 16;
    unsigned int inR : 16;
} Ainterleave;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int pad1 : 24;
    unsigned int addr;
} Aloadbuff;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int flags : 8;
    unsigned int pad1 : 16;
    unsigned int addr;
} Aenvmixer;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int flags : 8;
    unsigned int gain : 16;
    unsigned int dmemi : 16;
    unsigned int dmemo : 16;
} Amixer;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int flags : 8;
    unsigned int dmem2 : 16;
    unsigned int addr;
} Apan;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int flags : 8;
    unsigned int pitch : 16;
    unsigned int addr;
} Aresample;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int flags : 8;
    unsigned int pad1 : 16;
    unsigned int addr;
} Areverb;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int pad1 : 24;
    unsigned int addr;
} Asavebuff;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int pad1 : 24;
    unsigned int pad2 : 2;
    unsigned int number : 4;
    unsigned int base : 24;
} Asegment;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int flags : 8;
    unsigned int dmemin : 16;
    unsigned int dmemout : 16;
    unsigned int count : 16;
} Asetbuff;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int flags : 8;
    unsigned int vol : 16;
    unsigned int voltgt : 16;
    unsigned int volrate : 16;
} Asetvol;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int pad1 : 8;
    unsigned int dmemin : 16;
    unsigned int dmemout : 16;
    unsigned int count : 16;
} Admemmove;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int pad1 : 8;
    unsigned int count : 16;
    unsigned int addr;
} Aloadadpcm;

typedef struct
{
    unsigned int cmd : 8;
    unsigned int pad1 : 8;
    unsigned int pad2 : 16;
    unsigned int addr;
} Asetloop;





typedef struct
{
    unsigned int w0;
    unsigned int w1;
} Awords;

typedef union {
    Awords words;
    Aadpcm adpcm;
    Apolef polef;
    Aclearbuff clearbuff;
    Aenvelope envelope;
    Ainterleave interleave;
    Aloadbuff loadbuff;
    Aenvmixer envmixer;
    Aresample resample;
    Areverb reverb;
    Asavebuff savebuff;
    Asegment segment;
    Asetbuff setbuff;
    Asetvol setvol;
    Admemmove dmemmove;
    Aloadadpcm loadadpcm;
    Amixer mixer;
    Asetloop setloop;
    long long int force_union_align;
} Acmd;






typedef short ADPCM_STATE[16];




typedef short POLEF_STATE[4];




typedef short RESAMPLE_STATE[16];
# 278 "mm/include\\PR/abi.h"
typedef short ENVMIX_STATE[40];
# 70 "mm/include\\PR\\mbi.h" 2
# 2 "mm/include\\PR/gbi.h" 2
# 6 "mm/include\\ultra64.h" 2

# 1 "mm/include\\PR/gu.h" 1




# 1 "mm/include\\PR/gbi.h" 1
# 6 "mm/include\\PR/gu.h" 2
# 22 "mm/include\\PR/gu.h"
void guMtxIdent(Mtx* mtx);
void guMtxIdentF(float mf[4][4]);

void guOrtho(Mtx* m, f32 l, f32 r, f32 b, f32 t, f32 n, f32 f, f32 scale);
void guOrthoF(float m[4][4], f32 l, f32 r, f32 b, f32 t, f32 n, f32 f, f32 scale);

void guPerspective(Mtx* m, u16* perspNorm, f32 fovy, f32 aspect, f32 near, f32 far, f32 scale);
void guPerspectiveF(float mf[4][4], u16* perspNorm, f32 fovy, f32 aspect, f32 near, f32 far, f32 scale);

void guLookAt(Mtx* m, f32 xEye, f32 yEye, f32 zEye, f32 xAt, f32 yAt, f32 zAt, f32 xUp, f32 yUp, f32 zUp);
void guLookAtF(float mf[4][4], f32 xEye, f32 yEye, f32 zEye, f32 xAt, f32 yAt, f32 zAt, f32 xUp, f32 yUp, f32 zUp);

void guLookAtHilite(Mtx* m, LookAt* l, Hilite* h, f32 xEye, f32 yEye, f32 zEye, f32 xAt, f32 yAt, f32 zAt, f32 xUp, f32 yUp, f32 zUp, f32 xl1, f32 yl1, f32 zl1, f32 xl2, f32 yl2, f32 zl2, s32 hiliteWidth, s32 hiliteHeight);
void guLookAtHiliteF(float mf[4][4], LookAt* l, Hilite* h, f32 xEye, f32 yEye, f32 zEye, f32 xAt, f32 yAt, f32 zAt, f32 xUp, f32 yUp, f32 zUp, f32 xl1, f32 yl1, f32 zl1, f32 xl2, f32 yl2, f32 zl2, s32 hiliteWidth, s32 hiliteHeight);

void guRotate(Mtx* m, f32 a, f32 x, f32 y, f32 z);
void guRotateF(float m[4][4], f32 a, f32 x, f32 y, f32 z);

void guScale(Mtx* mtx, f32 x, f32 y, f32 z);
void guTranslate(Mtx* mtx, f32 x, f32 y, f32 z);

void guPosition(Mtx* m, f32 rot, f32 pitch, f32 yaw, f32 scale, f32 x, f32 y, f32 z);
void guPositionF(float mf[4][4], f32 rot, f32 pitch, f32 yaw, f32 scale, f32 x, f32 y, f32 z);

void guMtxF2L(float mf[4][4], Mtx* m);
void guMtxL2F(float m1[4][4], Mtx* m2);

void guNormalize(float* x, float* y, float* z);


f32 sinf(f32 __x);
f32 cosf(f32 __x);

s16 sins(u16 x);
s16 coss(u16 x);

f32 sqrtf(f32 f);
# 8 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/guint.h" 1





typedef union {
    f64 d;
    struct {
        u32 hi;
        u32 lo;
    } word;
} du;

typedef union {
    u32 i;
    f32 f;
} fu;



extern f32 __libm_qnan_f;
# 9 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/controller_voice.h" 1




# 1 "mm/include\\PR\\os_voice.h" 1




# 1 "mm/include\\PR\\os_message.h" 1



# 1 "mm/include\\PR\\os_thread.h" 1








typedef s32 OSPri;
typedef s32 OSId;

typedef union {
    struct {
                  f32 f_odd;
                  f32 f_even;
    } f;
} __OSfp;

typedef struct {
                u64 at, v0, v1, a0, a1, a2, a3;
                u64 t0, t1, t2, t3, t4, t5, t6, t7;
                u64 s0, s1, s2, s3, s4, s5, s6, s7;
                u64 t8, t9, gp, sp, s8, ra;
                u64 lo, hi;
                u32 sr, pc, cause, badvaddr, rcp;
                u32 fpcsr;
                __OSfp fp0, fp2, fp4, fp6, fp8, fp10, fp12, fp14;
                __OSfp fp16, fp18, fp20, fp22, fp24, fp26, fp28, fp30;
} __OSThreadContext;

typedef struct {
              u32 flag;
              u32 count;
              u64 time;
} __OSThreadprofile;

typedef struct OSThread {
               struct OSThread* next;
               OSPri priority;
               struct OSThread** queue;
               struct OSThread* tlnext;
               u16 state;
               u16 flags;
               OSId id;
               s32 fp;
               __OSThreadprofile* thprof;
               __OSThreadContext context;
} OSThread;
# 73 "mm/include\\PR\\os_thread.h"
void osCreateThread(OSThread* thread, OSId id, void* entry, void* arg, void* sp, OSPri p);
void osDestroyThread(OSThread* t);
void osYieldThread(void);
void osStartThread(OSThread* t);
void osStopThread(OSThread* t);
OSId osGetThreadId(OSThread* t);
void osSetThreadPri(OSThread* thread, OSPri p);
OSPri osGetThreadPri(OSThread* t);


OSThread* __osGetActiveQueue(void);
# 5 "mm/include\\PR\\os_message.h" 2

typedef void* OSMesg;
typedef u32 OSEvent;

typedef struct OSMesgQueue {
               OSThread* mtQueue;
               OSThread* fullQueue;
               s32 validCount;
               s32 first;
               s32 msgCount;
               OSMesg* msg;
} OSMesgQueue;
# 53 "mm/include\\PR\\os_message.h"
void osCreateMesgQueue(OSMesgQueue* mq, OSMesg* msq, s32 count);
s32 osSendMesg(OSMesgQueue* mq, OSMesg msg, s32 flags);
s32 osJamMesg(OSMesgQueue* mq, OSMesg msg, s32 flag);
s32 osRecvMesg(OSMesgQueue* mq, OSMesg* msg, s32 flags);

void osSetEventMesg(OSEvent e, OSMesgQueue* mq, OSMesg m);
# 6 "mm/include\\PR\\os_voice.h" 2

typedef enum OsVoiceHandleMode {
            VOICE_HANDLE_MODE_0,
            VOICE_HANDLE_MODE_1,
            VOICE_HANDLE_MODE_2,
            VOICE_HANDLE_MODE_3,
            VOICE_HANDLE_MODE_4
} OsVoiceHandleMode;

typedef struct {
              OSMesgQueue* __mq;
              s32 __channel;
              s32 __mode;
              u8 cmd_status;
} OSVoiceHandle;

typedef struct {
               u16 warning;
               u16 answer_num;
               u16 voice_level;
               u16 voice_sn;
               u16 voice_time;
               u16 answer[5];
               u16 distance[5];
} OSVoiceData;
# 43 "mm/include\\PR\\os_voice.h"
s32 osVoiceInit(OSMesgQueue* mq, OSVoiceHandle* hd, int channel);
s32 osVoiceSetWord(OSVoiceHandle* hd, u8* word);
s32 osVoiceCheckWord(u8* word);
s32 osVoiceStartReadData(OSVoiceHandle* hd);
s32 osVoiceStopReadData(OSVoiceHandle* hd);
s32 osVoiceGetReadData(OSVoiceHandle* hd, OSVoiceData* result);
s32 osVoiceClearDictionary(OSVoiceHandle* hd, u8 numWords);
s32 osVoiceMaskDictionary(OSVoiceHandle* hd, u8* maskPattern, int size);
s32 osVoiceControlGain(OSVoiceHandle* hd, s32 analog, s32 digital);
# 6 "mm/include\\PR/controller_voice.h" 2

# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 1 3
# 72 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 3
# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stddef_ptrdiff_t.h" 1 3
# 18 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stddef_ptrdiff_t.h" 3
typedef long long int ptrdiff_t;
# 73 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 2 3




# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stddef_size_t.h" 1 3
# 78 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 2 3
# 87 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 3
# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stddef_wchar_t.h" 1 3
# 24 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stddef_wchar_t.h" 3
typedef unsigned short wchar_t;
# 88 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 2 3




# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stddef_null.h" 1 3
# 93 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 2 3
# 107 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 3
# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stddef_max_align_t.h" 1 3
# 14 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stddef_max_align_t.h" 3
typedef double max_align_t;
# 108 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 2 3




# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stddef_offsetof.h" 1 3
# 113 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 2 3
# 8 "mm/include\\PR/controller_voice.h" 2

typedef struct {
              u8 dummy;
              u8 txsize;
              u8 rxsize;
              u8 cmd;
              u8 addrh;
              u8 addrl;
              u8 data[2];
              u8 datacrc;
} __OSVoiceRead2Format;

typedef struct {
               u8 dummy;
               u8 txsize;
               u8 rxsize;
               u8 cmd;
               u8 addrh;
               u8 addrl;
               u8 data[36];
               u8 datacrc;
} __OSVoiceRead36Format;

typedef struct {
              u8 dummy;
              u8 txsize;
              u8 rxsize;
              u8 cmd;
              u8 addrh;
              u8 addrl;
              u8 data[4];
              u8 datacrc;
} __OSVoiceWrite4Format;

typedef struct {
               u8 dummy;
               u8 txsize;
               u8 rxsize;
               u8 cmd;
               u8 addrh;
               u8 addrl;
               u8 data[20];
               u8 datacrc;
} __OSVoiceWrite20Format;

typedef struct {
              u8 txsize;
              u8 rxsize;
              u8 cmd;
              u8 data;
              u8 scrc;
              u8 datacrc;
} __OSVoiceSWriteFormat;

s32 __osVoiceContRead2(OSMesgQueue* mq, s32 channel, u16 address, u8 dst[2]);
s32 __osVoiceContRead36(OSMesgQueue* mq, s32 channel, u16 address, u8 dst[36]);
s32 __osVoiceContWrite4(OSMesgQueue* mq, s32 channel, u16 address, u8 dst[4]);
s32 __osVoiceContWrite20(OSMesgQueue* mq, s32 channel, u16 address, u8 dst[20]);
s32 __osVoiceCheckResult(OSVoiceHandle* hd, u8* status);
s32 __osVoiceGetStatus(OSMesgQueue* mq, s32 channel, u8* status);
s32 __osVoiceSetADConverter(OSMesgQueue* mq, s32 channel, u8 data);
u8 __osVoiceContDataCrc(u8* data, size_t numBytes);
# 10 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/os.h" 1



# 1 "mm/include\\PR\\os_ai.h" 1






u32 osAiGetLength(void);
s32 osAiSetFrequency(u32 frequency);
s32 osAiSetNextBuffer(void* buf, u32 size);
# 5 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_cache.h" 1




# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 1 3
# 6 "mm/include\\PR\\os_cache.h" 2

void osInvalDCache(void* vaddr, size_t nbytes);
void osInvalICache(void* vaddr, size_t nbytes);
void osWritebackDCache(void* vaddr, s32 nbytes);
void osWritebackDCacheAll(void);
# 6 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_cont.h" 1







typedef struct {
              u16 type;
              u8 status;
              u8 errno;
} OSContStatus;

typedef struct {
              u16 button;
              s8 stick_x;
              s8 stick_y;
              u8 errno;
} OSContPad;
# 69 "mm/include\\PR\\os_cont.h"
s32 osContInit(OSMesgQueue* mq, u8* bitpattern, OSContStatus* data);
s32 osContStartQuery(OSMesgQueue* mq);
s32 osContStartReadData(OSMesgQueue* mq);
s32 osContSetCh(u8 ch);
void osContGetQuery(OSContStatus* data);
void osContGetReadData(OSContPad* data);
# 7 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_convert.h" 1



# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stdint.h" 1 3
# 52 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stdint.h" 3
# 1 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\stdint.h" 1 3
# 11 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\stdint.h" 3
# 1 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vcruntime.h" 1 3
# 57 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vcruntime.h" 3
# 1 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\sal.h" 1 3
# 2974 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\sal.h" 3
# 1 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\concurrencysal.h" 1 3
# 2975 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\sal.h" 2 3
# 58 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vcruntime.h" 2 3
# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\vadefs.h" 1 3
# 18 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\vadefs.h" 3
# 1 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vadefs.h" 1 3
# 15 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vadefs.h" 3
#pragma pack(push, 8)
# 47 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vadefs.h" 3
#pragma warning(push)
#pragma warning(disable: 4514 4820)
# 61 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vadefs.h" 3
        typedef unsigned __int64 uintptr_t;
# 72 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vadefs.h" 3
        typedef char* va_list;
# 155 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vadefs.h" 3
    void __cdecl __va_start(va_list* , ...);
# 207 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vadefs.h" 3
#pragma warning(pop)
#pragma pack(pop)
# 19 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\vadefs.h" 2 3
# 59 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vcruntime.h" 2 3

#pragma warning(push)
#pragma warning(disable: 4514 4820)
# 96 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vcruntime.h" 3
#pragma pack(push, 8)
# 188 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vcruntime.h" 3
    typedef unsigned __int64 size_t;
    typedef __int64 ptrdiff_t;
    typedef __int64 intptr_t;
# 204 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vcruntime.h" 3
    typedef _Bool __vcrt_bool;
# 378 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vcruntime.h" 3
    void __cdecl __security_init_cookie(void);
# 387 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\vcruntime.h" 3
        void __cdecl __security_check_cookie( uintptr_t _StackCookie);
        __declspec(noreturn) void __cdecl __report_gsfailure( uintptr_t _StackCookie);



extern uintptr_t __security_cookie;







#pragma pack(pop)

#pragma warning(pop)
# 12 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\stdint.h" 2 3



#pragma warning(push)
#pragma warning(disable: 4514 4820)

typedef signed char int8_t;
typedef short int16_t;
typedef int int32_t;
typedef long long int64_t;
typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
typedef unsigned long long uint64_t;

typedef signed char int_least8_t;
typedef short int_least16_t;
typedef int int_least32_t;
typedef long long int_least64_t;
typedef unsigned char uint_least8_t;
typedef unsigned short uint_least16_t;
typedef unsigned int uint_least32_t;
typedef unsigned long long uint_least64_t;

typedef signed char int_fast8_t;
typedef int int_fast16_t;
typedef int int_fast32_t;
typedef long long int_fast64_t;
typedef unsigned char uint_fast8_t;
typedef unsigned int uint_fast16_t;
typedef unsigned int uint_fast32_t;
typedef unsigned long long uint_fast64_t;

typedef long long intmax_t;
typedef unsigned long long uintmax_t;
# 136 "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.41.34120\\include\\stdint.h" 3
#pragma warning(pop)
# 53 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stdint.h" 2 3
# 5 "mm/include\\PR\\os_convert.h" 2
# 23 "mm/include\\PR\\os_convert.h"
extern uintptr_t osVirtualToPhysical(void*);
# 8 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_exception.h" 1






typedef u32 OSIntMask;
typedef u32 OSHWIntr;
# 38 "mm/include\\PR\\os_exception.h"
OSIntMask osGetIntMask(void);
OSIntMask osSetIntMask(OSIntMask im);



void __osSetHWIntrRoutine(OSHWIntr interrupt, s32 (*handler)(void), void* stackEnd);
void __osGetHWIntrRoutine(OSHWIntr interrupt, s32 (**handler)(void), void** stackEnd);
void __osSetGlobalIntMask(OSHWIntr mask);
void __osResetGlobalIntMask(OSHWIntr mask);
# 9 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_flash.h" 1




# 1 "mm/include\\PR\\os_pi.h" 1





# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stddef.h" 1 3
# 7 "mm/include\\PR\\os_pi.h" 2



typedef struct {
               u32 errStatus;
               void* dramAddr;
               void* C2Addr;
               u32 sectorSize;
               u32 C1ErrNum;
               u32 C1ErrSector[4];
} __OSBlockInfo;

typedef struct {
               u32 cmdType;
               u16 transferMode;
               u16 blockNum;
               s32 sectorNum;
               uintptr_t devAddr;
               u32 bmCtlShadow;
               u32 seqCtlShadow;
               __OSBlockInfo block[2];
} __OSTranxInfo;

typedef struct OSPiHandle {
               struct OSPiHandle* next;
               u8 type;
               u8 latency;
               u8 pageSize;
               u8 relDuration;
               u8 pulse;
               u8 domain;
               uintptr_t baseAddress;
               u32 speed;
               __OSTranxInfo transferInfo;
} OSPiHandle;

typedef struct {
              u8 type;
              uintptr_t address;
} OSPiInfo;

typedef struct {
              u16 type;
              u8 pri;
              u8 status;
              OSMesgQueue* retQueue;
} OSIoMesgHdr;

typedef struct {
               OSIoMesgHdr hdr;
               void* dramAddr;
               uintptr_t devAddr;
               size_t size;
               OSPiHandle* piHandle;
} OSIoMesg;

typedef struct OSDevMgr {
               s32 active;
               OSThread* thread;
               OSMesgQueue* cmdQueue;
               OSMesgQueue* evtQueue;
               OSMesgQueue* acsQueue;
               s32 (*piDmaCallback)(s32, uintptr_t, void*, size_t);
               s32 (*epiDmaCallback)(OSPiHandle*, s32, uintptr_t, void*, size_t);
} OSDevMgr;
# 102 "mm/include\\PR\\os_pi.h"
extern OSPiHandle* __osPiTable;

void osCreatePiManager(OSPri pri, OSMesgQueue* cmdQ, OSMesg* cmdBuf, s32 cmdMsgCnt);

OSPiHandle* osCartRomInit(void);

s32 osEPiWriteIo(OSPiHandle* handle, uintptr_t devAddr, u32 data);
s32 osEPiReadIo(OSPiHandle* handle, uintptr_t devAddr, u32* data);
s32 osEPiStartDma(OSPiHandle* pihandle, OSIoMesg* mb, s32 direction);
s32 osEPiLinkHandle(OSPiHandle* handle);
# 6 "mm/include\\PR\\os_flash.h" 2
# 37 "mm/include\\PR\\os_flash.h"
OSPiHandle* osFlashReInit(u8 latency, u8 pulse, u8 pageSize, u8 relDuration, u32 start);
OSPiHandle* osFlashInit(void);
void osFlashReadStatus(u8* flashStatus);
void osFlashReadId(u32* flashType, u32* flashVendor);
void osFlashClearStatus(void);
s32 osFlashAllErase(void);
s32 osFlashSectorErase(u32 pageNum);
s32 osFlashWriteBuffer(OSIoMesg* mb, s32 priority, void* dramAddr, OSMesgQueue* mq);
s32 osFlashWriteArray(u32 pageNum);
s32 osFlashReadArray(OSIoMesg* mb, s32 priority, u32 pageNum, void* dramAddr, u32 pageCount, OSMesgQueue* mq);
void osFlashChange(u32 flashNum);
void osFlashAllEraseThrough(void);
void osFlashSectorEraseThrough(u32 pageNum);
s32 osFlashCheckEraseEnd(void);
# 10 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_host.h" 1



void __osInitialize_common(void);
void __osInitialize_autodetect(void);
# 11 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_internal_error.h" 1






OSThread* __osGetCurrFaultedThread(void);
# 12 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_internal_reg.h" 1







u32 __osGetCause(void);
void __osSetCause(u32);
u32 __osGetCompare(void);
void __osSetCompare(u32 value);
u32 __osGetConfig(void);
void __osSetConfig(u32);
u32 __osGetSR(void);
void __osSetSR(u32 value);
OSIntMask __osDisableInt(void);
void __osRestoreInt(OSIntMask im);
u32 __osGetWatchLo(void);
void __osSetWatchLo(u32 value);

u32 __osSetFpcCsr(u32 value);
u32 __osGetFpcCsr(void);
# 13 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_internal_si.h" 1







s32 __osSiRawWriteIo(uintptr_t devAddr, u32 data);
s32 __osSiRawReadIo(uintptr_t devAddr, u32* data);
s32 __osSiRawStartDma(s32 direction, void* dramAddr);
# 14 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_internal.h" 1






# 1 "mm/include\\PR\\os_internal_rsp.h" 1





u32 __osSpGetStatus(void);
void __osSpSetStatus(u32 data);
s32 __osSpSetPc(u32 pc);
s32 __osSpRawStartDma(s32 direction, u32 devAddr, void* dramAddr, size_t size);
# 8 "mm/include\\PR\\os_internal.h" 2

typedef struct __osHwInt {
              s32 (*handler)(void);
              void* stackEnd;
} __osHwInt;
# 15 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_libc.h" 1



# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stdarg.h" 1 3
# 55 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stdarg.h" 3
# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stdarg___gnuc_va_list.h" 1 3
# 12 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stdarg___gnuc_va_list.h" 3
typedef __builtin_va_list __gnuc_va_list;
# 56 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stdarg.h" 2 3




# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stdarg_va_list.h" 1 3
# 12 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stdarg_va_list.h" 3
typedef __builtin_va_list va_list;
# 61 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stdarg.h" 2 3




# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stdarg_va_arg.h" 1 3
# 66 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stdarg.h" 2 3




# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stdarg___va_copy.h" 1 3
# 71 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stdarg.h" 2 3




# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\__stdarg_va_copy.h" 1 3
# 76 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stdarg.h" 2 3
# 5 "mm/include\\PR\\os_libc.h" 2






void bzero(void* begin, int length);
int bcmp(const void* __s1, const void* __s2, int __n);
void bcopy(const void* __src, void* __dest, int __n);


void osSyncPrintf(const char* fmt, ...);
# 16 "mm/include\\PR/os.h" 2

# 1 "mm/include\\PR\\os_pfs.h" 1



# 1 "mm/include\\PR/os.h" 1
# 5 "mm/include\\PR\\os_pfs.h" 2
# 72 "mm/include\\PR\\os_pfs.h"
typedef struct {
               s32 status;
               OSMesgQueue* queue;
               s32 channel;
               u8 id[32];
               u8 label[32];
               s32 version;
               s32 dir_size;
               s32 inode_table;
               s32 minode_table;
               s32 dir_table;
               s32 inodeStartPage;
               u8 banks;
               u8 activebank;
} OSPfs;

typedef struct {
               u32 file_size;
               u32 game_code;
               u16 company_code;
               char ext_name[4];
               char game_name[16];
} OSPfsState;

typedef union {
    struct {
                  u8 bank;
                  u8 page;
    } inode_t;
              u16 ipage;
} __OSInodeUnit;

typedef struct {
              __OSInodeUnit inodePage[128];
} __OSInode;

typedef struct {
               u32 game_code;
               u16 company_code;
               __OSInodeUnit start_page;
               u8 status;
               s8 reserved;
               u16 data_sum;
               u8 ext_name[4];
               u8 game_name[16];
} __OSDir;

typedef struct {
               u32 repaired;
               u32 random;
               u64 serialMid;
               u64 serialLow;
               u16 deviceid;
               u8 banks;
               u8 version;
               u16 checksum;
               u16 invertedChecksum;
} __OSPackId;

typedef struct {
                __OSInode inode;
                u8 bank;
                u8 map[(8 * 32)];
} __OSInodeCache;


s32 osPfsInitPak(OSMesgQueue* queue, OSPfs* pfs, s32 channel);
s32 osPfsChecker(OSPfs* pfs);
s32 osPfsAllocateFile(OSPfs* pfs, u16 companyCode, u32 gameCode, u8* gameName, u8* extName, s32 fileSize, s32* fileNo);
s32 osPfsFindFile(OSPfs* pfs, u16 companyCode, u32 gameCode, u8* gameName, u8* extName, s32* fileNo);
s32 osPfsDeleteFile(OSPfs* pfs, u16 companyCode, u32 gameCode, u8* gameName, u8* extName);
s32 osPfsReadWriteFile(OSPfs* pfs, s32 fileNo, u8 flag, s32 offset, s32 size, u8* data);
s32 osPfsFileState(OSPfs* pfs, s32 fileNo, OSPfsState* state);
s32 osPfsIsPlug(OSMesgQueue* mq, u8* pattern);
s32 osPfsFreeBlocks(OSPfs* pfs, s32* leftoverBytes);
# 18 "mm/include\\PR/os.h" 2

# 1 "mm/include\\PR\\os_reg.h" 1






u32 osGetCount(void);
# 20 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_system.h" 1
# 19 "mm/include\\PR\\os_system.h"
extern s32 osTvType;
extern s32 osRomType;
extern void* osRomBase;
extern s32 osResetType;
extern s32 osCicId;
extern s32 osVersion;
extern u32 osMemSize;
extern s32 osAppNMIBuffer[];

extern u64 osClockRate;

extern s32 osViClock;

extern u32 __OSGlobalIntMask;

u32 osGetMemSize(void);
s32 osAfterPreNMI(void);
# 21 "mm/include\\PR/os.h" 2

# 1 "mm/include\\PR\\os_time.h" 1







typedef u64 OSTime;

typedef struct OSTimer_s {
               struct OSTimer_s* next;
               struct OSTimer_s* prev;
               OSTime interval;
               OSTime value;
               OSMesgQueue* mq;
               OSMesg msg;
} OSTimer;

OSTime osGetTime(void);
void osSetTime(OSTime ticks);
int osSetTimer(OSTimer* t, OSTime countdown, OSTime interval, OSMesgQueue* mq, OSMesg msg);
int osStopTimer(OSTimer* t);
# 23 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_tlb.h" 1





void osMapTLBRdb(void);
void osUnmapTLBAll(void);
# 24 "mm/include\\PR/os.h" 2
# 1 "mm/include\\PR\\os_vi.h" 1
# 19 "mm/include\\PR\\os_vi.h"
typedef struct {
               u32 ctrl;
               u32 width;
               u32 burst;
               u32 vSync;
               u32 hSync;
               u32 leap;
               u32 hStart;
               u32 xScale;
               u32 vCurrent;
} OSViCommonRegs;

typedef struct {
               u32 origin;
               u32 yScale;
               u32 vStart;
               u32 vBurst;
               u32 vIntr;
} OSViFieldRegs;

typedef struct {
               u8 type;
               OSViCommonRegs comRegs;
               OSViFieldRegs fldRegs[2];
} OSViMode;
# 106 "mm/include\\PR\\os_vi.h"
extern OSViMode osViModeNtscHpf1;
extern OSViMode osViModePalLan1;
extern OSViMode osViModeNtscHpn1;
extern OSViMode osViModeNtscLan1;
extern OSViMode osViModeMpalLan1;
extern OSViMode osViModeFpalLan1;

extern OSViMode osViModeNtscHpf1;
extern OSViMode osViModePalLan1;
extern OSViMode osViModeNtscHpn1;
extern OSViMode osViModeNtscLan1;
extern OSViMode osViModeMpalLan1;
extern OSViMode osViModeFpalLan1;

void* osViGetCurrentFramebuffer(void);
void* osViGetNextFramebuffer(void);
void osViSetXScale(f32 value);
void osViSetYScale(f32 value);
void osViExtendVStart(u32 value);
void osViSetSpecialFeatures(u32 func);
void osViSetMode(OSViMode* modep);
void osViSetEvent(OSMesgQueue* mq, OSMesg m, u32 retraceCount);
void osViSwapBuffer(void* frameBufPtr);
void osViBlack(u8 active);
void osCreateViManager(OSPri pri);
# 25 "mm/include\\PR/os.h" 2
# 11 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/osint.h" 1








typedef struct __OSEventState {
              OSMesgQueue* messageQueue;
              OSMesg message;
} __OSEventState;

typedef struct __OSThreadTail {
              OSThread* next;
              OSPri priority;
} __OSThreadTail;

void __osEnqueueAndYield(OSThread** param_1);
void __osDequeueThread(OSThread** queue, OSThread* t);
void __osEnqueueThread(OSThread** param_1, OSThread* param_2);
OSThread* __osPopThread(OSThread** param_1);
void __osDispatchThread(void);
void __osCleanupThread(void);

void __osSetTimerIntr(OSTime tim);
OSTime __osInsertTimer(OSTimer* t);
void __osTimerInterrupt(void);
u32 __osProbeTLB(void* param_1);
s32 __osSpDeviceBusy(void);

void __osTimerServicesInit(void);

extern __osHwInt __osHwIntTable[];
extern __OSEventState __osEventStateTab[15];

extern __OSThreadTail __osThreadTail;
extern OSThread* __osRunQueue;
extern OSThread* __osActiveQueue;
extern OSThread* __osRunningThread;
extern OSThread* __osFaultedThread;

extern u32 __osShutdown;

extern OSTimer* __osTimerList;

extern OSTimer __osBaseTimer;
extern OSTime __osCurrentTime;
extern u32 __osBaseCounter;
extern u32 __osViIntrCount;
extern u32 __osTimerCounter;
# 12 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/piint.h" 1
# 84 "mm/include\\PR/piint.h"
extern OSDevMgr __osPiDevMgr;
extern OSPiHandle* __osCurrentHandle[];
extern u32 __osPiAccessQueueEnabled;

extern OSPiHandle __Dom1SpeedParam;
extern OSPiHandle __Dom2SpeedParam;

extern OSMesgQueue __osPiAccessQueue;

void __osDevMgrMain(void* arg);
void __osPiCreateAccessQueue(void);
void __osPiRelAccess(void);
void __osPiGetAccess(void);
s32 __osPiRawStartDma(s32 direction, uintptr_t devAddr, void* dramAddr, size_t size);
s32 __osEPiRawWriteIo(OSPiHandle* handle, uintptr_t devAddr, u32 data);
s32 __osEPiRawReadIo(OSPiHandle* handle, uintptr_t devAddr, u32* data);
s32 __osEPiRawStartDma(OSPiHandle* handle, s32 direction, uintptr_t cartAddr, void* dramAddr, size_t size);
OSMesgQueue* osPiGetCmdQueue(void);
# 13 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/siint.h" 1





extern u8 __osPfsInodeCacheBank;

void __osSiGetAccess(void);
void __osSiRelAccess(void);
s32 __osSiDeviceBusy(void);
void __osSiCreateAccessQueue(void);
# 14 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/sptask.h" 1
# 20 "mm/include\\PR/sptask.h"
typedef struct {
               u32 type;
               u32 flags;

               u64* ucode_boot;
               u32 ucode_boot_size;

               u64* ucode;
               u32 ucode_size;

               u64* ucode_data;
               u32 ucode_data_size;

               u64* dram_stack;
               u32 dram_stack_size;

               u64* output_buff;
               u64* output_buff_size;

               u64* data_ptr;
               u32 data_size;

               u64* yield_data_ptr;
               u32 yield_data_size;
} OSTask_t;

typedef union {
    OSTask_t t;
    long long int force_structure_alignment;
} OSTask;

typedef u32 OSYieldResult;

void osSpTaskLoad(OSTask* intp);
void osSpTaskStartGo(OSTask* tp);

void osSpTaskYield(void);
OSYieldResult osSpTaskYielded(OSTask* task);
# 15 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/rcp.h" 1
# 16 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/rdp.h" 1
# 46 "mm/include\\PR/rdp.h"
u32 osDpGetStatus(void);
void osDpSetStatus(u32 data);
# 17 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/R4300.h" 1
# 18 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/ucode.h" 1
# 13 "mm/include\\PR/ucode.h"
extern u64 rspbootTextStart[];
extern u64 rspbootTextEnd[];

extern u64 aspMainTextStart[];
extern u64 aspMainTextEnd[];
extern u64 aspMainDataStart[];
extern u64 aspMainDataEnd[];

extern u64 gspF3DZEX2_NoN_PosLight_fifoTextStart[];
extern u64 gspF3DZEX2_NoN_PosLight_fifoTextEnd[];
extern u64 gspF3DZEX2_NoN_PosLight_fifoDataStart[];
extern u64 gspF3DZEX2_NoN_PosLight_fifoDataEnd[];
# 19 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/viint.h" 1
# 48 "mm/include\\PR/viint.h"
typedef struct {
              f32 factor;
              u16 offset;
              u32 scale;
} __OSViScale;

typedef struct {
               u16 state;
               u16 retraceCount;
               void* buffer;
               OSViMode* modep;
               u32 features;
               OSMesgQueue* mq;
               OSMesg* msg;
               __OSViScale x;
               __OSViScale y;
} __OSViContext;

extern OSDevMgr __osViDevMgr;

void __osViSwapContext(void);
extern __OSViContext* __osViCurr;
extern __OSViContext* __osViNext;
extern u32 __additional_scanline;
__OSViContext* __osViGetCurrentContext(void);
void __osViInit(void);
# 20 "mm/include\\ultra64.h" 2
# 1 "mm/include\\PR/xstdio.h" 1



# 1 "C:\\Program Files\\LLVM\\lib\\clang\\18\\include\\stdarg.h" 1 3
# 5 "mm/include\\PR/xstdio.h" 2








typedef struct {
               union {
        long long ll;
        long double ld;
    } v;
               char* s;
               int n0;
               int nz0;
               int n1;
               int nz1;
               int n2;
               int nz2;
               int prec;
               int width;
               size_t nchar;
               unsigned int flags;
               char qual;
} _Pft;

typedef void* (*PrintCallback)(void*, const char*, size_t);







int _Printf(PrintCallback pfn, void* arg, const char* fmt, va_list ap);
void _Litob(_Pft* args, char code);
void _Ldtob(_Pft* args, char code);
# 21 "mm/include\\ultra64.h" 2
# 2 "mm/src/libultra/os/gettime.c" 2

OSTime osGetTime(void) {
    u32 CurrentCount;
    u32 elapseCount;
    OSTime currentCount;
    register u32 savedMask;

    savedMask = __osDisableInt();

    CurrentCount = osGetCount();
    elapseCount = CurrentCount - __osBaseCounter;
    currentCount = __osCurrentTime;

    __osRestoreInt(savedMask);

    return elapseCount + currentCount;
}
