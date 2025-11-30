import requests
import time
from models import *
import logging
from moviepy import AudioFileClip, ImageClip, CompositeAudioClip
from typing import Optional, Dict, Tuple, List
from util import * 
from pathlib import Path
import pybraille
from gradio_client import Client, handle_file
import shutil
from datetime import datetime
from models import * 
from PIL import Image
import io
import unicodedata
import base64
import os
from huggingface_hub import InferenceClient

DEMONYM = {
    "Austria": "Austrian",
     "India": "Indian",
    "Brazil": "Brazilian",
    "Turkey": "Turkish",
    "Denmark": "Danish",
    "France": "French",
    "Nigeria": "Nigerian",
    "Germany": "German",
    "Ireland": "Irish",
    "Italy": "Italian",
    "Japan": "Japanese",
    "Mexico": "Mexican",
    "Netherlands": "Dutch",
    "Poland": "Polish",
    "Russia": "Russian",
    "Spain": "Spanish",
    "Switzerland": "Swiss",
    "UK": "British",
    "US": "American",
   "USA": "American",
    "United States": "American"
}

def get_text_request(content: str, model: str)-> Dict[str, str]:
    return {
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "model": model,
    }

def get_speech_request(inputs: str, field:str=None) -> Dict[str, str]:
    field = "inputs" if field is None else field
    return {
        field: inputs,
    }

def get_image_request(inputs: str) -> Dict[str, str]:
    return {
        "inputs": "{}".format(inputs),
    }

def get_music_request(inputs: str) -> Dict[str, str]:
    return {
        "inputs": inputs,
    }

def send_request(api_url : str, payload :str, logger: logging.Logger, attempts: int = 3, 
                 sleep_time: int = 5, headers: Dict[str, str] = None) -> Optional[requests.Response]:
    
    if headers is None:
        headers = HEADERS
    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        return response
    elif response.status_code == 429:
        logger.info("Rate limit exceeded. Retrying after 5 seconds...")
        time.sleep(5)
        logger.info(f"Retrying request...Atempts left: {attempts - 1}")
        if attempts > 1:
            return send_request(api_url, HEADERS, payload, logger, attempts - 1)
        
        logger.error(f"Max attempts reached. Request failed. " \
                     f"Response: {response.text}" \
                     f"Request failed for API: {api_url}" \
                     f" with payload: {payload}")
    else: 
        time.sleep(sleep_time)
        logger.error(f"Request URL: {api_url}")
        logger.error(f"Request Payload: {payload}")
        logger.error(f"Response headers: {dict(response.headers)}")
        logger.error(f"Request failed with status code {response.status_code}. " \
                        f"Response: {response.text}" \
                        f"Trying again in {sleep_time} seconds..." if attempts > 1 else "")
        if attempts > 1:
            return send_request(api_url, payload, logger, attempts - 1, sleep_time * attempts)

    return None
    
def gen_text(item : Dict[str, str], logger: logging.Logger, 
             output_dir: str, index: int, config: Optional[Dict[str, str]]=None) -> Tuple[bool, Optional[str]]:
    
  
    country = ""
    if item["country"] != "": 
        country = f'from {DEMONYM[item["country"]]}'
        
    text_prompt = "A one sentence textual description of {}{} {}".format(
        item["name"], country, item["domain"]
    )
    
    model = None
    endpoint = None
    text_gen = None

    if config is None: 
        model = QWEN3_NEXT_80B_A3B_INSTRUCT["model"]
        endpoint = QWEN3_NEXT_80B_A3B_INSTRUCT["endpoint"]
            
    else:
        model = config["model"]
        endpoint = config["endpoint"]

    request = get_text_request(text_prompt, model)
    response = send_request(endpoint, request, logger)
    
    if response is None:
        logger.error(f"Failed to generate text for item {item['id']}")
        return False, None
    elif "choices" in response.json() and response.json()["choices"]:
        text_gen = response.json()["choices"][0]["message"]["content"]
    else:
        logger.error(f"No choices found in response for item {item['id']}. Response: {response.text}")

    write_path = Path(output_dir) / f"{index}.txt"
    write_sucess = write_text(write_path, text_gen, logger)
    item["gen_text"] = str(write_path)
    return write_sucess, text_gen


