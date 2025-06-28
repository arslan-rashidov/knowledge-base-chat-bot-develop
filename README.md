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
pip install vllm
```

# VLLM Model Servings

## QWEN-2.5-VL(https://github.com/QwenLM/Qwen2.5-VL)
### 3B-Instruct
```
pip install "transformers<4.53.0"
vllm serve Qwen/Qwen2.5-VL-3B-Instruct --port 8000 --host 0.0.0.0 --dtype bfloat16
```

### 7B-Instruct
```
```
