import requests
import time
from models import *
import logging
from moviepy import AudioFileClip, ImageClip, CompositeAudioClip
from typing import Optional, Dict
from util import * 
from pathlib import Path
import pybraille
from gradio_client import Client, handle_file
import shutil
from datetime import datetime
from models import * 

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
        "inputs": prompt_music,
    }

def send_request(api_url : str, payload :str, logger: logging.Logger, attempts: int = 3):
    
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

    return None
    
def gen_text(item : Dict[str, str], logger: logging.Logger, output_dir: str, config: Optional[Dict[str, str]]=None) -> Tuple[bool, Optional[str]]:
    text_prompt = "A one sentence textual description of {} from {} {}".format(item["name"], DEMONYM[item["country"]], item["domain"])
    model = None
    endpoint = None
    text_gen = None

    if config is None: 
        model = TEXT_MODEL_PHI3_MINI_4K_INSTRUCT["model"]
        endpoint = TEXT_MODEL_PHI3_MINI_4K_INSTRUCT["endpoint"]
    else:
        model = config["model"]
        endpoint = config["endpoint"]


    request = get_text_request(text_prompt, model)
    response = send_request(endpoint, request, logger)

    if response is None:
        logger.error(f"Failed to generate text for item {item['id']}")
        return False, None
    elif "choices" in response.json and response.json()["choices"]:
        text_gen = response.json()["choices"][0]["message"]["content"]
    else:
        logger.error(f"No choices found in response for item {item['id']}. Response: {response.text}")

    write_path = Path(output_dir) / f"{item['id']}.txt"
    write_sucess = write_text(write_path, text_gen, logger)
    item["gen_text"] = str(write_path)
    return write_sucess, text_gen

def gen_braille(item : Dict[str, str], text_gen: str, logger: logging.Logger, output_dir: str) -> bool: 
    write_success = False
    try:
        text_braille = pybraille.convertText(str(text_gen))
        write_path = Path(output_dir) / f"{item['id']}_braille.txt"

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


# def gen_speech(item: Dict[str, str], text_gen :str, logger: logging.Logger, ,output_dir : str,config: Optional[Dict[str, str]]=None) -> None:
#     model = None
#     endpoint = None
#     if config is None:
#         endpoint = TEXT_TO_SPEECH_KOKORO["endpoint"]
    
#     else:
#         endpoint = config["endpoint"]
 
#     request = get_speech_request(text_gen)

#     response = send_request(endpoint, request, logger)
    
#     if response is None: 
#         logger.error(f"Failed to generate speech for item {item['id']}")
#         return False

#     audio, sampling_rate = response.json

#     write_path = Path(output_dir) / "speech/{}.wav".format(item["id"])
#     write_sucess = write_text(write_path, audio, logger)

#     logger.info(f"generated speech for: {item["id"]}")
#     item["prompt_speech"] = text_gen
#     item["gen_speech"] = "speech/{}.wav".format(item["id"])
    # return write_sucess

def gen_speech(item: Dict[str, str], text_gen :str, logger: logging.Logger, ,output_dir : str,config: Optional[Dict[str, str]]=None) -> None:
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

    write_path = Path(output_dir) / "speech/{}.wav".format(item["id"])
    write_sucess = write_text(write_path, text_gen, logger)

    logger.info(f"generated speech for: {item["id"]}")
    item["prompt_speech"] = text_gen
    item["gen_speech"] = "speech/{}.wav".format(item["id"])
    return write_sucess

    
def gen_image(item: Dict[str, str], logger: logging.Logger, output_dir: str,config: Optional[Dict[str, str]]=None) -> None:
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

    save_path = Path(output_dir) / "img/{}.png".format(item["id"])
    image.save(save_path)
    logger.info(f"Image with id {item['id']} saved to {save_path}")
    
    save_success = True

    if not save_path.exists():
        save_success = False

    item["prompt_image"] = image_prompt
    item["gen_image"] = "img/{}.png".format(item["id"])

    return save_sucess

def gen_music(item : Dict[str, str], logger: logging.Logger, output_dir: str, config: Optional[Dict[str, str]]=None) -> None:
    
    model = None
    endpoint = None
    if config is None:
        model = #TODO: Use a default model
        endpoint = #TODO: Use a default endpoint
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

    write_path = Path(output_dir) / "music/{}.wav".format(item["id"])
    write_sucess = write_text(write_path, audio_bytes, logger)

    logger.info(f"Generated music for: {item['id']}")
    item["prompt_music"] = prompt_music
    item["gen_music"] = "music/{}.wav".format(item["id"])
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


