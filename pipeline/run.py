import json
from pathlib import Path
from logging import Logger
from util import * 
from request_handler import *

def text_to_multimodal(logger : Logger, input: str = "input/schedule.json"):
    
    try:
        with open(input, 'r') as f:
            schedule = json.load(f)
            logger.info(f"Loaded schedule with {len(schedule)} items")
    except FileNotFoundError:
        logger.error(f"File not found: {input}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {input}: {e}")
        return
    
    cache_dir = setup_cache()
    
    for schedule_item in schedule:
        input_file = schedule_item.get("input")
        output_dir = schedule_item.get("output_dir")
        
        if not input_file or not output_dir:
            logger.error(f"Invalid schedule item: {schedule_item}, skipping")
            continue


        process_item(input_file, output_dir, cache_dir, logger)
        logger.info(f"Processing input file: {input_file} with output directory: {output_dir}")


def generate_modalities(item: dict, logger: Logger, output_dir: str, config: dict):
        text_sucess, text_gen = gen_text(item, logger, output_dir)

        if not text_sucess:
            raise ValueError(f"Failed to generate text for item {item['id']}")

        braille_success = gen_braille(item, text_gen, logger, output_dir)

        if not braille_success:
            logger.error(f"Failed to generate braille for item {item['id']}")
            raise ValueError(f"Failed to generate braille for item {item['id']}")
        
        speech_success = gen_speech(item, text_gen, logger, output_dir, config)

        if not speech_success: 
            raise ValueError(f"Failed to generate sppech for item {item['id']}")

        image_success = gen_image(item)

        if not image_success:
            raise ValueError(f"Failed to generate image for item {item['id']}")
        
        speech_success = gen_speech(item, text_gen, logger, output_dir, config)

        if not speech_success: 
            raise ValueError(f"Failed to generate speech for item {item['id']}")
        
        music_success = gen_music(item, logger, output_dir)
        if not music_success:
            raise ValueError(f"Failed to generate music for item {item['id']}")

        three_d_success = gen_3d(item, logger, output_dir)

        if not three_d_success:
            raise ValueError(f"Failed to generate 3D model for item {item['id']}")

def process_item(input_file: str, output_dir: str, cache_dir: Path, logger: Logger):

    setup_placeholders(output_dir, logger)

    last_index = get_last_processed_index(input_file, cache_dir, logger)

    data = None
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
            logger.info(f"Loaded data from {input_file}")
    except Exception as e:
        logger.error(f"Error reading {input_file}: {e}")
        return
    
    for index, item in enumerate(data[last_index:], start=last_index):
        logger.info(f"Processing item {index} from {input_file}")

        # Will generate modalities using default models stated in `models.py`
        generate_modalities(item, logger, output_dir) 

if __name__ == "__main__":
    logger = setup_logging()
    text_to_multimodal()
