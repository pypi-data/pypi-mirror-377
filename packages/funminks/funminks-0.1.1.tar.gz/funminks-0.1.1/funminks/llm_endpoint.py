import os, torch, random
from transformers import AutoTokenizer, AutoModelForCausalLM


def load_llm(model_dir: str):
    global model, tok
    # Pick dtype based on GPU capability (A100/H100 -> bfloat16; V100 -> float16)
    major, _ = torch.cuda.get_device_capability(0)
    dtype = torch.bfloat16 if major >= 8 else torch.float16

    print("GPUs:", torch.cuda.device_count(), "| capability[0] =", major)
    print("Using dtype:", dtype)

    # Load tokenizer & model strictly from disk
    tok = AutoTokenizer.from_pretrained(model_dir, local_files_only=True, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        local_files_only=True,
        torch_dtype=dtype,
        device_map="auto",          # <-- shards across the 4 GPUs
        low_cpu_mem_usage=True
    )
    return {'model': model, 'tok': tok}


