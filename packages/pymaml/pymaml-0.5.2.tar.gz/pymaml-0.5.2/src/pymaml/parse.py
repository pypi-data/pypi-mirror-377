"""
Helper module to parse and check valid maml data structures.
"""

from pydantic_core import ValidationError

from .model_v1p0 import V1P0
from .model_v1p1 import V1P1
from .read import read_maml


MODELS = {
    "v1.0": V1P0,
    "v1.1": V1P1,
}


def _assert_version(version: str) -> None:
    """
    Determines if the version is supported and crashes if it isn't.
    """
    if version not in MODELS:
        raise ValueError(
            f"{version} is not a valid version. Supported MAML versions: {list(MODELS.keys())}"
        )


def valid_for(file_name: str) -> list[str]:
    """
    Reads in a file and determines if it is valid for versions of maml.
    """
    dictionary = read_maml(file_name)
    valid = []
    for version, model in MODELS.items():
        try:
            model(**dictionary)
            valid.append(version)
        except ValidationError:
            pass
    if not valid:
        return ["Not valid for any version of MAML"]
    return valid
