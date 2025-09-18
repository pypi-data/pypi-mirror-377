"""
Memory-optimized forward methods and diffusion generation for LLaDA models.
"""

import logging
import math
import types
from typing import Optional, Tuple, List, Union

import torch
from transformers.modeling_outputs import BaseModelOutputWithPast, CausalLMOutputWithPast

logger = logging.getLogger(__name__)


def forward_llada_model_memory_efficient(
    self,
    input_ids: torch.LongTensor,
    input_embeddings: Optional[torch.FloatTensor] = None,
    attention_mask: Optional[torch.Tensor] = None,
    attention_bias: Optional[torch.Tensor] = None,
    past_key_values: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None,
    use_cache: bool = False,
    last_logits_only: bool = False,
    output_hidden_states: Optional[bool] = None,
    num_logits_to_keep: int = 0,
):
    """
    Memory-optimized forward pass for LLaDA model with num_logits_to_keep parameter.
    
    WARNING: This implementation ignores attention_bias for memory efficiency.
    See: https://github.com/ML-GSAI/LLaDA/issues/90#issuecomment-3040649162
    
    Args:
        num_logits_to_keep: Only compute logits for the last num_logits_to_keep tokens.
                           If 0, compute logits for all tokens. This saves memory during training.
    """
    # Add Basic MDM Model config check (from original LLaDA)
    assert not self.config.alibi, "Alibi length extrapolation is not supported for MDM."
    assert self.config.rope, "Rope must be used in Llama-Encoder for MDM."
    assert (past_key_values is None and not use_cache), "The kvcache is not suppotred for MDM."

    # Warn about attention_bias removal
    if attention_bias is not None:
        logger.warning(
            "attention_bias is ignored in this memory-optimized implementation for memory efficiency. "
            "This is generally safe for LLaDA models. See: https://github.com/ML-GSAI/LLaDA/issues/90#issuecomment-3040649162"
        )

    output_hidden_states = output_hidden_states if output_hidden_states is not None else False

    if past_key_values:
        assert len(past_key_values) == self.config.n_layers

    batch_size, seq_len = input_ids.size() if input_embeddings is None else input_embeddings.size()[:2]
    if past_key_values is None:
        past_length = 0
    else:
        past_length = past_key_values[0][0].size(-2)

    # Get embeddings of input.
    # shape: (batch_size, seq_len, d_model)
    x = self.transformer.wte(input_ids) if input_embeddings is None else input_embeddings

    if self.config.input_emb_norm:
        x = x * (self.config.d_model**0.5)

    if not (self.config.alibi or self.config.rope):
        # Get positional embeddings.
        # shape: (1, seq_len)
        pos = torch.arange(past_length, past_length + seq_len, dtype=torch.long, device=x.device).unsqueeze(0)
        # shape: (1, seq_len, d_model)
        pos_emb = self.transformer.wpe(pos)
        x = pos_emb + x

    # Add input + positional embeddings and apply dropout.
    # shape: (batch_size, seq_len, d_model)
    x = self.transformer.emb_drop(x)

    # Transform the attention mask into what the blocks expect.
    if attention_mask is not None and 0.0 in attention_mask:
        # shape: (batch_size, 1, 1, seq_len)
        attention_mask = attention_mask.to(dtype=torch.float).view(batch_size, -1)[:, None, None, :]
        attention_mask = (1.0 - attention_mask) * torch.finfo(attention_mask.dtype).min
    else:
        attention_mask = None

    attn_key_values: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = [] if use_cache else None

    # decoder layers
    all_hidden_states = []

    # Apply blocks one-by-one.
    if self.config.block_group_size == 1:
        for block_idx, block in enumerate(self.transformer.blocks):
            if output_hidden_states:
                # add hidden states
                all_hidden_states.append(x)

            layer_past = None if past_key_values is None else past_key_values[block_idx]
            
            # Use activation checkpointing if configured
            from .configuration_llada import ActivationCheckpointingStrategy
            if (
                (self.activation_checkpointing_strategy == ActivationCheckpointingStrategy.whole_layer)
                or (
                    self.activation_checkpointing_strategy == ActivationCheckpointingStrategy.one_in_two
                    and block_idx % 2 == 0
                )
                or (
                    self.activation_checkpointing_strategy == ActivationCheckpointingStrategy.one_in_three
                    and block_idx % 3 == 0
                )
                or (
                    self.activation_checkpointing_strategy == ActivationCheckpointingStrategy.one_in_four
                    and block_idx % 4 == 0
                )
            ):
                # shape: (batch_size, seq_len, d_model)
                x, cache = self._activation_checkpoint_fn(
                    block, x, attention_bias=None, layer_past=layer_past, use_cache=use_cache
                )
            else:
                # shape: (batch_size, seq_len, d_model)
                # NOTE: attention_bias=None for memory efficiency
                x, cache = block(x, attention_bias=None, layer_past=layer_past, use_cache=use_cache)
            if attn_key_values is not None:
                assert cache is not None
                attn_key_values.append(cache)
    else:
        for group_idx, block_group in enumerate(self.transformer.block_groups):
            if output_hidden_states:
                # add hidden states
                all_hidden_states.append(x)

            layers_past = (
                None
                if past_key_values is None
                else past_key_values[
                    group_idx * self.config.block_group_size : (group_idx + 1) * self.config.block_group_size
                ]
            )
            # NOTE: attention_bias=None for memory efficiency
            x, cache = block_group(
                x, attention_bias=None, layers_past=layers_past, use_cache=use_cache
            )
            if attn_key_values is not None:
                assert cache is not None
                attn_key_values.extend(cache)

    if last_logits_only:
        # shape: (batch_size, 1, d_model)
        x = x[:, -1, :].unsqueeze(1)

    # Apply final layer norm with chunking for memory efficiency
    # shape: (batch_size, seq_len or 1, d_model)
    norm = self.transformer.ln_f
    batch, seq_len_final, embed_dim = x.shape
    for start_idx in range(0, seq_len_final, 16384):
        end_idx = min(seq_len_final, start_idx + 16384)
        x[:, start_idx:end_idx, :] = norm(x[:, start_idx:end_idx, :])

    if output_hidden_states:
        # add final hidden state post-final-layernorm, following HuggingFace's convention
        all_hidden_states.append(x)

    # Only compute necessary logits, and do not upcast them to float if we are not computing the loss
    # shape: (batch_size, num_logits_to_keep or seq_len, vocab_size)
    if num_logits_to_keep > 0:
        hidden_states = x[:, -num_logits_to_keep:, :]
    else:
        hidden_states = x

    # Get logits with chunking for memory efficiency
    if self.config.weight_tying:
        # Chunk the logits computation to save memory
        logits_list = []
        for start_idx in range(0, hidden_states.shape[1], 16384):
            end_idx = min(hidden_states.shape[1], start_idx + 16384)
            chunk_logits = torch.nn.functional.linear(hidden_states[:, start_idx:end_idx, :], self.transformer.wte.weight, None)
            logits_list.append(chunk_logits)
        logits = torch.cat(logits_list, dim=1)
    else:
        # Chunk the logits computation to save memory
        logits_list = []
        for start_idx in range(0, hidden_states.shape[1], 16384):
            end_idx = min(hidden_states.shape[1], start_idx + 16384)
            chunk_logits = self.transformer.ff_out(hidden_states[:, start_idx:end_idx, :])
            logits_list.append(chunk_logits)
        logits = torch.cat(logits_list, dim=1)

    if self.config.scale_logits:
        logits.mul_(1 / math.sqrt(self.config.d_model))

    # Return LLaDA-specific output format
    try:
        # Try to import LLaDAOutput - this may fail in the package environment
        from transformers import PreTrainedModel
        if hasattr(PreTrainedModel, 'LLaDAOutput'):
            return PreTrainedModel.LLaDAOutput(
                logits=logits, 
                attn_key_values=attn_key_values, 
                hidden_states=tuple(all_hidden_states) if output_hidden_states else None
            )
        else:
            raise ImportError("LLaDAOutput not available")
    except ImportError:
        # Fallback to standard output if LLaDAOutput is not available
        return BaseModelOutputWithPast(
            last_hidden_state=logits,
            past_key_values=attn_key_values,
            hidden_states=tuple(all_hidden_states) if output_hidden_states else None,
        )


