import torch
from transformers import AutoModel, AutoTokenizer
from longdllm import adapt_for_long_context
import logging
import re

# logging.basicConfig(level=logging.INFO)

# Load your model as usual
model = AutoModel.from_pretrained(
    "apple/DiffuCoder-7B-Instruct",
    dtype=torch.float16,
    attn_implementation="flash_attention_2",
    trust_remote_code=True
)

model_path = "apple/DiffuCoder-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)


model = adapt_for_long_context(model, target_length=131072)
model = model.to("cuda").eval()

with open("./passkey-128k-idx-4.txt", "r") as f:
    query = f.read().strip()

passkey_phrase = re.search(r'\d+', query).group(0)
prompt = f"""<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
{query.strip()}
<|im_end|>
<|im_start|>assistant
""" ## following the template of qwen; you can also use apply_chat_template function

TOKEN_PER_STEP = 1 # diffusion timesteps * TOKEN_PER_STEP = total new tokens

inputs = tokenizer(prompt, return_tensors="pt")

print("\n" + "="*60)
print("LONGDLLM DIFFUCODER TEST - PASSKEY RETRIEVAL TASK")
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
    max_new_tokens=10,
    output_history=True,
    return_dict_in_generate=True,
    steps=10,
    temperature=0.3,
    top_p=0.95,
    alg="entropy",
    alg_temp=0.,
)

generations = [
    tokenizer.decode(g[len(p) :].tolist())
    for p, g in zip(input_ids, output.sequences)
]

response = generations[0].split('<|dlm_pad|>')[0]

print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"🤖 Model's raw output: '{response.strip()}'")

answer = re.search(r'\d+', response).group(0)
print(f"🔍 Extracted answer: {answer}")
print(f"✅ Success: {answer == passkey_phrase}" if answer == passkey_phrase else f"❌ Failed: Expected {passkey_phrase}, got {answer}")
print("="*60)