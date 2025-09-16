# -*- coding: utf-8 -*-
import uuid
import numpy as np
def str_to_bool(val):
    return str(val).lower() in ["1", "yes", "true"]

def list2np_array(list, precision="float32"):
    try:
        match precision.lower():
            case "float32":
                return np.array(list, dtype=np.float32)
            case "float16":
                return np.array(list, dtype=np.float16)
            case "int8":
                return np.array(list, dtype=np.int8)
            case "int16":
                return np.array(list, dtype=np.int16)
            case "int32":
                return np.array(list, dtype=np.int32)
            case "int64":
                return np.array(list, dtype=np.int64)
            case "uint8":
                return np.array(list, dtype=np.uint8)
            case "uint16":
                return np.array(list, dtype=np.uint16)
            case "uint32":
                return np.array(list, dtype=np.uint32)
            case "uint64":
                return np.array(list, dtype=np.uint64)
            case _:
                return np.array(list, dtype=np.float32)
    except ValueError as e:
        raise ValueError(f"转换numpy数组失败，错误信息: {e}")
