"""
Core functionality for adapting diffusion language models for long context.
"""

import os
import numpy as np
import logging
from typing import Dict, Any, Union, Optional
import torch
from transformers import AutoModel, AutoConfig

from .rope_classes import LongRoPEScaledRotaryEmbedding
from .utils import get_model_info
from .diffucoder_patches import patch_diffucoder_diffusion_generate
from .llada_patches import patch_llada_forward_methods, patch_llada_diffusion_generate

logger = logging.getLogger(__name__)


def _load_optimized_rescale_factors(model_arch: str) -> list:
    """
    Load optimized rescale factors for specific model architectures.
    
    Args:
        model_arch (str): Model architecture ('dream' for DiffuCoder, 'llada' for LLaDA)
        
    Returns:
        list: Optimized rescale factors
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if model_arch == 'dream':
        factors_path = os.path.join(current_dir, 'data', 'diffucoder_rescale_factors.csv')
    elif model_arch == 'llada':
        factors_path = os.path.join(current_dir, 'data', 'llada_rescale_factors.csv')
    else:
        raise ValueError(f"No optimized factors available for architecture: {model_arch}")
    
    try:
        rescale_factors = np.loadtxt(open(factors_path, 'rb'), delimiter=',', skiprows=0)
        logger.info(f"Loaded {len(rescale_factors)} optimized rescale factors for {model_arch}")
        return rescale_factors
    except Exception as e:
        logger.warning(f"Failed to load optimized factors from {factors_path}: {e}")
        # Fallback to generic factors
        return np.array([1.0] * 64, dtype=np.float64)  # Default to 64 dimensions


def _detect_model_architecture(model) -> str:
    """
    Detect the model architecture type.
    
    Args:
        model: The loaded model
        
    Returns:
        str: Model architecture type ('llada' or 'dream')
    """
    config = model.config
    
    # Check model name first for accurate detection
    model_name = getattr(config, '_name_or_path', '').lower()
    if 'llada' in model_name:
        return 'llada'
    elif 'diffucoder' in model_name or 'dream' in model_name:
        return 'dream'
    
    # Check for LLaDA architecture first (more specific)
    if hasattr(config, 'is_llada') or (config.architectures and 'LLaDA' in str(config.architectures)):
        return 'llada'
    
    # Check for Dream architecture (DiffuCoder)
    if hasattr(config, 'is_dream') or (config.architectures and 'Dream' in str(config.architectures)):
        return 'dream'
    
    # Check architecture names for these specific models
    if hasattr(config, 'architectures') and config.architectures:
        arch_name = config.architectures[0].lower()
        if 'llada' in arch_name:
            return 'llada'
        elif 'dream' in arch_name:
            return 'dream'
    
    # Default based on known models (fallback)
    return 'dream'  # Default for DiffuCoder-like models


def _validate_model_support(model_name: str, config) -> bool:
    """
    Validate that the model is supported for long context adaptation.
    
    Args:
        model_name (str): Name/path of the model
        config: Model configuration
        
    Returns:
        bool: True if model is supported
    """
    supported_models = [
        'apple/DiffuCoder-7B-Instruct',
        'GSAI-ML/LLaDA-8B-Instruct'
    ]
    
    # Check exact model name matches
    if any(model_name == supported or model_name.endswith(supported) for supported in supported_models):
        return True
    
    # Check architecture compatibility
    arch = _detect_model_architecture(type('MockModel', (), {'config': config})())
    if arch in ['dream', 'llada']:
        logger.warning(f"Model {model_name} has compatible architecture ({arch}) but is not explicitly tested.")
        return True
    
    return False


def adapt_for_long_context(
    model,
    target_length: int = 32768,
    scaling_method: str = "longrope",
    rescale_factors: Optional[list] = None,
    magnitude_scaling: str = "su",
    **kwargs
) -> Any:
    """
    Adapt a diffusion language model for long context processing.
    
    This function modifies the model's RoPE embeddings in-place to support longer sequences.
    For DiffuCoder models, it also patches the diffusion_generate() method with memory-efficient generation.
    For LLaDA models, it patches forward methods and adds a diffusion_generate() interface for consistency.
    
    Args:
        model: The loaded model (from transformers library)
        target_length (int): Target sequence length. Defaults to 32768.
        scaling_method (str): Scaling method to use ('longrope' or 'ntk'). Defaults to 'longrope'.
        rescale_factors (list, optional): Custom rescale factors for LongRoPE. If None, uses optimized factors.
        magnitude_scaling (str): Magnitude scaling policy ('su' or 'yarn'). Defaults to 'su'.
        **kwargs: Additional arguments (unused in simplified version).
        
    Returns:
        The modified model (same object, modified in-place)
        
    Raises:
        ValueError: If model architecture is not supported or scaling method is invalid.
        RuntimeError: If RoPE replacement fails.
    """
    config = model.config
    
    # Validate model support
    model_name = getattr(config, '_name_or_path', 'unknown')
    if not _validate_model_support(model_name, config):
        raise ValueError(f"Model {model_name} is not supported. Supported models: apple/DiffuCoder-7B-Instruct, GSAI-ML/LLaDA-8B-Instruct")
    
    # Detect architecture
    model_arch = _detect_model_architecture(model)
    logger.info(f"Detected model architecture: {model_arch}")
    
    # Get model dimensions
    head_dim = config.hidden_size // config.num_attention_heads
    original_max_pos = getattr(config, 'max_position_embeddings', 4096)
    
    # Special handling for DiffuCoder models - set original_max_position_embeddings to 16k
    # Based on experimental results showing good performance up to 16k tokens
    if model_arch == 'dream':
        original_max_pos = 16384  # 16k tokens
        logger.info(f"DiffuCoder model detected: setting original_max_position_embeddings to {original_max_pos}")
    
    # Validate scaling method
    supported_methods = ['longrope', 'ntk']
    if scaling_method not in supported_methods:
        raise ValueError(f"Unsupported scaling method: {scaling_method}. Supported methods: {supported_methods}")
    
    # Calculate scale factor
    scale_factor = target_length / original_max_pos
    logger.info(f"Scaling from {original_max_pos} to {target_length} (factor: {scale_factor:.2f})")
    
    # Set default rescale factors for LongRoPE methods
    if rescale_factors is None and scaling_method == 'longrope':
        try:
            rescale_factors = _load_optimized_rescale_factors(model_arch)
            # Truncate or pad to match head dimension
            if len(rescale_factors) > head_dim//2:
                rescale_factors = rescale_factors[:head_dim//2]
                logger.info(f"Truncated rescale factors to {head_dim//2} dimensions")
            elif len(rescale_factors) < head_dim//2:
                # Pad with 1.0 if we need more factors
                rescale_factors.extend([1.0] * (head_dim//2 - len(rescale_factors)))
                logger.info(f"Padded rescale factors to {head_dim//2} dimensions")
        except Exception as e:
            logger.warning(f"Failed to load optimized factors: {e}. Using uniform scaling.")
            rescale_factors = [1.0 / scale_factor] * (head_dim // 2)
    
    # Replace RoPE in model layers
    success_count = 0
    total_layers = 0

    rope_args = {
        'original_max_position_embeddings': original_max_pos,
        'max_position_embeddings': target_length,
        'scale': scale_factor,
        'base': getattr(config, 'rope_embedding_base', getattr(config, 'rope_theta', None)),
        'model_type': model_arch,
    }
    
    try:
        # Detect model architecture and get blocks
        if model_arch == "llada":
            blocks = model.model.transformer.blocks
        elif model_arch == "dream":
            # Dream/DiffuCoder model structure
            if hasattr(model, 'layers'):
                blocks = model.layers
            elif hasattr(model, 'model') and hasattr(model.model, 'layers'):
                blocks = model.model.layers
            else:
                raise ValueError(f"Dream model detected but no layers found in model structure")
        else:
            raise ValueError(f"Unsupported model architecture: {model_arch}")
        
        total_layers = len(blocks)
        logger.info(f"Found {total_layers} layers in {model_arch} model")
        
        # Replace RoPE in each layer using architecture-specific logic
        if model_arch == "llada":
            for idx, layer in enumerate(blocks):
                if hasattr(layer, 'rotary_emb'):
                    # Create a new instance of our RoPE class for each layer
                    if scaling_method == "longrope":
                        layer_rope = LongRoPEScaledRotaryEmbedding(
                            dim=head_dim,
                            rescale_factors=rescale_factors,
                            magnitude_scaling_policy=magnitude_scaling,
                            **rope_args,
                            device=next(model.parameters()).device
                        )
                    elif scaling_method == "ntk":
                        # NTK uses modified base frequency
                        ntk_factor = scale_factor
                        new_base = getattr(config, 'rope_theta', 10000) * (ntk_factor ** (head_dim / (head_dim - 2)))
                        rescale_factors_ntk = [1.0] * (head_dim // 2)  # No rescaling for NTK
                        
                        layer_rope = LongRoPEScaledRotaryEmbedding(
                            dim=head_dim,
                            rescale_factors=rescale_factors_ntk,
                            max_position_embeddings=target_length,
                            original_max_position_embeddings=original_max_pos,
                            base=int(new_base),
                            magnitude_scaling_policy=magnitude_scaling,
                            model_type=model_arch,
                            device=next(model.parameters()).device
                        )
                    
                    # Replace the rotary embedding
                    layer.rotary_emb = layer_rope
                    success_count += 1
                    logger.info(f"Replaced RoPE in LLaDA layer {idx}")
                    
        elif model_arch == "dream":
            for idx, layer in enumerate(blocks):
                if hasattr(layer, 'self_attn') and hasattr(layer.self_attn, 'rotary_emb'):
                    # Create a new instance of our RoPE class for each layer
                    if scaling_method == "longrope":
                        layer_rope = LongRoPEScaledRotaryEmbedding(
                            dim=head_dim,
                            rescale_factors=rescale_factors,
                            magnitude_scaling_policy=magnitude_scaling,
                            **rope_args,
                            device=next(model.parameters()).device
                        )
                    else:
                        raise ValueError(f"Scaling method {scaling_method} not supported")
                    
                    # Replace the rotary embedding
                    layer.self_attn.rotary_emb = layer_rope
                    success_count += 1
                    logger.info(f"Replaced RoPE in Dream layer {idx}")
            
            # Also replace the model-level rotary_emb if it exists (Dream models)
            model_rotary_location = None
            if hasattr(model, 'rotary_emb'):
                model_rotary_location = model
            elif hasattr(model, 'model') and hasattr(model.model, 'rotary_emb'):
                model_rotary_location = model.model
                
            if model_rotary_location is not None:
                if scaling_method == "longrope":
                    model_rope = LongRoPEScaledRotaryEmbedding(
                        dim=head_dim,
                        rescale_factors=rescale_factors,
                        magnitude_scaling_policy=magnitude_scaling,
                        **rope_args,
                        device=next(model.parameters()).device
                    )
                else: 
                    raise ValueError(f"Scaling method {scaling_method} not supported")

                model_rotary_location.rotary_emb = model_rope
                success_count += 1
                logger.info("Replaced model-level RoPE for Dream model")
        
        if success_count == 0:
            logger.warning("No RoPE embeddings found to replace")
        else:
            logger.info(f"Successfully replaced {success_count}/{total_layers} RoPE embeddings")
            
        # Update model config
        config.max_position_embeddings = target_length
        logger.info(f"Updated model config max_position_embeddings to {target_length}")
        
        # Patch models with memory-efficient generation methods
        if model_arch == 'dream':
            patch_diffucoder_diffusion_generate(model)
            logger.info("Patched DiffuCoder model's diffusion_generate method with memory-efficient version")
        elif model_arch == 'llada':
            patch_llada_forward_methods(model)
            patch_llada_diffusion_generate(model)
            logger.info("Patched LLaDA model with memory-efficient forward methods and diffusion_generate interface")
        
    except Exception as e:
        raise RuntimeError(f"Failed to replace RoPE embeddings: {e}")
    
    return model
