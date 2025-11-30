
# CUBE-MT (Generating models for cultural awareness)

This repository provides the **CUBE-MT cultural awareness pipeline**, which can generate multiple modalities (text, braille, image, 3D, music, speech) from different input sources.

---

## 1. Environment setup

1. **Create a `.env` file** in the project root.
2. Add your Hugging Face token in the following format:

```bash
   HF_TOKEN=<your_token>
````

* Use a **read** token.
* For details on how to create a token, see the Hugging Face docs:
  [https://huggingface.co/docs/hub/en/security-tokens](https://huggingface.co/docs/hub/en/security-tokens)

---

## 2. Configure the pipeline

Create a JSON configuration file that describes:

* which input file to read,
* where to save outputs,
* which modalities to generate.

Example:

```jsonc
[
  {
    "input": "<path to the JSON file with your sources>",
    "output_dir": "<path to the directory where outputs will be saved>",
    "modalities": {
      "text": true,
      "braille": true,
      "img": true,
      "3d": false,
      "music": true,
      "speech": true
    }
  }
]
```

### 2.1. Choosing the dataset / extension

* To run the **CUBE** extension, set the `input` to:

  ```json
  "input": "CUBE_1K.json"
  ```
* To run the **MUSE-IT** extension, set the `input` to:

  ```json
  "input": "muse_it.json"
  ```

### 2.2. Selecting modalities

* Set each modality flag in `"modalities"` to:

  * `true` to **enable** generation for that modality.
  * `false` to **disable** it.
* If you set **all modalities to `true`**, the pipeline will:

  * run all supported modalities,
  * use **default models** defined in `models.py`.

### 2.3. Using custom models

If you need models different from the defaults:

1. Open `models.py` and select the model/endpoints you want to use.
2. Update configuration (and post-processing if endpoint output is different, an example is given in `custom_func.py`) to use those endpoints.
 For a list of available models per modality, see:

* Images: [Text-to-image models](https://huggingface.co/models?pipeline_tag=text-to-image&sort=trending)
* Text: [Text generation](https://huggingface.co/models?pipeline_tag=text-generation&sort=trending)
* Speech: [Text-to-speech models](https://huggingface.co/models?pipeline_tag=text-to-speech&sort=trending)
* Music: [Text-to-audio models](https://huggingface.co/models?pipeline_tag=text-to-audio&sort=trending)
* 3D: [Image-to-3D models](https://huggingface.co/models?pipeline_tag=image-to-3d&sort=trending)
* Braille: See documentation of the [pybraille](https://pypi.org/project/pybraille/) library


---

## 3. Running the pipeline

Run your pipeline script with the configuration file you created. For example:

```bash
python <your_entrypoint>.py --config <path_to_config.json>
```

* Replace `<your_entrypoint>.py` with the actual script name that launches the CUBE-MT pipeline.
* Replace `<path_to_config.json>` with the path to the JSON configuration file shown above.

After a successful run, the pipeline will create a subfolder in `output_dir` containing up to **six modalities**:

* `image/`
* `text/`
* `braille/`
* `3d/`
* `music/`
* `speech/`

(Only the modalities enabled will be populated.)

---




## 4. Resuming from cache

If the execution terminates unexpectedly:

* The **last state** is saved in `system/cache.json`.
* There is **no need to re-run from the beginning**.
* Restarting the pipeline will pick up from where it left off, based on this cache.

---

## 5. 3D modality (Hunyuan3D)

The 3D model API for **Hunyuan3D** may not always be available as a remote service, so a **local API** option is also supported.

To use the local 3D API:

1. Set up and run the Hunyuan3D model as described in the **“API Server”** section of the Hunyuan3D-2 repository:
   [https://github.com/Tencent-Hunyuan/Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2)

2. In your configuration, set:

   ```json
   "3d": true
   ```

3. Once the local API server is running, enabling `"3d": true` will automatically route 3D generation requests to the local Hunyuan API.


