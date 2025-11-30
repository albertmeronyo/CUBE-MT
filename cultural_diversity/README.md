# CUBE-MT (Generating artifacts for cultural diversity)
This module generates image and text modalities to test cultural diversity across several concepts, and then tags the generated images with cultural metadata (artifact name, country, continent).

Supported cultural concepts:

* `landmarks`
* `art-cube`
* `art-muse`
* `cuisine`

---

## 1. What This Module Does

### 1.1. Image / Text Generation

The notebook `gen_diverse_modalities.ipynb` uses:

* **Prompts** from `prompts.py`
* **Model settings** from `models.py`
* **Generation logic** from the provided `ImageGenerator` and `TextGenerator` classes

For **images**:

* Each cultural concept has **5 prompt variants** (`IMAGE_PROMPTS[CULTURAL_CONCEPT]` in `prompts.py`)
* For each prompt, the script uses **80 seeds** (`0–79`)
* Images are generated in **batches of 8 seeds**
  → **10 batches × 8 images = 80 images per prompt**
  → **5 prompts × 80 images = 400 images per cultural concept**

For text, the logic is analogous but saves JSON files instead of images.

---

## 2. Prerequisites


   For generation (image or text):

   * `HF_TOKEN` — your Hugging Face API token

     ```bash
     export HF_TOKEN="your_hf_token_here"
     ```

   For image tagging:

   * `OPENAI_API_KEY` — your OpenAI API key

     ```bash
     export OPENAI_API_KEY="your_openai_api_key_here"
     ```

   Or put them in a `.env` file:

   ```env
   HF_TOKEN=your_hf_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

---

## 3. Generating Modalities (Images / Text)


* Run notebook: `gen_diverse_modalities.ipynb`


Below assumes you are running a script with the `if __name__ == "__main__":` block you provided.

### 3.1. Configure the Script

In the main section of the generation script, you will see something like:

```python
if __name__ == "__main__":
    GEN_TYPE = CubeMTGenerator.IMAGE   # or CubeMTGenerator.TEXT
    CULTURAL_CONCEPT = "landmarks"     # one of: "landmarks", "art-cube", "art-muse", "cuisine"
    OUTPUT_ROOT = "/mnt/rds/CUBE_MT/Test"
    
    if GEN_TYPE == CubeMTGenerator.IMAGE:
        prompts = IMAGE_PROMPTS[CULTURAL_CONCEPT]
        default_image_model = QWEN_IMAGE
        run_image_generation(prompts, OUTPUT_ROOT,
                             model_id=QWEN_IMAGE["model_id"],
                             provider=QWEN_IMAGE["provider"])
    else:
        prompts = TEXT_PROMPTS[CULTURAL_CONCEPT]
        default_text_model = GOOGLE_GEMMA_2_2B_IT
        run_text_generation(prompts, OUTPUT_ROOT,
                            model_id=GOOGLE_GEMMA_2_2B_IT)
```

Adjust as needed:

* Set `GEN_TYPE` to:

  * `CubeMTGenerator.IMAGE` for **image generation**
  * `CubeMTGenerator.TEXT` for **text generation**
* Set `CULTURAL_CONCEPT` to one of:

  * `"landmarks"`, `"art-cube"`, `"art-muse"`, `"cuisine"`
* Set `OUTPUT_ROOT` to your desired output directory.

Model details (`QWEN_IMAGE`, `GOOGLE_GEMMA_2_2B_IT`, etc.) are defined in **`models.py`**. Prompt lists are defined in **`prompts.py`** (`IMAGE_PROMPTS` and `TEXT_PROMPTS`).

#### Using custom models 
 These models can be replaced by any other model to be benchmarked. CUBE-MT currently supports [models hosted on Hugging Face](https://huggingface.co/models?sort=trending) for each modality. For a list of available models per modality, see:

* Images: [Text-to-image models](https://huggingface.co/models?pipeline_tag=text-to-image&sort=trending)
* Text: [Text generation](https://huggingface.co/models?pipeline_tag=text-generation&sort=trending)
* Speech: [Text-to-speech models](https://huggingface.co/models?pipeline_tag=text-to-speech&sort=trending)
* Music: [Text-to-audio models](https://huggingface.co/models?pipeline_tag=text-to-audio&sort=trending)
* 3D: [Image-to-3D models](https://huggingface.co/models?pipeline_tag=image-to-3d&sort=trending)
* Braille: See documentation of the [pybraille](https://pypi.org/project/pybraille/) library


### 3.2. Output Structure

The generator:

* Creates a folder per prompt (slugified prompt text)
* Inside each prompt folder, creates subfolders like `round-00`, `round-01`, ..., based on the seed batch
* Saves:

  * **Images:** `seed-XX.png`
  * **Text:** `seed-XX.json` with metadata `{ seed, prompt, response, model }`

Example path for images:

```
<OUTPUT_ROOT>/
    eiffel-tower-at-sunset/
        round-00/
            seed-00.png
            seed-01.png
            ...
        round-01/
            seed-08.png
            ...
```

---

## 4. Tagging Generated Images (Artifact, Country, Continent)

Once you have generated images, you can automatically tag them using `image_tagging.ipynb` (the `image_tagging` code you pasted).

### 4.1. Requirements

1. **Images generated and stored in folders**
   For example:

   ```
   /path/to/data/landmarks/
       eiffel-tower-at-sunset/
           round-00/...
       taj-mahal-at-dawn/
           round-00/...
   ```

2. **Environment variable**
   Make sure `OPENAI_API_KEY` is set (or present in `.env`):

   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

### 4.2. Set Paths in the Tagging Notebook

In `image_tagging.ipynb`, specify:

```python
parent_folder = "<folder_path_to_cuisine_or_landmarks_or_art>"
save_folder = "<save_folder>"
```

For example:

```python
parent_folder = "CUBE_MT/landmarks"
save_folder = "CUBE_MT/Annotations"
```

Then, get all subfolder paths:

```python
subfolder_paths = [
    os.path.join(parent_folder, name)
    for name in os.listdir(parent_folder)
    if os.path.isdir(os.path.join(parent_folder, name))
]
```

Each `subfolder_path` should correspond to a prompt folder containing image files.

