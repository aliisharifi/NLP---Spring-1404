import pathlib
import json
from typing import List, Dict
import argparse


first_level_keys = [
    'title',
    'location',
    'geographical_features',
    'topography',
    'natural_resources',
    'tourist_attractions',
    'additional_info',
]

geographical_features_names = {
    'رودخانه‌ها',
    'کوه‌ها',
    'دریاچه‌ها',
    'پوشش گیاهی',
}


topography_names = {
    'منطقه اقلیمی',
    'ارتفاع',
    'توپوگرافی',
    'ویژگی‌های زمین‌شناسی',
}

tourist_attractions_keys = {
    'name',
    'images',
    'year_built',
    'architect',
    'constructor',
    'description',
}

additional_info_keys = {
    'wikipedia_source',
    'books_source',
}



def check_field_for_names(path: str, first_level_key: str, second_level_names: set):
    present_keys = [x['name'] for x in content[first_level_key]]
    if not second_level_names.issubset(present_keys):
        print(f'names {second_level_names.difference(present_keys)} are not present in {first_level_key} in {path}')

def check_field_for_keys(path: str, first_level_key: str, expected_keys: set, records: List[Dict[str, str]]):
    for x in records:
        if not expected_keys.issubset(x.keys()):
            print(f"keys {expected_keys.difference(x.keys())} are not present in {x['name']} in {first_level_key} in {path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('base_path', type=str, help='enter the base path for JSON files to be checked')

    args = parser.parse_args()
    base_path = pathlib.Path(args.base_path)
    

    for path in base_path.rglob('*.json'):
        with open(path, 'r') as f:
            content = json.load(f)
            for first_level_key in first_level_keys:
                if not first_level_key in content:
                    print(f'key {first_level_key} is not present in {path}')

            if 'title' in content:
                if 'شهرستان' in content['title']:
                    print(f"remove شهرستان from title of {path}")
            
            if 'geographical_features' in content:
                check_field_for_names(path, 'geographical_features', geographical_features_names)

            if 'topography' in content:
                check_field_for_names(path, 'topography', topography_names)

            if 'tourist_attractions' in content:
                check_field_for_keys(
                    path,
                    'tourist_attractions',
                    tourist_attractions_keys,
                    content['tourist_attractions'],
                )

            if 'additional_info' in content:
                if not additional_info_keys.issubset(content['additional_info']):
                    print(f"keys {additional_info_keys.difference(content['additional_info'])} are not present in additional_info in {path}")   

            
