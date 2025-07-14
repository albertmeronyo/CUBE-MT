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


        
        logger.info(f"Processing input file: {input_file} with output directory: {output_dir}")


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

        gen_text(item, logger, output_dir)

        #TODO: Rewrite gen_braille, gen_speech, gen_image





    


    


if __name__ == "__main__":
    logger = setup_logging()
    text_to_multimodal()
