"""
Utilities and helper functions for LongDLLM.
"""

from typing import Optional


def validate_model_name(model_name_or_path: str) -> Optional[str]:
    """
    Validate and normalize model name/path.
    
    Returns:
        str: Normalized model name, or None if not supported
    """
    supported_models = {
        "apple/DiffuCoder-7B-Instruct": "diffucoder",
        "GSAI-ML/LLaDA-8B-Instruct": "llada",
    }
    
    # Direct match
    if model_name_or_path in supported_models:
        return model_name_or_path
    
    # Partial match for local paths or variations
    model_lower = model_name_or_path.lower()
    if 'diffucoder' in model_lower:
        return "apple/DiffuCoder-7B-Instruct"
    elif 'llada' in model_lower:
        return "GSAI-ML/LLaDA-8B-Instruct"
    
    return None


def get_model_info(model_name_or_path: str) -> dict:
    """Get information about a supported model."""
    model_info = {
        "apple/DiffuCoder-7B-Instruct": {
            "type": "diffucoder",
            "architecture": "dream",
            "context_length": 4096,
            "recommended_extension": 16384,
            "description": "Apple's DiffuCoder - A diffusion-based code generation model"
        },
        "GSAI-ML/LLaDA-8B-Instruct": {
            "type": "llada", 
            "architecture": "llada",
            "context_length": 4096,
            "recommended_extension": 32768,
            "description": "GSAI's LLaDA - A diffusion-based language model"
        }
    }
    
    normalized_name = validate_model_name(model_name_or_path)
    if normalized_name:
        return model_info[normalized_name]
    else:
        return {
            "type": "unknown",
            "architecture": "unknown", 
            "context_length": None,
            "recommended_extension": None,
            "description": f"Unknown model: {model_name_or_path}"
        }
