import math
import numpy as np
from collections import namedtuple
from tacocompression.functions import *


func_dict = {
    "cantor": [cantor_pairing, inverse_cantor_pairing],
    "szudzik": [szudzik_pairing, inverse_szudzik_pairing],
    "rosenberg": [rosenberg_strong_pairing, inverse_rosenberg_strong_pairing]
}
IntTuple = namedtuple("IntTuple", ["z_int", "l", "m_int"])
FloatTuple = namedtuple("FloatTuple", ["z_int", "z_frac", "l", "m_int", "m_frac"])

def element_wise_pairing(time_series: list[int], func: callable) -> list[int]:
    """
    Iteratively pairs neighboring elements of the given time series until only one element remains or an overflow
    occurs, returning the sequence of last valid step.

    :param time_series: Values to compress via pairing.
    :param func: Pairing function to use.
    :return: Compressed sequence, ideally with length 1.
    """
    d = time_series.copy()
    while len(d) > 1:
        n = len(d)
        if n % 2 == 0:
            b = [func(d[i], d[i + 1]) for i in range(0, n - 1, 2)]
        else:
            b = [func(d[i], d[i + 1]) for i in range(0, n - 2, 2)]
            b.append(d[n - 1])
        if any(math.isnan(x) or math.isinf(x) for x in b):
            return d
        if any(x > 10 ** 128 for x in b):
            return d
        d = b
    return d

def reverse_element_pairing(z: int, num: int, func: callable) -> list[int]:
    """
    Reverses a value pairing with the given function, returning the reconstruction of the represented sequence.

    :param z: A single paired value representing (a subsequence of) the original time series.
    :param num: The size of the subsequence.
    :param func: The inverse of the pairing function.
    :return: The subsequence represented by z.
    """
    if num == 1:
        return [z]
    elif num == 2:
        return list(func(z))
    f = math.ceil(math.log2(num)) - 1
    z_n = func(z)
    l = reverse_element_pairing(z_n[0], 2**f, func)
    r = reverse_element_pairing(z_n[1], num - 2**f, func)
    return l + r

def reverse_pairing(z: list[int], num: int, func: callable):
    """
    Reverses a list of value pairings with the given function returning to the original time series.

    :param z: Paired values representing the original time series.
    :param num: The length of the time series.
    :param func: The inverse of the pairing function.
    :return: The time series represented by z.
    """
    if len(z) == 1:
        return reverse_element_pairing(z[0], num, func)
    f = 2 ** math.ceil(math.log2(math.ceil(num / len(z))))
    seq = []
    n = num
    for i in range(len(z)):
        if n > f:
            seq.extend(reverse_element_pairing(z[i], f, func))
        else:
            seq.extend(reverse_element_pairing(z[i], n, func))
        n -= f
    return seq

def compress(ts_dataset: list[list[float]], func: str, digits: int = 1) -> tuple[list[FloatTuple|IntTuple], int]:
    """
    Compresses the given time series data into an integer representation using the specified function up to the number
    of digits.

    :param ts_dataset: A set of univariate time series.
    :param func: One of the keys in the func_dict.
    :param digits: Precision of the compressed representation, that is, the number of digits the deconstructed time
        series will have.
    :return: One representation for each time series, plus the digits at second position.
    """
    return [_compress(ts, func, digits) for ts in ts_dataset], digits

def _compress(time_series: list[float], func: str, digits: int = 1) -> IntTuple|FloatTuple:
    l = len(time_series)
    int_parts = [int(x) for x in time_series]  # Extract integer parts
    frac_parts = np.round([x - i for x, i in zip(time_series, int_parts)], 10)  # Extract fractional parts
    frac_as_digits = [int(np.round(x * 10 ** digits, 0)) for x in frac_parts]

    m_int = min(int_parts)
    if m_int <= 0:
        int_parts = [x - m_int + 1 for x in int_parts]
    z_int = element_wise_pairing(int_parts, func_dict[func][0])

    if not all(x == 0 for x in frac_as_digits):
        m_frac = min(frac_as_digits)
        if m_frac <= 0:
            frac_as_digits = [x - m_frac + 1 for x in frac_as_digits]
        z_frac = element_wise_pairing(frac_as_digits, func_dict[func][0])
        return FloatTuple(z_int, z_frac, l, m_int, m_frac)
    return IntTuple(z_int, l, m_int)

def decompress(compression: tuple[list[FloatTuple|IntTuple], int], func: str) -> list[list[float]]:
    """
    Decompresses the given representation back to the original time series.

    :param compression: The list of representations, one for each time series, plus the number of digits of each value
        included in the compression.
    :param func: One of the keys in the func_dict, the same as for the compression.
    :return: A lossy reconstruction of the original time series dataset, order preserved.
    """
    compressed_ts, digits = compression
    decompressed_ts = []
    for t in compressed_ts:
        decompressed_int_parts = _decompress(t.z_int, t.l, t.m_int, func)
        if isinstance(t, FloatTuple):
            decompressed_frac_parts = _decompress(t.z_frac, t.l, t.m_frac, func)
            reconstruct = [float(x + np.round(i / 10 ** digits, 10)) for x, i in zip(decompressed_int_parts, decompressed_frac_parts)]
        else:
            reconstruct = decompressed_int_parts
        decompressed_ts.append(reconstruct)
    return decompressed_ts

def _decompress(z: list[int], l: int, m: int, func: str) -> list[float]:
    p = reverse_pairing(z, l, func_dict[func][1])
    if (m <= 0):
        p = [x + m - 1 for x in p]
    return p
