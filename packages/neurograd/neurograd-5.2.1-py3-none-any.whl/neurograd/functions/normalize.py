import neurograd as ng
from neurograd import xp
from neurograd.nn.module import Module
from neurograd.functions.base import Function
import math





import cupy as cp
# CUDA kernel for BatchNorm backward pass
batchnorm_backward_kernel = cp.RawKernel(r'''
extern "C" __global__
void batchnorm_backward(
    const float* dout,
    const float* x,
    const float* mean_scaler,
    const float* std_scaler,
    const float* x_mean,
    const float* x_std,
    float* dx,
    float* dmean_scaler,
    float* dstd_scaler,
    float* temp_sums,  // temporary storage for reductions
    int batch_size,
    int channels,
    int spatial_size,
    int total_size,
    float inv_N,
    bool memsave,
    bool need_dx,
    bool need_dmean,
    bool need_dstd,
    bool axis_0_only
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int c = blockIdx.y;
    
    if (c >= channels) return;
    
    // Shared memory for reductions
    extern __shared__ float sdata[];
    float* s_sum1 = sdata;
    float* s_sum2 = &sdata[blockDim.x];
    float* s_sum3 = &sdata[2 * blockDim.x];
    
    int lane = threadIdx.x;
    float sum1 = 0.0f, sum2 = 0.0f, sum3 = 0.0f;
    
    float std_val = std_scaler[c];
    float inv_std = 1.0f / x_std[c];
    
    // Each thread processes multiple elements
    int elements_per_channel = axis_0_only ? batch_size : (batch_size * spatial_size);
    int stride = blockDim.x * gridDim.x;
    
    for (int i = tid; i < elements_per_channel; i += stride) {
        int idx;
        if (axis_0_only) {
            idx = i * channels + c;  // (N, C) layout
        } else {
            int n = i / spatial_size;
            int s = i % spatial_size;
            idx = n * channels * spatial_size + c * spatial_size + s;  // (N, C, H, W) layout
        }
        
        if (idx < total_size) {
            float x_val = x[idx];
            float dout_val = dout[idx];
            
            // Calculate x_hat
            float x_hat;
            if (memsave) {
                x_hat = (x_val - mean_scaler[c]) * inv_std;
            } else {
                x_hat = (x_val - x_mean[c]) * inv_std;
            }
            
            // Accumulate sums for gradients
            if (need_dmean) sum1 += dout_val;
            if (need_dstd) sum2 += dout_val * x_hat;
            if (need_dx) sum3 += dout_val * x_hat;
        }
    }
    
    // Block-level reductions
    s_sum1[lane] = sum1;
    s_sum2[lane] = sum2;
    s_sum3[lane] = sum3;
    __syncthreads();
    
    // Parallel reduction within block
    for (int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (lane < s) {
            s_sum1[lane] += s_sum1[lane + s];
            s_sum2[lane] += s_sum2[lane + s];
            s_sum3[lane] += s_sum3[lane + s];
        }
        __syncthreads();
    }
    
    // Store block results
    if (lane == 0) {
        int block_idx = blockIdx.x + c * gridDim.x;
        temp_sums[block_idx] = s_sum1[0];
        temp_sums[block_idx + channels * gridDim.x] = s_sum2[0];
        temp_sums[block_idx + 2 * channels * gridDim.x] = s_sum3[0];
    }
}
''', 'batchnorm_backward')

# Reduction kernel to sum across blocks
reduction_kernel = cp.RawKernel(r'''
extern "C" __global__
void reduce_blocks(
    const float* temp_sums,
    float* dmean_scaler,
    float* dstd_scaler,
    float* sum_dx_hat_x_hat,
    int channels,
    int num_blocks,
    bool need_dmean,
    bool need_dstd
) {
    int c = blockIdx.x * blockDim.x + threadIdx.x;
    if (c >= channels) return;
    
    float sum1 = 0.0f, sum2 = 0.0f, sum3 = 0.0f;
    for (int b = 0; b < num_blocks; b++) {
        sum1 += temp_sums[b + c * num_blocks];
        sum2 += temp_sums[b + c * num_blocks + channels * num_blocks];
        sum3 += temp_sums[b + c * num_blocks + 2 * channels * num_blocks];
    }
    
    if (need_dmean) dmean_scaler[c] = sum1;
    if (need_dstd) dstd_scaler[c] = sum2;
    sum_dx_hat_x_hat[c] = sum3;
}
''', 'reduce_blocks')

