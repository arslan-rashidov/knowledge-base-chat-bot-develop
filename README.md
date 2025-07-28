# knowledge-base-chat-bot-develop

# Preparation

## Anaconda Installation
```
cd /tmp
curl -O https://repo.anaconda.com/archive/Anaconda3-2025.06-0-MacOSX-x86_64.sh
bash Anaconda3-2025.06-0-MacOSX-x86_64.sh
cd /workspace
```

## Setting Environment
```
conda create --name kb_dev python==3.10 --yes
conda activate kb_dev
```

## Install Dependencies
```
sudo apt install tesseract-ocr tesseract-ocr-rus
```
```
pip install numpy==1.* docx2txt langchain_huggingface langchain_core langchain_community FlagEmbedding docling streamlit faiss-gpu vllm pymupdf pytesseract flashinfer-python
```
if vllm serving VL crashes:
```
pip install "transformers<4.53.0"
```

# VLLM Model Servings

## QWEN-2.5-VL(https://github.com/QwenLM/Qwen2.5-VL)
### 3B-Instruct
```
# No-Quant
vllm serve Qwen/Qwen2.5-VL-3B-Instruct --port 8000 --host 0.0.0.0 --dtype bfloat16

vllm serve Qwen/Qwen2.5-VL-3B-Instruct --port 8000 --host 0.0.0.0 --dtype bfloat16 --quantization bitsandbytes

# AWQ
vllm serve Qwen/Qwen2.5-VL-3B-Instruct-AWQ --port 8000 --host 0.0.0.0 --dtype bfloat16
```

### 7B-Instruct
```
```

### 32B-Instruct-AWQ
```
vllm serve Qwen/Qwen2.5-VL-32B-Instruct-AWQ --port 8000 --host 0.0.0.0 --dtype bfloat16 --kv-cache-dtype fp8   --max-model-len 512   --max-num-batched-tokens 512   --max-num-seqs 1   --enforce-eager   --tensor-parallel-size 1 --gpu_memory_utilization 0.95
```

### QWEN-14B
```
vllm serve Qwen/Qwen3-14B-AWQ --port 8000 --host 0.0.0.0 --max-model-len 9192 --enforce-eager  --tensor-parallel-size 1 --gpu_memory_utilization 0.8
```

### Vikhr
```
vllm serve --dtype half --max-model-len 32000 -tp 1 Vikhrmodels/Vikhr-Llama3.1-8B-Instruct-R-21-09-24 --gpu_memory_utilization 0.8
```

# Utils

### Free used by vllm VRAM
```
sudo fuser -v /dev/nvidia*
kill -9 ...
```

```
kill -9 $(lsof -t -i:9000)
```

# GPU Usage Results

RTX 3090 - QWEN-2.5-VL-3B-Instruct(No Quant)
