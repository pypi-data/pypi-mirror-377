from typing import Dict, Any
from pathlib import Path


def create_input_file(
    model_name: str, kmc_inputs: Dict[str, Any], filepath: Path | str
) -> str:

    base_dir = Path(__file__).parent.parent.parent

    if model_name == "FRP2":
        model_filepath = base_dir / "templates/FRP2_Template.txt"
    elif model_name == "CRP3":
        model_filepath = base_dir / "templates/CRP3_Template.txt"
    elif model_name == "AMS_MMA":
        model_filepath = base_dir / "templates/AMS_MMA_Template.txt"
    else:
        raise ValueError(f"Model {model_name} not supported")

    # Read model template file
    with open(model_filepath, "r") as file:
        template_content = file.read()

    # Replace placeholders in template with input values
    for key, value in kmc_inputs.items():
        placeholder = "{" + key + "}"

        try:
            value = str(value)
        except ValueError:
            raise ValueError(f"Value for {key} cannot be converted to string.")

        template_content = template_content.replace(placeholder, value)

    with open(filepath, "w") as file:
        file.write(template_content)
