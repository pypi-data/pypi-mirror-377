"""
LongDLLM: Plug-and-play long context adaptation for diffusion language models.

This package provides easy-to-use functions for adapting DiffuCoder and LLaDA models
to support long-context inputs using advanced RoPE scaling techniques.
"""

__version__ = "0.1.0"
__author__ = "Albert Ge"
__email__ = "lbertge@gmail.com"

from .core import adapt_for_long_context
from .rope_classes import LongRoPEScaledRotaryEmbedding
from .diffucoder_patches import patch_diffucoder_diffusion_generate, DreamGenerationConfig, memory_efficient_diffusion_generate
from .llada_patches import patch_llada_forward_methods, patch_llada_diffusion_generate

__all__ = [
    "adapt_for_long_context",
    "LongRoPEScaledRotaryEmbedding",
    "patch_diffucoder_diffusion_generate",
    "DreamGenerationConfig", 
    "memory_efficient_diffusion_generate",
    "patch_llada_forward_methods",
    "patch_llada_diffusion_generate",
]
