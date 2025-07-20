# import os 

# HEADERS = {
#     "Authorization": f"Bearer {os.getenv['HF_TOKEN']}",
# }

# # Ref: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct?inference_api=true&inference_provider=featherless-ai&language=python
# TEXT_MODEL_PHI3_MINI_4K_INSTRUCT = {
#     "model": "microsoft/Phi-3-mini-4k-instruct", 
#     "endpoint": "https://router.huggingface.co/featherless-ai/v1/chat/completions", 
# }

# # Ref: https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407?inference_api=true&inference_provider=nebius&language=python
# TEXT_MODEL_MISTRAL_NEMO_INSTRUCT = {
#     "model":  "mistralai/Mistral-Nemo-Instruct-2407", 
#     "endpoint":  "https://router.huggingface.co/nebius/v1/chat/completions",
    
# }

# # Ref: https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407?inference_api=true&inference_provider=nebius&language=python
# TEXT_MODEL_LLAMA_3_1_8B_INSTRUCT = {
#     "model": "accounts/fireworks/models/llama-v3p1-8b-instruct", 
#     "endpoint": "https://router.huggingface.co/fireworks-ai/inference/v1/chat/completions",
# }

# # Ref: https://huggingface.co/stabilityai/stable-diffusion-3-medium-diffusers
# IMAGE_MODEL_DIFFUSION_3_MEDIUM_DIFFUSERS = {
#     "model": "stabilityai/stable-diffusion-3-medium-diffusers",
#     "endpoint": "https://api-inference.huggingface.co/models",
# }

# # Ref: https://huggingface.co/hexgrad/Kokoro-82M?inference_api=true&inference_provider=fal-ai&language=python
# TEXT_TO_SPEECH_KOKORO = {
#     "endpoint": "https://router.huggingface.co/fal-ai/fal-ai/kokoro/american-english"
# }

# # Ref: https://huggingface.co/facebook/fastspeech2-en-ljspeech
# TEXT_TO_SPEECH_FASTSPEECH2 = {
#     "endpoint": "https://api-inference.huggingface.co/models/facebook/fastspeech2-en-ljspeech"
# }

# # Ref:https://huggingface.co/facebook/musicgen-small
# MUSIC_GEN_SMALL = {
    
# }

import os 

HEADERS = {
    "Authorization": f"Bearer {os.getenv['HF_TOKEN']}",
}

# Ref: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct?inference_api=true&inference_provider=featherless-ai&language=python
TEXT_MODEL_PHI3_MINI_4K_INSTRUCT = {
    "model": "microsoft/Phi-3-mini-4k-instruct", 
    "endpoint": "https://router.huggingface.co/featherless-ai/v1/chat/completions", 
}

# Ref: https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407?inference_api=true&inference_provider=nebius&language=python
TEXT_MODEL_MISTRAL_NEMO_INSTRUCT = {
    "model":  "mistralai/Mistral-Nemo-Instruct-2407", 
    "endpoint":  "https://router.huggingface.co/nebius/v1/chat/completions",
    
}

# Ref: https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407?inference_api=true&inference_provider=nebius&language=python
TEXT_MODEL_LLAMA_3_1_8B_INSTRUCT = {
    "model": "accounts/fireworks/models/llama-v3p1-8b-instruct", 
    "endpoint": "https://router.huggingface.co/fireworks-ai/inference/v1/chat/completions",
}

# Ref: https://huggingface.co/stabilityai/stable-diffusion-3-medium-diffusers
IMAGE_MODEL_DIFFUSION_3_MEDIUM_DIFFUSERS = {
    "model": "stabilityai/stable-diffusion-3-medium-diffusers",
    "endpoint": "https://api-inference.huggingface.co/models/",
}

# Ref: https://huggingface.co/hexgrad/Kokoro-82M?inference_api=true&inference_provider=fal-ai&language=python
TEXT_TO_SPEECH_KOKORO = {
    "endpoint": "https://router.huggingface.co/fal-ai/fal-ai/kokoro/american-english"
}

# Ref: https://huggingface.co/facebook/fastspeech2-en-ljspeech
TEXT_TO_SPEECH_FASTSPEECH2 = {
    "endpoint": "https://api-inference.huggingface.co/models/facebook/fastspeech2-en-ljspeech"
}

# Ref:https://huggingface.co/facebook/musicgen-small
MUSIC_GEN_SMALL = {
    "endpoint": "https://api-inference.huggingface.co/models/facebook/musicgen-small"
}

HUNYUAN_3D2 = {
    "endpoint": "https://huggingface.co/spaces/tencent/Hunyuan3D-2"
}


