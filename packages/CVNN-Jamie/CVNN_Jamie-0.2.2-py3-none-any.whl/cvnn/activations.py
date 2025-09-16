from typing import Optional
import numpy as np
from numpy.typing import NDArray

def jam(z: NDArray) -> NDArray:
    """JAM activation function.

    A specialized activation function that uses the imaginary part of the sigmoid
    to make binary decisions. Useful for XOR-like problems in complex domain.

    Args:
        z: Input tensor of complex values

    Returns:
        Binary tensor (0s and 1s) based on sigmoid(z).imag > 0

    Example:
        >>> x = np.array([1+1j, 1-1j, -1+1j, -1-1j])
        >>> jam(x)
        array([1., 0., 1., 0.])
    """
    s = 1 / (1 + np.exp(-z))
    return (s.imag > 0).astype(np.float64)

def jam_derivative(z: NDArray, grad_output: NDArray) -> NDArray:
    """Derivative of the JAM activation function.

    Computes the gradient for backpropagation through JAM activation.

    Args:
        z: Input tensor that was fed to the JAM activation
        grad_output: Gradient of the loss with respect to JAM output

    Returns:
        Gradient tensor for backpropagation
    """
    s = 1 / (1 + np.exp(-z))
    ds = s * (1 - s)
    return grad_output * (ds.real + 1j * ds.imag)


def complex_relu(z: NDArray) -> NDArray:
    """Complex-valued ReLU activation function.

    Applies ReLU separately to real and imaginary parts:
    f(z) = ReLU(Re(z)) + j*ReLU(Im(z))

    Args:
        z: Input tensor of complex values

    Returns:
        Complex tensor with ReLU applied to both real and imaginary parts

    Example:
        >>> x = np.array([1+1j, -1-1j])
        >>> complex_relu(x)
        array([1.+1.j, 0.+0.j])
    """
    return np.maximum(z.real, 0) + 1j * np.maximum(z.imag, 0)

def complex_relu_backward(z: NDArray, grad_output: NDArray) -> NDArray:
    """Derivative of complex-valued ReLU.

    Computes gradients for backpropagation through complex ReLU.

    Args:
        z: Input tensor that was fed to complex_relu
        grad_output: Gradient of the loss with respect to ReLU output

    Returns:
        Gradient tensor for backpropagation
    """
    grad_real = grad_output.real * (z.real > 0)
    grad_imag = grad_output.imag * (z.imag > 0)
    return grad_real + 1j * grad_imag

# Additional complex activation functions

# Separable (real/imag) sigmoid
def complex_sigmoid(z, fully_complex=False):
    if not fully_complex:
        s_real = 1 / (1 + np.exp(-z.real))
        s_imag = 1 / (1 + np.exp(-z.imag))
        return s_real + 1j * s_imag
    else:
        return 1 / (1 + np.exp(-z))

def complex_sigmoid_backward(z, grad_output, fully_complex=False):
    if not fully_complex:
        s_real = 1 / (1 + np.exp(-z.real))
        s_imag = 1 / (1 + np.exp(-z.imag))
        grad_real = grad_output.real * s_real * (1 - s_real)
        grad_imag = grad_output.imag * s_imag * (1 - s_imag)
        return grad_real + 1j * grad_imag
    else:
        s = 1 / (1 + np.exp(-z))
        return grad_output * s * (1 - s)


# Separable (real/imag) tanh
def complex_tanh(z, fully_complex=False):
    if not fully_complex:
        t_real = np.tanh(z.real)
        t_imag = np.tanh(z.imag)
        return t_real + 1j * t_imag
    else:
        return np.tanh(z)

def complex_tanh_backward(z, grad_output, fully_complex=False):
    if not fully_complex:
        t_real = np.tanh(z.real)
        t_imag = np.tanh(z.imag)
        grad_real = grad_output.real * (1 - t_real ** 2)
        grad_imag = grad_output.imag * (1 - t_imag ** 2)
        return grad_real + 1j * grad_imag
    else:
        t = np.tanh(z)
        return grad_output * (1 - t ** 2)


def modrelu(z, bias=0):
    # modReLU: relu on modulus, keep phase
    modulus = np.abs(z)
    phase = np.angle(z)
    return np.maximum(modulus + bias, 0) * np.exp(1j * phase)

# Initialisation methods
def complex_glorot_uniform(shape):
    # Glorot uniform for complex weights
    limit = np.sqrt(6 / np.sum(shape))
    real = np.random.uniform(-limit, limit, size=shape)
    imag = np.random.uniform(-limit, limit, size=shape)
    return real + 1j * imag

def complex_he_normal(shape):
    # He normal for complex weights
    stddev = np.sqrt(2 / shape[0])
    real = np.random.normal(0, stddev, size=shape)
    imag = np.random.normal(0, stddev, size=shape)
    return real + 1j * imag
