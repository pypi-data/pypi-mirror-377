import jax.numpy as jnp
from ..helper.jax import get_complex_tensor_from_tuple


def derivative(x, axis=-1, d=1.0, n=1):
    """
    Derivative in Fourier space

    Parameters
    ----------
    x : array_like
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
    dx : array_like
        `n`th derivative of `x` along `axis`.

    Examples
    --------
    >>> t = jnp.linspace(0, 2 * jnp.pi, 32, endpoint=False)
    >>> dt = jnp.mean(jnp.diff(t))
    >>> x = jnp.sin(t)
    >>> dx_ref = jnp.cos(t)
    >>> dx = fft_derivative(x, d=dt, n=1.0)
    >>> jnp.allclose(dx_ref, dx, atol=1e-5)
    True

    Notes
    -----
    For higher orders, the derivatives may get noisy.
    The intensity depends on the signal length, i.e.,
    this effect is less significant for short signals.

    """
    
    nx = x.shape[axis]

    x = get_complex_tensor_from_tuple(x)
    freqs = jnp.fft.fftfreq(n=nx, d=d) * 2 * jnp.pi

    complex_diff = jnp.fft.ifft((1j * freqs)**n * jnp.fft.fft(x, axis=axis), axis=axis)
    diff = jnp.real(complex_diff)

    return diff