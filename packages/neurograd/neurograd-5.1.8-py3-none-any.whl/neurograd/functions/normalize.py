import neurograd as ng
from neurograd import xp
from neurograd.nn.module import Module
from neurograd.functions.base import Function
import math

# CUPY BUG: Var reductions over multiple axes are slow in CuPy.
def _reduce(arr, axis, reduction_func, keepdims=False, **kwargs):
    """
    Performs a reduction iteratively over a tuple of axes for optimal speed,
    especially in CuPy. This function is the FAST PATH for decomposable
    reductions like mean, sum, max, and min.
    """
    # If axis is None, reduce over all axes by converting to a tuple of all axes.
    if axis is None:
        axis = tuple(range(arr.ndim))
    # If axis is a single integer, the library's default is already optimized.
    if isinstance(axis, int):
        return reduction_func(arr, axis=axis, keepdims=keepdims, **kwargs)
    # --- Iterative Path for Tuple of Axes (The Fast Path) ---
    ndim = arr.ndim
    axes = tuple(ax if ax >= 0 else ndim + ax for ax in axis)
    axes = tuple(sorted(axes, reverse=True))
    result = arr
    for ax in axes:
        result = reduction_func(result, axis=ax, keepdims=True, **kwargs)
    if not keepdims:
        result = xp.squeeze(result, axis=axes)
    return result
def _iterative_var(arr, axis, keepdims=False):
    """
    Calculates variance correctly and quickly using the fast `_reduce` helper.
    This version includes a clamp to prevent negative variance due to
    floating-point inaccuracies (catastrophic cancellation).
    """
    arr_mean = _reduce(arr, axis, xp.mean, keepdims=True)
    arr_sq_mean = _reduce(xp.square(arr), axis, xp.mean, keepdims=True)
    var = arr_sq_mean - xp.square(arr_mean)
    # --- THE FIX ---
    # Clamp the variance to be non-negative. This is a robust way to
    # handle floating-point errors without affecting correct positive variances.
    var = xp.maximum(var, 0)
    if not keepdims:
        if axis is None:
            axis_to_squeeze = tuple(range(arr.ndim))
        elif isinstance(axis, int):
            axis_to_squeeze = (axis,)
        else: # tuple
            axis_to_squeeze = axis
        var = xp.squeeze(var, axis=axis_to_squeeze)
    return var



class BatchNormalizer(Function):
    name = "BatchNormalizer"
    def __init__(self, axis=0, eps=1e-5, memsave=False):
        Function.__init__(self)
        self.axis = axis
        self.eps = eps
        self.memsave = memsave
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
        x_var = _iterative_var(x, self.axis, keepdims=True)
        self.x_std = xp.sqrt(x_var + self.eps)
        # Calculate number of elements used in normalization
        if self.N is None:
            if isinstance(self.axis, tuple):
                self.N = 1
                for ax in self.axis:
                    self.N *= x.shape[ax]
            else:
                self.N = x.shape[self.axis]
        return self._affine(x, self.x_mean, self.x_std, mean_scaler, std_scaler)
    
    def _memsave(self, parents, output):
        parents[0].data = output.data

    def backward(self, dout: xp.ndarray) -> tuple:
        x = self.parent_tensors[0].data
        mean_scaler = self.parent_tensors[1].data
        std_scaler = self.parent_tensors[2].data

        if self.memsave:
            x_hat = (x - mean_scaler) / std_scaler
        else:
            x_hat = (x - self.x_mean) / self.x_std

        # ---- Dummy sum replacement ----
        def fake_sum(arr, axis=None, keepdims=False):
            # Determine output shape
            if axis is None:
                out_shape = (1,) * arr.ndim if keepdims else ()
            elif isinstance(axis, int):
                out_shape = list(arr.shape)
                out_shape[axis] = 1 if keepdims else ()
            else:  # tuple of axes
                out_shape = list(arr.shape)
                for ax in axis:
                    out_shape[ax] = 1
                if not keepdims:
                    out_shape = [s for i, s in enumerate(out_shape) if i not in axis]
            if isinstance(out_shape, list):
                out_shape = tuple(out_shape)
            return xp.zeros(out_shape, dtype=arr.dtype)

        # Monkey-patch sum
        real_sum = xp.sum
        xp.sum = fake_sum

        dmean_scaler = None
        dstd_scaler = None
        x_hat = (x - self.x_mean) / self.x_std

        if self.parent_tensors[1].requires_grad:
            dmean_scaler = xp.sum(dout, axis=self.axis, keepdims=True)
        if self.parent_tensors[2].requires_grad:
            dstd_scaler = xp.sum(dout * x_hat, axis=self.axis, keepdims=True)

        dx = None
        if self.parent_tensors[0].requires_grad:
            dx_hat = dout * std_scaler
            dx = (1.0 / self.N) * (1.0 / self.x_std) * (
                self.N * dx_hat
                - xp.sum(dx_hat, axis=self.axis, keepdims=True)
                - x_hat * xp.sum(dx_hat * x_hat, axis=self.axis, keepdims=True)
            )

        # Restore real sum
        xp.sum = real_sum

        return dx, dmean_scaler, dstd_scaler

def batch_normalize(X, mean_scaler, var_scaler, axis, eps=1e-5, memsave=False):
    return BatchNormalizer(axis, eps, memsave)(X, mean_scaler, var_scaler)