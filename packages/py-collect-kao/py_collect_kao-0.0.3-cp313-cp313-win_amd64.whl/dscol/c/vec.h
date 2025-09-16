#ifndef DS_COL_VEC_H
#define DS_COL_VEC_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*vec_drop_fn)(void* elem);                 // 釋放單一元素（可為 NULL）
typedef void (*vec_copyin_fn)(void* dst, const void* src); // 元素拷貝（預設用 memcpy）

typedef struct Vec {
    void*  data;
    size_t len;
    size_t cap;
    size_t elem_size;
    vec_drop_fn   drop;    // 元素被移除/覆蓋/清空時呼叫
    vec_copyin_fn copyin;  // 元素寫入時呼叫
} Vec;

Vec*  vec_new(size_t elem_size, vec_drop_fn drop, vec_copyin_fn copyin);
void  vec_free(Vec* v);                           // 釋放整個容器(會對每個元素呼叫 drop)
bool  vec_push(Vec* v, const void* elem);         // 尾端加入一個元素
bool  vec_pop(Vec* v, void* out);                 // 尾端彈出到 out(可為 NULL)
size_t vec_len(const Vec* v);
bool  vec_get(const Vec* v, size_t idx, void* out);
bool  vec_set(Vec* v, size_t idx, const void* elem); // 覆蓋會先 drop 舊值
bool  vec_reserve(Vec* v, size_t new_cap);
void  vec_clear(Vec* v);                          // 清空(對每個元素 drop)

#ifdef __cplusplus
}
#endif

#endif // DS_COL_VEC_H
