import io


def encode_jpeg(data):
    import imageio.v2 as imageio

    with io.BytesIO() as f:
        imageio.imwrite(f, data, format='jpeg', quality=95)
        return f.getvalue()


def decode_jpeg(data):
    import jpeg4py
    import numpy as np

    return jpeg4py.JPEG(np.frombuffer(data, np.uint8)).decode()


def encode_msgpack_np(data):
    import msgpack_numpy

    return msgpack_numpy.packb(data)


def decode_msgpack_np(data):
    import msgpack_numpy

    return msgpack_numpy.unpackb(data)


def encode_npy(data):
    import numpy as np

    with io.BytesIO() as f:
        np.save(f, data)
        return f.getvalue()


def decode_npy(data):
    import numpy as np

    with io.BytesIO(data) as f:
        return np.load(f)


def encode_npz(data):
    import numpy as np

    with io.BytesIO() as f:
        np.savez(f, **data)
        return f.getvalue()


def decode_npz(data):
    import numpy as np

    with io.BytesIO(data) as f:
        return dict(np.load(f))
