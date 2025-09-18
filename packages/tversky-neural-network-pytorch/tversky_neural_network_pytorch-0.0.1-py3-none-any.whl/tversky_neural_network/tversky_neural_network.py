from __future__ import annotations
from typing import (
    Tuple,
    Union,
    Optional,
    Callable,
    Literal
)
import torch
from torch import (
    nn, 
    Tensor, 
)
from torch.nn import Module
from torch.nn import functional as F


def _tversky_prepare(
    a: Tensor,
    b: Tensor,
    feature_bank: Tensor,
    eps: float = 1e-8
) -> Tuple[Tensor, Tensor]:
    
    # sanity check
    if a.dim() != 2 or b.dim() != 2 or feature_bank.dim() != 2:
        raise ValueError("a, b, feature_banks must be 2D tensors")
    
    _N, d_a = a.shape
    _P, d_b = b.shape
    _F, d_f = feature_bank.shape
    
    if not (d_a == d_b == d_f):
        raise ValueError(f"Dimension mismatch: a:{d_a}, b:{d_b}, features:{d_f}")
    
    # normalize
    a_norm = F.normalize(a, dim=-1, eps=eps)                  
    b_norm = F.normalize(b, dim=-1, eps=eps)                  
    feature_norm = F.normalize(feature_bank, dim=-1, eps=eps)
    
    # calculate projection a·f_{k}, b·f_{k} => (N, F), (P, F)
    print(a_norm.device)
    print(feature_norm.device)
    print(feature_norm.T.device)
    a_norm_fk = a_norm @ feature_norm.T
    b_norm_fk = b_norm @ feature_norm.T

    # broadcasting
    _a = a_norm_fk.unsqueeze(1)  # (N, 1, F)
    _b = b_norm_fk.unsqueeze(0)  # (1, P, F)
    
    return _a, _b

def _tversky_intersection(
    a: Tensor,
    b: Tensor,
    psi: Union[str, Callable[[Tensor, Tensor], Tensor]] = "min",
    softmin_tau: float = 1.0,
    eps: float = 1e-8
) -> Tensor:
    # Eq. 3:  f(A ∩ B) dimension (N, P, F)
    # implement psi(min/max/product/mean/gmean/softmin)
    inter_mask = (a > 0) & (b > 0)
    a_masked = (a * inter_mask)
    b_masked = (b * inter_mask)

    if isinstance(psi, str):
        if psi == "min":
            inter_val = torch.minimum(a_masked, b_masked)
        elif psi == "max":
            inter_val = torch.maximum(a_masked, b_masked)    
        elif psi == "product":
            inter_val = a_masked*b_masked
        elif psi == "mean":
            inter_val = 0.5*(a_masked + b_masked)
        elif psi == "gmean":
            inter_val = torch.sqrt(torch.clamp(a_masked*b_masked, min=0.0) + eps)
        elif psi == "softmin":
            # use softmin-weighted average which support elementwise calculation
            w_a = torch.exp(-softmin_tau * a_masked)
            w_b = torch.exp(-softmin_tau * b_masked)
            denom = (w_a + w_b).clamp_min(eps)
            inter_val = (a_masked * w_a + b_masked * w_b) / denom
        else:
            raise ValueError(f"Unknown `psi` which found: {psi}. Please use one of them: ['min', 'max', 'product', 'mean', 'gmean', 'softmin']  or a callable.")
    elif callable(psi):
        inter_val = psi(a_masked, b_masked)
        if inter_val.shape != inter_mask.shape:
            raise ValueError(f"Callable psi must return a tensor of shape {inter_mask.shape}")
    else:
        raise TypeError(f"`psi` must be str or callable, which get {type(psi)} here.")
    return inter_val