def forward_llada_for_causal_lm(
    self,
    input_ids: torch.LongTensor = None,
    inputs_embeds: Optional[torch.FloatTensor] = None,
    attention_mask: Optional[torch.Tensor] = None,
    attention_bias: Optional[torch.Tensor] = None,
    past_key_values: Optional[List[torch.FloatTensor]] = None,
    labels: Optional[torch.LongTensor] = None,
    use_cache: Optional[bool] = None,
    output_attentions: Optional[bool] = None,
    output_hidden_states: Optional[bool] = None,
    return_dict: Optional[bool] = None,
    num_logits_to_keep: int = 0,
) -> Union[Tuple, CausalLMOutputWithPast]:
    """
    Memory-optimized forward pass for LLaDA CausalLM with num_logits_to_keep parameter.
    
    WARNING: This implementation ignores attention_bias for memory efficiency.
    See: https://github.com/ML-GSAI/LLaDA/issues/90#issuecomment-3040649162
    
    Args:
        num_logits_to_keep: Only compute logits for the last num_logits_to_keep tokens.
                           If 0, compute logits for all tokens. This saves memory during training.
    """
    output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
    output_hidden_states = (
        output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
    )
    return_dict = return_dict if return_dict is not None else self.config.use_return_dict

    # decoder outputs consists of (dec_features, layer_state, dec_hidden, dec_attn)
    outputs = forward_llada_model_memory_efficient(
        self.model,
        input_ids=input_ids,
        input_embeddings=inputs_embeds,
        attention_mask=attention_mask,
        attention_bias=attention_bias,  # Will be ignored with warning
        past_key_values=past_key_values,
        use_cache=use_cache,
        last_logits_only=False,
        output_hidden_states=output_hidden_states,
        num_logits_to_keep=num_logits_to_keep,
    )
    
    # Clear CUDA cache to free memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Extract logits from LLaDA output format
    if hasattr(outputs, 'logits'):
        logits = outputs.logits
    else:
        logits = outputs.last_hidden_state

    # Handle loss calculation if labels are provided
    loss = None
    if labels is not None:
        import warnings
        warnings.warn("Note that for LLaDA, you cannot calculate the loss here.", UserWarning)

    if not return_dict:
        output = (logits,) + outputs[1:]
        return (loss,) + output if loss is not None else output

    return CausalLMOutputWithPast(
        loss=loss,
        logits=logits,
        past_key_values=getattr(outputs, 'attn_key_values', None),
        hidden_states=getattr(outputs, 'hidden_states', None),
        attentions=None,  # LLaDA doesn't return attentions
    )


