
// generated from codegen/templates/_pod.hpp

#ifndef E_MATH_U64_HPP
#define E_MATH_U64_HPP

// stdlib
#include <limits>
#include <functional>
// python
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
// emath
#include "_modulestate.hpp"
#include "_podtype.hpp"
#include "_type.hpp"


static PyObject *
U64Array__new__(PyTypeObject *cls, PyObject *args, PyObject *kwds)
{
    if (kwds && PyDict_Size(kwds) != 0)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "U64 does accept any keyword arguments"
        );
        return 0;
    }

    auto arg_count = PyTuple_GET_SIZE(args);
    if (arg_count == 0)
    {
        auto self = (U64Array *)cls->tp_alloc(cls, 0);
        if (!self){ return 0; }
        self->length = 0;
        self->pod = 0;
        return (PyObject *)self;
    }

    auto *self = (U64Array *)cls->tp_alloc(cls, 0);
    if (!self){ return 0; }
    self->length = arg_count;
    self->pod = new uint64_t[arg_count];

    for (int i = 0; i < arg_count; i++)
    {
        auto arg = PyTuple_GET_ITEM(args, i);
        self->pod[i] = pyobject_to_c_uint64_t(arg);
        if (PyErr_Occurred())
        {
            Py_DECREF(self);
            PyErr_Format(
                PyExc_TypeError,
                "invalid type %R, expected uint64_t",
                arg
            );
            return 0;
        }
    }

    return (PyObject *)self;
}


static void
U64Array__dealloc__(U64Array *self)
{
    if (self->weakreflist)
    {
        PyObject_ClearWeakRefs((PyObject *)self);
    }

    delete self->pod;

    PyTypeObject *type = Py_TYPE(self);
    type->tp_free(self);
    Py_DECREF(type);
}


// this is roughly copied from how python hashes tuples in 3.11
#if SIZEOF_PY_UHASH_T > 4
#define _HASH_XXPRIME_1 ((Py_uhash_t)11400714785074694791ULL)
#define _HASH_XXPRIME_2 ((Py_uhash_t)14029467366897019727ULL)
#define _HASH_XXPRIME_5 ((Py_uhash_t)2870177450012600261ULL)
#define _HASH_XXROTATE(x) ((x << 31) | (x >> 33))  /* Rotate left 31 bits */
#else
#define _HASH_XXPRIME_1 ((Py_uhash_t)2654435761UL)
#define _HASH_XXPRIME_2 ((Py_uhash_t)2246822519UL)
#define _HASH_XXPRIME_5 ((Py_uhash_t)374761393UL)
#define _HASH_XXROTATE(x) ((x << 13) | (x >> 19))  /* Rotate left 13 bits */
#endif


static Py_hash_t
U64Array__hash__(U64Array *self)
{
    Py_ssize_t len = self->length;
    Py_uhash_t acc = _HASH_XXPRIME_5;
    for (Py_ssize_t i = 0; i < (Py_ssize_t)self->length; i++)
    {
        Py_uhash_t lane = std::hash<uint64_t>{}(self->pod[i]);
        acc += lane * _HASH_XXPRIME_2;
        acc = _HASH_XXROTATE(acc);
        acc *= _HASH_XXPRIME_1;
    }
    acc += len ^ (_HASH_XXPRIME_5 ^ 3527539UL);

    if (acc == (Py_uhash_t)-1) {
        return 1546275796;
    }
    return acc;
}


static PyObject *
U64Array__repr__(U64Array *self)
{
    return PyUnicode_FromFormat("U64Array[%zu]", self->length);
}


static Py_ssize_t
U64Array__len__(U64Array *self)
{
    return self->length;
}


static PyObject *
U64Array__sq_getitem__(U64Array *self, Py_ssize_t index)
{
    if (index < 0 || index > (Py_ssize_t)self->length - 1)
    {
        PyErr_Format(PyExc_IndexError, "index out of range");
        return 0;
    }
    return c_uint64_t_to_pyobject(self->pod[index]);
}


static PyObject *
U64Array__mp_getitem__(U64Array *self, PyObject *key)
{
    if (PySlice_Check(key))
    {
        Py_ssize_t start;
        Py_ssize_t stop;
        Py_ssize_t step;
        Py_ssize_t length;
        if (PySlice_GetIndicesEx(key, self->length, &start, &stop, &step, &length) != 0)
        {
            return 0;
        }
        auto cls = Py_TYPE(self);
        auto *result = (U64Array *)cls->tp_alloc(cls, 0);
        if (!result){ return 0; }
        if (length == 0)
        {
            result->length = 0;
            result->pod = 0;
        }
        else
        {
            result->length = length;
            result->pod = new uint64_t[length];
            for (Py_ssize_t i = 0; i < length; i++)
            {
                result->pod[i] = self->pod[start + (i * step)];
            }
        }
        return (PyObject *)result;
    }
    else if (PyLong_Check(key))
    {
        auto index = PyLong_AsSsize_t(key);
        if (PyErr_Occurred()){ return 0; }
        if (index < 0)
        {
            index = (Py_ssize_t)self->length + index;
        }
        if (index < 0 || index > (Py_ssize_t)self->length - 1)
        {
            PyErr_Format(PyExc_IndexError, "index out of range");
            return 0;
        }

        return c_uint64_t_to_pyobject(self->pod[index]);
    }
    PyErr_Format(PyExc_TypeError, "expected int or slice");
    return 0;
}


