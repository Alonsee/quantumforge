import json
import os
import re
from pathlib import Path
import shutil
from typing import Dict, List

def extract_title_from_first_line(text):
    lines = text.split('\n')
    if not lines:
        return text, "unknown"

    first_line = lines[0].strip()

    parts = first_line.split(' | ')
    if parts:
        title_part = parts[0].strip()

        lines[0] = title_part

        cleaned_text = '\n'.join(lines)

        safe_title = re.sub(r'[^\w\s-]', '', title_part)
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        safe_title = safe_title.strip('-_')

        return cleaned_text, safe_title

    return text, "unknown"

def load_replacements_map(json_file_path: str) -> List[Dict[str, str]]:
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            replacements = json.load(file)
            print(f"loaded {len(replacements)} replacement from {json_file_path}")
            return replacements
    except FileNotFoundError:
        print(f"file not found {json_file_path}")
        raise
    except json.JSONDecodeError:
        print(f"wrong JSON {json_file_path}")
        raise


def process_files(input_dir: str, output_dir: str, replacements: List[Dict[str, str]]):

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    text_files = []
    for ext in ['*.txt', '*.md', '*.csv', '*.json', '*.xml', '*.html', '*.htm']:
        text_files.extend(Path(input_dir).glob(ext))

    print(f"Found {len(text_files)} documents")

    processed_count = 0
    for file_path in text_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            for replacement in replacements:
                from_text = replacement['from']
                to_text = replacement['to']

                pattern = re.escape(from_text)
                content = re.sub(pattern, to_text, content)

            modified_content, title = extract_title_from_first_line(content)

            output_file_path = Path(output_dir) / f"{title}.txt"

            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)

            processed_count += 1
            print(f"Processed: {file_path.name}")

        except Exception as e:
            print(f"Failed to process file {file_path}: {e}")

    print(f"{processed_count} filed processed")


def main():
    json_file_path = "etc/terms_map.json"
    input_directory = "raw_data"
    output_directory = "knowledge_base"

    print("start to replace terms")

    try:
        replacements = load_replacements_map(json_file_path)

        process_files(input_directory, output_directory, replacements)

        print("end")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
