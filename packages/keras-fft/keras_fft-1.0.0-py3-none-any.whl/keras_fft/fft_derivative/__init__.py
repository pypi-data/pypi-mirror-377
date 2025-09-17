from keras.src.backend.config import backend
from keras.src.backend import any_symbolic_tensors
from keras.src.ops.operation import Operation
from keras import ops
from keras import KerasTensor


if backend() == "jax":
    from .jax import derivative as _derivative

elif backend() == "tensorflow":
    from .tensorflow import derivative as _derivative

else:
    raise ImportError(f"`keras-fft` does not support {backend()} backend, please use either `'jax'` or `'tensorflow'`.")


def cast_to_complex(x):
    if isinstance(x, tuple):
        return x
    else:
        return x, ops.zeros_like(x, dtype=x.dtype)
    

class FFTDerivative(Operation):
    def __init__(self):
        super().__init__()

    def compute_output_spec(self, x):
        """
        Compute output spec of Fourier transform

        Parameters
        ----------
        x : KerasTensor | tuple | list
            Real- or complex input to FFT. A complex input must be composed of a tuple or list of the real- and imaginary part `(x_real, x_imag)`.

        Returns
        -------
        diff_spec : KerasTensor
            spec of derivative of x

        """
        if not isinstance(x, (tuple, list)) or len(x) != 2:
            real = x
            imag = ops.zeros_like(x)
        else:
            real, imag = x
        # Both real and imaginary parts should have the same shape.
        if real.shape != imag.shape:
            raise ValueError(
                "Input `x` should be a tuple of two tensors - real and "
                "imaginary. Both the real and imaginary parts should have the "
                f"same shape. Received: x[0].shape = {real.shape}, "
                f"x[1].shape = {imag.shape}"
            )
        return KerasTensor(shape=real.shape, dtype=real.dtype)
    
    def call(self, x, axis=-1, d=1.0, n=1):
        """
        Derivative in Fourier space

        Parameters
        ----------
        x : KerasTensor
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
        dx : KerasTensor
            `n`th derivative of `x` along `axis`.

        Notes
        -----
        For higher orders, the derivatives may get noisy.
        The intensity depends on the signal length, i.e.,
        this effect is less significant for short signals.

        """

        return _derivative(x=x, axis=axis, d=d, n=n)
    
    
def derivative(x, axis=-1, d=1.0, n=1):
    """
    Derivative in Fourier space

    Parameters
    ----------
    x : KerasTensor
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
    dx : KerasTensor
        `n`th derivative of `x` along `axis`.

    Notes
    -----
    For higher orders, the derivatives may get noisy.
    The intensity depends on the signal length, i.e.,
    this effect is less significant for short signals.

    """
    
    if any_symbolic_tensors(cast_to_complex(x)):
        return FFTDerivative.symbolic_call(x, axis=axis, d=d, n=n)
    return _derivative(x=x, axis=axis, d=d, n=n)
