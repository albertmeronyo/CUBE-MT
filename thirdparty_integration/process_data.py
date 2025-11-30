import json
from constants import *

def process_data(input_file, output_file):
    
    muse_data= []
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    try:

        muse_data = json.loads(content)
    except json.JSONDecodeError:
        
        muse_data = []
        for line in content.split('\n'):
            line = line.strip()
            if line:
                muse_data.append(json.loads(line))
                
    cube_mt = []
    
    unique_countries = set()
    for item in muse_data:
        entry = TEMPLATE.copy()
        
        name = item.get('title', '')
        artist = item.get('artistName', '')
        period = item.get('period', '')
        style = item.get('style', '')
        gallery_name = item.get('galleryName', [])
        artist_name = item.get('artistName', '')
        
        country = gallery_name.split(',')[-1].strip() if gallery_name else ''
        if country == 'Private Collection': 
            country = f"REPLACE_WITH_ARTIST_COUNTRY_{artist_name}"

        entry['name'] = name
        entry['country'] = country

        prompt = f"A painting of {name} by {artist} from {period} period in {style} style, realistic" \
                if period else f"A painting of {name} by {artist} in {style} style, realistic"

        entry['prompt'] = prompt
        
        unique_countries.add(entry['country'])

        cube_mt.append(entry)
    
    print(f"Unique countries found: {unique_countries}")
    print(f"Total entries processed: {len(cube_mt)}")
    
    dir = '/'.join(output_file.split('/')[:-1])
    unique_countries_file = f"{dir}/unique_countries.txt"
    with open(unique_countries_file, 'w') as f:
        for country in unique_countries:
            f.write(f"{country}\n")
                
    with open(output_file, 'w') as f:
        json.dump(cube_mt, f, indent=2)
                

if __name__ == "__main__":
    input_path = 'raw_data.json' 
    output_path = 'muse_no_qids_cube_mt.json' 

    process_data(input_path, output_path)