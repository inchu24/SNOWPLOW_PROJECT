import os
import json
import yaml
import logging
from utils.mapper import TemplateProcessor

config_file = "config/config.yml"
log_dir = 'log'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "auto-dbt-profile.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w')
    ],
)


def read_file(file_path: str, file_type: str) -> dict:
    """
    Reads and parses a file (YAML or JSON)
    and returns its content as a dictionary.

    Args:
        file_path (str): Path to the input file.
        file_type (str): Type of the file ('yml' or 'json').

    Returns:
        dict: Parsed contents of the file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"The {file_type} file not found at {file_path}"
        )
    with open(file_path, "r", encoding="utf-8") as f:
        if file_type.lower() == 'yml':
            data = yaml.safe_load(f)
        elif file_type.lower() == 'json':
            data = json.load(f)
        else:
            raise ValueError(
                f"Unsupported file type: {file_type}. "
                f"Only 'yml' and 'json' are allowed."
            )
        logging.info(f"{file_path}: Valid {file_type} data.")
    return data


def main():
    try:
        logging.info("Config file reading!")
        dict_config_data = read_file(config_file, 'yml')
        input_dir = dict_config_data.get("input_dir")
        output_dir = dict_config_data.get("output_dir")
        mapping_file = dict_config_data.get("mapping_file")
        template_file = dict_config_data.get("template_file")

        logging.info(
            f"Config loaded: input_dir={input_dir}, "
            f"output_dir={output_dir}, "
            f"mapping_file={mapping_file}, "
            f"template_file={template_file}"
        )

        # Reading input JSON files
        json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
        if not json_files:
            logging.warning(f"No JSON files found in {input_dir}")
            return

        # Iterate over each input JSON file
        for filename in json_files:
            file_path = os.path.join(input_dir, filename)
            processor = TemplateProcessor(
                config_file=config_file,
                json_input_file=file_path
            )

            logging.info("render_mappings to intermediate file is started!")
            processor.render_mappings()
            logging.info(
                f"render_mappings to the file {file_path} is success!"
            )
            processor.create_dbt_profile()

    except Exception as e:
        logging.info(f"Last exception block in the main: {e}")


if __name__ == "__main__":
    main()