static PyObject *
U64Array__richcmp__(
    U64Array *self,
    U64Array *other,
    int op
)
{
    if (Py_TYPE(self) != Py_TYPE(other))
    {
        Py_RETURN_NOTIMPLEMENTED;
    }

    switch(op)
    {
        case Py_EQ:
        {
            if (self->length == other->length)
            {
                for (size_t i = 0; i < self->length; i++)
                {
                    if (self->pod[i] != other->pod[i])
                    {
                        Py_RETURN_FALSE;
                    }
                }
                Py_RETURN_TRUE;
            }
            else
            {
                Py_RETURN_FALSE;
            }
        }
        case Py_NE:
        {
            if (self->length != other->length)
            {
                Py_RETURN_TRUE;
            }
            else
            {
                for (size_t i = 0; i < self->length; i++)
                {
                    if (self->pod[i] != other->pod[i])
                    {
                        Py_RETURN_TRUE;
                    }
                }
                Py_RETURN_FALSE;
            }
        }
    }
    Py_RETURN_NOTIMPLEMENTED;
}


static int
U64Array__bool__(U64Array *self)
{
    return self->length ? 1 : 0;
}


static int
U64Array_getbufferproc(U64Array *self, Py_buffer *view, int flags)
{
    if (flags & PyBUF_WRITABLE)
    {
        PyErr_SetString(PyExc_TypeError, "U64 is read only");
        view->obj = 0;
        return -1;
    }
    view->buf = self->pod;
    view->obj = (PyObject *)self;
    view->len = sizeof(uint64_t) * self->length;
    view->readonly = 1;
    view->itemsize = sizeof(uint64_t);
    view->ndim = 1;
    if (flags & PyBUF_FORMAT)
    {
        view->format = "=Q";
    }
    else
    {
        view->format = 0;
    }
    if (flags & PyBUF_ND)
    {
        view->shape = new Py_ssize_t[1] {
            (Py_ssize_t)self->length
        };
    }
    else
    {
        view->shape = 0;
    }
    if (flags & PyBUF_STRIDES)
    {
        view->strides = &view->itemsize;
    }
    else
    {
        view->strides = 0;
    }
    view->suboffsets = 0;
    view->internal = 0;
    Py_INCREF(self);
    return 0;
}


static void
U64Array_releasebufferproc(U64Array *self, Py_buffer *view)
{
    delete view->shape;
}


static PyMemberDef U64Array_PyMemberDef[] = {
    {"__weaklistoffset__", T_PYSSIZET, offsetof(U64Array, weakreflist), READONLY},
    {0}
};


static PyObject *
U64Array_address(U64Array *self, void *)
{
    return PyLong_FromSsize_t((Py_ssize_t)self->pod);
}


static PyObject *
U64Array_pointer(U64Array *self, void *)
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    auto c_p = module_state->ctypes_c_uint64_t_p;
    return PyObject_CallMethod(c_p, "from_address", "n", (Py_ssize_t)&self->pod);
}


static PyObject *
U64Array_size(U64Array *self, void *)
{
    return PyLong_FromSize_t(sizeof(uint64_t) * self->length);
}


static PyGetSetDef U64Array_PyGetSetDef[] = {
    {"address", (getter)U64Array_address, 0, 0, 0},
    {"pointer", (getter)U64Array_pointer, 0, 0, 0},
    {"size", (getter)U64Array_size, 0, 0, 0},
    {0, 0, 0, 0, 0}
};


static PyObject *
U64Array_from_buffer(PyTypeObject *cls, PyObject *buffer)
{
    static Py_ssize_t expected_size = sizeof(uint64_t);
    Py_buffer view;
    if (PyObject_GetBuffer(buffer, &view, PyBUF_SIMPLE) == -1){ return 0; }
    auto view_length = view.len;
    if (view_length % sizeof(uint64_t))
    {
        PyBuffer_Release(&view);
        PyErr_Format(PyExc_BufferError, "expected buffer evenly divisible by %zd, got %zd", sizeof(uint64_t), view_length);
        return 0;
    }
    auto array_length = view_length / sizeof(uint64_t);

    auto *result = (U64Array *)cls->tp_alloc(cls, 0);
    if (!result)
    {
        PyBuffer_Release(&view);
        return 0;
    }
    result->length = array_length;
    if (array_length > 0)
    {
        result->pod = new uint64_t[array_length];
        std::memcpy(result->pod, view.buf, view_length);
    }
    else
    {
        result->pod = 0;
    }
    PyBuffer_Release(&view);
    return (PyObject *)result;
}


