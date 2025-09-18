#!/usr/bin/env python3
"""
Test LongDLLM without installing the package.
This script adds the package to Python path and tests functionality.
"""

import sys
import os

# Add LongDLLM to Python path (avoids pip install issues)
sys.path.insert(0, '/home/t-albertge/longdllm')

def test_without_installation(model_name: str, passkey_file: str):
    """
    Test LongDLLM functionality without pip installation.
    
    Args:
        model_name: Path to your model
        passkey_file: Path to passkey test file
    """
    print("🧪 Testing LongDLLM Without Installation")
    print("=" * 60)
    print(f"Model: {model_name}")
    print(f"Passkey file: {passkey_file}")
    print("=" * 60)
    
    try:
        # Import from local path
        import longdllm
        print(f"✅ Imported LongDLLM from: {longdllm.__file__}")
        
        # Import required components
        import torch
        import re
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        # Read passkey file
        with open(passkey_file, 'r') as f:
            prompt_text = f.read().strip()
        
        # Extract expected passkey
        expected_match = re.search(r'The pass key is (\d+)', prompt_text)
        expected_passkey = expected_match.group(1) if expected_match else "Unknown"
        print(f"🎯 Expected passkey: {expected_passkey}")
        
        # Load model
        print("📦 Loading model...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto", 
            trust_remote_code=True
        )
        
        print(f"📏 Original max_position_embeddings: {model.config.max_position_embeddings}")
        
        # Apply LongDLLM adaptation (this is where the dictionary error was occurring)
        print("🔧 Applying LongDLLM adaptation...")
        model = longdllm.adapt_for_long_context(model, target_length=32768)
        print(f"📏 Adapted max_position_embeddings: {model.config.max_position_embeddings}")
        
        # Verify diffusion_generate method
        if hasattr(model, 'diffusion_generate'):
            print("✅ diffusion_generate method available")
        else:
            print("❌ diffusion_generate method not found")
            return False
        
        # Prepare input
        if 'llada' in model_name.lower():
            messages = [{"role": "user", "content": prompt_text}]
            formatted_prompt = tokenizer.apply_chat_template(
                messages, add_generation_prompt=True, tokenize=False
            )
        else:
            formatted_prompt = prompt_text
        
        input_ids = tokenizer(formatted_prompt, return_tensors="pt").input_ids.to(model.device)
        input_length = input_ids.shape[1]
        print(f"📊 Input length: {input_length:,} tokens")
        
        # Test generation
        print("🚀 Testing diffusion_generate...")
        outputs = model.diffusion_generate(
            input_ids=input_ids,
            max_new_tokens=10,
            temperature=0.0,
            steps=32
        )
        
        # Decode response
        generated_tokens = outputs[:, input_length:]
        response = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        
        # Extract generated passkey
        generated_numbers = re.findall(r'\d+', response)
        generated_passkey = generated_numbers[0] if generated_numbers else "NO_NUMBER"
        
        # Results
        is_correct = generated_passkey == expected_passkey
        status = "✅ CORRECT" if is_correct else "❌ WRONG"
        
        print(f"📊 RESULT: {status}")
        print(f"   Expected: {expected_passkey}")
        print(f"   Generated: {generated_passkey}")
        print(f"   Response: '{response}'")
        
        print(f"\\n🎉 Testing complete without installation!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_usage_guide():
    """Show how to use this testing approach."""
    print("🎓 Usage Guide: Testing Without Installation")
    print("=" * 60)
    print()
    print("🔧 This approach:")
    print("   ✅ Avoids pip install conflicts with flash-attn")
    print("   ✅ Uses your existing environment dependencies") 
    print("   ✅ Tests the actual package functionality")
    print("   ✅ Perfect for development and validation")
    print()
    print("💡 To use this script:")
    print("   1. Make sure you're in the llada conda environment")
    print("   2. Run: python test_no_install.py YOUR_MODEL_PATH PASSKEY_FILE")
    print()
    print("📄 Available passkey files:")
    passkey_dir = "/home/t-albertge/v2-longrope/analysis/attention_map"
    if os.path.exists(passkey_dir):
        for file in os.listdir(passkey_dir):
            if 'passkey' in file.lower() and file.endswith('.txt'):
                file_path = os.path.join(passkey_dir, file)
                size = os.path.getsize(file_path) // 4  # Rough token estimate
                print(f"   - {file} (~{size:,} tokens)")
    print()
    print("🚀 Example commands:")
    print("   # Test with short passkey:")
    print("   python test_no_install.py \\")
    print("     YOUR_MODEL_PATH \\")
    print("     /home/t-albertge/v2-longrope/analysis/attention_map/passkey.txt")
    print()
    print("   # Test with long passkey:")
    print("   python test_no_install.py \\")
    print("     YOUR_MODEL_PATH \\")
    print("     /home/t-albertge/v2-longrope/analysis/attention_map/passkey-32k-idx-2.txt")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Usage: python test_no_install.py MODEL_PATH PASSKEY_FILE")
        print()
        show_usage_guide()
        exit(1)
    
    model_path = sys.argv[1]
    passkey_file = sys.argv[2]
    
    if not os.path.exists(model_path):
        print(f"❌ Model path not found: {model_path}")
        exit(1)
        
    if not os.path.exists(passkey_file):
        print(f"❌ Passkey file not found: {passkey_file}")
        exit(1)
    
    success = test_without_installation(model_path, passkey_file)
    exit(0 if success else 1)
