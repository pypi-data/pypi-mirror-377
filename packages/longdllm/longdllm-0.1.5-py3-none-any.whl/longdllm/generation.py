"""
Memory-efficient generation utilities for DiffuCoder models.
"""

import torch
import warnings
import copy
from typing import Any, Dict, Optional, Tuple, Union
from torch.nn import functional as F
from transformers import __version__
from transformers.generation.configuration_utils import GenerationConfig
from transformers.utils import ModelOutput, is_torchdynamo_compiling, logging
from dataclasses import dataclass

logger = logging.get_logger(__name__)


def top_p_logits(logits, top_p=None):
    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
    sorted_indices_to_remove = cumulative_probs > top_p
    # Shift the indices to the right to keep the first token above the threshold
    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
    sorted_indices_to_remove[..., 0] = 0

    mask = torch.zeros_like(logits, dtype=torch.bool, device=logits.device)
    mask = mask.scatter_(-1, sorted_indices, sorted_indices_to_remove)
    logits = logits.masked_fill(mask, torch.finfo(logits.dtype).min)
    return logits


def top_k_logits(logits, top_k=None):
    top_k = min(top_k, logits.size(-1))  # Safety check
    # Remove all tokens with a probability less than the last token of the top-k
    indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
    logits = logits.masked_fill(indices_to_remove, torch.finfo(logits.dtype).min)
    return logits


def sample_tokens(logits, temperature=0.0, top_p=None, top_k=None, margin_confidence=False, neg_entropy=False):
    if temperature > 0:
        logits = logits / temperature
    if top_p is not None and top_p < 1:
        logits = top_p_logits(logits, top_p)
    if top_k is not None:
        logits = top_k_logits(logits, top_k)
    probs = torch.softmax(logits, dim=-1)

    if temperature > 0:
        try:
            import torch.distributions as dists
            x0 = dists.Categorical(probs=probs).sample()
            confidence = torch.gather(probs, -1, x0.unsqueeze(-1)).squeeze(-1)
        except:
            confidence, x0 = probs.max(dim=-1)
    else:
        confidence, x0 = probs.max(dim=-1)
    
    if margin_confidence:
        sorted_probs, _ = torch.sort(probs, dim=-1, descending=True)
        # Extract top1 and top2 probabilities
        top1_probs = sorted_probs[:, 0] 
        top2_probs = sorted_probs[:, 1] 
        # Calculate confidence as top1 - top2
        confidence = top1_probs - top2_probs 
    
    if neg_entropy:
        epsilon = 1e-10
        log_probs = torch.log(probs + epsilon)
        confidence = torch.sum(probs * log_probs, dim=-1)
    
    return confidence, x0


@dataclass
class DreamModelOutput(ModelOutput):
    sequences: torch.LongTensor = None
    history: Optional[Tuple[torch.FloatTensor]] = None


class DreamGenerationConfig(GenerationConfig):
    def __init__(self, **kwargs):
        self.temperature: float = kwargs.pop("temperature", 0.0)
        self.top_p: Optional[float] = kwargs.pop("top_p", None)
        self.top_k: Optional[int] = kwargs.pop("top_k", None)
        self.max_length = kwargs.pop("max_length", 20)
        self.max_new_tokens = kwargs.pop("max_new_tokens", None)
        # diffusion specific params
        self.eps: float = kwargs.pop("eps", 1e-3)
        self.steps: int = kwargs.pop("steps", 512)
        self.alg: str = kwargs.pop("alg", 'origin')
        self.alg_temp: Optional[float] = kwargs.pop("alg_temp", None)

        # Parameters that define the output variables of `generate`
        self.num_return_sequences: int = kwargs.pop("num_return_sequences", 1)
        self.return_dict_in_generate: bool = kwargs.pop("return_dict_in_generate", False)
        self.output_history: bool = kwargs.pop("output_history", False)

        # Special tokens that can be used at generation time
        self.mask_token_id = kwargs.pop("mask_token_id", None)
        self.pad_token_id = kwargs.pop("pad_token_id", None)
        self.bos_token_id = kwargs.pop("bos_token_id", None)
        self.eos_token_id = kwargs.pop("eos_token_id", None)

        # Wild card
        self.generation_kwargs = kwargs.pop("generation_kwargs", {})

        # The remaining attributes do not parametrize `.generate()`, but are informative and/or used by the hub
        # interface.
        self._from_model_config = kwargs.pop("_from_model_config", False)
        self._commit_hash = kwargs.pop("_commit_hash", None)
        self.transformers_version = kwargs.pop("transformers_version", __version__)

        # Additional attributes without default values
        if not self._from_model_config:
            # we don't want to copy values from the model config if we're initializing a `GenerationConfig` from a
            # model's default configuration file
            for key, value in kwargs.items():
                try:
                    setattr(self, key, value)
                except AttributeError as err:
                    logger.error(f"Can't set {key} with value {value} for {self}")
                    raise err

        # Validate the values of the attributes
        self.validate(is_init=True)

    def validate(self, is_init=False, strict=True):
        pass


