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

DEMONYM = {
        "Brazil": "Brazilian",
        "France": "French",
        "India": "Indian",
        "Italy": "Italian",
        "Japan": "Japanese",
        "Nigeria": "Nigerian",
        "Turkey": "Turkish",
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

def get_speech_request(inputs: str) -> Dict[str, str]:
    return {
        "inputs": inputs,
    }

def get_image_request(inputs: str) -> Dict[str, str]:
    return {
        "inputs": "{}".format(inputs),
    }

def get_music_request(inputs: str) -> Dict[str, str]:
    return {
        "inputs": inputs,
    }

def send_request(api_url : str, payload :str, logger: logging.Logger, attempts: int = 3, sleep_time: int = 5) -> Optional[requests.Response]:
    
    response = requests.post(api_url, headers=HEADERS, json=payload)

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
        logger.error(f"Request failed with status code {response.status_code}. " \
                        f"Response: {response.text}" \
                        f"Trying again in {sleep_time} seconds..." if attempts > 1 else "")
        if attempts > 1:
            return send_request(api_url, payload, logger, attempts - 1, sleep_time * attempts)
        

    return None
    
def gen_text(item : Dict[str, str], logger: logging.Logger, 
             output_dir: str, index: int, config: Optional[Dict[str, str]]=None) -> Tuple[bool, Optional[str]]:
    text_prompt = "A one sentence textual description of {} from {} {}".format(item["name"], DEMONYM[item["country"]], item["domain"])
    model = None
    endpoint = None
    text_gen = None

    if config is None: 
        model = TEXT_MODEL_LLAMA_3_1_8B_INSTRUCT["model"]
        endpoint = TEXT_MODEL_LLAMA_3_1_8B_INSTRUCT["endpoint"]
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


def gen_speech(item: Dict[str, str], text_gen :str, logger: logging.Logger, output_dir : str, index: int, config: Optional[Dict[str, str]]=None) -> None:
    endpoint = None
    if config is None:
        endpoint = TEXT_TO_SPEECH_FASTSPEECH2["endpoint"]
    else:
        endpoint = config["endpoint"]
 
    request = get_speech_request(text_gen)

    if request is None: 
        logger.error(f"Failed to generate speech request for item {item['id']}")
        return False

    response = send_request(endpoint, request, logger)
    
    if response is None: 
        logger.error(f"Failed to generate speech for item {item['id']}")
        return False

    audio_bytes = response.content

    write_path = Path(output_dir) / "speech/{}.wav".format(index)
    write_sucess = write_text(write_path, text_gen, logger)

    logger.info(f'generated speech for: {item["id"]}')
    item["prompt_speech"] = text_gen
    item["gen_speech"] = "speech/{}.wav".format(index)
    return write_sucess

    
def gen_image(item: Dict[str, str], logger: logging.Logger, output_dir: str, index: int, config: Optional[Dict[str, str]]=None) -> None:
    model = None
    endpoint = None
    if config is None:
        model = IMAGE_MODEL_DIFFUSION_3_MEDIUM_DIFFUSERS["model"]
        endpoint = IMAGE_MODEL_DIFFUSION_3_MEDIUM_DIFFUSERS["endpoint"]
    
    else:
        model = config["model"]
        endpoint = config["endpoint"]

    image_prompt = item["prompt"]

    request = get_image_request(image_prompt)

    response = send_request(endpoint, request, logger)

    if response is None: 
        logger.error(f"Failed to generate image for item {item['id']}, ")
        return False

    image_bytes = response.content
    image = Image.open(io.BytesIO(image_bytes))

    save_path = Path(output_dir) / "img/{}.png".format(index)
    image.save(save_path)
    logger.info(f"Image with id {item['id']} saved to {save_path}")
    
    save_success = True

    if not save_path.exists():
        save_success = False

    item["prompt_image"] = image_prompt
    item["gen_image"] = "img/{}.png".format(item["id"])

    return save_sucess, image_bytes

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
        
    response = requests.post(LOCAL_HUNYUAN_3D2, json=payload)
    
    output_path = Path(output_dir) / f"{index}.glb"
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        logger.info(f"3D model saved to {output_path}")
        return True
    else:
        logger.error(f"Failed to generate 3D model for item {index}. Status code: {response.status_code}, Response: {response.text}")
        return False

    