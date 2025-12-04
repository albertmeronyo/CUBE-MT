# CUBE-MT: A Cultural Benchmark for Multimodal Knowledge Graph Construction with Generative Models

![CUBE-MT examples](https://raw.githubusercontent.com/albertmeronyo/CUBE-MT/master/examples.png)

CUBE-MT (CUltural BEnchmark with Multimodal Transformations) is an extension to the CUltural BEnchmark for Text-to-Image models ([CUBE](https://github.com/google-research-datasets/cube/tree/main)). CUBE contains cultural artifacts across 16 countries (Austria, Denmark, Germany, Ireland, Mexico, Netherlands, Poland, Russia, Spain, Switzerland, Brazil, France, Italy, Japan, UK, USA) and 3 domains (cuisine, landmarks, art(cube, muse-IT)) extracted from Wikidata; and 1K text-to-image generation prompts that enable evaluation of cultural awareness of generative AI models. 
These prompts are automatically generated from the Wikidata KG properties directly, and thus the KG plays the key role of being the central and unique source of authoritative knowledge.

CUBE-MT extends CUBE in various ways:

1. We extend the *modalities* supported by the benchmark, originally just images, to include also include 6  modalities: text, Braille, speech, music, video, and 3D---modalities that are relevant for the provision of audio, haptics, etc.
2. We extend the *prompts* in the benchmark to account for the cultural awareness of generating those modalities
3. We *run* the benchmark to generate a dataset with instances of those modalities, using publicly available models in Hugging Face ( e.g., Stable Diffusion, Phi3, FastSpeech, for the full list, refer to the table). 

## Dataset

The CUBE-MT dataset consists of:

*  The [CUBE-MT.json](CUBE-MT.json)  metadata file and thirdparty integration file [MUSE_IT.json](MUST_IT.json)
*  The same version of the dataset with generated items is available on [Hugging Face](https://huggingface.co/datasets/albertmeronyo/CUBE-MT)



## Using the benchmark

* For **cultural awareness artifact generation**, refer to the `cultural_awareness` folder and its corresponding `README.md` file for detailed execution instructions.

* For **cultural diversity artifact generation**, refer to the `cultural_diversity` folder and its corresponding `README.md` file for detailed execution instructions.

* For **evaluation of generated artifacts for cultural diversity**, refer to the `evaluate` folder and its corresponding `README.md` file for evaluation instructions.

* For **integration of third-party sources with CUBE-MT**, refer to the `third_party` folder and its corresponding `README.md` file for details on mapping entities to CUBE-MT and traversing WikiData QIDs.


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