def _expand_inputs_for_generation(
    expand_size: int = 1,
    input_ids: Optional[torch.LongTensor] = None,
    attention_mask: Optional[torch.LongTensor] = None
) -> Tuple[torch.LongTensor, Dict[str, Any]]:
    """Expands tensors from [batch_size, ...] to [batch_size * expand_size, ...]"""
    # Do not call torch.repeat_interleave if expand_size is 1 because it clones
    # the input tensor and thus requires more memory although no change is applied
    if expand_size == 1:
        return input_ids, attention_mask
    if input_ids is not None:
        input_ids = input_ids.repeat_interleave(expand_size, dim=0)
    if attention_mask is not None:
        attention_mask = attention_mask.repeat_interleave(expand_size, dim=0)
    return input_ids, attention_mask


def _validate_generated_length(model, generation_config, input_ids_length, has_default_max_length):
    """Performs validation related to the resulting generated length"""

    # Can't throw warnings/exceptions during compilation
    if is_torchdynamo_compiling():
        return

    # 1. Max length warnings related to poor parameterization
    if has_default_max_length and generation_config.max_new_tokens is None and generation_config.max_length == 20:
        # 20 is the default max_length of the generation config
        warnings.warn(
            f"Using the model-agnostic default `max_length` (={generation_config.max_length}) to control the "
            "generation length. We recommend setting `max_new_tokens` to control the maximum length of the "
            "generation.",
            UserWarning,
        )
    if input_ids_length >= generation_config.max_length:
        input_ids_string = "input_ids"
        raise ValueError(
            f"Input length of {input_ids_string} is {input_ids_length}, but `max_length` is set to"
            f" {generation_config.max_length}. This can lead to unexpected behavior. You should consider"
            " increasing `max_length` or, better yet, setting `max_new_tokens`."
        )


def _prepare_generated_length(
    model,
    generation_config,
    has_default_max_length,
    input_ids_length,
):
    """Prepared max and min length in generation configs to avoid clashes between similar attributes"""

    if generation_config.max_new_tokens is not None:
        if not has_default_max_length and generation_config.max_length is not None:
            logger.warning(
                f"Both `max_new_tokens` (={generation_config.max_new_tokens}) and `max_length`(="
                f"{generation_config.max_length}) seem to have been set. `max_new_tokens` will take precedence. "
                "Please refer to the documentation for more information. "
                "(https://huggingface.co/docs/transformers/main/en/main_classes/text_generation)"
            )
        generation_config.max_length = generation_config.max_new_tokens + input_ids_length

    elif has_default_max_length:
        if generation_config.max_length == DreamGenerationConfig().max_length:
            generation_config.max_length = generation_config.max_length + input_ids_length
            max_position_embeddings = getattr(model.config, "max_position_embeddings", None)
            if max_position_embeddings is not None:
                generation_config.max_length = min(generation_config.max_length, max_position_embeddings)

    return generation_config


