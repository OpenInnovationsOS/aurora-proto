# core/aurora_base.py
"""
AURORA-Base: Foundation Model Core
- Loads Qwen2.5-7B-Instruct (AWQ quantized for 12GB VRAM)
- Fallback to CPU if no GPU
- Supports tool_call output parsing (for agent integration)
- Compatible with vLLM ≥0.5.4
"""

import os
import torch
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer


class ToolCall(BaseModel):
    """Structured tool call output (mirroring OpenAI function_call schema)"""
    name: str
    arguments: Dict[str, Any]


class AuroraGenerationConfig(BaseModel):
    temperature: float = 0.3
    top_p: float = 0.9
    max_tokens: int = 2048
    stop: Optional[List[str]] = None
    stream: bool = False


class AuroraBase:
    def __init__(
        self,
        model_id: str = "Qwen/Qwen2.5-7B-Instruct",
        quantization: str = "awq",  # or "none", "gguf" (not implemented here)
        max_model_len: int = 32768,
        dtype: str = "auto",
        gpu_memory_utilization: float = 0.9,
        enforce_eager: bool = True,  # Avoid CUDA graphs on small GPUs
        trust_remote_code: bool = True,
    ):
        self.model_id = model_id
        self.quantization = quantization
        self.max_model_len = max_model_len

        # Auto-detect device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔍 Detected device: {self.device.upper()}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=trust_remote_code
        )
        if self.tokenizer.chat_template is None:
            # Qwen2.5 has built-in chat template — but fallback if needed
            self.tokenizer.chat_template = "{% for message in messages %}{{'<|im_start|>'


from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

class AuroraBase:
    def __init__(self, model_id: str, quantization: str = None, max_model_len: int = 32768):
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # vLLM for fast inference
        kwargs = {}
        if quantization == "awq":
            kwargs["quantization"] = "awq"
            kwargs["dtype"] = "float16"
        elif quantization == "gguf":
            raise NotImplementedError("GGUF requires llama.cpp backend (see deploy/edge/)")
        
        self.llm = LLM(
            model=model_id,
            max_model_len=max_model_len,
            enforce_eager=True,  # Avoid CUDA graph issues on small GPUs
            **kwargs
        )
        self.sampling_params = SamplingParams(
            temperature=0.3,
            top_p=0.9,
            max_tokens=2048
        )

    def generate(self, prompt: str, **kwargs) -> str:
        sampling = self.sampling_params.clone()
        sampling.update(**kwargs)
        outputs = self.llm.generate([prompt], sampling)
        return outputs[0].outputs[0].text.strip()
