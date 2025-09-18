"""
RoPE (Rotary Positional Embedding) implementations for long context adaptation.

Simplified version supporting only LongRoPE for DiffuCoder and LLaDA models.
"""

import math
import torch
from typing import Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


class LongRoPEScaledRotaryEmbedding(torch.nn.Module):
    """
    LongRoPE Scaled Rotary Positional Encoding class for Llama-like model.

    Args:
        dim (int): Head dimension.
        rescale_factors (list): List of rescale factors for each dimension.
        scale (float, optional): Length scale for code compatibility.
        max_position_embeddings (int, optional): Maximum number of position embeddings (after scaled).
        original_max_position_embeddings (int, optional): Original maximum number of position embeddings (before scaled).
        base (int, optional): Base value for the positional encoding. Defaults to 10000.
        magnitude_scaling_policy (str, optional): Attention temperature scaling function. Defaults to "su".
        device (torch.device, optional): Device on which to create the embedding. Defaults to None.
        force_fp32_rope (bool, optional): Whether to force FP32 calculations for rotary position embedding. Defaults to False.
    """

    def __init__(
        self,
        dim, 
        rescale_factors,
        scale=1.0,
        max_position_embeddings=4096,
        original_max_position_embeddings=4096,
        base=10000,
        magnitude_scaling_policy="su",
        model_type="llama",
        mscale_factors=None,
        device=None,
        force_fp32_rope=False,
    ):
        super().__init__()

        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.original_max_position_embeddings = original_max_position_embeddings
        self.base = base
        self.force_fp32_rope = force_fp32_rope

        if magnitude_scaling_policy == "su":
            calc_mscale = self._calc_mscale_su
        elif magnitude_scaling_policy == "yarn":
            calc_mscale = self._calc_mscale_yarn
        else:
            calc_mscale = lambda scale: float(magnitude_scaling_policy)
        if mscale_factors is None:
            self.mscale = calc_mscale(self.max_position_embeddings / self.original_max_position_embeddings)
        else:
            self.mscale = torch.tensor([*mscale_factors, *mscale_factors], dtype=torch.float32, device=device)

        self.rescale_factors = torch.tensor(rescale_factors, dtype=torch.float32, device=device)
        assert self.rescale_factors.shape == (self.dim // 2, ), \
            f"misaligned shape for LongRoPE rescale factors: {self.rescale_factors.shape}"

        if model_type == "llama":
            self.forward = self._forward_llama
        elif model_type == "mistral":
            self.forward = self._forward_mistral
            self.register_buffer("inv_freq", self._calc_inv_freq(max_position_embeddings, device))
        elif model_type == "llada":
            self.forward = self._forward_llada
        elif model_type == "dream":
            # Dream/DiffuCoder models use their own RoPE implementation with attention scaling
            self.forward = self._forward_dream
        else:
            raise ValueError(f"Unsupported model type for LongRoPE: {model_type}")

    def _calc_mscale_su(self, scale):
        if scale <= 1.0:
            return 1.0
        return math.sqrt(1 + math.log(scale) / math.log(self.original_max_position_embeddings))

    def _calc_mscale_yarn(self, scale):
        if scale <= 1.0:
            return 1.0
        return 0.1 * math.log(scale) + 1.0

    def _calc_inv_freq(self, seq_len, device):
        rescale_factors = self.rescale_factors.to(device)
        exponent = torch.arange(0, self.dim, 2, dtype=torch.float32, device=device) / self.dim
        return 1.0 / (rescale_factors * (self.base ** exponent))

    @torch.no_grad()
    def _forward_mistral(self, x, seq_len=None):
        seq_len = x.shape[-2] if seq_len is None else seq_len
        t = torch.arange(seq_len, device=x.device, dtype=torch.float32)
        inv_freq = self.inv_freq.to(x.device)
        freqs = torch.outer(t, inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        return (emb.cos() * self.mscale).to(x.dtype), (emb.sin() * self.mscale).to(x.dtype)

    @torch.no_grad()
    def _forward_llama(self, x, position_ids, seq_len=None):
        seq_len = x.shape[-2] if seq_len is None else seq_len
        inv_freq = self._calc_inv_freq(seq_len, x.device)
        inv_freq_expanded = inv_freq[None, :, None].float().expand(position_ids.shape[0], -1, 1)
        position_ids_expanded = position_ids[:, None, :].float()

        # Force float32 since bfloat16 loses precision on long contexts
        # See https://github.com/huggingface/transformers/pull/29285
        device_type = x.device.type
        device_type = device_type if isinstance(device_type, str) and device_type != "mps" else "cpu"
        with torch.autocast(device_type=device_type, enabled=False):
            freqs = (inv_freq_expanded.float() @ position_ids_expanded.float()).transpose(1, 2)
            emb = torch.cat((freqs, freqs), dim=-1)
            cos = emb.cos() * self.mscale
            sin = emb.sin() * self.mscale
        return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)

    @torch.no_grad()
    def _forward_dream(self, x, position_ids, seq_len=None):
        """
        Forward pass for Dream/DiffuCoder models - similar to LLaMA but with attention_scaling.
        
        This method replicates the behavior of DreamRotaryEmbedding.forward() from the
        Dream model implementation, which includes attention scaling factors.
        """
        seq_len = x.shape[-2] if seq_len is None else seq_len
        inv_freq = self._calc_inv_freq(seq_len, x.device)

        # Core RoPE block - matches Dream implementation exactly
        inv_freq_expanded = inv_freq[None, :, None].float().expand(position_ids.shape[0], -1, 1)
        position_ids_expanded = position_ids[:, None, :].float()
        
        # Force float32 since bfloat16 loses precision on long contexts
        # See https://github.com/huggingface/transformers/pull/29285
        device_type = x.device.type
        device_type = device_type if isinstance(device_type, str) and device_type != "mps" else "cpu"
        with torch.autocast(device_type=device_type, enabled=False):
            freqs = (inv_freq_expanded.float() @ position_ids_expanded.float()).transpose(1, 2)
            emb = torch.cat((freqs, freqs), dim=-1)
            cos = emb.cos()
            sin = emb.sin()

        # Apply magnitude scaling and attention scaling (key difference from LLaMA)
        cos = cos * self.mscale
        sin = sin * self.mscale
        
        return cos.to(dtype=x.dtype), sin.to(dtype=x.dtype)

    def rotate_half(self, x: torch.Tensor) -> torch.Tensor:
        """Rotates half the hidden dims of the input for LLaDA format."""
        B, nh, T, hs = x.size()
        x = x.view(B, nh, T, 2, hs // 2)
        x1, x2 = x.unbind(dim=-2)
        return torch.cat((-x2, x1), dim=-1)

    def apply_rotary_pos_emb(self, pos_sin: torch.Tensor, pos_cos: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """Apply rotary position embedding for LLaDA format."""
        return ((t * pos_cos) + (self.rotate_half(t) * pos_sin)).to(t.dtype)

    @torch.no_grad()
    def _forward_llada(self, q: torch.Tensor, k: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass for LLaDA model - takes q,k tensors and returns rotated q,k tensors.
        
        Args:
            q: Query tensor of shape (B, nh, T, hs)
            k: Key tensor of shape (B, n_kv_h, T, hs)
            
        Returns:
            Tuple of (rotated_q, rotated_k)
        """
        # Get sequence length from the tensors
        query_len, key_len = q.shape[-2], k.shape[-2]
        seq_len = max(query_len, key_len)
        
        # Calculate inverse frequencies with rescaling
        inv_freq = self._calc_inv_freq(seq_len, q.device)
        
        # Create position sequence
        positions = torch.arange(key_len, device=q.device, dtype=torch.float32)
        
        # Force float32 for precision
        device_type = q.device.type
        device_type = device_type if isinstance(device_type, str) and device_type != "mps" else "cpu"
        
        with torch.autocast(device_type=device_type, enabled=False):
            # Calculate frequencies
            freqs = torch.outer(positions, inv_freq)
            emb = torch.cat((freqs, freqs), dim=-1)
            
            if self.force_fp32_rope:
                # Get sin/cos embeddings with magnitude scaling - keep in FP32
                pos_sin = (emb.sin() * self.mscale)[None, None, :, :]
                pos_cos = (emb.cos() * self.mscale)[None, None, :, :]
                
                # Apply to query (handle different sequence lengths)
                if query_len != key_len:
                    q_pos_sin = pos_sin[:, :, key_len - query_len:key_len, :]
                    q_pos_cos = pos_cos[:, :, key_len - query_len:key_len, :]
                else:
                    q_pos_sin = pos_sin
                    q_pos_cos = pos_cos
                
                # Convert q and k to FP32 for rotary embedding application
                q_fp32 = q.float()
                k_fp32 = k.float()
                    
                # Apply rotary embeddings in FP32
                q_rotated_fp32 = self.apply_rotary_pos_emb(q_pos_sin, q_pos_cos, q_fp32)
                k_rotated_fp32 = self.apply_rotary_pos_emb(pos_sin, pos_cos, k_fp32)
                
                # Convert back to original dtypes
                q_rotated = q_rotated_fp32.to(q.dtype)
                k_rotated = k_rotated_fp32.to(k.dtype)
            else:
                # Original behavior - use input tensor dtype
                pos_sin = (emb.sin() * self.mscale)[None, None, :, :].to(q.dtype)
                pos_cos = (emb.cos() * self.mscale)[None, None, :, :].to(q.dtype)
                
                # Apply to query (handle different sequence lengths)
                if query_len != key_len:
                    q_pos_sin = pos_sin[:, :, key_len - query_len:key_len, :]
                    q_pos_cos = pos_cos[:, :, key_len - query_len:key_len, :]
                else:
                    q_pos_sin = pos_sin
                    q_pos_cos = pos_cos
                    
                # Apply rotary embeddings
                q_rotated = self.apply_rotary_pos_emb(q_pos_sin, q_pos_cos, q)
                k_rotated = self.apply_rotary_pos_emb(pos_sin, pos_cos, k)
            
        return q_rotated, k_rotated
