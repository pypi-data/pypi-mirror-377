import tensorflow as tf
from math import pi


def fftfreq(n, d, rad=False):
    fs = 1.0 / d
    df = fs / tf.cast(n, tf.float32)
    fft_freqs = tf.cast(tf.range(n) - n // 2, dtype=tf.float32)
    fft_freqs *= df

    if rad:
        fft_freqs *= (2.0 * pi)

    fft_freqs = tf.roll(fft_freqs, shift=n // 2, axis=0)
    return fft_freqs


def get_complex_tensor_from_tuple(x):
    """
    Get a complex tensor from a tuple of two real-valued tensors.

    Parameters
    ----------
    x : tf.Tensor | list | tuple
        Input tensor, either `tf.Tensor` (real part) or tuple/list (real- and imaginary part).
        If only the real part is provided, the imaginary part is assumed 0.

    Returns
    -------
    y : tf.Tensor
        Tensor with `dtype=tf.complex`.

    Raises
    ------
    ValueError
        If shapes of real- and imaginary part to not match.

    """

    if not isinstance(x, (tuple, list)) or len(x) != 2:
        real = x
        imag = tf.zeros_like(x)
    else:
        real, imag = x
    # Check shapes.
    if real.shape != imag.shape:
        raise ValueError(
            "Input `x` should be a tuple of two tensors - real and imaginary."
            "Both the real and imaginary parts should have the same shape. "
            f"Received: x[0].shape = {real.shape}, x[1].shape = {imag.shape}"
        )

    complex_input = tf.complex(real=real, imag=imag)
    return complex_input
