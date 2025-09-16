#include "vec.h"
#include <stdlib.h>
#include <string.h>

static bool vec_grow(Vec* v, size_t min_cap) {
    size_t new_cap = v->cap ? v->cap : 4;
    while (new_cap < min_cap) new_cap *= 2;
    void* p = realloc(v->data, new_cap * v->elem_size);
    if (!p) return false;
    v->data = p;
    v->cap  = new_cap;
    return true;
}

static void default_copyin(void* dst, const void* src, size_t n) {
    memmove(dst, src, n);
}

Vec* vec_new(size_t elem_size, vec_drop_fn drop, vec_copyin_fn copyin) {
    Vec* v = (Vec*)calloc(1, sizeof(Vec));
    if (!v) return NULL;
    v->elem_size = elem_size;
    v->drop = drop;
    v->copyin = copyin;
    return v;
}

void vec_free(Vec* v) {
    if (!v) return;
    if (v->drop && v->data) {
        for (size_t i = 0; i < v->len; ++i) {
            void* elem = (char*)v->data + i * v->elem_size;
            v->drop(elem);
        }
    }
    free(v->data);
    free(v);
}

bool vec_push(Vec* v, const void* elem) {
    if (!v) return false;
    if (v->len == v->cap && !vec_grow(v, v->len + 1)) return false;
    void* dst = (char*)v->data + v->len * v->elem_size;
    if (v->copyin) v->copyin(dst, elem);
    else           default_copyin(dst, elem, v->elem_size);
    v->len += 1;
    return true;
}

bool vec_pop(Vec* v, void* out) {
    if (!v || v->len == 0) return false;
    size_t i = v->len - 1;
    void* src = (char*)v->data + i * v->elem_size;
    if (out) default_copyin(out, src, v->elem_size);
    if (v->drop) v->drop(src);
    v->len -= 1;
    return true;
}

size_t vec_len(const Vec* v) { return v ? v->len : 0; }

bool vec_get(const Vec* v, size_t idx, void* out) {
    if (!v || idx >= v->len) return false;
    if (!out) return true;
    void* src = (char*)v->data + idx * v->elem_size;
    default_copyin(out, src, v->elem_size);
    return true;
}

bool vec_set(Vec* v, size_t idx, const void* elem) {
    if (!v || idx >= v->len) return false;
    void* dst = (char*)v->data + idx * v->elem_size;
    if (v->drop) v->drop(dst);
    if (v->copyin) v->copyin(dst, elem);
    else           default_copyin(dst, elem, v->elem_size);
    return true;
}

bool vec_reserve(Vec* v, size_t new_cap) {
    if (!v) return false;
    if (new_cap <= v->cap) return true;
    return vec_grow(v, new_cap);
}

void vec_clear(Vec* v) {
    if (!v) return;
    if (v->drop && v->data) {
        for (size_t i = 0; i < v->len; ++i) {
            void* elem = (char*)v->data + i * v->elem_size;
            v->drop(elem);
        }
    }
    v->len = 0;
}
