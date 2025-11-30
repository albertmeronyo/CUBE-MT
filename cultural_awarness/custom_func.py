from typing import Dict
import logging
import requests
from pathlib import Path
from PIL import Image
from util import *
from huggingface_hub import InferenceClient
from PIL import Image
import time
from huggingface_hub.errors import HfHubHTTPError

def post_process_speech(response : Dict[str, str], logger: logging.Logger, save_path: Path) -> bool: 
    response = response.json()
    if not isinstance(response, dict) and "audio" in response:
        logger.error("Invalid response format from Kokoro TTS mode;, it should return a dictionary with an 'audio' key.")
        return False
    
    url = response["audio"]["url"]
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        logger.error(f"Failed to download audio from Kokoro TTS model, status code: {response.status_code}")
        logger.error(f"Response content: {response.content}")
        response.raise_for_status() 
        return False
    
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    if not is_valid_wav(str(save_path), logger):
        logger.error(f"Downloaded audio file is not a valid WAV: {save_path}")
        raise ValueError(f"Downloaded audio file is not a valid WAV: {save_path}") 
    
    return True

def send_request_qwen(prompt: str, save_path: str, logger: logging.Logger)->Image: 
    
    client = InferenceClient(
        provider="fal-ai",
        api_key=os.environ["HF_TOKEN"]
    )
    try: 
        image = client.text_to_image(
            prompt,
            model="Qwen/Qwen-Image",
        )
    except HfHubHTTPError as e: 
        status = getattr(getattr(e, "response", None), "status_code", None)
        if status == 422:
            logger.info(f"Qwen-Image model could not process the prompt: {prompt}. Error: {e}, skipping image generation.")
            return True
        
    if not isinstance(image, Image.Image):
        logger.error("Invalid response format from Qwen-Image model, it should return a PIL.Image object.")
        return False
    
    image.save(save_path)
    time.sleep(5)  
    return True