def patch_llada_forward_methods(model):
    """
    Patch LLaDA model with memory-optimized forward methods that support num_logits_to_keep.
    
    WARNING: The patched forward methods ignore attention_bias for memory efficiency.
    This is safe for LLaDA models according to: 
    https://github.com/ML-GSAI/LLaDA/issues/90#issuecomment-3040649162
    
    Args:
        model: The LLaDA model to patch
        
    Returns:
        The model with patched forward methods
    """
    # Patch model.model.forward with memory-efficient method that supports num_logits_to_keep
    model.model.forward = types.MethodType(forward_llada_model_memory_efficient, model.model)
    
    # Patch model.forward (CausalLM level) 
    model.forward = types.MethodType(forward_llada_for_causal_lm, model)
    
    logger.info("Patched LLaDA model with memory-optimized forward methods supporting num_logits_to_keep")
    logger.warning(
        "Patched forward methods ignore attention_bias for memory efficiency. "
        "This is safe for LLaDA models per https://github.com/ML-GSAI/LLaDA/issues/90#issuecomment-3040649162"
    )
    
    return model


def add_gumbel_noise(logits, temperature):
    """
    The Gumbel max is a method for sampling categorical distributions.
    According to arXiv:2409.02908, for MDM, low-precision Gumbel Max improves perplexity score but reduces generation quality.
    Thus, we use float64.
    """
    if temperature == 0:
        return logits
    logits = logits.to(torch.float64)
    noise = torch.rand_like(logits, dtype=torch.float64)
    gumbel_noise = (- torch.log(noise)) ** temperature
    return logits.exp() / gumbel_noise


