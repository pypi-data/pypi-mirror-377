import math
import random

import numpy

from ._backend import Backend, ComputeDevice
from ._dtype import DType, OBJECT


class ObjectBackend(Backend):
    """
    Backend for Python objects.
    """

    def __init__(self):
        device = ComputeDevice(self, 'Python', 'CPU', -1, 1, "", None)
        super().__init__('object', [device], device)

    def is_tensor(self, x, only_native=False):
        return isinstance(x, str)

    def is_module(self, obj) -> bool:
        return False

    def is_sparse(self, x) -> bool:
        return False

    def as_tensor(self, x, convert_external=True):
        return x

    def seed(self, seed: int):
        random.seed(seed)

    def dtype(self, array) -> DType:
        return OBJECT

    def staticshape(self, tensor) -> tuple:
        return ()

    def shape(self, tensor):
        return ()

    def equal(self, x, y):
        return x == y

    def not_equal(self, x, y):
        return x != y

    def isnan(self, x):
        return False

    def all(self, boolean_tensor, axis=None, keepdims=False):
        return bool(boolean_tensor)

    def any(self, boolean_tensor, axis=None, keepdims=False):
        return bool(boolean_tensor)

    def numpy(self, tensor) -> numpy.ndarray:
        return numpy.asarray(tensor)

    sqrt = math.sqrt
    exp = math.exp
    sin = math.sin
    arcsin = math.asin
    cos = math.cos
    arccos = math.acos
    tan = math.tan
    arctan = math.atan
    arctan2 = staticmethod(math.atan2)
    sinh = math.sinh
    arcsinh = math.asinh
    cosh = math.cosh
    arccosh = math.acosh
    tanh = math.tanh
    arctanh = math.atanh
    log = math.log
    log2 = math.log2
    log10 = math.log10
    isfinite = math.isfinite
    abs = abs
    round = round
    ceil = math.ceil
    floor = math.floor

    def sign(self, x):
        return math.copysign(1, x)

    def stop_gradient(self, value):
        return value
