import neurograd as ng
from neurograd import xp
from neurograd.nn.module import Module
from neurograd.functions.normalize import BatchNormalizer

# @ng.fuse

def exp_mov_avg(old, new, momentum): # ndarrays
    # new_running = momentum*old + (1-momentum)*new
    return momentum * old + (1.0 - momentum) * new


class BatchNorm(Module):
    """
    BN for inputs shaped (N, C)
    """
    def __init__(self, num_features: int, batch_momentum: float = 0.9, epsilon: float = 1e-5):
        super().__init__()
        self.num_features = int(num_features)
        self.batch_momentum = float(batch_momentum)
        self.epsilon = float(epsilon)
        # Learnable scale/shift
        self.add_parameter("mean_scaler", ng.zeros((1, num_features), dtype=ng.float32, requires_grad=True)) # beta
        self.add_parameter("std_scaler",  ng.ones((1, num_features), dtype=ng.float32, requires_grad=True))  # gamma
        # Running stats (buffers, no grad)
        self.add_buffer("running_mean", ng.zeros((1, num_features), dtype=ng.float32, requires_grad=False))
        self.add_buffer("running_std",  ng.ones((1, num_features), dtype=ng.float32, requires_grad=False))
        # Pre-create the op with the right axes
        self._bn_op = BatchNormalizer(axis=(0,), eps=self.epsilon)

    def forward(self, X):
        from neurograd import Tensor
        if self.training:
            out = self._bn_op(X, self.mean_scaler, self.std_scaler)
            # Update running stats (on .data to avoid autograd tracking)
            self.running_mean.data[:] = exp_mov_avg(self.running_mean.data, self._bn_op.x_mean, self.batch_momentum)
            self.running_std.data[:]  = exp_mov_avg(self.running_std.data,  self._bn_op.x_std,  self.batch_momentum)
        else:
            # Detached affine transform using running stats
            out = self._bn_op._affine(X.data, self.running_mean.data, 
                                      self.running_std.data, self.mean_scaler.data, self.std_scaler.data)
            return Tensor(out)
        return out



class BatchNorm2D(Module):
    """
    BN for NCHW inputs (N, C, H, W)
    """
    def __init__(self, num_features: int, batch_momentum: float = 0.9, epsilon: float = 1e-5):
        super().__init__()
        self.num_features = int(num_features)
        self.batch_momentum = float(batch_momentum)
        self.epsilon = float(epsilon)
        shape = (1, num_features, 1, 1)
        # Learnable scale/shift
        self.add_parameter("mean_scaler", ng.zeros(shape, dtype=ng.float32, requires_grad=True))  # beta
        self.add_parameter("std_scaler",  ng.ones(shape, dtype=ng.float32, requires_grad=True))   # gamma
        # Running stats
        self.add_buffer("running_mean", ng.zeros(shape, dtype=ng.float32, requires_grad=False))
        self.add_buffer("running_std",  ng.ones(shape,  dtype=ng.float32, requires_grad=False))
        # Axes over which per-channel stats are computed: (N, H, W)
        self._bn_op = BatchNormalizer(axis=(0, 2, 3), eps=self.epsilon)
    
    def forward(self, X):
        from neurograd import Tensor
        if self.training:
            out = self._bn_op(X, self.mean_scaler, self.std_scaler)
            # Update running stats (on .data to avoid autograd tracking)
            self.running_mean.data[:] = exp_mov_avg(self.running_mean.data, self._bn_op.x_mean, self.batch_momentum)
            self.running_std.data[:]  = exp_mov_avg(self.running_std.data,  self._bn_op.x_std,  self.batch_momentum)
        else:
            # Detached affine transform using running stats
            out = self._bn_op._affine(X.data, self.running_mean.data, 
                                      self.running_std.data, self.mean_scaler.data, self.std_scaler.data)
            return Tensor(out)
        return out