def get_num_transfer_tokens(mask_index, steps):
    """
    In the reverse process, the interval [0, 1] is uniformly discretized into steps intervals.
    Furthermore, because LLaDA employs a linear noise schedule (as defined in Eq. (8)),
    the expected number of tokens transitioned at each step should be consistent.

    This function is designed to precompute the number of tokens that need to be transitioned at each step.
    """
    mask_num = mask_index.sum(dim=1, keepdim=True)

    base = mask_num // steps
    remainder = mask_num % steps

    num_transfer_tokens = torch.zeros(mask_num.size(0), steps, device=mask_index.device, dtype=torch.int64) + base

    for i in range(mask_num.size(0)):
        num_transfer_tokens[i, :remainder[i]] += 1

    return num_transfer_tokens


@torch.no_grad()
def generate_sparse_llada(model, prompt, steps=128, gen_length=128, block_length=128, temperature=0.,
                         cfg_scale=0., remasking='low_confidence', mask_id=126336):
    """
    Memory-efficient generation using sparse logits (num_logits_to_keep) for LLaDA.
    Works directly with sparse logits without materializing full logits tensor.
    
    Args:
        model: LLaDA mask predictor.
        prompt: A tensor of shape (1, L).
        steps: Sampling steps, less than or equal to gen_length.
        gen_length: Generated answer length.
        block_length: Block length, less than or equal to gen_length.
        temperature: Categorical distribution sampling temperature.
        cfg_scale: Unsupervised classifier-free guidance scale.
        remasking: Remasking strategy. 'low_confidence' or 'random'.
        mask_id: The token id of [MASK] is 126336.
    """
    x = torch.full((1, prompt.shape[1] + gen_length), mask_id, dtype=torch.long).to(model.device)
    x[:, :prompt.shape[1]] = prompt.clone()

    prompt_index = (x != mask_id)
    prompt_len = prompt.shape[1]

    assert gen_length % block_length == 0
    num_blocks = gen_length // block_length

    assert steps % num_blocks == 0
    steps = steps // num_blocks

    for num_block in range(num_blocks):
        # Current block range in the generation region
        block_start = prompt_len + num_block * block_length
        block_end = prompt_len + (num_block + 1) * block_length
        
        block_mask_index = (x[:, block_start:block_end] == mask_id)
        num_transfer_tokens = get_num_transfer_tokens(block_mask_index, steps)
        
        for i in range(steps):
            # Only compute logits for the generation region (gen_length tokens)
            num_logits_to_keep = gen_length
            
            if cfg_scale > 0.:
                un_x = x.clone()
                un_x[prompt_index] = mask_id
                x_ = torch.cat([x, un_x], dim=0)
                
                # Use memory-efficient forward pass with num_logits_to_keep
                model_output = model(x_, num_logits_to_keep=num_logits_to_keep)
                sparse_logits = model_output.logits
                    
                sparse_logits, un_sparse_logits = torch.chunk(sparse_logits, 2, dim=0)
                sparse_logits = un_sparse_logits + (cfg_scale + 1) * (sparse_logits - un_sparse_logits)
            else:
                # Use memory-efficient forward pass with num_logits_to_keep
                model_output = model(x, num_logits_to_keep=num_logits_to_keep)
                sparse_logits = model_output.logits

            # Add Gumbel noise to sparse logits
            sparse_logits_with_noise = add_gumbel_noise(sparse_logits, temperature=temperature)
            sparse_x0 = torch.argmax(sparse_logits_with_noise, dim=-1)  # [batch_size, gen_length]

            # Compute confidence for sparse region
            if remasking == 'low_confidence':
                sparse_p = torch.nn.functional.softmax(sparse_logits, dim=-1)
                sparse_x0_p = torch.squeeze(
                    torch.gather(sparse_p, dim=-1, index=torch.unsqueeze(sparse_x0, -1)), -1)
            elif remasking == 'random':
                sparse_x0_p = torch.rand_like(sparse_x0, dtype=torch.float)
            else:
                raise NotImplementedError(remasking)

            # Map sparse results back to full sequence
            # Only work on the generation region
            gen_start = prompt_len
            gen_end = prompt_len + gen_length
            gen_x = x[:, gen_start:gen_end]
            gen_mask_index = (gen_x == mask_id)
            
            # Apply block constraints to confidence
            block_offset = num_block * block_length
            next_block_start = (num_block + 1) * block_length
            if next_block_start < gen_length:
                sparse_x0_p[:, next_block_start:] = -float('inf')
            
            # Create generation region outputs
            gen_x0 = torch.where(gen_mask_index, sparse_x0, gen_x)
            gen_confidence = torch.where(gen_mask_index, sparse_x0_p, torch.tensor(-float('inf')))

            # Transfer tokens within generation region
            transfer_index_gen = torch.zeros_like(gen_x0, dtype=torch.bool, device=gen_x0.device)
            for j in range(gen_confidence.shape[0]):
                _, select_index = torch.topk(gen_confidence[j], k=num_transfer_tokens[j, i])
                transfer_index_gen[j, select_index] = True
            
            # Update only the generation region
            x[:, gen_start:gen_end] = torch.where(transfer_index_gen, gen_x0, gen_x)
            
            # Clean up intermediate tensors
            del sparse_x0, sparse_x0_p, gen_confidence, transfer_index_gen, gen_mask_index, gen_x0

    return x


