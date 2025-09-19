""".. include:: ../../README.md"""

import ctypes


class C11Stream(ctypes.Structure):  # forward declaration
    pass


# Define the function pointer type
READ_CB = ctypes.CFUNCTYPE(
    ctypes.c_int32,
    ctypes.POINTER(C11Stream),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_int32,
)
WRITE_CB = ctypes.CFUNCTYPE(
    ctypes.c_int32,
    ctypes.POINTER(C11Stream),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_int32,
)
SEEK_CB = ctypes.CFUNCTYPE(
    ctypes.c_int64, ctypes.POINTER(C11Stream), ctypes.c_int64, ctypes.c_int
)
FLUSH_CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(C11Stream))
TRUNC_CB = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.POINTER(C11Stream), ctypes.c_int64)


# now that callbacks are defined, we can define the structure:
class C11Stream(ctypes.Structure):
    _fields_ = [
        ("read", READ_CB),  #
        ("write", WRITE_CB),  #
        ("seek", SEEK_CB),  #
        ("flush", FLUSH_CB),  #
        ("trunc", TRUNC_CB),
    ]


class PyC11Stream:
    def __init__(self, file_like):
        """doc."""
        self._file_like = file_like
        self._c11_stream = C11Stream()

        def py_buf_read(_, out_buffer, count):
            try:
                data = self._file_like.read(count)
                ctypes.memmove(out_buffer, data, len(data))
                # short-read ok
                return len(data)
            except Exception as e:
                print("Read error occurred: ", e)
                return -1

        def py_buf_write(_, in_buffer, count):
            try:
                data = ctypes.string_at(in_buffer, count)
                self._file_like.write(data)
                return count
            except Exception as e:
                print("Write error occurred: ", e)
                return -1

        def py_seek(_, offset, seek_dir):
            try:
                return self._file_like.seek(offset, seek_dir)
            except Exception as e:
                print("Seek error occurred: ", e)
                return -1

        def py_flush(_):
            try:
                self._file_like.flush()
                return 0
            except Exception as e:
                print("Flush error occurred: ", e)
                return -1

        def py_trunc(_, new_size):
            try:
                self._file_like.truncate(new_size)
                return new_size
            except Exception as e:
                print("Trunc error occurred: ", e)
                return -1

        self._c11_stream.read = READ_CB(py_buf_read)
        self._c11_stream.write = WRITE_CB(py_buf_write)
        self._c11_stream.seek = SEEK_CB(py_seek)
        self._c11_stream.flush = FLUSH_CB(py_flush)
        self._c11_stream.trunc = TRUNC_CB(py_trunc)

    def get_stream_ptr(self):
        """return the internal stream pointer"""
        return ctypes.byref(self._c11_stream)
