static CYTHON_INLINE PyObject* __Pyx_PyLong_From_long(long value) {
#ifdef __Pyx_HAS_GCC_DIAGNOSTIC
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wconversion"
#endif
    const long neg_one = (long) -1, const_zero = (long) 0;
#ifdef __Pyx_HAS_GCC_DIAGNOSTIC
#pragma GCC diagnostic pop
#endif
    const int is_unsigned = neg_one > const_zero;
    if (is_unsigned) {
        if (sizeof(long) < sizeof(long)) {
            return PyLong_FromLong((long) value);
        } else if (sizeof(long) <= sizeof(unsigned long)) {
            return PyLong_FromUnsignedLong((unsigned long) value);
#if defined(HAVE_LONG_LONG) && !CYTHON_COMPILING_IN_PYPY
        } else if (sizeof(long) <= sizeof(unsigned PY_LONG_LONG)) {
            return PyLong_FromUnsignedLongLong((unsigned PY_LONG_LONG) value);
#endif
        }
    } else {
        if (sizeof(long) <= sizeof(long)) {
            return PyLong_FromLong((long) value);
#ifdef HAVE_LONG_LONG
        } else if (sizeof(long) <= sizeof(PY_LONG_LONG)) {
            return PyLong_FromLongLong((PY_LONG_LONG) value);
#endif
        }
    }
    {
        unsigned char *bytes = (unsigned char *)&value;
#if !CYTHON_COMPILING_IN_LIMITED_API && PY_VERSION_HEX >= 0x030d00A4
        if (is_unsigned) {
            return PyLong_FromUnsignedNativeBytes(bytes, sizeof(value), -1);
        } else {
            return PyLong_FromNativeBytes(bytes, sizeof(value), -1);
        }
#elif !CYTHON_COMPILING_IN_LIMITED_API && PY_VERSION_HEX < 0x030d0000
        int one = 1; int little = (int)*(unsigned char *)&one;
        return _PyLong_FromByteArray(bytes, sizeof(long),
                                     little, !is_unsigned);
#else
        int one = 1; int little = (int)*(unsigned char *)&one;
        PyObject *from_bytes, *result = NULL, *kwds = NULL;
        PyObject *py_bytes = NULL, *order_str = NULL;
        from_bytes = PyObject_GetAttrString((PyObject*)&PyLong_Type, "from_bytes");
        if (!from_bytes) return NULL;
        py_bytes = PyBytes_FromStringAndSize((char*)bytes, sizeof(long));
        if (!py_bytes) goto limited_bad;
        order_str = PyUnicode_FromString(little ? "little" : "big");
        if (!order_str) goto limited_bad;
        {
            PyObject *args[3+(CYTHON_VECTORCALL ? 1 : 0)] = { NULL, py_bytes, order_str };
            if (!is_unsigned) {
                kwds = __Pyx_MakeVectorcallBuilderKwds(1);
                if (!kwds) goto limited_bad;
                if (__Pyx_VectorcallBuilder_AddArgStr("signed", __Pyx_NewRef(Py_True), kwds, args+3, 0) < 0) goto limited_bad;
            }
            result = __Pyx_Object_Vectorcall_CallFromBuilder(from_bytes, args+1, 2 | __Pyx_PY_VECTORCALL_ARGUMENTS_OFFSET, kwds);
        }
        limited_bad:
        Py_XDECREF(kwds);
        Py_XDECREF(order_str);
        Py_XDECREF(py_bytes);
        Py_XDECREF(from_bytes);
        return result;
#endif
    }
}

