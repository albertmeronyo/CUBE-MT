import requests
import time
from models import *
import logging
from moviepy import AudioFileClip, ImageClip, CompositeAudioClip
from typing import Optional, Dict
from util import * 
from pathlib import Path


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

def get_payload_text(content: str, model: str)-> Dict[str, str]:
    return {
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "model": model,
    }


def send_request(api_url : str, payload :str, logger: logging.Logger, attempts: int = 3):
    
    response = requests.post(api_url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return response.json()
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
    

def gen_text(item, logger: logging.Logger, output_dir: str, config: Optional[Dict[str, str]]=None) -> Optional[str]:
    text_prompt = "A one sentence textual description of {} from {} {}".format(item["name"], DEMONYM[item["country"]], item["domain"])
    model = None
    endpoint = None

    if config is None: 
        model = TEXT_MODEL_MISTRAL_NEMO_INSTRUCT["model"]
        endpoint = TEXT_MODEL_MISTRAL_NEMO_INSTRUCT["endpoint"]
    else:
        model = config["model"]
        endpoint = config["endpoint"]

    text_gen = None
    if response.json()["choices"]:
        text_gen = response.json()["choices"][0]["message"]["content"]
    else:
        logger.error(f"No choices found in response for item {item['id']}. Response: {response.text}")
        raise ValueError(f"Response does not contain choices for item {item['id']}")
    
    payload_text = get_payload_text(text_prompt, model)
    response = send_request(endpoint, payload_text, logger)

    output_dir = Path(output_dir)
    write_sucess = write_text("txt/{}.txt".format(item["id"]), text_gen, logger)

    return write_sucess

def gen_braille(item, text_gen):
    try:
        text_braille = pybraille.convertText(str(text_gen))
        with open('braille/{}.txt'.format(item["id"]), 'w') as textfile:
            textfile.write(text_braille)
        print(item["id"], text_braille)
    except TypeError:
        print("TypeError when converting string to braille, possibly non-unicode?")
        pass
    item["gen_braille"] = "braille/{}.txt".format(item["id"])
    # time.sleep(1)
    return

def gen_speech(item, text_gen):
    payload_speech = {
        "inputs": text_gen,
    }
    response = requests.post(API_URL_SPEECH, headers=headers, json=payload_speech)
    audio_bytes = response.content
    with open("speech/{}.wav".format(item["id"]), "wb") as wav_file:
        wav_file.write(audio_bytes)
    print(item["id"], "generated speech for: {}".format(text_gen))
    item["prompt_speech"] = text_gen
    item["gen_speech"] = "speech/{}.wav".format(item["id"])
    time.sleep(2.5)
    return

def gen_image(item):
    # safety net
    image_prompt = item["prompt"]

    # if item["domain"] in ["landmarks", "landscapes"]:
    #     image_prompt = "A panoramic view of {} in {}, realistic".format(item["name"], item["country"])
    # elif item["domain"] == "cuisine":
    #     image_prompt = "A high resolution image of {} from {} cuisine, realistic".format(item["name"], DEMONYM[item["country"]])
    # elif item["domain"] == "art":
    #     # TODO: Needs to support different prompts for dances, clothing, etc.
    #     image_prompt = "An image of cocktail dress from American clothing, realistic".format(item["name"], DEMONYM[item["country"]])


    payload_image = {
        "inputs": "{}".format(image_prompt),
    }
    response = requests.post(API_URL_IMAGE, headers=headers, json=payload_image)
    image_bytes = response.content
    image = Image.open(io.BytesIO(image_bytes))
    image.save("img/{}.png".format(item["id"]))
    print(item["id"], image_prompt)
    item["prompt_image"] = image_prompt
    item["gen_image"] = "img/{}.png".format(item["id"])
    time.sleep(2.5)
    return

def gen_music(item):
    prompt_music = "A short song representing {} from {} {}".format(item["name"], DEMONYM[item["country"]], item["domain"])
    payload_music = {
        "inputs": prompt_music,
    }
    response = requests.post(API_URL_MUSIC, headers=headers, json=payload_music)
    audio_bytes = response.content
    with open("music/{}.wav".format(item["id"]), "wb") as wav_file:
        wav_file.write(audio_bytes)
    print(item["id"], prompt_music)
    item["prompt_music"] = prompt_music
    item["gen_music"] = "music/{}.wav".format(item["id"])
    time.sleep(2.5)
    return

def gen_video(item):
    audio_clip = AudioFileClip("music/{}.wav".format(item["id"]))
    # speech_clip = AudioFileClip("speech/{}.wav".format(item["id"]))
    # audio_clip = CompositeAudioClip([music_clip, speech_clip])
    image_clip = ImageClip("img/{}.png".format(item["id"]))
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.duration = audio_clip.duration
    video_clip.fps = 30
    video_clip.write_videofile("video/{}.mp4".format(item["id"]))
    print(item["id"], "Video generated from speech, music, image")
    item["gen_video"] = "video/{}.mp4".format(item["id"])
    return