def _prepare_generation_config(
    model, generation_config: Optional[DreamGenerationConfig], **kwargs: Dict
) -> DreamGenerationConfig:
    """
    Prepares the base generation config, then applies any generation configuration options from kwargs. This
    function handles retrocompatibility with respect to configuration files.
    """
    # priority: `generation_config` argument > `model.generation_config` (the default generation config)
    using_model_generation_config = False
    if generation_config is None:
        generation_config = DreamGenerationConfig.from_model_config(model.config)
        using_model_generation_config = True

    # `torch.compile` can't compile `copy.deepcopy`, arguments in `kwargs` that are part of `generation_config`
    # will mutate the object with `.update`. As such, passing these arguments through `kwargs` is disabled -- an
    # exception will be raised in `_validate_model_kwargs`
    if not is_torchdynamo_compiling():
        generation_config = copy.deepcopy(generation_config)
        _kwargs = generation_config.update(**kwargs)
        # If `generation_config` is provided, let's fallback ALL special tokens to the default values for the model
        if not using_model_generation_config:
            if generation_config.bos_token_id is None:
                generation_config.bos_token_id = model.config.bos_token_id
            if generation_config.eos_token_id is None:
                generation_config.eos_token_id = model.config.eos_token_id
            if generation_config.pad_token_id is None:
                generation_config.pad_token_id = model.config.pad_token_id
            if generation_config.mask_token_id is None:
                generation_config.mask_token_id = model.config.mask_token_id

    return generation_config


def _prepare_special_tokens(
    model,
    generation_config: DreamGenerationConfig,
    device: Optional[Union[torch.device, str]] = None,
):
    """
    Prepares the special tokens for generation, overwriting the generation config with their processed versions
    converted to tensor.
    Note that `generation_config` is changed in place and stops being serializable after this method is called.
    That is no problem if called within `generate` (`generation_config` is a local copy that doesn't leave the
    function). However, if called outside `generate`, consider creating a copy of `generation_config` first.
    """

    # Convert special tokens to tensors
    def _tensor_or_none(token, device=None):
        if token is None:
            return token

        device = device if device is not None else model.device
        if isinstance(token, torch.Tensor):
            return token.to(device)
        return torch.tensor(token, device=device, dtype=torch.long)

    bos_token_tensor = _tensor_or_none(generation_config.bos_token_id, device=device)
    eos_token_tensor = _tensor_or_none(generation_config.eos_token_id, device=device)
    pad_token_tensor = _tensor_or_none(generation_config.pad_token_id, device=device)
    mask_token_tensor = _tensor_or_none(generation_config.mask_token_id, device=device)

    # We can have more than one eos token. Always treat it as a 1D tensor (when it exists).
    if eos_token_tensor is not None and eos_token_tensor.ndim == 0:
        eos_token_tensor = eos_token_tensor.unsqueeze(0)

    # Set pad token if unset (and there are conditions to do so)
    if pad_token_tensor is None and eos_token_tensor is not None:
        pad_token_tensor = eos_token_tensor[0]
        logger.warning(f"Setting `pad_token_id` to `eos_token_id`:{pad_token_tensor} for open-end generation.")

    # Update generation config with the updated special tokens tensors
    # NOTE: this must be written into a different attribute name than the one holding the original special tokens
    # (in their non-tensor form), in order to enable end-to-end compilation. See
    # https://pytorch.org/docs/stable/torch.compiler_cudagraph_trees.html#limitations
    generation_config._bos_token_tensor = bos_token_tensor
    generation_config._eos_token_tensor = eos_token_tensor
    generation_config._pad_token_tensor = pad_token_tensor
    generation_config._mask_token_tensor = mask_token_tensor


