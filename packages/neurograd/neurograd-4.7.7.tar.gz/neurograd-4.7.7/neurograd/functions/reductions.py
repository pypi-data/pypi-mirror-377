### REDUCTIONS AFTER 
from neurograd import xp
import builtins
from .base import Function
from neurograd.nn.module import Module

### NOT USED ANYMORE - kept for reference
# def _reduce(arr, axis, reduction_func, keepdims=False, **kwargs):
#     """Helper to perform reductions over multiple axes iteratively for CuPy compatibility."""
#     if axis is None or isinstance(axis, int):
#         return reduction_func(arr, axis=axis, keepdims=keepdims, **kwargs)
#     # For tuple of axes, reduce iteratively
#     ndim = arr.ndim
#     axes = tuple(ax if ax >= 0 else ndim + ax for ax in axis)
#     axes = tuple(sorted(axes, reverse=True))
#     result = arr
#     for ax in axes:
#         result = reduction_func(result, axis=ax, keepdims=True, **kwargs)
#     if not keepdims:
#         result = xp.squeeze(result, axis=axes)
#     return result


class Sum(Function, Module):
    name = "Sum"
    def __init__(self, axis=None, keepdims=False):
        Function.__init__(self)
        Module.__init__(self)
        self.axis = axis
        self.keepdims = keepdims
        
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        # Use direct sum without intermediate conversions
        result = xp.sum(x, axis=self.axis, keepdims=self.keepdims)
        return result
        
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if not x.requires_grad:
            return None
            
        # Optimized broadcasting - avoid intermediate arrays when possible
        if self.axis is None:
            # Most efficient path for full reduction
            if grad_output.shape == ():
                return xp.full(x.shape, grad_output.item(), dtype=x.dtype)
            return xp.broadcast_to(grad_output, x.shape)
            
        # Handle partial reductions efficiently
        grad = grad_output
        if not self.keepdims:
            # Use negative indexing for better performance
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            for ax in sorted(axes):
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                grad = xp.expand_dims(grad, axis=ax_norm)
                
        return xp.broadcast_to(grad, x.shape)

class Mean(Function, Module):
    name = "Mean"
    def __init__(self, axis=None, keepdims=False):
        Function.__init__(self)
        Module.__init__(self)
        self.axis = axis
        self.keepdims = keepdims
        
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        # Direct mean computation
        return xp.mean(x, axis=self.axis, keepdims=self.keepdims)
        
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if not x.requires_grad:
            return None
            
        # Pre-compute scaling factor
        if self.axis is None:
            scale = 1.0 / x.size
        else:
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            scale = 1.0
            for ax in axes:
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                scale /= x.shape[ax_norm]
        
        # Expand dimensions if needed
        grad = grad_output
        if self.axis is not None and not self.keepdims:
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            for ax in sorted(axes):
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                grad = xp.expand_dims(grad, axis=ax_norm)
        
        # Single fused operation: broadcast and scale
        return xp.broadcast_to(grad, x.shape) * scale

class Max(Function, Module):
    name = "Max"
    def __init__(self, axis=None, keepdims=False):
        Function.__init__(self)
        Module.__init__(self)
        self.axis = axis
        self.keepdims = keepdims
        
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        # Store max values with keepdims=True for efficient backward
        self.max_keepdims = xp.max(x, axis=self.axis, keepdims=True)
        
        if self.keepdims:
            return self.max_keepdims
        
        # Efficient squeeze operation
        if self.axis is None:
            return self.max_keepdims.squeeze()
        
        axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
        return xp.squeeze(self.max_keepdims, axis=axes)
            
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if not x.requires_grad:
            return None
            
        # Efficient mask computation using broadcasting
        mask = (x.data == self.max_keepdims)
        
        # Normalize mask to handle ties - single reduction operation
        if self.axis is None:
            norm_factor = 1.0 / xp.sum(mask)
            mask = mask * norm_factor
        else:
            # Use keepdims=True to avoid reshape operations
            count = xp.sum(mask, axis=self.axis, keepdims=True)
            # Avoid division by zero with fused operation
            mask = xp.where(count > 0, mask / count, mask)
            
        # Expand gradient efficiently
        grad = grad_output
        if self.axis is not None and not self.keepdims:
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            for ax in sorted(axes):
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                grad = xp.expand_dims(grad, axis=ax_norm)
                
        # Single fused multiply-broadcast operation
        return mask * xp.broadcast_to(grad, x.shape)

