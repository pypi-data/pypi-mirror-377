#if CYTHON_COMPILING_IN_LIMITED_API && __PYX_LIMITED_VERSION_HEX < 0x030C0000
static PyObject *__Pyx_SelflessCall(PyObject *method, PyObject *args, PyObject *kwargs) {
    PyObject *result;
    PyObject *selfless_args = PyTuple_GetSlice(args, 1, PyTuple_Size(args));
    if (unlikely(!selfless_args)) return NULL;
    result = PyObject_Call(method, selfless_args, kwargs);
    Py_DECREF(selfless_args);
    return result;
}
#elif CYTHON_COMPILING_IN_PYPY && PY_VERSION_HEX < 0x03090000
static PyObject *__Pyx_SelflessCall(PyObject *method, PyObject **args, Py_ssize_t nargs, PyObject *kwnames) {
        return _PyObject_Vectorcall
            (method, args ? args+1 : NULL, nargs ? nargs-1 : 0, kwnames);
}
#else
static PyObject *__Pyx_SelflessCall(PyObject *method, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    return
#if PY_VERSION_HEX < 0x03090000
    _PyObject_Vectorcall
#else
    PyObject_Vectorcall
#endif
        (method, args ? args+1 : NULL, nargs ? (size_t) nargs-1 : 0, kwnames);
}
#endif
static PyMethodDef __Pyx_UnboundCMethod_Def = {
     "CythonUnboundCMethod",
     __PYX_REINTERPRET_FUNCION(PyCFunction, __Pyx_SelflessCall),
#if CYTHON_COMPILING_IN_LIMITED_API && __PYX_LIMITED_VERSION_HEX < 0x030C0000
     METH_VARARGS | METH_KEYWORDS,
#else
     METH_FASTCALL | METH_KEYWORDS,
#endif
     NULL
};
static int __Pyx_TryUnpackUnboundCMethod(__Pyx_CachedCFunction* target) {
    PyObject *method, *result=NULL;
    method = __Pyx_PyObject_GetAttrStr(target->type, *target->method_name);
    if (unlikely(!method))
        return -1;
    result = method;
#if CYTHON_COMPILING_IN_CPYTHON
    if (likely(__Pyx_TypeCheck(method, &PyMethodDescr_Type)))
    {
        PyMethodDescrObject *descr = (PyMethodDescrObject*) method;
        target->func = descr->d_method->ml_meth;
        target->flag = descr->d_method->ml_flags & ~(METH_CLASS | METH_STATIC | METH_COEXIST | METH_STACKLESS);
    } else
#endif
#if CYTHON_COMPILING_IN_PYPY
#else
    if (PyCFunction_Check(method))
#endif
    {
        PyObject *self;
        int self_found;
#if CYTHON_COMPILING_IN_LIMITED_API || CYTHON_COMPILING_IN_PYPY
        self = PyObject_GetAttrString(method, "__self__");
        if (!self) {
            PyErr_Clear();
        }
#else
        self = PyCFunction_GET_SELF(method);
#endif
        self_found = (self && self != Py_None);
#if CYTHON_COMPILING_IN_LIMITED_API || CYTHON_COMPILING_IN_PYPY
        Py_XDECREF(self);
#endif
        if (self_found) {
            PyObject *unbound_method = PyCFunction_New(&__Pyx_UnboundCMethod_Def, method);
            if (unlikely(!unbound_method)) return -1;
            Py_DECREF(method);
            result = unbound_method;
        }
    }
#if !CYTHON_COMPILING_IN_CPYTHON_FREETHREADING
    if (unlikely(target->method)) {
        Py_DECREF(result);
    } else
#endif
    target->method = result;
    return 0;
}

