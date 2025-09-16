from importlib.metadata import version as get_version
from logging import getLogger
from pathlib import Path

from .git_helpers import get_repo_name
from .presets import DISTRIBUTION_ARTIFACTS_DIR
from .semantic_release_config import SemanticReleaseConfig

__version__ = get_version(__package__)

logger = getLogger(__name__)


def generate_semantic_release_config(project_repo_path: Path, target_path: Path) -> None:
    repo_name = get_repo_name(project_repo_path)

    config = SemanticReleaseConfig(repo_name, DISTRIBUTION_ARTIFACTS_DIR)
    config.write_to_path(target_path)
