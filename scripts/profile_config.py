"""Load and validate the editable profile configuration."""
import re

import yaml

SORTS = {"recently_pushed", "most_starred", "alphabetical", "recently_created"}
LIST_FIELDS = {"exclude_repositories", "featured_repositories", "currently_working_on", "learning_interests"}


def load_config(path):
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    keys = LIST_FIELDS | {"username", "sort", "repository_limit", "include_forks"}
    if not isinstance(config, dict) or set(config) != keys:
        raise ValueError("Profile settings are missing or contain unknown keys")
    if not isinstance(config["username"], str) or not re.fullmatch(
        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", config["username"]
    ):
        raise ValueError("Invalid GitHub username")
    if not isinstance(config["sort"], str) or config["sort"] not in SORTS:
        raise ValueError("Invalid repository sort")
    if type(config["repository_limit"]) is not int or not 1 <= config["repository_limit"] <= 50:
        raise ValueError("repository_limit must be an integer between 1 and 50")
    if type(config["include_forks"]) is not bool:
        raise ValueError("include_forks must be true or false")
    for key in LIST_FIELDS:
        values = config[key]
        if not isinstance(values, list) or any(not isinstance(item, str) or not item.strip() for item in values):
            raise ValueError(f"{key} must be a list of nonempty strings")
        if len({item.casefold() for item in values}) != len(values):
            raise ValueError(f"{key} contains duplicates")
    return config
