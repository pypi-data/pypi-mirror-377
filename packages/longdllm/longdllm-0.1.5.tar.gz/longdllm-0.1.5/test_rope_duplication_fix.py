#!/usr/bin/env python3
"""
Test script to validate the RoPE duplication fix in longdllm package.
This script tests that each layer gets its own unique RoPE instance.
"""

import sys
import logging
import torch
from transformers import AutoModel, AutoTokenizer

# Add longdllm to path
sys.path.insert(0, '/home/t-albertge/longdllm')

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_rope_duplication_fix():
    """Test that RoPE modules are properly replaced without duplication."""
    print("Testing RoPE duplication fix...")
    
    try:
        from longdllm.core import adapt_for_long_context
        
        # Load a small model for testing
        model_name = "deepseek-ai/DeepSeek-Coder-1.3B-Base"  # Small model for testing
        print(f"Loading model: {model_name}")
        
        model = AutoModel.from_pretrained(model_name, torch_dtype=torch.float16, trust_remote_code=True)
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        # Count RoPE modules before adaptation
        print("\nCounting RoPE modules before adaptation:")
        rope_modules_before = []
        for name, module in model.named_modules():
            if name.endswith('rotary_emb') and hasattr(module, 'dim'):
                rope_modules_before.append(name)
                print(f"  Found: {name} -> {type(module).__name__}")
        
        print(f"Total RoPE modules before: {len(rope_modules_before)}")
        
        # Adapt the model for long context
        print(f"\nAdapting model for long context (32k tokens)...")
        adapted_model = adapt_for_long_context(
            model, 
            target_length=32768, 
            scaling_method="longrope",
            magnitude_scaling="yarn"
        )
        
        # Count RoPE modules after adaptation
        print("\nCounting RoPE modules after adaptation:")
        rope_modules_after = []
        for name, module in adapted_model.named_modules():
            if name.endswith('rotary_emb'):
                rope_modules_after.append(name)
                print(f"  Found: {name} -> {type(module).__name__}")
        
        print(f"Total RoPE modules after: {len(rope_modules_after)}")
        
        # Check for duplication
        if len(rope_modules_after) == len(rope_modules_before):
            print("✅ SUCCESS: No RoPE module duplication detected!")
            print(f"   Before: {len(rope_modules_before)} modules")
            print(f"   After:  {len(rope_modules_after)} modules")
        else:
            print("❌ FAILED: RoPE module count mismatch!")
            print(f"   Before: {len(rope_modules_before)} modules")
            print(f"   After:  {len(rope_modules_after)} modules")
            print(f"   Difference: {len(rope_modules_after) - len(rope_modules_before)}")
            
            # Show the difference
            before_set = set(rope_modules_before)
            after_set = set(rope_modules_after)
            added = after_set - before_set
            removed = before_set - after_set
            
            if added:
                print(f"   Added modules: {added}")
            if removed:
                print(f"   Removed modules: {removed}")
        
        # Test that all modules are of the correct type
        print("\nValidating RoPE module types:")
        all_correct_type = True
        for name, module in adapted_model.named_modules():
            if name.endswith('rotary_emb'):
                from longdllm.rope import LongRoPEScaledRotaryEmbedding
                if not isinstance(module, LongRoPEScaledRotaryEmbedding):
                    print(f"❌ {name}: {type(module).__name__} (should be LongRoPEScaledRotaryEmbedding)")
                    all_correct_type = False
                else:
                    print(f"✅ {name}: {type(module).__name__}")
        
        if all_correct_type:
            print("✅ All RoPE modules are of the correct type!")
        else:
            print("❌ Some RoPE modules are not of the expected type!")
            
        return len(rope_modules_after) == len(rope_modules_before) and all_correct_type
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("LongDLLM RoPE Duplication Fix Test")
    print("=" * 60)
    
    success = test_rope_duplication_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! RoPE duplication fix is working correctly.")
    else:
        print("❌ TESTS FAILED! Please check the RoPE replacement logic.")
    print("=" * 60)