# Final dx computation kernel
dx_kernel = cp.RawKernel(r'''
extern "C" __global__
void compute_dx(
    const float* dout,
    const float* x,
    const float* mean_scaler,
    const float* std_scaler,
    const float* x_mean,
    const float* x_std,
    const float* sum_dx_hat,
    const float* sum_dx_hat_x_hat,
    float* dx,
    int batch_size,
    int channels,
    int spatial_size,
    int total_size,
    float inv_N,
    bool memsave,
    bool axis_0_only
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= total_size) return;
    
    int c;
    if (axis_0_only) {
        c = idx % channels;  // (N, C) layout
    } else {
        int spatial_idx = idx % spatial_size;
        int temp = (idx - spatial_idx) / spatial_size;
        c = temp % channels;  // (N, C, H, W) layout
    }
    
    float x_val = x[idx];
    float dout_val = dout[idx];
    float std_val = std_scaler[c];
    float inv_std = 1.0f / x_std[c];
    
    // Calculate x_hat
    float x_hat;
    if (memsave) {
        x_hat = (x_val - mean_scaler[c]) * inv_std;
    } else {
        x_hat = (x_val - x_mean[c]) * inv_std;
    }
    
    float dx_hat = dout_val * std_val;
    float dx_val = inv_N * inv_std * (
        batch_size * spatial_size * dx_hat
        - sum_dx_hat[c]
        - x_hat * sum_dx_hat_x_hat[c]
    );
    
    dx[idx] = dx_val;
}
''', 'compute_dx')

def fast_batchnorm_backward(dout, x, mean_scaler, std_scaler, x_mean, x_std, 
                           axis, N, memsave, requires_grad):
    """
    Fast CUDA implementation of BatchNorm backward pass
    
    Args:
        axis: int (0) or tuple (0,2,3) for reduction axes
    """
    axis_0_only = (axis == 0) or (axis == (0,))
    
    if axis_0_only:
        batch_size, channels = x.shape
        spatial_size = 1
    else:  # axis == (0,2,3)
        batch_size, channels, h, w = x.shape
        spatial_size = h * w
    
    total_size = x.size
    inv_N = 1.0 / N
    
    # Grid and block dimensions
    block_size = 256
    num_blocks = min(32, (batch_size * spatial_size + block_size - 1) // block_size)
    grid_dim = (num_blocks, channels)
    shared_mem = 3 * block_size * 4  # 3 float arrays
    
    # Allocate temporary storage and outputs
    temp_sums = cp.zeros((3 * channels * num_blocks,), dtype=cp.float32)
    
    dx = cp.zeros_like(x) if requires_grad[0] else None
    dmean_scaler = cp.zeros((channels,), dtype=cp.float32) if requires_grad[1] else None
    dstd_scaler = cp.zeros((channels,), dtype=cp.float32) if requires_grad[2] else None
    sum_dx_hat_x_hat = cp.zeros((channels,), dtype=cp.float32)
    
    # Launch main kernel
    batchnorm_backward_kernel(
        grid_dim, (block_size,), shared_mem,
        (dout, x, mean_scaler, std_scaler, x_mean, x_std,
         dx, dmean_scaler, dstd_scaler, temp_sums,
         batch_size, channels, spatial_size, total_size, inv_N,
         memsave, requires_grad[0], requires_grad[1], requires_grad[2], axis_0_only)
    )
    
    # Reduce across blocks
    reduction_blocks = (channels + block_size - 1) // block_size
    reduction_kernel(
        (reduction_blocks,), (block_size,),
        (temp_sums, dmean_scaler, dstd_scaler, sum_dx_hat_x_hat,
         channels, num_blocks, requires_grad[1], requires_grad[2])
    )
    
    # Compute final dx if needed
    if requires_grad[0]:
        dx_blocks = (total_size + block_size - 1) // block_size
        dx_kernel(
            (dx_blocks,), (block_size,),
            (dout, x, mean_scaler, std_scaler, x_mean, x_std,
             dmean_scaler if dmean_scaler is not None else temp_sums,  # reuse temp if dmean not needed
             sum_dx_hat_x_hat, dx,
             batch_size, channels, spatial_size, total_size, inv_N,
             memsave, axis_0_only)
        )
    
    return dx, dmean_scaler, dstd_scaler





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

    # Usage in your backward function:
    def backward(self, dout):
        x = self.parent_tensors[0].data
        mean_scaler = self.parent_tensors[1].data
        std_scaler = self.parent_tensors[2].data
        
        requires_grad = [t.requires_grad for t in self.parent_tensors]
        
        return fast_batchnorm_backward(
            dout, x, mean_scaler, std_scaler, 
            self.x_mean, self.x_std, self.axis, self.N, 
            self.memsave, requires_grad
        )

def batch_normalize(X, mean_scaler, var_scaler, axis, eps=1e-5, memsave=False):
    return BatchNormalizer(axis, eps, memsave)(X, mean_scaler, var_scaler)





# Usage in your backward function:
def backward(self, dout):
    x = self.parent_tensors[0].data
    mean_scaler = self.parent_tensors[1].data
    std_scaler = self.parent_tensors[2].data
    
    requires_grad = [t.requires_grad for t in self.parent_tensors]
    
    return fast_batchnorm_backward(
        dout, x, mean_scaler, std_scaler, 
        self.x_mean, self.x_std, self.axis, self.N, 
        self.memsave, requires_grad
    )