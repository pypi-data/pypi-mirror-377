"""
Tests for memory-efficient generation functionality.
"""

import unittest
from unittest.mock import MagicMock, patch
import torch

try:
    from longdllm.diffucoder_patches import (
        patch_diffucoder_diffusion_generate, 
        DreamGenerationConfig,
        memory_efficient_diffusion_generate
    )
    from longdllm.llada_patches import (
        patch_llada_forward_methods,
        patch_llada_diffusion_generate
    )
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


@unittest.skipIf(not IMPORTS_AVAILABLE, "Generation dependencies not available")
class TestDiffuCoderPatches(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock model
        self.mock_model = MagicMock()
        self.mock_model.device = torch.device('cpu')
        self.mock_model.config = MagicMock()
        self.mock_model.config.max_position_embeddings = 4096
        self.mock_model.config.bos_token_id = 1
        self.mock_model.config.eos_token_id = 2
        self.mock_model.config.pad_token_id = 0
        self.mock_model.config.mask_token_id = 32000
    
    def test_dream_generation_config_creation(self):
        """Test DreamGenerationConfig creation with default values."""
        config = DreamGenerationConfig()
        
        self.assertEqual(config.temperature, 0.0)
        self.assertIsNone(config.top_p)
        self.assertIsNone(config.top_k)
        self.assertEqual(config.max_length, 20)
        self.assertEqual(config.eps, 1e-3)
        self.assertEqual(config.steps, 512)
        self.assertEqual(config.alg, 'origin')
    
    def test_dream_generation_config_custom_values(self):
        """Test DreamGenerationConfig creation with custom values."""
        config = DreamGenerationConfig(
            temperature=0.7,
            top_p=0.9,
            max_new_tokens=256,
            steps=128
        )
        
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.top_p, 0.9)
        self.assertEqual(config.max_new_tokens, 256)
        self.assertEqual(config.steps, 128)
    
    def test_patch_diffucoder_diffusion_generate(self):
        """Test that patch_diffucoder_diffusion_generate replaces the diffusion_generate method."""
        # Add a mock diffusion_generate method
        self.mock_model.diffusion_generate = MagicMock(return_value="original")
        original_diffusion_generate = self.mock_model.diffusion_generate
        
        # Patch the model
        patched_model = patch_diffucoder_diffusion_generate(self.mock_model)
        
        # Check that the model is the same object (in-place modification)
        self.assertIs(patched_model, self.mock_model)
        
        # Check that the diffusion_generate method has been replaced
        self.assertIsNot(self.mock_model.diffusion_generate, original_diffusion_generate)
    
    @patch('longdllm.diffucoder_patches.memory_efficient_diffusion_generate')
    def test_patched_diffusion_generate_calls_memory_efficient(self, mock_efficient_generate):
        """Test that the patched diffusion_generate method calls memory_efficient_diffusion_generate."""
        # Patch the model
        patch_diffucoder_diffusion_generate(self.mock_model)
        
        # Mock inputs
        input_ids = torch.tensor([[1, 2, 3, 4]])
        attention_mask = torch.tensor([[1, 1, 1, 1]])
        
        # Call the patched diffusion_generate method
        self.mock_model.diffusion_generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=10,
            temperature=0.7
        )
        
        # Verify that memory_efficient_diffusion_generate was called
        mock_efficient_generate.assert_called_once()
        call_args = mock_efficient_generate.call_args
        self.assertEqual(call_args.kwargs['model'], self.mock_model)
        self.assertTrue(torch.equal(call_args.kwargs['inputs'], input_ids))
        self.assertTrue(torch.equal(call_args.kwargs['attention_mask'], attention_mask))


class TestLLaDAPatches(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures for LLaDA."""
        # Create a mock LLaDA model
        self.mock_model = MagicMock()
        self.mock_model.device = torch.device('cpu')
        self.mock_model.config = MagicMock()
        self.mock_model.config.max_position_embeddings = 4096
        self.mock_model.config.mask_token_id = 126336
        
        # Mock the model.model attribute for forward patching
        self.mock_model.model = MagicMock()
    
    def test_patch_llada_forward_methods(self):
        """Test that patch_llada_forward_methods replaces forward methods."""
        original_model_forward = self.mock_model.model.forward
        original_forward = self.mock_model.forward
        
        # Patch the model
        patched_model = patch_llada_forward_methods(self.mock_model)
        
        # Check that the model is the same object (in-place modification)
        self.assertIs(patched_model, self.mock_model)
        
        # Check that the forward methods have been replaced
        self.assertIsNot(self.mock_model.model.forward, original_model_forward)
        self.assertIsNot(self.mock_model.forward, original_forward)
    
    def test_patch_llada_diffusion_generate(self):
        """Test that patch_llada_diffusion_generate adds diffusion_generate method."""
        # Initially, model should not have diffusion_generate
        self.assertFalse(hasattr(self.mock_model, 'diffusion_generate'))
        
        # Patch the model
        patched_model = patch_llada_diffusion_generate(self.mock_model)
        
        # Check that the model is the same object (in-place modification)
        self.assertIs(patched_model, self.mock_model)
        
        # Check that diffusion_generate method has been added
        self.assertTrue(hasattr(self.mock_model, 'diffusion_generate'))
        self.assertTrue(callable(self.mock_model.diffusion_generate))
    
    def test_llada_diffusion_generate_interface(self):
        """Test that LLaDA diffusion_generate has the same interface as DiffuCoder."""
        # Patch the model
        patch_llada_diffusion_generate(self.mock_model)
        
        # Check the method signature
        import inspect
        sig = inspect.signature(self.mock_model.diffusion_generate)
        
        # Verify key parameters exist
        expected_params = [
            'input_ids', 'attention_mask', 'max_new_tokens', 'steps', 
            'temperature', 'alg', 'block_length', 'cfg_scale', 'remasking'
        ]
        
        for param in expected_params:
            self.assertIn(param, sig.parameters, f"Missing parameter: {param}")


if __name__ == "__main__":
    unittest.main()