class Min(Function, Module):
    name = "Min"
    def __init__(self, axis=None, keepdims=False):
        Function.__init__(self)
        Module.__init__(self)
        self.axis = axis
        self.keepdims = keepdims
        
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        # Store min values with keepdims=True for efficient backward
        self.min_keepdims = xp.min(x, axis=self.axis, keepdims=True)
        
        if self.keepdims:
            return self.min_keepdims
        
        # Efficient squeeze operation
        if self.axis is None:
            return self.min_keepdims.squeeze()
        
        axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
        return xp.squeeze(self.min_keepdims, axis=axes)
            
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if not x.requires_grad:
            return None
            
        # Efficient mask computation using broadcasting
        mask = (x.data == self.min_keepdims)
        
        # Normalize mask to handle ties - single reduction operation
        if self.axis is None:
            norm_factor = 1.0 / xp.sum(mask)
            mask = mask * norm_factor
        else:
            # Use keepdims=True to avoid reshape operations
            count = xp.sum(mask, axis=self.axis, keepdims=True)
            # Avoid division by zero with fused operation
            mask = xp.where(count > 0, mask / count, mask)
            
        # Expand gradient efficiently
        grad = grad_output
        if self.axis is not None and not self.keepdims:
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            for ax in sorted(axes):
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                grad = xp.expand_dims(grad, axis=ax_norm)
                
        # Single fused multiply-broadcast operation
        return mask * xp.broadcast_to(grad, x.shape)

class Std(Function, Module):
    name = "Std"
    def __init__(self, axis=None, keepdims=False, eps=1e-8):
        Function.__init__(self)
        Module.__init__(self)
        self.axis = axis
        self.keepdims = keepdims
        self.eps = eps
        
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        # Use CuPy's optimized std function directly when possible
        if self.eps == 0:
            return xp.std(x, axis=self.axis, keepdims=self.keepdims)
            
        # For numerical stability with eps
        self.mean_keepdims = xp.mean(x, axis=self.axis, keepdims=True)
        
        # Single pass variance computation
        diff = x - self.mean_keepdims
        var_keepdims = xp.mean(diff * diff, axis=self.axis, keepdims=True)
        
        # Stable sqrt with eps
        std_keepdims = xp.sqrt(var_keepdims + self.eps)
        self.std_keepdims = std_keepdims
        
        if self.keepdims:
            return std_keepdims
        
        if self.axis is None:
            return std_keepdims.squeeze()
        
        axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
        return xp.squeeze(std_keepdims, axis=axes)
            
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if not x.requires_grad:
            return None
            
        # Pre-compute scaling factor
        if self.axis is None:
            n = x.size
        else:
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            n = 1
            for ax in axes:
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                n *= x.shape[ax_norm]
                
        # Expand gradient if needed
        grad = grad_output
        if self.axis is not None and not self.keepdims:
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            for ax in sorted(axes):
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                grad = xp.expand_dims(grad, axis=ax_norm)
        
        # Fused computation: (x - mean) / (n * std) * grad
        numerator = x.data - self.mean_keepdims
        denominator = n * self.std_keepdims
        
        return xp.broadcast_to(grad, x.shape) * (numerator / denominator)

class Var(Function, Module):
    name = "Var"
    def __init__(self, axis=None, keepdims=False, ddof=0):
        Function.__init__(self)
        Module.__init__(self)
        self.axis = axis
        self.keepdims = keepdims
        self.ddof = ddof
        
    def forward(self, x: xp.ndarray) -> xp.ndarray:
        # Use CuPy's var when ddof=0
        if self.ddof == 0:
            return xp.var(x, axis=self.axis, keepdims=self.keepdims)
            
        # Custom implementation for Bessel correction
        self.mean_keepdims = xp.mean(x, axis=self.axis, keepdims=True)
        diff = x - self.mean_keepdims
        var_keepdims = xp.mean(diff * diff, axis=self.axis, keepdims=True)
        
        # Apply Bessel's correction
        if self.axis is None:
            n = x.size
        else:
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            n = 1
            for ax in axes:
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                n *= x.shape[ax_norm]
        
        correction_factor = n / max(n - self.ddof, 1)
        var_keepdims = var_keepdims * correction_factor
        self.correction_factor = correction_factor
        
        if self.keepdims:
            return var_keepdims
            
        if self.axis is None:
            return var_keepdims.squeeze()
        
        axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
        return xp.squeeze(var_keepdims, axis=axes)
        
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        x = self.parent_tensors[0]
        if not x.requires_grad:
            return None
        
        # Expand gradient if needed
        grad = grad_output
        if self.axis is not None and not self.keepdims:
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            for ax in sorted(axes):
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                grad = xp.expand_dims(grad, axis=ax_norm)
        
        # Fused gradient computation
        scale = 2.0 * self.correction_factor
        if self.axis is None:
            scale /= x.size
        else:
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            for ax in axes:
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                scale /= x.shape[ax_norm]
        
        # Single fused operation
        centered = x.data - self.mean_keepdims
        return xp.broadcast_to(grad, x.shape) * (centered * scale)