def _tversky_difference(
    a: Tensor, 
    b: Tensor, 
    match_type: Literal["ignore", "subtract"]
) -> Tuple[Tensor, Tensor]:
    # f(A - B) & f(B - A) => both with dimensions (N, P, F)
    if match_type == "ignore":
        # Eq. 4
        diff_mask_a_b = (a > 0) & (b <= 0)
        diff_mask_b_a = (b > 0) & (a <= 0)
        diff_a_b = a * diff_mask_a_b
        diff_b_a = b * diff_mask_b_a
    elif match_type == "subtract": 
        # Eq. 5
        diff_mask_a_b = (a > 0) & (b > 0) & (a > b)
        diff_mask_b_a = (a > 0) & (b > 0) & (b > a)
        diff_a_b = a * diff_mask_a_b - b * diff_mask_a_b
        diff_b_a = b * diff_mask_b_a - a * diff_mask_b_a
    else:
        raise ValueError(f"Unknown match_type: {match_type}")
    
    return diff_a_b, diff_b_a

def tversky_similarity(
    a: Tensor,              
    b: Tensor,             
    feature_bank: Tensor,  
    alpha: Tensor = 0.5,
    beta: Tensor = 0.5,
    theta: Tensor = 1.0,
    psi: Union[str, Callable[[Tensor, Tensor], Tensor]] = "min",
    softmin_tau: float = 1.0,
    eps: float = 1e-8,
    match_type: Literal["ignore", "subtract"] = "subtract",
) -> Tensor:
    _a, _b = _tversky_prepare(a=a, b=b, feature_bank=feature_bank, eps=eps)
    inter_val = _tversky_intersection(a=_a, b=_b, psi=psi ,softmin_tau=softmin_tau, eps=eps)
    diff_a_b, diff_b_a = _tversky_difference(_a, _b, match_type)

    # sum over feature dimension
    inter_val = torch.sum(inter_val, dim=-1)
    diff_a_b = torch.sum(diff_a_b, dim=-1)
    diff_b_a = torch.sum(diff_b_a, dim=-1)
    
    # Eq. 2 calculate tversky similarity 
    similarity = theta * inter_val - alpha * diff_a_b - beta * diff_b_a
    
    return similarity

class TverskyProjectionLayer(Module):
    __doc__ = (
        r"""Applies a Tversky similarity projection to the incoming data."""
    )

    __constants__ = ["in_features", "out_features"]
    in_features: int
    out_features: int
    prototype: Tensor
    feature_bank: Tensor

    def __init__(
        self,
        in_features: int,
        out_features: int,
        num_features: Optional[int] = None,
        alpha: float = 0.5,
        beta: float = 0.5,
        theta: float = 1.0,
        eps: float = 1e-8,
        psi: Union[str, Callable[[Tensor, Tensor], Tensor]] = "min",
        softmin_tau: float = 1.0,
        match_type: Literal["ignore", "subtract"] = "subtract",
        device: Union[str, torch.device] = "cpu",
        dtype: torch.dtype = torch.float16,
    ) -> None:
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.num_features = num_features if num_features is not None else min(in_features, 64)
        
        # prototype (P, d)
        self.prototype = nn.Parameter(torch.empty(out_features, in_features, **factory_kwargs))

        # feature bank (F, d)
        self.feature_bank = nn.Parameter(torch.empty(num_features, in_features, **factory_kwargs))
        
        self._alpha = nn.Parameter(torch.log(torch.expm1(torch.tensor(alpha, **factory_kwargs))))
        self._beta = nn.Parameter(torch.log(torch.expm1(torch.tensor(beta, **factory_kwargs))))
        self._theta = nn.Parameter(torch.log(torch.expm1(torch.tensor(theta, **factory_kwargs))))

        self.eps = eps
        self.psi = psi
        self.softmin_tau = softmin_tau
        self.match_type = match_type

    @property
    def alpha(self) -> Tensor:
        """Tversky similarity parameter of f(A-B)."""
        return F.softplus(self._alpha)
    
    @property
    def beta(self) -> Tensor:
        """Tversky similarity parameter of f(B-A)."""
        return F.softplus(self._beta)
    
    @property
    def theta(self) -> Tensor:
        """Tversky similarity parameter of f(A∩B)."""
        return F.softplus(self._theta)
    
    def forward(self, input: Tensor) -> Tensor:
        return tversky_similarity(
            a=input, 
            b=self.prototype,
            feature_bank=self.feature_bank,
            alpha=self.alpha,
            beta=self.beta,
            theta=self.theta,
            match_type=self.match_type,
            psi=self.psi,
            softmin_tau=self.softmin_tau,
            eps=self.eps,
        )
        