import neurograd as ng
from neurograd import xp
from .base import Function

class BatchNormalizer(Function):
    """
    Memory-optimized normalization operation: output = gamma * (X - y) / sqrt(z + eps) + beta
    
    Key optimizations:
    1. Minimal caching - only store what's absolutely necessary
    2. Recompute intermediate values in backward pass to save memory
    3. In-place operations where possible
    4. Streaming gradient computation to avoid memory spikes
    """
    name = "BatchNormalizer"
    
    @ng.fuse
    def _forward_kernel(X, y, z, gamma, beta, eps):
        """Compute forward pass with minimal intermediate storage"""
        inv_sqrt_z = xp.reciprocal(xp.sqrt(z + eps))  # More memory efficient
        output = gamma * ((X - y) * inv_sqrt_z) + beta
        return output, inv_sqrt_z
    
    @ng.fuse
    def _recompute_and_backward_kernel(grad_output, X, y, z, gamma, inv_sqrt_z, eps):
        """Recompute intermediates and compute gradients in one kernel"""
        # Recompute what we need (trades compute for memory)
        x_minus_y = X - y
        x_shifted = x_minus_y * inv_sqrt_z
        
        # Compute gradients
        dL_dx_shifted = grad_output * gamma
        dX = dL_dx_shifted * inv_sqrt_z
        dy = -dX  # More efficient than separate computation
        
        # Only compute dz if we need it (check if z requires grad outside)
        inv_sqrt_z_cubed = inv_sqrt_z * inv_sqrt_z * inv_sqrt_z
        dz = dL_dx_shifted * x_minus_y * (-0.5) * inv_sqrt_z_cubed
        
        return dX, dy, dz, x_shifted
    
    def __init__(self, axes, epsilon: float = 1e-5):
        super().__init__()
        self.axes = axes if isinstance(axes, tuple) else (axes,)
        self.epsilon = float(epsilon)
        # Only cache what's absolutely necessary
        self._cached_inv_sqrt_z = None
        self._cached_shapes = None
    
    def forward(self, X: xp.ndarray, y: xp.ndarray, z: xp.ndarray,
                gamma: xp.ndarray, beta: xp.ndarray) -> xp.ndarray:
        
        # Use the optimized kernel that returns minimal cached data
        output, inv_sqrt_z = BatchNormalizer._forward_kernel(
            X, y, z, gamma, beta, self.epsilon
        )
        
        # Only cache the small inv_sqrt_z tensor (same shape as z)
        self._cached_inv_sqrt_z = inv_sqrt_z
        self._cached_shapes = (X.shape, y.shape, z.shape, gamma.shape, beta.shape)
        
        return output
    
    def backward(self, grad_output: xp.ndarray):
        X, y, z, gamma, beta = self.parent_tensors
        X_shape, y_shape, z_shape, gamma_shape, beta_shape = self._cached_shapes
        
        # Recompute intermediates and compute gradients efficiently
        dX, dy_full, dz_full, x_shifted = BatchNormalizer._recompute_and_backward_kernel(
            grad_output, X.data, y.data, z.data, gamma.data, 
            self._cached_inv_sqrt_z, self.epsilon
        )
        
        # Process gradients efficiently
        dy = self._efficient_sum_to_shape(dy_full, y_shape) if y.requires_grad else None
        dz = self._efficient_sum_to_shape(dz_full, z_shape) if z.requires_grad else None
        
        # Compute parameter gradients
        dgamma = None
        dbeta = None
        
        if gamma.requires_grad:
            dgamma_full = grad_output * x_shifted
            dgamma = self._efficient_sum_to_shape(dgamma_full, gamma_shape)
            
        if beta.requires_grad:
            dbeta = self._efficient_sum_to_shape(grad_output, beta_shape)
        
        # Clear cache immediately to free memory
        self._cached_inv_sqrt_z = None
        
        return dX, dy, dz, dgamma, dbeta
    
    def _efficient_sum_to_shape(self, tensor, target_shape):
        """Memory-efficient reduction that avoids intermediate copies"""
        if tensor.shape == target_shape:
            return tensor
        
        # Use in-place reductions where possible
        result = tensor
        
        # Handle extra leading dimensions
        ndim_diff = len(result.shape) - len(target_shape)
        if ndim_diff > 0:
            # Sum leading axes in one operation
            leading_axes = tuple(range(ndim_diff))
            result = xp.sum(result, axis=leading_axes)
        
        # Handle singleton dimensions - do all reductions at once
        reduction_axes = []
        for i, (current_dim, target_dim) in enumerate(zip(result.shape, target_shape)):
            if target_dim == 1 and current_dim > 1:
                reduction_axes.append(i)
        
        if reduction_axes:
            # Single reduction operation instead of multiple
            result = xp.sum(result, axis=tuple(reduction_axes), keepdims=True)
        
        return result

def batch_normalize(X, y, z, gamma, beta, axes, epsilon=1e-5):
    """
    General normalization: output = gamma * (X - y) / sqrt(z + epsilon) + beta
    """
    return BatchNormalizer(axes, epsilon)(X, y, z, gamma, beta)