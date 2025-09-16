#ifndef DS_COL_DA_H
#define DS_COL_DA_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct IntVector IntVector;

IntVector* iv_new(void);                 // 建立空 vector
void       iv_free(IntVector* v);        // 釋放
bool       iv_push(IntVector* v, int x); // 末端加入；失敗回 false
bool       iv_pop(IntVector* v, int* out); // 末端彈出；空回 false
size_t     iv_len(const IntVector* v);   // 目前長度
bool       iv_get(const IntVector* v, size_t idx, int* out);       // 取得
bool       iv_set(IntVector* v, size_t idx, int value);            // 設值
bool       iv_reserve(IntVector* v, size_t new_cap);               // 預留容量(可選)
void       iv_clear(IntVector* v);       // 清空

#ifdef __cplusplus
}
#endif

#endif // DS_COL_DA_H
