import os
import ctypes as ct
import numpy as np

class MallocVector(ct.Structure):
    _fields_ = [("pointer", ct.c_void_p),
                ("length", ct.c_int64),
                ("s1", ct.c_int64)]

class MallocMatrix(ct.Structure):
    _fields_ = [("pointer", ct.c_void_p),
                ("length", ct.c_int64),
                ("s1", ct.c_int64),
                ("s2", ct.c_int64)]

def mvptr(A):
    ptr = A.ctypes.data_as(ct.c_void_p)
    a = MallocVector(ptr, ct.c_int64(A.size), ct.c_int64(A.shape[0]))
    return ct.byref(a)

def mmptr(A):
    ptr = A.ctypes.data_as(ct.c_void_p)
    a = MallocMatrix(ptr, ct.c_int64(A.size), ct.c_int64(A.shape[1]), ct.c_int64(A.shape[0]))
    return ct.byref(a)

root_dir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(root_dir, "lib/rqatrend.so")
lib = ct.CDLL(filename)

def rqatrend(y: np.ndarray, threshold: float, border: int = 10, theiler: int = 1) -> float:
    """
    Calculate the RQA trend for a single time series.
    
    :param y: Input time series data as a numpy array.
    :param threshold: Threshold value for the RQA calculation.
    :param border: Border size for the RQA calculation.
    :param theiler: Theiler window size for the RQA calculation.
    :return: The RQA trend value.
    """
    py = mvptr(y)
    lib.rqatrend.argtypes = (ct.POINTER(MallocVector), ct.c_double, ct.c_int64, ct.c_int64)
    lib.rqatrend.restype = ct.c_double
    result_single = lib.rqatrend(py, threshold, border, theiler)
    return result_single

def main() -> None:
    pass

main()
