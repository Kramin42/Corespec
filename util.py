from base64 import b64encode, b64decode
import numpy as np


def encode_data(obj):
    if isinstance(obj, dict):
        return {key: encode_data(val) for key, val in obj.items()}
    elif isinstance(obj, list):
        return [encode_data(x) for x in obj]
    elif isinstance(obj, np.ndarray):
        if obj.dtype == np.float64:
            obj = np.float32(obj) # no need for 64 bit precision, save on data size
        return {'base64': b64encode(obj.tobytes()).decode('utf-8'), 'dtype': str(obj.dtype)}
    return obj
