static void __Pyx_WriteUnraisable(const char *name, int clineno,
                                  int lineno, const char *filename,
                                  int full_traceback, int nogil) {
    PyObject *old_exc, *old_val, *old_tb;
    PyObject *ctx;
    __Pyx_PyThreadState_declare
    PyGILState_STATE state;
    if (nogil)
        state = PyGILState_Ensure();
    else state = (PyGILState_STATE)0;
    CYTHON_UNUSED_VAR(clineno);
    CYTHON_UNUSED_VAR(lineno);
    CYTHON_UNUSED_VAR(filename);
    CYTHON_MAYBE_UNUSED_VAR(nogil);
    __Pyx_PyThreadState_assign
    __Pyx_ErrFetch(&old_exc, &old_val, &old_tb);
    if (full_traceback) {
        Py_XINCREF(old_exc);
        Py_XINCREF(old_val);
        Py_XINCREF(old_tb);
        __Pyx_ErrRestore(old_exc, old_val, old_tb);
        PyErr_PrintEx(0);
    }
    ctx = PyUnicode_FromString(name);
    __Pyx_ErrRestore(old_exc, old_val, old_tb);
    if (!ctx) {
        PyErr_WriteUnraisable(Py_None);
    } else {
        PyErr_WriteUnraisable(ctx);
        Py_DECREF(ctx);
    }
    if (nogil)
        PyGILState_Release(state);
}

