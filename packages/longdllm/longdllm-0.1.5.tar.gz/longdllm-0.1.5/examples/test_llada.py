import torch
from transformers import AutoModel, AutoTokenizer
from longdllm import adapt_for_long_context
import logging
import re 

# logging.basicConfig(level=logging.INFO)

# Load your model as usual
model_path = "GSAI-ML/LLaDA-8B-Instruct"
model = AutoModel.from_pretrained(
    model_path,
    dtype=torch.float16,
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

model = adapt_for_long_context(model, target_length=131072)
model = model.to("cuda").eval()

with open("./passkey-128k-idx-4.txt", "r") as f:
    query = f.read().strip()

passkey_phrase = re.search(r'\d+', query).group(0)

# Apply chat template for instruct model
m = [{"role": "user", "content": query}]
formatted_prompt = tokenizer.apply_chat_template(m, add_generation_prompt=True, tokenize=False)

inputs = tokenizer(formatted_prompt, return_tensors="pt")

print("\n" + "="*60)
print("LONGDLLM LLADA TEST - PASSKEY RETRIEVAL TASK")
print("="*60)
print(f"📄 Input length: {len(inputs.input_ids[0])} tokens")
print(f"🔑 Hidden passkey (ground truth): {passkey_phrase}")
first_sentence = query.split('\n')[0] + '.' if '\n' in query else query[:100] + '...'
print(f"\n first line of query: \"{first_sentence}\"")

input_ids = inputs.input_ids.to(device="cuda")
attention_mask = inputs.attention_mask.to(device="cuda")

print("\n🚀 Running LongDLLM-adapted model with diffusion generation...")

# Use the adapted model with long sequences
output = model.diffusion_generate(
    input_ids,
    attention_mask=attention_mask,
    steps=10,
    gen_length=10,
    block_length=10,
    temperature=0.,
    cfg_scale=0.0,
    remasking='low_confidence',
)

response = tokenizer.batch_decode(output[:, input_ids.shape[1]:], skip_special_tokens=True)[0]

print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"🤖 Model's raw output: '{response.strip()}'")

answer = re.search(r'\d+', response).group(0)
print(f"🔍 Extracted answer: {answer}")
print(f"✅ Success: {answer == passkey_phrase}" if answer == passkey_phrase else f"❌ Failed: Expected {passkey_phrase}, got {answer}")
print("="*60)
