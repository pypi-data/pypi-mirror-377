import neurograd as ng
from neurograd import xp
from .base import Function

class BatchNormalizer(Function):
    """
    General normalization: output = gamma * (X - y) / sqrt(z + eps) + beta
    
    Computes independent gradients for X, y, z treating each as separate variables.
    """
    name = "BatchNormalizer"
    
    @ng.fuse
    def _forward_kernel(X, y, z, gamma, beta, eps):
        inv_sqrt_z = 1.0 / xp.sqrt(z + eps)
        x_minus_y = X - y
        x_shifted = x_minus_y * inv_sqrt_z
        output = gamma * x_shifted + beta
        return output, x_shifted, inv_sqrt_z, x_minus_y
    
    @ng.fuse  
    def _backward_kernel(grad_output, gamma, x_shifted, inv_sqrt_z, x_minus_y):
        dL_dx_shifted = grad_output * gamma
        dX = dL_dx_shifted * inv_sqrt_z
        dy = -dL_dx_shifted * inv_sqrt_z
        inv_sqrt_z_cubed = inv_sqrt_z * inv_sqrt_z * inv_sqrt_z
        dz = dL_dx_shifted * x_minus_y * (-0.5) * inv_sqrt_z_cubed
        return dX, dy, dz, dL_dx_shifted
    
    @ng.fuse
    def _param_grad_kernel(grad_output, x_shifted):
        return grad_output * x_shifted, grad_output
    
    def __init__(self, axes, epsilon: float = 1e-5):
        super().__init__()
        self.axes = axes if isinstance(axes, tuple) else (axes,)
        self.epsilon = float(epsilon)
        self._cached_x_shifted = None
        self._cached_inv_sqrt_z = None
        self._cached_x_minus_y = None
        self._cached_shapes = None
    
    def forward(self, X: xp.ndarray, y: xp.ndarray, z: xp.ndarray,
                gamma: xp.ndarray, beta: xp.ndarray) -> xp.ndarray:
        
        output, x_shifted, inv_sqrt_z, x_minus_y = BatchNormalizer._forward_kernel(
            X, y, z, gamma, beta, self.epsilon
        )
        
        self._cached_x_shifted = x_shifted
        self._cached_inv_sqrt_z = inv_sqrt_z  
        self._cached_x_minus_y = x_minus_y
        self._cached_shapes = (X.shape, y.shape, z.shape, gamma.shape, beta.shape)
        
        return output
    
    def backward(self, grad_output: xp.ndarray):
        X, y, z, gamma, beta = self.parent_tensors
        X_shape, y_shape, z_shape, gamma_shape, beta_shape = self._cached_shapes
        
        dX, dy_full, dz_full, dL_dx_shifted = BatchNormalizer._backward_kernel(
            grad_output, gamma, self._cached_x_shifted, 
            self._cached_inv_sqrt_z, self._cached_x_minus_y
        )
        
        dy = None
        if y.requires_grad:
            dy = self._sum_to_shape(dy_full, y_shape)
            
        dz = None  
        if z.requires_grad:
            dz = self._sum_to_shape(dz_full, z_shape)
        
        dgamma, dbeta = None, None
        if gamma.requires_grad or beta.requires_grad:
            if gamma.requires_grad and beta.requires_grad:
                dgamma_full, dbeta_full = self._param_grad_kernel(grad_output, self._cached_x_shifted)
                dgamma = self._sum_to_shape(dgamma_full, gamma_shape)
                dbeta = self._sum_to_shape(dbeta_full, beta_shape)
            else:
                if gamma.requires_grad:
                    dgamma_full = grad_output * self._cached_x_shifted
                    dgamma = self._sum_to_shape(dgamma_full, gamma_shape)
                if beta.requires_grad:
                    dbeta = self._sum_to_shape(grad_output, beta_shape)
        
        return dX, dy, dz, dgamma, dbeta
    
    def _sum_to_shape(self, tensor, target_shape):
        if tensor.shape == target_shape:
            return tensor
        
        result = tensor
        
        ndim_diff = len(result.shape) - len(target_shape)
        if ndim_diff > 0:
            leading_axes = tuple(range(ndim_diff))
            result = xp.sum(result, axis=leading_axes)
        
        reduction_axes = []
        for i, (current_dim, target_dim) in enumerate(zip(result.shape, target_shape)):
            if target_dim == 1 and current_dim > 1:
                reduction_axes.append(i)
        
        if reduction_axes:
            result = xp.sum(result, axis=tuple(reduction_axes), keepdims=True)
        
        return result


def batch_normalize(X, y, z, gamma, beta, axes, epsilon=1e-5):
    """
    General normalization: output = gamma * (X - y) / sqrt(z + epsilon) + beta
    """
    return BatchNormalizer(axes, epsilon)(X, y, z, gamma, beta)