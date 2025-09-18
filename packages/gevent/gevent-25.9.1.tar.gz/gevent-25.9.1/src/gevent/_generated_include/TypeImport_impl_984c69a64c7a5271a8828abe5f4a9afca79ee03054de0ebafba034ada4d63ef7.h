#ifndef __PYX_HAVE_RT_ImportType_3_1_4
#define __PYX_HAVE_RT_ImportType_3_1_4
static PyTypeObject *__Pyx_ImportType_3_1_4(PyObject *module, const char *module_name, const char *class_name,
    size_t size, size_t alignment, enum __Pyx_ImportType_CheckSize_3_1_4 check_size)
{
    PyObject *result = 0;
    Py_ssize_t basicsize;
    Py_ssize_t itemsize;
#ifdef Py_LIMITED_API
    PyObject *py_basicsize;
    PyObject *py_itemsize;
#endif
    result = PyObject_GetAttrString(module, class_name);
    if (!result)
        goto bad;
    if (!PyType_Check(result)) {
        PyErr_Format(PyExc_TypeError,
            "%.200s.%.200s is not a type object",
            module_name, class_name);
        goto bad;
    }
#ifndef Py_LIMITED_API
    basicsize = ((PyTypeObject *)result)->tp_basicsize;
    itemsize = ((PyTypeObject *)result)->tp_itemsize;
#else
    if (size == 0) {
        return (PyTypeObject *)result;
    }
    py_basicsize = PyObject_GetAttrString(result, "__basicsize__");
    if (!py_basicsize)
        goto bad;
    basicsize = PyLong_AsSsize_t(py_basicsize);
    Py_DECREF(py_basicsize);
    py_basicsize = 0;
    if (basicsize == (Py_ssize_t)-1 && PyErr_Occurred())
        goto bad;
    py_itemsize = PyObject_GetAttrString(result, "__itemsize__");
    if (!py_itemsize)
        goto bad;
    itemsize = PyLong_AsSsize_t(py_itemsize);
    Py_DECREF(py_itemsize);
    py_itemsize = 0;
    if (itemsize == (Py_ssize_t)-1 && PyErr_Occurred())
        goto bad;
#endif
    if (itemsize) {
        if (size % alignment) {
            alignment = size % alignment;
        }
        if (itemsize < (Py_ssize_t)alignment)
            itemsize = (Py_ssize_t)alignment;
    }
    if ((size_t)(basicsize + itemsize) < size) {
        PyErr_Format(PyExc_ValueError,
            "%.200s.%.200s size changed, may indicate binary incompatibility. "
            "Expected %zd from C header, got %zd from PyObject",
            module_name, class_name, size, basicsize+itemsize);
        goto bad;
    }
    if (check_size == __Pyx_ImportType_CheckSize_Error_3_1_4 &&
            ((size_t)basicsize > size || (size_t)(basicsize + itemsize) < size)) {
        PyErr_Format(PyExc_ValueError,
            "%.200s.%.200s size changed, may indicate binary incompatibility. "
            "Expected %zd from C header, got %zd-%zd from PyObject",
            module_name, class_name, size, basicsize, basicsize+itemsize);
        goto bad;
    }
    else if (check_size == __Pyx_ImportType_CheckSize_Warn_3_1_4 && (size_t)basicsize > size) {
        if (PyErr_WarnFormat(NULL, 0,
                "%.200s.%.200s size changed, may indicate binary incompatibility. "
                "Expected %zd from C header, got %zd from PyObject",
                module_name, class_name, size, basicsize) < 0) {
            goto bad;
        }
    }
    return (PyTypeObject *)result;
bad:
    Py_XDECREF(result);
    return NULL;
}
#endif