def _sample(
    model,
    input_ids: torch.LongTensor,
    attention_mask: Optional[torch.LongTensor],
    generation_config: DreamGenerationConfig,
    generation_tokens_hook_func,
    generation_logits_hook_func
) -> Union["DreamModelOutput", torch.LongTensor]:
    # init values
    output_history = generation_config.output_history
    return_dict_in_generate = generation_config.return_dict_in_generate
    max_length = generation_config.max_length
    mask_token_id = generation_config.mask_token_id
    steps = generation_config.steps
    eps = 1e-12
    alg = generation_config.alg
    alg_temp = generation_config.alg_temp
    temperature = generation_config.temperature
    top_p = generation_config.top_p
    top_k = generation_config.top_k

    histories = [] if (return_dict_in_generate and output_history) else None

    # pad input_ids to max_length
    x = F.pad(input_ids, (0, max_length - input_ids.shape[1]), value=mask_token_id)

    if attention_mask is not None and torch.any(attention_mask == 0.0):
        # we do not mask the [MASK] tokens so value = 1.0
        attention_mask = F.pad(attention_mask, (0, max_length - attention_mask.shape[1]), value=1.0)
        tok_idx = attention_mask.long().cumsum(-1) - 1
        tok_idx.masked_fill_(attention_mask == 0, 1)
        # attention_mask is of shape [B, N]
        # broadcast to [B, 1, N, N]
        attention_mask = torch.logical_and(
            attention_mask.unsqueeze(1).unsqueeze(-2),
            attention_mask.unsqueeze(1).unsqueeze(-1),
        )
    else:
        tok_idx = None
        attention_mask = "full"

    timesteps = torch.linspace(1, eps, steps + 1, device=x.device)

    # this allows user-defined token control of the intermediate steps
    x = generation_tokens_hook_func(None, x, None)
    for i in range(steps):
        mask_index = (x == mask_token_id)
        
        # MEMORY OPTIMIZATION: Only compute logits for the last num_logits_to_keep tokens
        # since DiffuCoder only needs logits for mask positions, and masks are typically at the end
        max_new_tokens = generation_config.max_new_tokens or 20
        num_logits_to_keep = min(max_new_tokens + 10, x.shape[1])  # Add small buffer

        # Call the model with num_logits_to_keep parameter
        model_output = model(x, attention_mask, tok_idx, num_logits_to_keep=num_logits_to_keep)
        logits = model_output.logits
        
        # Handle sparse logits - work directly with the sparse tensor to avoid memory allocation
        batch_size, actual_seq_len, vocab_size = logits.shape
        full_seq_len = x.shape[1]
        
        if actual_seq_len < full_seq_len:
            # The model returned sparse logits (only the last actual_seq_len positions)
            # We need to map the mask indices to the sparse logits
            sparse_start_idx = full_seq_len - actual_seq_len
            
            # Convert boolean mask_index to actual position indices
            mask_positions = torch.nonzero(mask_index, as_tuple=False)[:, 1]  # Get column indices (sequence positions)
            
            # Check which masked positions fall within the sparse logits range
            valid_positions = mask_positions >= sparse_start_idx
            if not torch.any(valid_positions):
                # No masked positions in the sparse logits range, skip sampling
                continue
            
            # Get the valid mask positions and convert to sparse indices
            valid_mask_positions = mask_positions[valid_positions]
            sparse_mask_indices = valid_mask_positions - sparse_start_idx
            
            # For sparse logits, we need to handle shifting differently
            # Since masked positions are at the end and we only have logits for the last num_logits_to_keep positions,
            # we need to get the logit for the position right before the first masked position
            # and concatenate it with the masked positions' logits (excluding the last one)
            
            if sparse_mask_indices.numel() > 0:
                # Get the logit for the position before the first masked position (this acts like the "first" logit in the shift)
                first_logit_idx = sparse_mask_indices[0] - 1 if sparse_mask_indices[0] > 0 else 0
                first_logit = logits[:, first_logit_idx:first_logit_idx+1, :]  # Shape: [batch, 1, vocab_size]
                
                # Concatenate the 'first logit' to shift all logits over (matching full logits logic)
                shifted_logits = torch.cat([first_logit, logits[:, :-1]], dim=1)
                
                # Extract mask logits using the sparse mask indices
                mask_logits = shifted_logits[:, sparse_mask_indices, :]
                
                # Reshape for sampling
                mask_logits = mask_logits.view(-1, mask_logits.size(-1))  # [num_masked_positions, vocab_size]
            else:
                # No valid masked positions in sparse range
                mask_logits = torch.empty(0, logits.size(-1), device=logits.device, dtype=logits.dtype)
            
            # Store the mapping for later confidence assignment
            sparse_valid_positions = valid_positions
            valid_mask_positions_global = valid_mask_positions
        else:
            # Full logits returned, use original logic
            # Shift logits as in original implementation
            logits = torch.cat([logits[:,:1], logits[:, :-1]], dim=1)
            mask_logits = logits[mask_index]
            sparse_valid_positions = None
            valid_mask_positions_global = None

        # this allows user-defined logits control of the intermediate steps
        logits = generation_logits_hook_func(i, x, logits)
        t = timesteps[i]
        s = timesteps[i + 1]

        if alg == 'origin':
            p_transfer = 1 - s / t if i < steps - 1 else 1
            
            if sparse_valid_positions is not None:
                # Handle sparse logits case for 'origin' algorithm
                # Create boolean mask for the valid positions
                valid_mask = torch.zeros_like(mask_index, dtype=torch.bool)
                for pos in valid_mask_positions_global:
                    valid_mask[0, pos] = True
                
                x0 = torch.zeros_like(x[valid_mask], device=model.device, dtype=torch.long) + mask_token_id
                transfer_index_t_s = torch.rand(*x0.shape, device=model.device) < p_transfer
                _, x0[transfer_index_t_s] = sample_tokens(mask_logits[transfer_index_t_s], temperature=temperature, top_p=top_p, top_k=top_k)
                x[valid_mask] = x0.clone()
            else:
                # Full logits case - original logic
                x0 = torch.zeros_like(x[mask_index], device=model.device, dtype=torch.long) + mask_token_id
                transfer_index_t_s = torch.rand(*x0.shape, device=model.device) < p_transfer
                _, x0[transfer_index_t_s] = sample_tokens(mask_logits[transfer_index_t_s], temperature=temperature, top_p=top_p, top_k=top_k)
                x[mask_index] = x0.clone()
        else:
            if alg == 'maskgit_plus':
                confidence, x0 = sample_tokens(mask_logits, temperature=temperature, top_p=top_p, top_k=top_k)
            elif alg == 'topk_margin':
                confidence, x0 = sample_tokens(mask_logits, temperature=temperature, top_p=top_p, top_k=top_k, margin_confidence=True)
            elif alg == 'entropy':
                confidence, x0 = sample_tokens(mask_logits, temperature=temperature, top_p=top_p, top_k=top_k, neg_entropy=True)
            else:
                raise RuntimeError(f"Unknown alg: {alg}")
            num_mask_token = mask_index.sum() / mask_index.shape[0]
            number_transfer_tokens = int(num_mask_token * (1 - s / t)) if i < steps - 1 else int(num_mask_token)
            full_confidence = torch.full_like(x, -torch.inf, device=model.device, dtype=logits.dtype)
            
            if sparse_valid_positions is not None:
                # Handle sparse logits case - only assign confidence for positions in sparse range
                # Create boolean mask for the valid positions (reuse the same logic as above)
                valid_mask = torch.zeros_like(mask_index, dtype=torch.bool)
                for pos in valid_mask_positions_global:
                    valid_mask[0, pos] = True
                full_confidence[valid_mask] = confidence
                # DON'T update x here - we only update x in the transfer logic below
                effective_mask_index = valid_mask  # Use valid_mask as the effective mask for downstream logic
            else:
                # Full logits case
                full_confidence[mask_index] = confidence
                effective_mask_index = mask_index  # Use original mask_index for downstream logic
                
            if number_transfer_tokens > 0:
                if alg_temp is None or alg_temp == 0:
                    _, transfer_index = torch.topk(full_confidence, number_transfer_tokens)
                else:
                    full_confidence = full_confidence / alg_temp
                    full_confidence = F.softmax(full_confidence, dim=-1)
                    transfer_index = torch.multinomial(full_confidence, num_samples=number_transfer_tokens)
                
                # Unified transfer logic for both full and sparse cases
                x_ = torch.zeros_like(x, device=model.device, dtype=torch.long) + mask_token_id
                x_[effective_mask_index] = x0.clone()
                row_indices = torch.arange(x.size(0), device=model.device).unsqueeze(1).expand_as(transfer_index)
                x[row_indices,transfer_index] = x_[row_indices,transfer_index]

        # this allows user-defined token control of the intermediate steps
        x = generation_tokens_hook_func(i, x, logits)

        if histories is not None:
            histories.append(x.clone())
    
    if return_dict_in_generate:
        return DreamModelOutput(
            sequences=x,
            history=histories,
        )
    else:
        return x


