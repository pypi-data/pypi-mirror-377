# icw/attention.py
"""A utility for dynamically patching Hugging Face models to enable on-the-fly INT8 KV cache quantization.

This allows for a significant reduction in memory consumption when working with long
contexts, unlocking inference with sequences that would otherwise cause Out-of-Memory (OOM) errors.

Key Improvements:
1. Model Support: Llama, Mistral, Gemma, Phi-3, Qwen2.
2. Higher Precision: Quantization is performed per-head, which preserves information better than per-tensor.
3. Clean Code: Logic is refactored into helper functions for better readability.
"""

import torch
import torch.nn as nn
import warnings
import math
from typing import Optional, Tuple

# --- Dynamic import of attention modules for supported models ---
# This allows the module to be flexible and easily extensible.
_SUPPORTED_MODULES = []
_MODEL_HELPERS = {}

try:
    from transformers.models.llama.modeling_llama import LlamaAttention, apply_rotary_pos_emb, repeat_kv
    _SUPPORTED_MODULES.append(LlamaAttention)
    # Store common functions that can be used by other models
    _MODEL_HELPERS['default'] = {'apply_rotary_pos_emb': apply_rotary_pos_emb, 'repeat_kv': repeat_kv}
except ImportError:
    pass

try:
    from transformers.models.mistral.modeling_mistral import MistralAttention
    _SUPPORTED_MODULES.append(MistralAttention)
except ImportError:
    pass

try:
    from transformers.models.gemma.modeling_gemma import GemmaAttention
    _SUPPORTED_MODULES.append(GemmaAttention)
except ImportError:
    pass

try:
    from transformers.models.phi3.modeling_phi3 import Phi3Attention
    _SUPPORTED_MODULES.append(Phi3Attention)
except ImportError:
    pass

try:
    # Qwen2 uses its own RoPE and repeat_kv implementations, but the core forward pass is compatible.
    from transformers.models.qwen2.modeling_qwen2 import Qwen2Attention, apply_rotary_pos_emb, repeat_kv
    _SUPPORTED_MODULES.append(Qwen2Attention)
    _MODEL_HELPERS[Qwen2Attention] = {'apply_rotary_pos_emb': apply_rotary_pos_emb, 'repeat_kv': repeat_kv}
except ImportError:
    pass

# --- Helper functions for quantization and dequantization ---

def _quantize_kv(key_states: torch.Tensor, value_states: torch.Tensor) -> Tuple:
    """Quantizes K and V tensors to INT8 with per-head scale calculation."""
    # Calculate scale over the last two dimensions (sequence length and head dimension).
    # This provides a separate scale for each head in the batch.
    k_scale = key_states.abs().amax(dim=(-2, -1), keepdim=True) / 127.0
    v_scale = value_states.abs().amax(dim=(-2, -1), keepdim=True) / 127.0

    # Prevent division by zero
    k_scale = torch.clamp(k_scale, min=1e-8)
    v_scale = torch.clamp(v_scale, min=1e-8)

    k_quant = (key_states / k_scale).round().to(torch.int8)
    v_quant = (value_states / v_scale).round().to(torch.int8)
        
    return k_quant, k_scale, v_quant, v_scale

def _dequantize_kv(past_key_value: Tuple) -> Tuple[torch.Tensor, torch.Tensor]:
    """Dequantizes K and V from INT8 format or returns them as is."""
    if len(past_key_value) == 4:
        # Quantized format: (k_quant, k_scale, v_quant, v_scale)
        k_quant, k_scale, v_quant, v_scale = past_key_value
        # Ensure dequantization happens in the same dtype as the scale
        past_key = k_quant.to(k_scale.dtype) * k_scale
        past_value = v_quant.to(v_scale.dtype) * v_scale
        return past_key, past_value
    elif len(past_key_value) == 2:
        # Standard float format
        return past_key_value
    else:
        raise ValueError(f"Unexpected past_key_value format. Expected 2 or 4 elements, got {len(past_key_value)}")

# --- Main patched forward method ---

