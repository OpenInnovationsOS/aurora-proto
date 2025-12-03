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
