# CUBE-MT: A Cultural Benchmark for Multimodal Knowledge Graph Construction with Generative Models

[[https://raw.githubusercontent.com/albertmeronyo/CUBE-MT/master/examples.png]]

CUBE-MT (CUltural BEnchmark with Multimodal Transformations) is an extension to the CUltural BEnchmark for Text-to-Image models ([CUBE](https://github.com/google-research-datasets/cube/tree/main)). CUBE contains 300K cultural artifacts across 8 countries (Brazil, France, India, Italy, Japan, Nigeria, Turkey, and USA) and 3 domains (cuisine, landmarks, art) extracted from Wikidata; and 1K text-to-image generation prompts that enable evaluation of cultural awareness of generative AI models. 
These prompts are automatically generated from the Wikidata KG properties directly, and thus the KG plays the key role of being the central and unique source of authoritative knowledge.

CUBE-MT extends CUBE in various ways:

1. We extend the *modalities* supported by the benchmark, originally just images, to include also include 6  modalities: text, Braille, speech, music, video, and 3D---modalities that are relevant for the provision of audio, haptics, etc.
2. We extend the *prompts* in the benchmark to account for the cultural awareness of generating those modalities
3. We *run* the benchmark to generate a dataset with instances of those modalities, using publicly available models in Hugging Face (Stable Diffusion, Phi3, FastSpeech, MusicGen)

## Dataset

The CUBE-MT dataset consists of:

*  The [CUBE-MT.json](CUBE-MT.json)  metadata file
*  A [data dump](https://emckclac-my.sharepoint.com/:u:/g/personal/k2037030_kcl_ac_uk/EXq1lYs06n1Lg_flWv1mM0kBvrxFMSVRcx5R21JXKpJrMQ?e=rDQiFQ) with the results of the benchmark and generated modalities *(NOTE: not included in this repo to keep it light)*

## Using the benchmark

The [main file](mt.ipynb) contains as variables the models to be used for each modality. These models can be replaced by any other model to be benchmarked. CUBE-MT currently supports [models hosted on Hugging Face](https://huggingface.co/models?sort=trending) for each modality. For a list of available models per modality, see:

* Images: [Text-to-image models](https://huggingface.co/models?pipeline_tag=text-to-image&sort=trending)
* Text: [Text generation](https://huggingface.co/models?pipeline_tag=text-generation&sort=trending)
* Speech: [Text-to-speech models](https://huggingface.co/models?pipeline_tag=text-to-speech&sort=trending)
* Music: [Text-to-audio models](https://huggingface.co/models?pipeline_tag=text-to-audio&sort=trending)
* 3D: [Image-to-3D models](https://huggingface.co/models?pipeline_tag=image-to-3d&sort=trending)
* Braille: See documentation of the [pybraille](https://pypi.org/project/pybraille/) library

## Documentation

Additional documentation for CUBE-MT is available on the [wiki](https://github.com/albertmeronyo/CUBE-MT/wiki)

## Citing

Please cite this work as

```
@misc{merono2025cubemt,
      title={{CUBE-MT: A Cultural Benchmark for Multimodal Knowledge Graph Construction with Generative Models}}, 
      author={Albert Meroño-Peñuela and Nitisha Jain and Filip BIrcanin and Timothy Neate},
      year={2025},
      url={doi:10.5281/zenodo.15398577}, 
}
```