static PyObject *
U64Array_pydantic(PyTypeObject *cls, PyObject *args, PyObject *kwargs)
{
    static char *keywords[] = {"source_type", "handler", 0};
    PyObject *py_source_type = 0;
    PyObject *py_handler = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OO", keywords, &py_source_type, &py_handler))
    {
        return 0;
    }

    PyObject *emath_pydantic = PyImport_ImportModule("emath._pydantic");
    if (!emath_pydantic){ return 0; }

    PyObject *core_schema = PyObject_GetAttrString(emath_pydantic, "U64Array__get_pydantic_core_schema__");
    Py_DECREF(emath_pydantic);
    if (!core_schema){ return 0; }

    return PyObject_CallFunction(core_schema, "OO", py_source_type, py_handler);
}


static PyObject *
U64Array_get_component_type(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nargs)
{
    if (nargs != 0)
    {
        PyErr_Format(PyExc_TypeError, "expected 0 arguments, got %zi", nargs);
        return 0;
    }

        Py_INCREF(&PyLong_Type);
        return (PyObject *)&PyLong_Type;

}


static PyMethodDef U64Array_PyMethodDef[] = {
    {"from_buffer", (PyCFunction)U64Array_from_buffer, METH_O | METH_CLASS, 0},
    {"get_component_type", (PyCFunction)U64Array_get_component_type, METH_FASTCALL | METH_CLASS, 0},
    {"__get_pydantic_core_schema__", (PyCFunction)U64Array_pydantic, METH_VARARGS | METH_KEYWORDS | METH_CLASS, 0},
    {0, 0, 0, 0}
};


static PyType_Slot U64Array_PyType_Slots [] = {
    {Py_tp_new, (void*)U64Array__new__},
    {Py_tp_dealloc, (void*)U64Array__dealloc__},
    {Py_tp_hash, (void*)U64Array__hash__},
    {Py_tp_repr, (void*)U64Array__repr__},
    {Py_sq_length, (void*)U64Array__len__},
    {Py_sq_item, (void*)U64Array__sq_getitem__},
    {Py_mp_subscript, (void*)U64Array__mp_getitem__},
    {Py_tp_richcompare, (void*)U64Array__richcmp__},
    {Py_nb_bool, (void*)U64Array__bool__},
    {Py_bf_getbuffer, (void*)U64Array_getbufferproc},
    {Py_bf_releasebuffer, (void*)U64Array_releasebufferproc},
    {Py_tp_getset, (void*)U64Array_PyGetSetDef},
    {Py_tp_members, (void*)U64Array_PyMemberDef},
    {Py_tp_methods, (void*)U64Array_PyMethodDef},
    {0, 0},
};


static PyType_Spec U64Array_PyTypeSpec = {
    "emath.U64Array",
    sizeof(U64Array),
    0,
    Py_TPFLAGS_DEFAULT,
    U64Array_PyType_Slots
};


static PyTypeObject *
define_U64Array_type(PyObject *module)
{
    PyTypeObject *type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module,
        &U64Array_PyTypeSpec,
        0
    );
    if (!type){ return 0; }
    // Note:
    // Unlike other functions that steal references, PyModule_AddObject() only
    // decrements the reference count of value on success.
    if (PyModule_AddObject(module, "U64Array", (PyObject *)type) < 0)
    {
        Py_DECREF(type);
        return 0;
    }
    return type;
}


static PyTypeObject *
get_U64Array_type()
{
    auto module_state = get_module_state();
    if (!module_state){ return 0; }
    return module_state->U64Array_PyTypeObject;
}


static PyObject *
create_U64Array(size_t length, const uint64_t *value)
{
    auto cls = get_U64Array_type();
    auto result = (U64Array *)cls->tp_alloc(cls, 0);
    if (!result){ return 0; }
    result->length = length;
    if (length > 0)
    {
        result->pod = new uint64_t[length];
        for (size_t i = 0; i < length; i++)
        {
            result->pod[i] = value[i];
        }
    }
    else
    {
        result->pod = 0;
    }
    return (PyObject *)result;
}


static uint64_t *
get_U64Array_value_ptr(const PyObject *self)
{
    if (Py_TYPE(self) != get_U64Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected U64Array, got %R",
            self
        );
        return 0;
    }
    return ((U64Array *)self)->pod;
}


static size_t
get_U64Array_length(const PyObject *self)
{
    if (Py_TYPE(self) != get_U64Array_type())
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected U64Array, got %R",
            self
        );
        return 0;
    }
    return ((U64Array *)self)->length;
}

#endif
