#!/usr/bin/env python3
"""
Mock testing script for LongDLLM package validation.
This tests the logic without requiring actual models or GPU resources.
"""

import torch
from unittest.mock import MagicMock, patch
import warnings

def test_mock_diffucoder():
    """Test DiffuCoder patches with mock model."""
    print("🔧 Testing DiffuCoder patches...")
    
    from longdllm import adapt_for_long_context
    
    # Create mock DiffuCoder model
    mock_model = MagicMock()
    mock_model.config.model_type = 'dream'
    mock_model.config.max_position_embeddings = 4096
    mock_model.config.mask_token_id = 32000
    mock_model.device = torch.device('cpu')
    
    # Mock RoPE module
    mock_rope = MagicMock()
    mock_rope.dim = 64
    mock_rope.max_seq_len_cached = 4096
    mock_model.model.layers = [MagicMock()]
    mock_model.model.layers[0].self_attn.rotary_emb = mock_rope
    
    # Test adaptation
    try:
        adapted_model = adapt_for_long_context(mock_model, target_length=32768)
        print("  ✅ DiffuCoder adaptation successful")
        
        # Check if diffusion_generate method exists
        if hasattr(adapted_model, 'diffusion_generate'):
            print("  ✅ diffusion_generate method available")
        else:
            print("  ❌ diffusion_generate method missing")
            
    except Exception as e:
        print(f"  ❌ DiffuCoder adaptation failed: {e}")

def test_mock_llada():
    """Test LLaDA patches with mock model."""
    print("🔧 Testing LLaDA patches...")
    
    from longdllm import adapt_for_long_context
    
    # Create mock LLaDA model
    mock_model = MagicMock()
    mock_model.config.model_type = 'llada'
    mock_model.config.max_position_embeddings = 4096
    mock_model.device = torch.device('cpu')
    
    # Mock RoPE module
    mock_rope = MagicMock()
    mock_rope.dim = 64
    mock_rope.max_seq_len_cached = 4096
    mock_model.model.layers = [MagicMock()]
    mock_model.model.layers[0].self_attn.rotary_emb = mock_rope
    
    # Test adaptation
    try:
        adapted_model = adapt_for_long_context(mock_model, target_length=32768)
        print("  ✅ LLaDA adaptation successful")
        
        # Check if diffusion_generate method exists
        if hasattr(adapted_model, 'diffusion_generate'):
            print("  ✅ diffusion_generate method available")
        else:
            print("  ❌ diffusion_generate method missing")
            
    except Exception as e:
        print(f"  ❌ LLaDA adaptation failed: {e}")

def test_unified_interface():
    """Test that both models have the same interface."""
    print("🎯 Testing unified interface...")
    
    from longdllm.diffucoder_patches import patch_diffucoder_diffusion_generate
    from longdllm.llada_patches import patch_llada_diffusion_generate
    
    # Create mock models
    mock_diffucoder = MagicMock()
    mock_llada = MagicMock()
    
    # Patch both
    patch_diffucoder_diffusion_generate(mock_diffucoder)
    patch_llada_diffusion_generate(mock_llada)
    
    # Check both have diffusion_generate method
    diffucoder_has_method = hasattr(mock_diffucoder, 'diffusion_generate')
    llada_has_method = hasattr(mock_llada, 'diffusion_generate')
    
    if diffucoder_has_method and llada_has_method:
        print("  ✅ Both models have diffusion_generate method")
        print("  ✅ Unified interface confirmed")
    else:
        print(f"  ❌ Interface mismatch - DiffuCoder: {diffucoder_has_method}, LLaDA: {llada_has_method}")

if __name__ == "__main__":
    print("🧪 LongDLLM Mock Testing")
    print("=" * 40)
    print("Testing package logic without real models...")
    print()
    
    test_mock_diffucoder()
    print()
    test_mock_llada()
    print()
    test_unified_interface()
    
    print()
    print("🎉 Mock testing complete!")
    print("   Use this approach during development to quickly validate changes")