@torch.no_grad()
def memory_efficient_diffusion_generate(
    model,
    inputs: Optional[torch.Tensor] = None,
    generation_config: Optional[DreamGenerationConfig] = None,
    **kwargs,
) -> Union["DreamModelOutput", torch.LongTensor]:
    """
    Memory-efficient diffusion generation for Dream/DiffuCoder models.
    This function uses num_logits_to_keep to avoid storing full logits for very long sequences.
    """
    # 1. Handle `generation_config` and kwargs that might update it, and validate the `.generate()` call
    generation_config = _prepare_generation_config(model, generation_config, **kwargs)
    generation_tokens_hook_func = kwargs.pop("generation_tokens_hook_func", lambda step, x, logits: x)
    generation_logits_hook_func = kwargs.pop("generation_logits_hook_func", lambda step, x, logits: logits)

    # 2. Define model inputs
    assert inputs is not None
    input_ids = inputs
    device = input_ids.device
    attention_mask = kwargs.pop("attention_mask", None)
    _prepare_special_tokens(model, generation_config, device=device)

    # 3. Prepare `max_length`.
    input_ids_length = input_ids.shape[-1]
    has_default_max_length = kwargs.get("max_length") is None and generation_config.max_length is not None
    generation_config = _prepare_generated_length(
        model=model,
        generation_config=generation_config,
        has_default_max_length=has_default_max_length,
        input_ids_length=input_ids_length,
    )

    _validate_generated_length(model, generation_config, input_ids_length, has_default_max_length)
    
    # 4. Check input_ids
    if not is_torchdynamo_compiling() and model.device.type != input_ids.device.type:
        warnings.warn(
            "You are calling .generate() with the `input_ids` being on a device type different"
            f" than your model's device. `input_ids` is on {input_ids.device.type}, whereas the model"
            f" is on {model.device.type}. You may experience unexpected behaviors or slower generation."
            " Please make sure that you have put `input_ids` to the"
            f" correct device by calling for example input_ids = input_ids.to('{model.device.type}') before"
            " running `.generate()`.",
            UserWarning,
        )
    if (
        hasattr(generation_config, "pad_token_id") and
        torch.any(input_ids == generation_config.pad_token_id) and 
        attention_mask is None
    ):
        warnings.warn(
            "Padding was detected but no attention mask is passed here. For correct "
            "generation results, please set `attention_mask` when batch-padding inputs.",
            UserWarning,
        )

    input_ids, attention_mask = _expand_inputs_for_generation(
        expand_size=generation_config.num_return_sequences,
        input_ids=input_ids,
        attention_mask=attention_mask 
    )

    result = _sample(
        model,
        input_ids,
        attention_mask=attention_mask,
        generation_config=generation_config,
        generation_tokens_hook_func=generation_tokens_hook_func,
        generation_logits_hook_func=generation_logits_hook_func
    )
    return result


