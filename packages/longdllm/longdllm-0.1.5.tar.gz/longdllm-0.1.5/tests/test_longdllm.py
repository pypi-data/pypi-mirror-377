"""
Tests for LongDLLM package.
"""

import pytest
import torch
from unittest.mock import Mock, patch

from longdllm import adapt_for_long_context
from longdllm.core import _detect_model_architecture, _validate_model_support


class TestLongDLLM:
    """Test cases for LongDLLM functionality."""
    
    def test_validate_model_support(self):
        """Test model support validation."""
        # Mock config for supported models
        mock_config = Mock()
        mock_config.architectures = ['DreamForCausalLM']
        
        # Should return True for supported model
        result = _validate_model_support("apple/DiffuCoder-7B-Instruct", mock_config)
        assert result is True
        
        # Mock config for LLaDA
        mock_config_llada = Mock()
        mock_config_llada.architectures = ['LLaDAForCausalLM']
        
        result = _validate_model_support("GSAI-ML/LLaDA-8B-Instruct", mock_config_llada)
        assert result is True
        
        # Should return False for unsupported model
        mock_config_unsupported = Mock()
        mock_config_unsupported.architectures = ['GPTForCausalLM']
        
        result = _validate_model_support("openai/gpt-3.5", mock_config_unsupported)
        assert result is False
        
    def test_detect_model_architecture_llada(self):
        """Test LLaDA architecture detection."""
        # Mock LLaDA model structure
        mock_model = Mock()
        mock_model.config = Mock()
    def test_detect_model_architecture_llada(self):
        """Test LLaDA architecture detection."""
        # Mock LLaDA model structure  
        mock_model = Mock()
        mock_model.config = Mock()
        mock_model.config.architectures = ['LLaDAForCausalLM']
        
        arch = _detect_model_architecture(mock_model)
        assert arch == "llada"
    
    def test_detect_model_architecture_dream(self):
        """Test Dream/DiffuCoder architecture detection."""
        # Mock Dream model structure
        mock_model = Mock()
        mock_model.config = Mock()
        mock_model.config.architectures = ['DreamForCausalLM']
        
        arch = _detect_model_architecture(mock_model)
        assert arch == "dream"


class TestRoPEClasses:
    """Test RoPE embedding classes."""
    
    def test_longrope_initialization(self):
        """Test LongRoPE initialization."""
        from longdllm.rope_classes import LongRoPEScaledRotaryEmbedding
        
        dim = 64
        rescale_factors = torch.ones(dim // 2) * 0.5
        
        rope = LongRoPEScaledRotaryEmbedding(
            dim=dim,
            rescale_factors=rescale_factors,
            max_position_embeddings=8192,
            original_max_position_embeddings=2048,
            model_type="dream"
        )
        
        assert rope.dim == dim
        assert rope.max_position_embeddings == 8192
        assert rope.original_max_position_embeddings == 2048
        assert rope.model_type == "dream"
        
    def test_longrope_unsupported_model_type(self):
        """Test that unsupported model types raise errors."""
        from longdllm.rope_classes import LongRoPEScaledRotaryEmbedding
        
        dim = 64
        rescale_factors = torch.ones(dim // 2) * 0.5
        
        with pytest.raises(ValueError, match="Unsupported model type"):
            LongRoPEScaledRotaryEmbedding(
                dim=dim,
                rescale_factors=rescale_factors,
                model_type="unsupported_type"
            )