def remove_accent(text: str) -> str:
    normalized = unicodedata.normalize('NFD', text)
    
    no_accents = normalized.encode('ascii', 'ignore').decode('ascii')
    no_accents = no_accents.replace('"', '').replace('"', '').replace('"', '')
    no_accents = no_accents.replace('*', '')
    no_accents = no_accents.replace('—', '-').replace('–', '-')
    no_accents = no_accents.replace('“', '').replace('”', '').replace('‘', '').replace('’', '')

    return no_accents

def gen_braille(item : Dict[str, str], text_gen: str, logger: logging.Logger, output_dir: str, index: int) -> bool: 
    write_success = False
    write_path = Path(output_dir) / f"{index}_braille.txt"
    try:
        no_accent_text = remove_accent(text_gen)
        text_braille = pybraille.convertText(no_accent_text)

        write_success = write_text(write_path, text_braille, logger)
        if not write_success:
            logger.error(f"Failed to write braille text for item {item['id']}")
            return write_success
        else: 
            write_success = True
            logger.info(f"Braille text written successfully for item {item['id']}")
    except TypeError:
        logger.error(f"TypeError in braille conversion for item {item['id']}: {text_gen}")
        
    item["gen_braille"] = str(write_path)
    return write_success


def gen_speech(item: Dict[str, str], text_gen :str, logger: logging.Logger, output_dir : str,
               index: int, config: Optional[Dict[str, str]]=None) -> None:
    
    folder_name = "speech" if config is None else "speech_" + config.get("name", "default")
    write_path = Path(output_dir) / f"{folder_name}/{index}.wav"

    if write_path.exists() and is_valid_wav(str(write_path), logger):
        logger.info(f"Speech file already exists and is valid: {write_path}, skipping generation.")
        item["gen_speech"] = f"{folder_name}/{index}.wav"
        return True
    
    endpoint = None
    post_process_func = None
    
    if config is None:
        endpoint = TEXT_TO_SPEECH_KOKORO["endpoint"]
        field = TEXT_TO_SPEECH_KOKORO.get("field", None)
        post_process_func = TEXT_TO_SPEECH_KOKORO["post_process"]
    else:
        endpoint = config["endpoint"]
        field = config.get("field", None)
        post_process_func = config["post_process"]

    request = get_speech_request(text_gen, field)

    if request is None: 
        logger.error(f"Failed to generate speech request for item {item['id']}")
        return False
    
    headers = HEADERS
    headers["Content-Type"] = "application/json"

    response = send_request(endpoint, request, logger, headers=headers)

    if response is None: 
        logger.error(f"Failed to generate speech for item {item['id']}")
        return False
    
    write_sucess = post_process_func(response, logger, write_path)    

    logger.info(f'generated speech for: {item["id"]}')
    item["prompt_speech"] = text_gen
    item["gen_speech"] = "speech/{}.wav".format(index)
    return write_sucess