def patch_llada_diffusion_generate(model):
    """
    Add a diffusion_generate method to LLaDA models for consistency with DiffuCoder interface.
    
    Args:
        model: The LLaDA model to patch
        
    Returns:
        The model with added diffusion_generate method
    """
    
    def diffusion_generate(
        input_ids,
        attention_mask=None,
        steps=128,
        gen_length=None,
        block_length=128,
        temperature=0.0,
        cfg_scale=0.0,
        output_history=False,
        return_dict_in_generate=False,
        remasking='low_confidence',
        top_p=None, # Not used for LLaDA but kept for interface consistency
        top_k=None, # Not used for LLaDA but kept for interface consistency
        alg='origin',  # Not used for LLaDA but kept for interface consistency
        alg_temp=None,  # Not used for LLaDA but kept for interface consistency
        eps=1e-3,  # Not used for LLaDA but kept for interface consistency
        **kwargs
    ):
        """
        Diffusion generation for LLaDA models using memory-efficient sparse logits.
        
        This method provides the same interface as DiffuCoder's diffusion_generate for consistency,
        but uses LLaDA's specific generation algorithm internally.
        
        Args:
            input_ids: Input token IDs (prompt)
            attention_mask: Attention mask (optional, unused in current implementation)
            max_new_tokens: Number of tokens to generate
            max_length: Maximum total length (unused, max_new_tokens takes precedence)
            output_history: Whether to return generation history (not implemented for LLaDA)
            return_dict_in_generate: Whether to return dict format (not implemented for LLaDA)
            steps: Number of diffusion sampling steps
            temperature: Gumbel noise temperature for sampling
            top_p: Top-p sampling (not used in LLaDA generation)
            top_k: Top-k sampling (not used in LLaDA generation) 
            alg: Algorithm type (kept for interface consistency, not used)
            alg_temp: Algorithm temperature (kept for interface consistency, not used)
            eps: Epsilon value (kept for interface consistency, not used)
            block_length: Block length for semi-autoregressive generation
            cfg_scale: Classifier-free guidance scale
            remasking: Remasking strategy ('low_confidence' or 'random')
            **kwargs: Additional arguments
        
        Returns:
            Generated sequences tensor
        """
        # Warn about unused parameters for interface consistency
        if top_p is not None or top_k is not None:
            logger.warning("top_p and top_k are not used in LLaDA generation algorithm")
        if alg != 'origin' or alg_temp is not None:
            logger.warning("alg and alg_temp parameters are not used in LLaDA generation algorithm")
        if output_history or return_dict_in_generate:
            logger.warning("output_history and return_dict_in_generate are not implemented for LLaDA")
        
        # Get mask token ID
        mask_token_id = getattr(model.config, 'mask_token_id', 126336)
        
        # Use memory-efficient sparse generation
        result = generate_sparse_llada(
            model=model,
            prompt=input_ids,
            steps=steps,
            gen_length=gen_length,
            block_length=block_length,
            temperature=temperature,
            cfg_scale=cfg_scale,
            remasking=remasking,
            mask_id=mask_token_id
        )
        
        return result
    
    # Add the diffusion_generate method to the model
    model.diffusion_generate = diffusion_generate
    logger.info("Added diffusion_generate method to LLaDA model for interface consistency")
    
    return model
