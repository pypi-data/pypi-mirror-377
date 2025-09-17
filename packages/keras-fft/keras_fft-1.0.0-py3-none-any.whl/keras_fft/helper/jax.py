import jax.numpy as jnp
import jax


def get_complex_tensor_from_tuple(x) -> jax.lax.complex:
    """
    Get a complex tensor from a tuple of two real-valued tensors.

    Parameters
    ----------
    x : jax.lax.real | list | tuple
        Input tensor, either `jax.lax.real` (real part) or tuple/list (real- and imaginary part).
        If only the real part is provided, the imaginary part is assumed 0.

    Returns
    -------
    y : jax.lax.complex
        Tensor with `dtype=jax.lax.complex`.

    Raises
    ------
    ValueError
        If shapes of real- and imaginary part to not match.
    ValueError
        If at least on of the inputs is not of type float.

    """

    if not isinstance(x, (tuple, list)) or len(x) != 2:
        real = x
        imag = jnp.zeros_like(x)
    else:
        real, imag = x
    # Check shapes.
    if real.shape != imag.shape:
        raise ValueError(
            "Input `x` should be a tuple of two tensors - real and imaginary."
            "Both the real and imaginary parts should have the same shape. "
            f"Received: x[0].shape = {real.shape}, x[1].shape = {imag.shape}"
        )
    # Ensure dtype is float.
    if not jnp.issubdtype(real.dtype, jnp.floating) or not jnp.issubdtype(
        imag.dtype, jnp.floating
    ):
        raise ValueError(
            "At least one tensor in input `x` is not of type float."
            f"Received: x={x}."
        )
    
    complex_input = jax.lax.complex(real, imag)
    return complex_input
