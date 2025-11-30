import os
import logging
from typing import Dict
import requests
from pathlib import Path
from util import *
import os 
from dotenv import load_dotenv
import os

from custom_func import post_process_speech, send_request_qwen


load_dotenv()


HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
}

# Ref: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct?inference_api=true&inference_provider=featherless-ai&language=python
TEXT_MODEL_PHI3_MINI_4K_INSTRUCT = {
    "model": "microsoft/Phi-3-mini-4k-instruct", 
    "endpoint": "https://router.huggingface.co/featherless-ai/v1/chat/completions", 
    "name": "phi3_mini_4k_instruct"
}

# Ref: https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407?inference_api=true&inference_provider=nebius&language=python
TEXT_MODEL_MISTRAL_NEMO_INSTRUCT = {
    "model":  "mistralai/Mistral-Nemo-Instruct-2407", 
    "endpoint":  "https://router.huggingface.co/nebius/v1/chat/completions",
    "name": "mistral_nemo_instruct"
}

# Ref: https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407?inference_api=true&inference_provider=nebius&language=python
# CUBE-MT
TEXT_MODEL_LLAMA_3_1_8B_INSTRUCT = {
    "model": "accounts/fireworks/models/llama-v3p1-8b-instruct", 
    "endpoint": "https://router.huggingface.co/fireworks-ai/inference/v1/chat/completions",
     "name": "llama_3_1_8b_instruct"
}

# Ref: https://huggingface.co/stabilityai/stable-diffusion-3-medium-diffusers
IMAGE_MODEL_DIFFUSION_3_MEDIUM_DIFFUSERS = {
    "model": "stabilityai/stable-diffusion-3-medium-diffusers",
    "endpoint": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3-medium-diffusers",
    "name": "diffusion_3_medium_diffusers"
}


# Ref: https://huggingface.co/hexgrad/Kokoro-82M?inference_api=true&inference_provider=fal-ai&language=python
TEXT_TO_SPEECH_KOKORO = {
    "endpoint": "https://router.huggingface.co/fal-ai/fal-ai/kokoro/american-english", 
    "field": "text", 
    "post_process": post_process_speech, 
    "name": "kokoro"
}
   
# Ref: https://huggingface.co/facebook/fastspeech2-en-ljspeech
TEXT_TO_SPEECH_FASTSPEECH2 = {
    "endpoint": "https://api-inference.huggingface.co/models/facebook/fastspeech2-en-ljspeech", 
    "name": "fastspeech2"
}

# Ref:https://huggingface.co/facebook/musicgen-small
MUSIC_GEN_SMALL = {
    "endpoint": "https://api-inference.huggingface.co/models/facebook/musicgen-small", 
    "name": "musicgen_small"
}

# Ref: https://huggingface.co/tencent/Hunyuan3D-2
HUNYUAN_3D2 = {
    "endpoint": "https://huggingface.co/spaces/tencent/Hunyuan3D-2", 
    "name": "hunyuan_3d2"
}

# Note: This is a local deployment of Hunyuan3D-2 model, in case the public API is not accessible
LOCAL_HUNYUAN_3D2 = {
    "endpoint":  "http://localhost:8080/generate",
    "name": "Hunyuan3D-2"
}


QWEN3_NEXT_80B_A3B_INSTRUCT = {
    "model": "Qwen/Qwen3-Next-80B-A3B-Instruct:novita",
    "endpoint": "https://router.huggingface.co/v1/chat/completions"
}

# Ref: https://huggingface.co/openai/gpt-oss-120b
GPT_OSS_120B = {
    "model": "openai/gpt-oss-120b:fireworks-ai",   
    "endpoint": "https://router.huggingface.co/v1/chat/completions", 
    "name": "gpt_oss_120b"
    
}

# Ref: https://huggingface.co/black-forest-labs/FLUX.1-schnell
FLUX_1_SCHNELL = {
    "endpoint": "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell", 
    "name": "flux_1_schnell"
    
}

# Ref: https://huggingface.co/ResembleAI/chatterbox?inference_api=true&inference_provider=fal-ai&language=python&client=requests
CHATTERBOX = {
    "endpoint":  "https://router.huggingface.co/fal-ai/fal-ai/chatterbox/text-to-speech", 
    "field": "text", 
    "post_process": post_process_speech, 
    "name": "chatterbox"
}

# Ref: https://huggingface.co/Qwen/Qwen-Image
QWEN_IMAGE = {
    "custom_send": send_request_qwen, 
    "post_process": None,
    "name": "qwen_image"
}