class MeanVar(Function, Module):
    """Highly optimized fused mean and variance computation"""
    name = "MeanVar"
    def __init__(self, axis=None, keepdims=False, ddof=0):
        Function.__init__(self)
        Module.__init__(self)
        self.axis = axis
        self.keepdims = keepdims
        self.ddof = ddof
    
    def forward(self, x: xp.ndarray) -> tuple:
        # Single pass through data for both computations
        self.mean_keepdims = xp.mean(x, axis=self.axis, keepdims=True)
        
        # Efficient variance computation
        centered = x - self.mean_keepdims
        var_keepdims = xp.mean(centered * centered, axis=self.axis, keepdims=True)
        
        # Bessel correction if needed
        if self.ddof > 0:
            if self.axis is None:
                n = x.size
            else:
                axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
                n = 1
                for ax in axes:
                    ax_norm = ax if ax >= 0 else len(x.shape) + ax
                    n *= x.shape[ax_norm]
            
            correction = n / max(n - self.ddof, 1)
            var_keepdims = var_keepdims * correction
            self.correction = correction
        else:
            self.correction = 1.0
            
        # Handle output dimensions efficiently
        if self.keepdims:
            return self.mean_keepdims, var_keepdims
        
        if self.axis is None:
            return self.mean_keepdims.squeeze(), var_keepdims.squeeze()
        
        axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
        mean_out = xp.squeeze(self.mean_keepdims, axis=axes)
        var_out = xp.squeeze(var_keepdims, axis=axes)
        
        return mean_out, var_out
    
    def backward(self, grad_mean: xp.ndarray, grad_var: xp.ndarray):
        x = self.parent_tensors[0]
        if not x.requires_grad:
            return None
        
        # Pre-compute scaling factors
        if self.axis is None:
            mean_scale = 1.0 / x.size
            var_scale = 2.0 * self.correction / x.size
        else:
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            n = 1
            for ax in axes:
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                n *= x.shape[ax_norm]
            mean_scale = 1.0 / n
            var_scale = 2.0 * self.correction / n
        
        # Expand gradients if needed
        if self.axis is not None and not self.keepdims:
            axes = (self.axis,) if isinstance(self.axis, int) else tuple(self.axis)
            for ax in sorted(axes):
                ax_norm = ax if ax >= 0 else len(x.shape) + ax
                grad_mean = xp.expand_dims(grad_mean, axis=ax_norm)
                grad_var = xp.expand_dims(grad_var, axis=ax_norm)
        
        # Broadcast to input shape
        grad_mean = xp.broadcast_to(grad_mean, x.shape)
        grad_var = xp.broadcast_to(grad_var, x.shape)
        
        # Single fused gradient computation
        centered = x.data - self.mean_keepdims
        return grad_mean * mean_scale + grad_var * (var_scale * centered)

# Optimized function interfaces
def sum(x, axis=None, keepdims=False):
    return Sum(axis=axis, keepdims=keepdims)(x)

def mean(x, axis=None, keepdims=False):
    return Mean(axis=axis, keepdims=keepdims)(x)

def max(x, axis=None, keepdims=False):
    return Max(axis=axis, keepdims=keepdims)(x)

def min(x, axis=None, keepdims=False):
    return Min(axis=axis, keepdims=keepdims)(x)

def std(x, axis=None, keepdims=False, eps=1e-8):
    return Std(axis=axis, keepdims=keepdims, eps=eps)(x)

def var(x, axis=None, keepdims=False, ddof=0):
    return Var(axis=axis, keepdims=keepdims, ddof=ddof)(x)

def mean_var(x, axis=None, keepdims=False, ddof=0):
    """Optimized fused mean and variance computation"""
    return MeanVar(axis=axis, keepdims=keepdims, ddof=ddof)(x) 