def gen_image(item: Dict[str, str], logger: logging.Logger, 
              output_dir: str, index: int, config: Optional[Dict[str, str]]=None) -> None:
    
    endpoint = None
    folder_name = "img"
    custom_send = None
    save_success = False
    image_bytes = None
    
    if config is None:
        endpoint = IMAGE_MODEL_DIFFUSION_3_MEDIUM_DIFFUSERS["endpoint"]
    else:
        endpoint = config.get("endpoint", None) 
        folder_name = folder_name + "_" + config["name"]
        custom_send = config.get("custom_send", None)
        
    image_prompt = item["prompt"]
    save_path = Path(output_dir) / f"{folder_name}/{index}.png"
    
    if custom_send is None:

        request = get_image_request(image_prompt)

        response = send_request(endpoint, request, logger)

        if response is None: 
            logger.error(f"Failed to generate image for item {item['id']}, ")
            return False

        image_bytes = response.content
        image = Image.open(io.BytesIO(image_bytes))

        image.save(save_path)
        logger.info(f"Image with id {item['id']} saved to {save_path}")
        
        save_success = True

        if not save_path.exists():
            save_success = False

        item["prompt_image"] = image_prompt
        item["gen_image"] = "img/{}.png".format(item["id"])
        
    else: 
        save_success = custom_send(image_prompt, save_path, logger)
    return save_success, image_bytes

def gen_music(item : Dict[str, str], logger: logging.Logger, output_dir: str, index :int, config: Optional[Dict[str, str]]=None) -> None:
    
    model = None
    endpoint = None
    if config is None:
        model = IMAGE_MODEL_DIFFUSION_3_MEDIUM_DIFFUSERS["model"]
        endpoint = IMAGE_MODEL_DIFFUSION_3_MEDIUM_DIFFUSERS["endpoint"]
    else:
        model = config["model"]
        endpoint = config["endpoint"]

    prompt_music = "A short song representing {} from {} {}".format(item["name"], DEMONYM[item["country"]], item["domain"])
    
    request = get_music_request(prompt_music)

    response = send_request(endpoint, request, logger)

    if response is None: 
        logger.error(f"Failed to generate music for item {item['id']}")
        return False

    audio_bytes = response.content

    write_path = Path(output_dir) / "music/{}.wav".format(index)
    write_sucess = write_text(write_path, audio_bytes, logger)

    logger.info(f"Generated music for: {item['id']}")
    item["prompt_music"] = prompt_music
    item["gen_music"] = "music/{}.wav".format(index)
    return write_sucess

def gen_video(item: Dict[str, str], logger: logging.Logger, output_dir: str, config: Optional[Dict[str, str]]=None) -> None:
    gen_sucess = True
    try: 
        audio_path = Path(output_dir) / "video/{}.mp4".format(item["id"])
        audio_clip = AudioFileClip(audio_path)

        image_path = Path(output_dir) / "img/{}.png".format(item["id"])
        image_clip = ImageClip(image_path)

        video_clip = image_clip.set_audio(audio_clip)
        video_clip.duration = audio_clip.duration
        video_clip.fps = 30

        video_path = Path(output_dir) / "video/{}.mp4".format(item["id"])
        video_clip.write_videofile(video_path)
        logger.info(f"Generated video for: {item['id']} at {video_path}")
        item["gen_video"] = "video/{}.mp4".format(item["id"])
    except Exception as e:
        logger.error(f"Failed to generate video for item {item['id']}: {e}")
        gen_sucess = False

    return gen_sucess

def gen_3d(image_bytes, logger: logging.Logger, output_dir: str, index, config: Optional[Dict[str, str]]=None) -> bool:
    image_b64_str = base64.b64encode(image_bytes).decode("utf-8")
    
    payload = {
    "image": image_b64_str
    }
    
    endpoint = LOCAL_HUNYUAN_3D2["endpoint"]
    name = LOCAL_HUNYUAN_3D2["name"]
    
    response = requests.post(endpoint, json=payload)
    
    output_path = Path(output_dir) / f"{index}.glb"
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        logger.info(f"3D model saved to {output_path}")
        time.sleep(10) 
        return True
    elif response.status_code == 422 or response.status_code == 500:
        logger.info(f"Unprocessable Entity: The input image may not be suitable for 3D model - {name} generation for item {index}. Skipping this item.")
        return True
    else:
        logger.error(f"Failed to generate 3D model for item {index}. Status code: {response.status_code}, Response: {response.text}")
        return False
