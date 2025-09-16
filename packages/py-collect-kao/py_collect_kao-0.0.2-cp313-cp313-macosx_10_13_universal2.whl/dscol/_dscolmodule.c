#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "c/vec.h"
#include "c/da.h"   // (可留) 先前 IntVector 的示範仍可使用

// -------------------- Object Vector (store PyObject*) --------------------

static void pyobj_drop(void* elem) {
    PyObject* obj = *(PyObject**)elem;
    if (obj) Py_DECREF(obj);
}

static void pyobj_copyin(void* dst, const void* src) {
    PyObject* obj = *(PyObject* const*)src;
    Py_XINCREF(obj);
    memcpy(dst, &obj, sizeof(PyObject*));
}

typedef struct {
    PyObject_HEAD
    Vec* v;  // Vec of PyObject*
} PyVector;

static int PyVector_init(PyVector* self, PyObject* args, PyObject* kw) {
    self->v = vec_new(sizeof(PyObject*), pyobj_drop, pyobj_copyin);
    if (!self->v) { PyErr_NoMemory(); return -1; }
    return 0;
}

static void PyVector_dealloc(PyVector* self) {
    vec_free(self->v);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static Py_ssize_t PyVector_len(PyObject* self_obj) {
    PyVector* self = (PyVector*)self_obj;
    return (Py_ssize_t)vec_len(self->v);
}

static PyObject* PyVector_getitem(PyObject* self_obj, Py_ssize_t i) {
    PyVector* self = (PyVector*)self_obj;
    size_t len = vec_len(self->v);
    if (i < 0) i += (Py_ssize_t)len;
    if ((size_t)i >= len) { PyErr_SetString(PyExc_IndexError, "index out of range"); return NULL; }
    PyObject* obj = NULL;
    if (!vec_get(self->v, (size_t)i, &obj)) { PyErr_SetString(PyExc_RuntimeError, "get failed"); return NULL; }
    Py_XINCREF(obj); // borrow -> new ref for return
    return obj;
}

static int PyVector_setitem(PyObject* self_obj, Py_ssize_t i, PyObject* value) {
    PyVector* self = (PyVector*)self_obj;
    size_t len = vec_len(self->v);
    if (i < 0) i += (Py_ssize_t)len;
    if ((size_t)i >= len) { PyErr_SetString(PyExc_IndexError, "index out of range"); return -1; }
    PyObject* tmp = value; // vec_set 會先 drop 舊值，再 copyin(new)=INCREF
    if (!vec_set(self->v, (size_t)i, &tmp)) { PyErr_SetString(PyExc_RuntimeError, "set failed"); return -1; }
    return 0;
}

static PyObject* PyVector_append(PyVector* self, PyObject* args) {
    PyObject* obj;
    if (!PyArg_ParseTuple(args, "O", &obj)) return NULL;
    if (!vec_push(self->v, &obj)) { PyErr_NoMemory(); return NULL; } // copyin=INCREF
    Py_RETURN_NONE;
}

static PyObject* PyVector_pop(PyVector* self, PyObject* Py_UNUSED(ignored)) {
    PyObject* obj = NULL;
    if (!vec_pop(self->v, &obj)) { PyErr_SetString(PyExc_IndexError, "pop from empty Vector"); return NULL; }
    // 注意：vec_pop 先把元素 copy 到 obj，再 drop 舊位址（drop=DECREF）
    // 但我們想「轉移所有權」：上面的流程會多 DECREF 一次。
    // 因此：對於 PyObject*，我們不要在 pop 時 drop！
    // 方案：對 pop 使用「不 drop」的特化版本。為簡化，這裡改成兩步：get + 手動移除尾端，不呼叫 drop。
    // ---- 改法：重寫 pop：直接存取底層緩衝，移除但不 drop，並回傳原物件。

    // 替換：直接操作底層 Vec（小心：這是簡化範例）
    if (self->v->len == 0) { PyErr_SetString(PyExc_IndexError, "pop from empty Vector"); return NULL; }
    size_t idx = self->v->len - 1;
    PyObject** slot = (PyObject**)((char*)self->v->data + idx * self->v->elem_size);
    PyObject* ret = *slot;   // 取出擁有的參考
    *slot = NULL;            // 清空避免 drop 作用到它
    self->v->len -= 1;
    return ret;              // 直接回傳擁有權（新參考）
}

static PyObject* PyVector_clear(PyVector* self, PyObject* Py_UNUSED(ignored)) {
    vec_clear(self->v); // 逐一 drop = DECREF
    Py_RETURN_NONE;
}

static PySequenceMethods PyVector_as_sequence = {
    .sq_length = PyVector_len,
    .sq_concat = 0,
    .sq_repeat = 0,
    .sq_item = PyVector_getitem,
    .was_sq_slice = 0,
    .sq_ass_item = PyVector_setitem,
    .was_sq_ass_slice = 0,
    .sq_contains = 0,
    .sq_inplace_concat = 0,
    .sq_inplace_repeat = 0,
};

static PyMethodDef PyVector_methods[] = {
    {"append", (PyCFunction)PyVector_append, METH_VARARGS, "Append any Python object"},
    {"pop",    (PyCFunction)PyVector_pop,    METH_NOARGS,  "Pop and return the last object"},
    {"clear",  (PyCFunction)PyVector_clear,  METH_NOARGS,  "Clear all items"},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject PyVectorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name      = "dscol.Vector",
    .tp_basicsize = sizeof(PyVector),
    .tp_itemsize  = 0,
    .tp_dealloc   = (destructor)PyVector_dealloc,
    .tp_flags     = Py_TPFLAGS_DEFAULT,
    .tp_doc       = "Generic dynamic array of Python objects",
    .tp_methods   = PyVector_methods,
    .tp_as_sequence = &PyVector_as_sequence,
    .tp_init      = (initproc)PyVector_init,
    .tp_new       = PyType_GenericNew,
};

// -------------------- (保留) IntVector 舊型別 --------------------
// 你可保留先前的 IntVector 型別原樣（略）。如要精簡，亦可移除。

static PyMethodDef module_methods[] = { {NULL, NULL, 0, NULL} };

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    .m_name = "dscol._dscol",
    .m_doc  = "C-backed data structures (generic + typed)",
    .m_size = -1,
    .m_methods = module_methods,
};

PyMODINIT_FUNC PyInit__dscol(void) {
    PyObject* m;
    if (PyType_Ready(&PyVectorType) < 0) return NULL;
    // 如果保留 IntVector，這裡也要 PyType_Ready(&PyIntVectorType)

    m = PyModule_Create(&moduledef);
    if (!m) return NULL;

    Py_INCREF(&PyVectorType);
    if (PyModule_AddObject(m, "Vector", (PyObject*)&PyVectorType) < 0) {
        Py_DECREF(&PyVectorType); Py_DECREF(m); return NULL;
    }

    // 若保留 IntVector，這裡也要加入
    // Py_INCREF(&PyIntVectorType);
    // PyModule_AddObject(m, "IntVector", (PyObject*)&PyIntVectorType);

    return m;
}
