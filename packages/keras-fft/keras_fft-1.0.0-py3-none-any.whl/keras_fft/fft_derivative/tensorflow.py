import tensorflow as tf
from ..helper.tensorflow import get_complex_tensor_from_tuple, fftfreq


def derivative(x, axis=-1, d=1.0, n=1):
    """
    Derivative in Fourier space

    Parameters
    ----------
    x : tf.Tensor
        Input array, can be either real or complex valued.
    axis : int (optional)
        Axis along which `x` is derived.
        Defaults to `-1`.
    d : float (optional)
        Discretization of `x` along the dimension of `axis`.
        Defaults to `1.0`.
    n : int (optional)
        Order of differentiation.
        Defaults to `1`.

    Returns
    -------
    dx : tf.Tensor
        `n`th derivative of `x` along `axis`.

    Examples
    --------
    >>> n = 32
    >>> t = tf.range(0, 2 * pi, 2 * pi / 32)
    >>> dt = 2 * pi / 32
    >>> x = tf.sin(t)
    >>> dxdt_ref = tf.cos(t)
    >>> dxdt = fft_derivative(x, d=dt)
    >>> tf.reduce_max(dxdt_ref - dxdt)  
    tf.Tensor(1.0728836e-06, shape=(), dtype=float32)

    Notes
    -----
    For higher orders, the derivatives may get noisy.
    The intensity depends on the signal length, i.e.,
    this effect is less significant for short signals.

    """
    
    nx = tf.shape(x)[axis]
    dim = len(tf.shape(x))

    if dim > 1:
        # tf.signal.fft is always along last axis --> move axis to last dimension
        perm = list(range(dim))
        
        # map axis to positive integer
        axis = perm[axis]
        perm.append(perm.pop(axis))

        # permute `x` such that `axis` is the last axis
        x = tf.transpose(x, perm=perm)

    x = get_complex_tensor_from_tuple(x)
    freqs = fftfreq(n=nx, d=d, rad=True)

    complex_diff = tf.signal.ifft(tf.pow((1j * tf.cast(freqs, dtype=x.dtype)), tf.cast(n, dtype=x.dtype)) * tf.signal.fft(x))
    diff = tf.math.real(complex_diff)

    if dim > 1:
        # revert permutation
        perm = list(range(dim))
        perm.insert(axis, perm.pop())
        diff = tf.transpose(diff, perm=perm)

    return diff