def gen_3d(item: Dict[str, str], logger: logging.Logger, output_dir: str, config: Optional[Dict[str, str]]=None) -> bool:

    gen_success = False
    
    try:

        if config is None:
            api_endpoint = "tencent/Hunyuan3D-2"
            api_name = "/shape_generation"
            steps = 30
            guidance_scale = 5.0
            octree_resolution = 256
            remove_background = True
            num_chunks = 8000
            randomize_seed = True
        else:
            api_endpoint = config.get("endpoint", "tencent/Hunyuan3D-2")
            api_name = config.get("api_name", "/shape_generation")
            steps = int(config.get("steps", 30))
            guidance_scale = float(config.get("guidance_scale", 5.0))
            octree_resolution = int(config.get("octree_resolution", 256))
            remove_background = config.get("remove_background", "true").lower() == "true"
            num_chunks = int(config.get("num_chunks", 8000))
            randomize_seed = config.get("randomize_seed", "true").lower() == "true"
        
        hf_token = os.getenv['HF_TOKEN']
        if hf_token:
            client = Client(api_endpoint, hf_token=hf_token)
            logger.info(f"Initialized 3D client with HF token for item {item['id']}")
        else:
            client = Client(api_endpoint)
            logger.info(f"Initialized 3D client (free tier) for item {item['id']}")
        
    
        image_path = Path(output_dir) / item.get("gen_image", f"img/{item['id']}.png")
        
        if not image_path.exists():
            logger.error(f"Input image not found for 3D generation: {image_path}")
            return False
        
        logger.info(f"Starting 3D model generation for item {item['id']} from image: {image_path}")
        

        result = client.predict(
            caption=None,
            image=handle_file(str(image_path)),
            mv_image_front=None,
            mv_image_back=None,
            mv_image_left=None,
            mv_image_right=None,
            steps=steps,
            guidance_scale=guidance_scale,
            seed=1234,
            octree_resolution=octree_resolution,
            check_box_rembg=remove_background,
            num_chunks=num_chunks,
            randomize_seed=randomize_seed,
            api_name=api_name
        )
        
        output_file_data = result[0]
        
        output_file_path = None
        if output_file_data:
            if isinstance(output_file_data, dict):
                output_file_path = (output_file_data.get('value') or 
                                   output_file_data.get('name') or 
                                   output_file_data.get('path'))
            else:
                output_file_path = str(output_file_data)
        
        if not output_file_path or not Path(output_file_path).exists():
            logger.error(f"No valid 3D model file generated for item {item['id']}")
            return False
        
        model_dir = Path(output_dir) / "3d"
        model_dir.mkdir(exist_ok=True)
        
        output_extension = Path(output_file_path).suffix
        output_filename = f"{item['id']}_3d_model{output_extension}"
        final_output_path = model_dir / output_filename
        
        shutil.copy2(output_file_path, final_output_path)
        
        
        metadata_path = model_dir / f"{item['id']}_3d_metadata.txt"
        _, html_output, mesh_stats, used_seed = result
        
        metadata_content = f"""Hunyuan3D Processing Metadata
                    Generated: {datetime.now().isoformat()}
                    --------------------------------------------------
                    source_image: {image_path.name}
                    generated_file: {output_filename}
                    used_seed: {used_seed}
                    steps: {steps}
                    guidance_scale: {guidance_scale}
                    octree_resolution: {octree_resolution}
                    remove_background: {remove_background}
                    num_chunks: {num_chunks}
                    randomize_seed: {randomize_seed}
                    mesh_stats: {mesh_stats}
                    html_output: {html_output}
        """
        
        write_success = write_text(metadata_path, metadata_content, logger)
        if not write_success:
            logger.warning(f"Failed to write metadata for 3D model {item['id']}")
        
        logger.info(f"Generated 3D model for item {item['id']} at {final_output_path}")
        
        item["gen_3d"] = f"3d/{output_filename}"
        item["gen_3d_metadata"] = f/{item['id']}_3d_metadata.txt"
        
        gen_success = True
        
    except ImportError as e:
        logger.error(f"Missing required dependencies for 3D generation: {e}")
        logger.error("Install with: pip install gradio-client")
        gen_success = False
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to generate 3D model for item {item['id']}: {error_msg}")
        
        if "exceeded your free GPU quota" in error_msg:
            logger.warning("GPU quota exceeded for 3D generation. Consider:")
            logger.warning("  1. Wait for quota to reset")
            logger.warning("  2. Use a Hugging Face Pro account")
            logger.warning("  3. Deploy your own instance")
        
        gen_success = False
    
    return gen_success