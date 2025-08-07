import os
import json
import yaml
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.mapper import TemplateProcessor  # noqa: E402


def test_render_mappings_and_create_profile(tmp_path):
    # Setup directory structure and files
    config_data = {
        "input_dir": str(tmp_path),
        "output_dir": str(tmp_path / "output"),
        "updated_input_dir": str(tmp_path / "intermediate"),
        "mapping_file": str(tmp_path / "mapping.yml"),
        "template_file": str(tmp_path / "template.txt"),
    }

    input_data = {
        "brand_name": "Test project",
        "snowplow__enable_web": "yes",
        "snowplow__enable_mobile": "no",
        "app_ids": ["app_web", "app_mobile"],
    }

    mapping_data = {
        "brand_name": "project_name",
        "snowplow__enable_web": "enable_web",
        "snowplow__enable_mobile": "enable_mobile",
        "app_ids": "app_id",
    }

    template = """
name: "{project_name}"
profile: "{project_name}"
models:
  {project_name}:
    enabled: true
    enable_web: {enable_web}
    enable_mobile: {enable_mobile}
    {vars_block}
"""

    expected_output = """
name: "Test project"
profile: "Test project"
models:
  Test project:
    enabled: true
    enable_web: True
    enable_mobile: False
    vars:
      app_id:
        - app_web
        - app_mobile
"""

    # Create directories
    (tmp_path / "output").mkdir()
    (tmp_path / "intermediate").mkdir()

    # Create required files
    config_path = tmp_path / "config.yml"
    mapping_path = tmp_path / "mapping.yml"
    template_path = tmp_path / "template.txt"
    input_path = tmp_path / "test_input.json"

    config_path.write_text(yaml.dump(config_data))
    mapping_path.write_text(yaml.dump(mapping_data))
    template_path.write_text(template)
    input_path.write_text(json.dumps(input_data))

    # Run TemplateProcessor
    processor = TemplateProcessor(
        config_file=str(config_path),
        json_input_file=str(input_path),
    )

    processor.render_mappings()
    processor.create_dbt_profile()

    # Check output file
    output_file = tmp_path / "output" / "test_input_profile.yml"
    assert output_file.exists()

    output_content = output_file.read_text()

    assert "enable_web: True" in output_content
    assert "enable_mobile: False" in output_content
    assert "app_id" in output_content

    expected_yaml = yaml.safe_load(expected_output)
    actual_yaml = yaml.safe_load(output_content)

    assert actual_yaml == expected_yaml, (
        f"\nExpected:\n{expected_yaml}\n\nActual:\n{actual_yaml}"
    )
