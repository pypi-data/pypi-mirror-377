from collections.abc import Iterable
from pathlib import Path
from sys import version_info
from tomllib import loads

from tomli_w import dump

from .placeholder import Placeholder

OLD_PYTHON_MINOR_VERSION = 11

if version_info.minor == OLD_PYTHON_MINOR_VERSION:
    from importlib_resources import files
else:
    from importlib.resources import files


class SemanticReleaseConfig:
    @staticmethod
    def get_semantic_release_toml_template() -> str:
        assets = files(f"{__package__}.assets")
        sr_config_asset: str = (
            assets.joinpath("toml").joinpath("semantic-release.toml").read_text(encoding="utf-8")
        )
        return sr_config_asset

    @staticmethod
    def replace_placeholders(s: str, placeholders: Iterable[Placeholder]) -> str:
        for placeholder in placeholders:
            s = s.replace(placeholder.placeholder, placeholder.value)
        return s

    def __init__(self, repo_name: str, distribution_artifacts_dir: str) -> None:
        placeholders: Iterable[Placeholder] = (
            Placeholder("repo name", repo_name),
            Placeholder("distribution artifacts dir", distribution_artifacts_dir),
        )
        toml_template: str = self.get_semantic_release_toml_template()
        self.toml_str: str = self.replace_placeholders(toml_template, placeholders)

    @property
    def toml_dict(self) -> dict[str, str]:
        return loads(self.toml_str)

    def write_to_path(self, path: Path) -> None:
        with path.open("wb") as target_config_file:
            dump(self.toml_dict, target_config_file, multiline_strings=True)
