# CUBE-MT

CUBE-MT is an extension to the CUltural BEnchmark for Text-to-Image models ([CUBE](https://github.com/google-research-datasets/cube/tree/main)). CUBE contains 300K cultural artifacts across 8 countries (Brazil, France, India, Italy, Japan, Nigeria, Turkey, and USA) and 3 domains (cuisine, landmarks, art) extracted from Wikidata; and 1K text-to-image generation prompts that enable evaluation of cultural awareness of generative AI models. 
These prompts are automatically generated from the Wikidata KG properties directly, and thus the KG plays the key role of being the central and unique source of authoritative knowledge.

CUBE-MT extends CUBE in various ways:

1. We extend the *modalities* supported by the benchmark, originally just images, to include also include 6 additional modalities: text, Braille, speech, music, video, and 3D---modalities that are relevant for the provision of audio, haptics, etc.
2. We extend the *prompts* in the benchmark to account for the cultural awareness of generating those modalities
3. We *run* the benchmark to generate a dataset with instances of those modalities, using publicly available models in Hugging Face (Stable Diffusion, Phi3, FastSpeech, MusicGen)

Metadata can be found in the **CUBE-MT.json** file. A data dump with the results of the benchmark and generated modalities can be found [here](https://emckclac-my.sharepoint.com/:u:/g/personal/k2037030_kcl_ac_uk/EXq1lYs06n1Lg_flWv1mM0kBvrxFMSVRcx5R21JXKpJrMQ?e=rDQiFQ).
