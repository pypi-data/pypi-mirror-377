from cxx11bindings import PyC11Stream


def test_default():
    filename = "default.bin"
    try:
        with open(filename, "wb") as f:
            stream = PyC11Stream(f)
            assert stream is not None
    except Exception as e:
        print("Error occurred: ", e)
        assert False, "Failed to create PyC11Stream"
