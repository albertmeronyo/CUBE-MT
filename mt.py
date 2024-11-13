#!/usr/bin/env python
# coding: utf-8

# # CUBE-MT: An Extension to CUBE for MuseIT Multimodal Transformations

# Outline of the approach:
# 
# 1. Load CUBE_SCSpace and CUBE_1K
# 2. Iterate over items and get RDF
# 3. Grab link to DBpedia and de-reference
# 4. Find DBpedia abstract of related item
# 5. Store RDF and abstract
# 6. Profit

# In[2]:


# Imports and gobals
import json
import requests
import io
from PIL import Image
import time
from IPython.display import Audio
import pybraille
from moviepy.editor import AudioFileClip, ImageClip, CompositeAudioClip



HUGGING_FACE_PREFIX = "https://api-inference.huggingface.co/models/"
IMAGE_MODEL = "stabilityai/stable-diffusion-3-medium-diffusers"
# IMAGE_MODEL = "black-forest-labs/FLUX.1-dev"
# TEXT_MODEL = "microsoft/Phi-3-mini-4k-instruct"
# TEXT_MODEL = "mistralai/Mistral-Nemo-Instruct-2407"
# TEXT_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"
# TEXT_MODEL = "google/gemma-2-2b-it/v1/chat/completions"
TEXT_MODEL = "microsoft/Phi-3-mini-4k-instruct/v1/chat/completions"
SPEECH_MODEL = "facebook/fastspeech2-en-ljspeech"
MUSIC_MODEL = "facebook/musicgen-small"

API_URL_IMAGE = HUGGING_FACE_PREFIX + IMAGE_MODEL
API_URL_TEXT = HUGGING_FACE_PREFIX + TEXT_MODEL
API_URL_SPEECH = HUGGING_FACE_PREFIX + SPEECH_MODEL
API_URL_MUSIC = HUGGING_FACE_PREFIX + MUSIC_MODEL

headers = {"Authorization": "Bearer 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"}


# In[3]:


# with open('CUBE_CSpace.json') as f:
#     cube_scs = json.load(f)

# cube_1k = cube_scs

with open('CUBE_1K.json') as f:
    cube_1k = json.load(f)

print("Dataset loaded with {} items".format(len(cube_1k)))


# In[ ]:


demonym = {
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

def gen_text(item):
    text_prompt = "A one sentence textual description of {} from {} {}".format(item["name"], demonym[item["country"]], item["domain"])
    # payload_text = { // TODO
    #     "inputs": "{}".format(text_prompt),
    # }
    payload_text = {
        "model": "microsoft/Phi-3-mini-4k-instruct",
        "messages": [{"role": "user", "content": "{}".format(text_prompt)}],
        "max_tokens": 500,
        "stream": False
    }
    response = requests.post(API_URL_TEXT, headers=headers, json=payload_text)
    with open('txt/{}.txt'.format(item["id"]), 'w') as textfile:
        text_gen = ""
        if response.json()["choices"]:
            text_gen = response.json()["choices"][0]["message"]["content"]
        # text_gen = response.json()["choices"][0]["message"]["content"]
        textfile.write(text_gen)
    print(item["id"], text_prompt)
    print(item["id"], text_gen)
    item["prompt_text"] = text_prompt
    item["gen_text"] = "txt/{}.txt".format(item["id"])
    time.sleep(2.5)
    return text_gen

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
    #     image_prompt = "A high resolution image of {} from {} cuisine, realistic".format(item["name"], demonym[item["country"]])
    # elif item["domain"] == "art":
    #     # TODO: Needs to support different prompts for dances, clothing, etc.
    #     image_prompt = "An image of cocktail dress from American clothing, realistic".format(item["name"], demonym[item["country"]])


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
    prompt_music = "A short song representing {} from {} {}".format(item["name"], demonym[item["country"]], item["domain"])
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



# In[17]:


# Empty output directories

import os, shutil

folders = ['braille', 'img', 'music', 'speech', 'txt', 'video']

def empty_folder(path):
    folder = path
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


for f in folders:
    empty_folder(f)


# In[18]:


# Sample

# 5 random cuisine, 5 random art, 5 random landmark

import random

# foo = ['a', 'b', 'c', 'd', 'e']
# print(random.choice(foo))

cuisine = []
art = []
landmarks = []

for item in cube_1k:
    if item["id"]:
        if item["domain"] == 'cuisine':
            cuisine.append(item)
        elif item["domain"] == 'art':
            art.append(item)
        elif item["domain"] == 'landmarks':
            landmarks.append(item)

items = []
for i in range(0,2):
    items.append(random.choice(cuisine))

for i in range(0,2):
    items.append(random.choice(art))

for i in range(0,2):
    items.append(random.choice(landmarks))
        




# In[5]:


import traceback
import random

items = cube_1k

# random.shuffle(items)


for i in items:
    # Skip all non-Wikidata items
    if not i["id"]:
        continue
    if i["id"] and i["id"][0] != 'Q':
        continue
    
    
    try:
        # Text
        text_gen = gen_text(i)
    except Exception as e:
        print("Error processing text_gen for item {}".format(i["id"]))
        print(traceback.format_exc())
        continue

    try:
        # Braille
        gen_braille(i, text_gen)
    except Exception as e:
        print("Error processing gen_braille for item {}".format(i["id"]))
        print(traceback.format_exc())
        continue

    try:
        # Speech
        gen_speech(i, text_gen)
    except Exception as e:
        print("Error processing gen_speech for item {}".format(i["id"]))
        print(traceback.format_exc())
        continue

    try:
        # Image
        gen_image(i)
    except Exception as e:
        print("Error processing gen_image for item {}".format(i["id"]))
        print(traceback.format_exc())
        continue

    try:
        # Music
        gen_music(i)
    except Exception as e:
        print("Error processing gen_music for item {}".format(i["id"]))
        print(traceback.format_exc())
        continue

        # Video (by composing image, speech, music)
        # TODO: moviepy seems to break with our saved wav files
        # gen_video(cube_1k[i])

        # 3d geometry
        # TODO: with local models from stabilityai, tencent, etc
        # https://github.com/Stability-AI/stable-fast-3d
    
    
with open('CUBE_MT.json', 'w') as fp:
    json.dump(items, fp)



# In[ ]:





# In[ ]:





# In[ ]:




