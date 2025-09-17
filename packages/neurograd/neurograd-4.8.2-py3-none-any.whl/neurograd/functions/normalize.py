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

    def _affine(self, x: xp.ndarray, mean: xp.ndarray, std: xp.ndarray,
                mean_scaler: xp.ndarray, std_scaler: xp.ndarray):
        # Normalize
        x_hat = (x - mean) / std
        # Scale and shift
        out = std_scaler * x_hat + mean_scaler
        return out
    
    def forward(self, x: xp.ndarray, mean_scaler: xp.ndarray, 
                std_scaler: xp.ndarray) -> xp.ndarray:
        # For BatchNorm1D: axis=0 (average over batch dimension)
        # For BatchNorm2D: axis=(0, 2, 3) (average over batch, height, width)
        self.x_mean = xp.mean(x, axis=self.axis, keepdims=True)
        # Calculate variance instead of std to avoid numerical issues
        x_var = xp.var(x, axis=self.axis, keepdims=True)
        self.x_std = xp.sqrt(x_var + self.eps)
        return self._affine(x, self.x_mean, self.x_std, mean_scaler, std_scaler)
    
    def backward(self, dout: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0].data
        std_scaler = self.parent_tensors[2].data
        N = x.shape[0]  # Batch size
        # Recompute x_hat from cached values
        x_hat = (x - self.x_mean) / self.x_std
        # For 2D case, we need to account for spatial dimensions
        m = math.prod(x.shape[ax] for ax in (self.axis if isinstance(self.axis, tuple) else (self.axis,)))
        # Gradients w.r.t. scale and bias parameters
        dmean_scaler = xp.sum(dout, axis=self.axis, keepdims=True) if self.parent_tensors[1].requires_grad else None
        dstd_scaler = xp.sum(dout * x_hat, axis=self.axis, keepdims=True) if self.parent_tensors[2].requires_grad else None
        # Gradient w.r.t. normalized input
        if self.parent_tensors[0].requires_grad:
            dx_hat = dout * std_scaler
            # Gradient w.r.t. input x (using chain rule)
            # This is the correct BatchNorm backward pass formula
            dx = (1.0 / m) * (1.0 / self.x_std) * (
                m * dx_hat 
                - xp.sum(dx_hat, axis=self.axis, keepdims=True)
                - x_hat * xp.sum(dx_hat * x_hat, axis=self.axis, keepdims=True)
            )
        else:
            dx = None
        return dx, dmean_scaler, dstd_scaler


def batch_normalize(X, mean_scaler, var_scaler, axis, eps=1e-5):
    return BatchNormalizer(axis, eps)(X, mean_scaler, var_scaler)
