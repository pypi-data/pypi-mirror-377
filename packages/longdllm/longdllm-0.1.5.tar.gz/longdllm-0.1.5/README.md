# LongDLLM

**🚀 Plug-and-play long context adaptation for diffusion language models**

LongDLLM enables seamless extension of diffusion language models to handle long-context inputs (up to 128k tokens) with minimal code changes and a unified interface. 

## ✨ Features

- 🎯 **Drop-in compatibility**: Works with existing code - just add one function call
- 🧠 **Memory efficient**: Handle 128k+ tokens on a single A6000 GPU (48GB VRAM)
- ⚡ **Long Context Performance**: Provide pre-tuned rescale factors for context extension
- 🔧 **Unified interface**: Same API for all supported models

## 🤖 Supported Models

- **Apple DiffuCoder-7B-Instruct** - Code generation with long context
- **GSAI-ML LLaDA-8B-Instruct** - General instruction following with extended context

## 📦 Installation

### Basic Installation
```bash
pip install longdllm
```

Installing FlashAttention is highly recommended, you can install it separately via `pip install flash-attn --no-build-isolation`. 

## 🚀 Quick Start

### DiffuCoder Example

```python
import torch
from transformers import AutoModel, AutoTokenizer
from longdllm import adapt_for_long_context

# 1. Load your model as usual
model = AutoModel.from_pretrained(
    "apple/DiffuCoder-7B-Instruct",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True
)

# 2. Adapt for long context (128k tokens)
model = adapt_for_long_context(model, target_length=131072)

# 3. Generate with long sequences
tokenizer = AutoTokenizer.from_pretrained("apple/DiffuCoder-7B-Instruct")
inputs = tokenizer("Your long prompt here...", return_tensors="pt")

output = model.diffusion_generate(
    inputs.input_ids,
    attention_mask=inputs.attention_mask,
    max_new_tokens=256,
    steps=32,  # Diffusion steps
    temperature=0.3,
    top_p=0.95,
    alg="entropy"
)
```

### LLaDA Example  
> **⚠️ LLaDA Note:** Patched methods ignore `attention_bias` for memory efficiency. This is safe per [LLaDA issue #90](https://github.com/ML-GSAI/LLaDA/issues/90#issuecomment-3040649162).

```python
from transformers import AutoTokenizer, AutoModel
from longdllm import adapt_for_long_context

# 1. Load and adapt LLaDA model  
model = AutoModel.from_pretrained("GSAI-ML/LLaDA-8B-Instruct", trust_remote_code=True)
model = adapt_for_long_context(model, target_length=131072)

# 2. Use unified diffusion_generate interface
tokenizer = AutoTokenizer.from_pretrained("GSAI-ML/LLaDA-8B-Instruct")
inputs = tokenizer("Your instruction here...", return_tensors="pt")

outputs = model.diffusion_generate(
    input_ids=inputs.input_ids,
    max_new_tokens=512,
    temperature=0.0,
    steps=128,
    block_length=128,
    remasking='low_confidence'
)
```

## 💡 Examples

Check out our example scripts to see LongDLLM in action:

- **[`examples/test_diffucoder.py`](examples/test_diffucoder.py)** - DiffuCoder passkey retrieval test
- **[`examples/test_llada.py`](examples/test_llada.py)** - LLaDA passkey retrieval test  

### Running Examples

```bash
# Test DiffuCoder with 128k context
cd examples && python test_diffucoder.py

# Test LLaDA with 128k context  
cd examples && python test_llada.py
```

Both examples demonstrate **passkey retrieval** - finding a hidden number in long documents, a common benchmark for long-context capabilities.


## ⚙️ Advanced Configuration

### Custom Rescale Factors

Want to experiment? You can provide custom factors:

```python
# Example: Exponential rescale factors (approximating optimized values)
import numpy as np
custom_factors = (
    list(np.logspace(0, 1.5, 34)) +  # 1.0 to ~31.6, exponentially spaced
    list(np.linspace(16.3, 31.3, 30))  # Linear spacing for higher frequencies
)  

model = adapt_for_long_context(
    model,
    target_length=65536,  # Custom length
    scaling_method='longrope',
    rescale_factors=custom_factors
)
```

## License

MIT

## Citation

If you use LongDLLM in your research, please cite:

```bibtex
@misc{ge2025longcontext,
  title = {Long-Context Extension for Language Diffusion Models up to 128k Tokens},
  url = {https://albertge.notion.site/longcontext},
  author = {Ge, Albert and Singh, Chandan and Zhang, Dinghuai and Peng, Letian and Zhuang, Yufan and Shang, Ning and Zhang, Li Lyna and Liu, Liyuan and Gao, Jianfeng},
  journal = {Albert Ge's Notion},
  year = {2025},
  month = sep,
}
```

## 🤝 Support & Contributing

### 🐛 Issues & Questions
- **GitHub Issues**: [Report bugs or ask questions](https://github.com/lbertge/longdllm/issues)
- **Email**: [Albert Ge](mailto:lbertge@gmail.com) for direct support