def patch_diffusion_generate(model):
    """
    Patch a DiffuCoder model's diffusion_generate method with memory-efficient version.
    
    Args:
        model: The DiffuCoder model to patch
        
    Returns:
        The model with patched diffusion_generate method
    """
    # Store the original method if it exists
    original_diffusion_generate = getattr(model, 'diffusion_generate', None)
    
    def patched_diffusion_generate(
        input_ids,
        attention_mask=None,
        max_new_tokens=None,
        max_length=None,
        output_history=False,
        return_dict_in_generate=False,
        steps=512,
        temperature=0.0,
        top_p=None,
        top_k=None,
        alg='origin',
        alg_temp=None,
        eps=1e-3,
        **kwargs
    ):
        """Memory-efficient diffusion generation with exact same interface as original."""
        
        # Create generation config from parameters
        generation_config = DreamGenerationConfig(
            max_new_tokens=max_new_tokens,
            max_length=max_length,
            output_history=output_history,
            return_dict_in_generate=return_dict_in_generate,
            steps=steps,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            alg=alg,
            alg_temp=alg_temp,
            eps=eps,
            mask_token_id=getattr(model.config, 'mask_token_id', 32000),
            **kwargs
        )
        
        # Use our memory-efficient generation
        return memory_efficient_diffusion_generate(
            model=model,
            inputs=input_ids,
            generation_config=generation_config,
            attention_mask=attention_mask
        )
    
    # Replace the diffusion_generate method
    model.diffusion_generate = patched_diffusion_generate
    logger.info("Patched DiffuCoder model's diffusion_generate method with memory-efficient version")
    return model