def _patched_attention_forward(
    self,
    hidden_states: torch.Tensor,
    attention_mask: Optional[torch.Tensor] = None,
    position_ids: Optional[torch.LongTensor] = None,
    past_key_value: Optional[Tuple[torch.Tensor]] = None,
    output_attentions: bool = False,
    use_cache: bool = False,
    **kwargs,
) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[Tuple[torch.Tensor]]]:
    if "padding_mask" in kwargs:
        warnings.warn(
            "The `padding_mask` argument is deprecated and will be removed in a future version. Please use `attention_mask` instead."
        )
    bsz, q_len, _ = hidden_states.size()

    # Get the required helper functions for the current model
    helpers = _MODEL_HELPERS.get(type(self), _MODEL_HELPERS['default'])
    _apply_rotary_pos_emb = helpers['apply_rotary_pos_emb']
    _repeat_kv = helpers['repeat_kv']

    query_states = self.q_proj(hidden_states)
    key_states = self.k_proj(hidden_states)
    value_states = self.v_proj(hidden_states)

    query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
    key_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
    value_states = value_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)

    kv_seq_len = key_states.shape[-2]
        
    if past_key_value is not None:
        # Dequantize the KV cache if it was stored in INT8
        past_key, past_value = _dequantize_kv(past_key_value)
        kv_seq_len += past_key.shape[-2]
        
    # RoPE
    cos, sin = self.rotary_emb(value_states, seq_len=kv_seq_len)
    query_states, key_states = _apply_rotary_pos_emb(query_states, key_states, cos, sin, position_ids)

    if past_key_value is not None:
        # Concatenate with previous values
        key_states = torch.cat([past_key, key_states], dim=2)
        value_states = torch.cat([past_value, value_states], dim=2)

    if use_cache:
        # Quantize the full K and V tensors before caching
        past_key_value = _quantize_kv(key_states, value_states)
    else:
        past_key_value = None

    # GQA / MQA
    key_states = _repeat_kv(key_states, self.num_key_value_groups)
    value_states = _repeat_kv(value_states, self.num_key_value_groups)

    attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) / math.sqrt(self.head_dim)

    if attention_mask is not None:
        attn_weights = attn_weights + attention_mask

    # Softmax and attention output
    attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query_states.dtype)
    attn_output = torch.matmul(attn_weights, value_states)
        
    attn_output = attn_output.transpose(1, 2).contiguous()
    attn_output = attn_output.reshape(bsz, q_len, self.hidden_size)

    attn_output = self.o_proj(attn_output)

    if not output_attentions:
        attn_weights = None

    return attn_output, attn_weights, past_key_value

def patch_model_with_int8_kv_cache(model: nn.Module):
    """Recursively finds all supported attention modules in a model and replaces their
    `forward` method with a custom implementation that uses INT8 KV cache.

    Args:
        model (nn.Module): The Hugging Face model to patch.
    
    Example:
        >>> from transformers import AutoModelForCausalLM
        >>> model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
        >>> patch_model_with_int8_kv_cache(model)
        >>> # The model is now ready for memory-efficient usage.
    """
    if getattr(model, "_is_kv_quant_patched", False):
        print("[INFO] Model has already been patched for INT8 KV cache. Skipping.")
        return

    if not _SUPPORTED_MODULES:
        warnings.warn("Could not apply patch for KV cache. No supported attention modules found. "
                      "Please ensure `transformers` is installed and you are using a compatible model.")
        return

    patched_targets = tuple(_SUPPORTED_MODULES)
    found_and_patched_count = 0
        
    for name, module in model.named_modules():
        if isinstance(module, patched_targets):
            # Replace the forward method, binding it to the module instance
            module.forward = _patched_attention_forward.__get__(module, type(module))
            found_and_patched_count += 1
            
    if found_and_patched_count > 0:
        supported_class_names = [cls.__name__ for cls in _SUPPORTED_MODULES]
        print(f"[INFO] Model patched successfully. Replaced {found_and_patched_count} modules.")
        print(f"[INFO] Supported module types: {supported_class_names}")
        model._is_kv_quant_patched = True
    else:
        warnings.warn("No compatible attention modules found in the model to patch.")
