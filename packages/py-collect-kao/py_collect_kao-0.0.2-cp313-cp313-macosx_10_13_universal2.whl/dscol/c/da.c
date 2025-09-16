#include "da.h"
#include <stdlib.h>
#include <string.h>

struct IntVector {
    int*    data;
    size_t  len;
    size_t  cap;
};

static bool iv_grow(IntVector* v, size_t min_cap) {
    size_t new_cap = v->cap ? v->cap : 4;
    while (new_cap < min_cap) new_cap *= 2;
    int* p = (int*)realloc(v->data, new_cap * sizeof(int));
    if (!p) return false;
    v->data = p;
    v->cap = new_cap;
    return true;
}

IntVector* iv_new(void) {
    IntVector* v = (IntVector*)calloc(1, sizeof(IntVector));
    return v;
}

void iv_free(IntVector* v) {
    if (!v) return;
    free(v->data);
    free(v);
}

bool iv_push(IntVector* v, int x) {
    if (!v) return false;
    if (v->len == v->cap && !iv_grow(v, v->len + 1)) return false;
    v->data[v->len++] = x;
    return true;
}

bool iv_pop(IntVector* v, int* out) {
    if (!v || v->len == 0) return false;
    int val = v->data[v->len - 1];
    v->len -= 1;
    if (out) *out = val;
    return true;
}

size_t iv_len(const IntVector* v) {
    return v ? v->len : 0;
}

bool iv_get(const IntVector* v, size_t idx, int* out) {
    if (!v || idx >= v->len) return false;
    if (out) *out = v->data[idx];
    return true;
}

bool iv_set(IntVector* v, size_t idx, int value) {
    if (!v || idx >= v->len) return false;
    v->data[idx] = value;
    return true;
}

bool iv_reserve(IntVector* v, size_t new_cap) {
    if (!v) return false;
    if (new_cap <= v->cap) return true;
    return iv_grow(v, new_cap);
}

void iv_clear(IntVector* v) {
    if (!v) return;
    v->len = 0;
}
