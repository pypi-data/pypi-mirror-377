# KerasFFT
A package that aims at simplifying the usage of FFT in Keras3.
Keras3 does not have a complex dtype. This means, that the `ops.fft` call is a bit cumbersome, as it expects a tuple of real- and imaginary part in `float32`.

### Basic FFT
The basic FFT part of this package acts as an inplace option for `ops.fft`, which handles the input automatically.
It accepts
- a tuple of real and imaginary part, `fft((x_real, x_imag))`, or
- a single float KerasTensor, which is then interpreted as the real part, `fft(x)`.

The latter option automatically initializes a zero-Tensor with the same shape and dtype as `x`.

### FFT-based differentiation
Additionally, the module `keras_fft.derivative` contains code for the differentiation in Fourier space,
which is an elegant way to get the `n`th derivative of a signal.

### Note
Keras backends JAX and Tensorflow are currently supported.

## Installation

## Usage
