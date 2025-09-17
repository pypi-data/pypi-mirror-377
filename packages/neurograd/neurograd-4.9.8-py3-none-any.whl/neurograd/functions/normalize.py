import neurograd as ng
from neurograd import xp
from neurograd.nn.module import Module
from neurograd.functions.base import Function
import math

class BatchNormalizer(Function):
    name = "BatchNormalizer"
    def __init__(self, axis=0, eps=1e-5):
        Function.__init__(self)
        self.axis = axis
        self.eps = eps
        # Cache for backward pass
        self.x_mean = None
        self.x_std = None
        self.N = None      # Cache number of elements for averaging
    def _affine(self, x: xp.ndarray, mean: xp.ndarray, std: xp.ndarray,
                mean_scaler: xp.ndarray, std_scaler: xp.ndarray):
        # Normalize
        x_hat = (x - mean) / std
        # Scale and shift
        out = std_scaler * x_hat + mean_scaler
        return out
    def forward(self, x: xp.ndarray, mean_scaler: xp.ndarray,
                std_scaler: xp.ndarray) -> xp.ndarray:
        # Calculate mean and std over the specified axes
        self.x_mean = xp.mean(x, axis=self.axis, keepdims=True)
        # Calculate variance instead of std to avoid numerical issues
        x_var = xp.var(x, axis=self.axis, keepdims=True)
        self.x_std = xp.sqrt(x_var + self.eps)
        # Calculate number of elements used in normalization
        if isinstance(self.axis, tuple):
            self.N = 1
            for ax in self.axis:
                self.N *= x.shape[ax]
        else:
            self.N = x.shape[self.axis]
        return self._affine(x, self.x_mean, self.x_std, mean_scaler, std_scaler)

    def backward(self, dout: xp.ndarray) -> tuple:
        x = self.parent_tensors[0].data
        std_scaler = self.parent_tensors[2].data
        # Gradients w.r.t. scale and bias parameters
        dmean_scaler = None
        dstd_scaler = None
        # Recompute x_hat (memory efficient)
        x_hat = (x - self.x_mean) / self.x_std
        if self.parent_tensors[1].requires_grad:
            dmean_scaler = xp.sum(dout, axis=self.axis, keepdims=True)
        if self.parent_tensors[2].requires_grad:
            dstd_scaler = xp.sum(dout * x_hat, axis=self.axis, keepdims=True)
        # Gradient w.r.t. input x
        dx = None
        if self.parent_tensors[0].requires_grad:
            # Standard batch normalization backward pass
            dx_hat = dout * std_scaler
            # Compute gradients using the standard BatchNorm backward formula
            dx = (1.0 / self.N) * (1.0 / self.x_std) * (
                self.N * dx_hat
                - xp.sum(dx_hat, axis=self.axis, keepdims=True)
                - x_hat * xp.sum(dx_hat * x_hat, axis=self.axis, keepdims=True)
            ) 
        return dx, dmean_scaler, dstd_scaler


def batch_normalize(X, mean_scaler, var_scaler, axis, eps=1e-5):
    return BatchNormalizer(axis, eps)(X, mean_scaler, var_scaler)