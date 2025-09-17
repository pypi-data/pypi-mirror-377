import jax.numpy as jnp
from typing import Tuple
from functools import partial
from ..helper.jax import get_complex_tensor_from_tuple


# === FFT ===
def _fft(x: tuple, fn: callable, **kwargs) -> Tuple[jnp.ndarray, jnp.ndarray]:
    complex_input = get_complex_tensor_from_tuple(x)
    complex_output = fn(complex_input, **kwargs)
    return jnp.real(complex_output), jnp.imag(complex_output)


# === real valued FFT ===
def _rfft(x: jnp.ndarray, fn: callable, **kwargs) -> Tuple[jnp.ndarray, jnp.ndarray]:
    complex_output = fn(x, **kwargs)
    return jnp.real(complex_output), jnp.imag(complex_output)


def _irfft(x: jnp.ndarray, fn: callable, **kwargs) -> jnp.ndarray:
    complex_input = get_complex_tensor_from_tuple(x)
    complex_output = fn(complex_input, **kwargs)
    return jnp.real(complex_output), jnp.imag(complex_output)


# === derived functions ===
def fft_fn(x):
    return partial(_fft, fn=jnp.fft.fft)(x)


def fft2_fn(x):
    return partial(_fft, fn=jnp.fft.fft2)(x)


def fft3_fn(x):
    return partial(_fft, fn=jnp.fft.fftn, axes=(-3, -2, -1))(x)


def ifft_fn(x):
    return partial(_fft, fn=jnp.fft.ifft)(x)


def ifft2_fn(x):
    return partial(_fft, fn=jnp.fft.ifft2)(x)


def ifft3_fn(x):
    return partial(_fft, fn=jnp.fft.ifftn, axes=(-3, -2, -1))(x)


def rfft_fn(x):
    return partial(_rfft, fn=jnp.fft.rfft)(x)


def rfft2_fn(x):
    return partial(_rfft, fn=jnp.fft.rfft2)(x)


def rfft3_fn(x):
    return partial(_rfft, fn=jnp.fft.rfftn, axes=(-3, -2, -1))(x)


def irfft_fn(x, n=None):
    if isinstance(n, tuple):
        n, = n  # unpack tuple
    y_real, _ = partial(_irfft, fn=jnp.fft.irfft, n=n)(x)
    return y_real


def irfft2_fn(x, n=None):
    y_real, _ = partial(_irfft, fn=jnp.fft.irfft2, s=n)(x)
    return y_real


def irfft3_fn(x, n=None):
    y_real, _ = partial(_irfft, fn=jnp.fft.irfftn, s=n, axes=(-3, -2, -1))(x)
    return y_real
