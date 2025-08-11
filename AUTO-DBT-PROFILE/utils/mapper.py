import os
import json
import yaml
import logging
import re
from typing import Dict


class TemplateProcessor:
    """
    TemplateProcessor transforms input JSON data using YAML
    mappings and templates to generate output YAML configurations,
    such as dynamic DBT profile configurations.

    Attributes:
        config_file (str): Path to the main configuration YAML file.
        json_input_file (str): Path to the input JSON file
            containing user data.
        output_dir (str): Directory where the final output will be saved.
        mapping_file (str): Path to the YAML mapping file.
        template_file (str): Path to the template text file for
            rendering.
        intermediate_dir (str): Directory where intermediate
            JSON will be saved.
        mapping_data (dict): Data from the mapping file.
        template_str (str): Template text loaded as a string.
        input_data (dict): Input JSON data loaded from file.
        intermediate_input (dict): Intermediate JSON data after
            applying mappings.
    """

    def __init__(self, config_file: str, json_input_file: str):
        self.config_file = config_file
        self.json_input_file = json_input_file
        self.dict_config_data = self._read_file(config_file, "yml")

        self.output_dir = self.dict_config_data.get("output_dir")
        self.mapping_file = self.dict_config_data.get("mapping_file")
        self.template_file = self.dict_config_data.get("template_file")
        self.intermediate_dir = self.dict_config_data.get("updated_input_dir")

        self.mapping_data = self._read_file(self.mapping_file, "yml")
        self.template_str = self._read_txt(self.template_file)
        self.input_data = self._read_file(self.json_input_file, "json")
        self.intermediate_input = {}

    def _read_file(self, file_path: str, file_type: str) -> Dict:
        """
        Reads and parses a YAML or JSON file.

        Args:
            file_path (str): The full path to the input file.
            file_type (str): The file type to parse, either 'yml' or 'json'.

        Returns:
            Dict: The parsed file content as a Python dictionary.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"{file_type.upper()} file not found at {file_path}"
            )

        with open(file_path, "r", encoding="utf-8") as f:
            if file_type.lower() == "yml":
                data = yaml.safe_load(f)
            elif file_type.lower() == "json":
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        logging.info(f"{file_path}: Valid {file_type.upper()} data loaded.")
        return data

    def _read_txt(self, file_path: str) -> str:
        """
        Reads a plain text file and returns its contents as a string.

        Args:
            file_path (str): Path to the text file.

        Returns:
            str: Content of the file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"TXT file not found at {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()

        logging.info(f"{file_path}: Template file loaded.")
        return data

    def indent_yaml_block(self, yaml_str: str, base_indent: int = 8) -> str:
        lines = yaml_str.splitlines()
        result = []
        key_indent = base_indent
        list_indent = base_indent + 2

        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith("-"):
                result.append(" " * list_indent + stripped)
            else:
                result.append(" " * key_indent + stripped)

        return "\n".join(result) + "\n"

    def render_mappings(self):
        """
        Renders a DBT profile configuration by replacing template variables
        using the intermediate transformed JSON data.

        Output:
            Writes final rendered profile YAML to `output_dir`.
        """
        updated_json = {}
        unknown_json = {}
        bool_mapping = {"yes": True, "no": False}

        for json_key, json_value in self.input_data.items():
            if json_key == "user_set_variables":
                for lv_key, lv_value in json_value.items():
                    value = self._extract_value(lv_key) or "unknown"
                    if value == "unknown":
                        unknown_json[lv_key] = lv_value
                        updated_json[value] = unknown_json
                    else:
                        updated_json[value] = (
                            bool_mapping.get(lv_value, lv_value)
                            if isinstance(lv_value, str)
                            else lv_value
                        )
            else:
                value = self._extract_value(json_key) or "unknown"
                if value == "unknown":
                    unknown_json[json_key] = json_value
                    updated_json[value] = unknown_json
                else:
                    updated_json[value] = (
                        bool_mapping.get(json_value, json_value)
                        if isinstance(json_value, str)
                        else json_value
                    )

        self.intermediate_input = updated_json
        intermediate_file = os.path.join(
            self.intermediate_dir,
            "updated_" + os.path.basename(self.json_input_file),
        )

        with open(intermediate_file, "w") as f:
            json.dump(updated_json, f, indent=2)

        logging.info("render_mappings to the variable is success!")

    def create_dbt_profile(self) -> str:
        """
        Rendering the mappings and create a new input
        file with matched string from the mappings
        """
        rendered = self.template_str
        var_json = {}

        for json_key, json_value in self.intermediate_input.items():
            if json_key == "unknown":
                continue
            elif re.search(json_key, rendered):
                rendered = rendered.replace(
                    "{" + json_key + "}", str(json_value)
                )
            else:
                var_json[json_key] = json_value

        yaml_string = yaml.dump(
            var_json, default_flow_style=False, sort_keys=False
        )
        indented_yaml = self.indent_yaml_block(yaml_string)
        vars_block = (
            f"vars:\n{indented_yaml}" if indented_yaml.strip() != "{}" else ""
        )

        rendered = rendered.replace("{vars_block}", vars_block)
        rendered = rendered.replace("{project_name}", "Default project name")

        output_file = os.path.join(
            self.output_dir,
            os.path.splitext(
                os.path.basename(self.json_input_file)
            )[0] + "_profile.yml",
        )

        with open(output_file, "w") as file:
            file.write(rendered)
        return output_file

    def _extract_value(self, json_key: str):
        """
        Extracts a mapped value for a given key,
        supports nested keys using dot notation.

        Args:
            json_key (str): The input key from JSON.

        Returns:
            str: Corresponding mapped value or empty string if not found.
        """
        keys = json_key.split(".")
        value = self.mapping_data
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            logging.warning(f"Key '{json_key}' not found in mapped data.")
            return ""
