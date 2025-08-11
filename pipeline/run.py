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
        modalities = schedule_item.get("modalities", [])
        
        if not input_file or not output_dir:
            logger.error(f"Invalid schedule item: {schedule_item}, skipping")
            continue

        process_item(input_file, output_dir, cache_dir, logger, modalities)
        logger.info(f"Processing input file: {input_file} with output directory: {output_dir}")


def generate_modalities(item: dict, logger: Logger, output_dir: str, index: int, modalities:List= None, config: Optional[Dict[str, str]] = None):
        
        if modalities["text"] or len(modalities) == 0:
            text_sucess, text_gen = gen_text(item, logger, output_dir + "/text", index)
            if not text_sucess:
                raise ValueError(f"Failed to generate text for item {item['id']}")

        if modalities["braille"] or len(modalities) == 0:
            braille_success = gen_braille(item, text_gen, logger, output_dir + "/braille", index)
            if not braille_success:
                logger.error(f"Failed to generate braille for item {item['id']}")
                raise ValueError(f"Failed to generate braille for item {item['id']}")
        
        if modalities["speech"] or len(modalities) == 0:
            speech_success = gen_speech(item, text_gen, logger, output_dir, index, config)
            if not speech_success: 
                raise ValueError(f"Failed to generate sppech for item {item['id']}")
        
        image_bytes = None
        if modalities["img"] or len(modalities) == 0:
            image_success, image_bytes = gen_image(item, logger, output_dir, config)
            if not image_success:
                raise ValueError(f"Failed to generate image for item {item['id']}")
        
        if modalities["music"] or len(modalities) == 0:
            music_success = gen_music(item, logger, output_dir, index)
            if not music_success:
                raise ValueError(f"Failed to generate music for item {item['id']}")

        if modalities["3d"] or len(modalities) == 0:
            if image_bytes is None:
                image_path = Path(output_dir) / "img/{}.png".format(index)
                
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                
            three_d_success = gen_3d(image_bytes, logger, output_dir + "/3d", index)
            if not three_d_success:
                raise ValueError(f"Failed to generate 3D model for item {item['id']}")

        
def process_item(input_file: str, output_dir: str, cache_dir: Path, logger: Logger, modalities:Optional[List] = None):

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
        generate_modalities(item, logger, output_dir, index, modalities) 
        write_cache(input_file, index+1, cache_dir, logger)
if __name__ == "__main__":
    logger = setup_logging()
    # Update CUB_MT
    config_path = "/home/ubuntu/Xin_Fan/CUBE-MT/pipeline/input/update_cube_mt.json"
    text_to_multimodal(logger, config_path)
