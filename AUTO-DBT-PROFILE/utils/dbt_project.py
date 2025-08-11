import os
import json
import yaml
from typing import Dict
import logging
from pathlib import Path


DEFAULT_PACKAGES = {
    "packages": [
        {
            "package": "snowplow/snowplow_unified",
            "version": "0.5.5",
        }
    ]
}


class DBTProjectGenerator:
    """
    A class to generate a dbt project structure
    based on a given profile YAML file
    and a target directory. It reads configuration
    from the profile file to create
    folder structure and generates the necessary
    `dbt_project.yml` and `packages.yml`
    files.

    Attributes:
        profile_file (Path): Path to the dbt profile YAML file.
        final_dir (Path): Directory where the dbt
        project folder will be created.
        profiles (dict): Parsed contents of the
        profile YAML file.
    """

    def __init__(self, profile_file, final_dir):
        self.profile_file = Path(profile_file)
        self.final_dir = Path(final_dir)
        self.profiles = self._read_file(self.profile_file, "yml")

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

    def create_project(self):
        """
        Creates the dbt project directory structure
        based on the profile configuration.

        - Creates a project folder named after
        the profile file (without extension) inside `final_dir`.
        - Creates subdirectories listed in the profile
        under keys containing list of paths.
        - Generates `dbt_project.yml` with the
        loaded profile configuration.
        - Generates `packages.yml` with default
        package settings.

        Prints confirmation message with the
        project path upon success.
        """
        logging.info(
            f"create_project method called"
            f"with profile_file: {self.profile_file} "
            f"and final_dir: {self.final_dir}"
        )

        profile_name = os.path.splitext(os.path.basename(self.profile_file))[0]

        project_root = self.final_dir / profile_name
        project_root.mkdir(parents=True, exist_ok=True)
        logging.info(f"Creating DBT project folder at {project_root}")

        # Create directories based on keys with list values in profile
        for key, paths in self.profiles.items():
            if (
                isinstance(paths, list)
                and all(isinstance(p, str) for p in paths)
            ):
                for folder in paths:
                    (project_root / folder).mkdir(parents=True, exist_ok=True)

        # Write dbt_project.yml
        with open(project_root / "dbt_project.yml", "w") as f:
            yaml.safe_dump(self.profiles, f, sort_keys=False)

        # Write packages.yml
        with open(project_root / "packages.yml", "w") as f:
            yaml.safe_dump(DEFAULT_PACKAGES, f, sort_keys=False)

        logging.info(
            f"DBT project '{profile_name}' created at "
            f"{project_root.resolve()}"
        )
