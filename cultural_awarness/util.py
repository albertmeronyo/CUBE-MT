import logging
from pathlib import Path
import json
from logging import Logger
import os
from datetime import datetime
import wave
from typing import Dict

LOG_PATH = "system/logs"
CACHE_PATH = "/system/cache"

def is_valid_wav(file_path: str, logger: logging.Logger) -> bool:
    try:
        if not os.path.exists(file_path):
            return False
        
        with wave.open(file_path, 'rb') as wav_file:

            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            if frames <= 0 or sample_rate <= 0 or channels <= 0:
                return False

            logger.info(f"Valid WAV: {frames} frames, {sample_rate}Hz, {channels} channels")
            return True
            
    except (wave.Error, OSError, EOFError):
        return False
    
def setup_logging():
    # create a log file 
    log_dir = Path(LOG_PATH)
    log_dir.mkdir(parents=True, exist_ok=True)
    curr_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = log_dir / f"{curr_time}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    return logging.getLogger(__name__)

def setup_cache(): 
    cache_dir = Path(CACHE_PATH)
    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir


def setup_placeholders(output_dir: str, logger: logging.Logger, modalities: Dict[str, str]):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    subfolders = ["3d", "music", "braille", "img", "speech", "text"]
    names = []
    for folder in subfolders:
        
        if modalities[folder]: 
            folder = folder + "_" + modalities[folder]
        names.append(folder)
        
    for subfolder in names:
        subfolder_path = output_path / subfolder
        subfolder_path.mkdir(exist_ok=True)
        logger.info(f"Created/verified subfolder: {subfolder_path}")


def write_cache(input_file: str, index: int, cache_dir: Path, logger: logging.Logger):
    cache_filename = Path(input_file).stem + "_cache.json"
    cache_path = cache_dir / cache_filename
    cache_data = None
   
    with open(cache_path, 'r') as f:
        cache_data = json.load(f)
    
    cache_data["last_processed_index"] = index

    with open(cache_path, 'w') as f:
        json.dump(cache_data, f, indent=2)

    logger.info(f"Updated cache for {input_file} at index {index}")
    

def read_cache(input_file: str, cache_dir: Path, logger: logging.Logger) -> dict:
    cache_filename = Path(input_file).stem + "_cache.json"
    cache_path = cache_dir / cache_filename
    
    with open(cache_path, 'r') as f:
        cache_data = json.load(f)
    
    logger.info(f"Read cache for {input_file}: {cache_data}")
    
    return cache_data

def get_last_processed_index(input_file: str, cache_dir: Path, logger: logging.Logger) -> int:

    cache_filename = Path(input_file).stem + "_cache.json"
    cache_path = cache_dir / cache_filename
    last_processed = 0
    if cache_path.exists():
        logger.info(f"Cache file found: {cache_path}")
        
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)

        if "last_processed_index" in cache_data:
            last_processed = cache_data["last_processed_index"]
            logger.info(f"Last processed index: {last_processed}")
        else:
            logger.warning(f"'last_processed_index' not found in cache data, defaulting to 0")
            last_processed = 0

            cache_data["last_processed_index"] = last_processed
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
    else:
        logger.info(f"Cache file not found: {cache_path}, creating new cache")
        last_processed = 0
        cache_data = {"last_processed_index": last_processed}
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
            
    return last_processed


def write_text(text_file :str, text_content : str, logger: Logger) -> bool:
    try:
        with open(text_file, 'w') as f:
            f.write(text_content)
        return True
    except Exception as e:
        logger.error(f"Error writing to {text_file}: {e}")
        return False