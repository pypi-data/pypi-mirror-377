# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0


from pathlib import Path
from typing import Any, Optional, Union

import msgspec
import ruamel.yaml

from . import models as cici_config


def loads(
    text: str,
    gitlab_ci_jobs: Optional[dict[str, Any]] = None,
    precommit_hooks: Optional[dict[str, Any]] = None,
) -> cici_config.File:
    # parse YAML into fully-typed File object
    if gitlab_ci_jobs is None:
        gitlab_ci_jobs = {}
    if precommit_hooks is None:
        precommit_hooks = {}

    yaml = ruamel.yaml.YAML(typ="safe")
    data = yaml.load(text)

    # verifying target key exists
    data.setdefault("targets", [])
    data.setdefault("variables", {})

    # for variables to pre inject name into each entry if it is there or not
    for key, value in data["variables"].items():
        value["name"] = key

    # this is where we inject additional external fields if they exist
    for target in data["targets"]:
        if target["name"] in precommit_hooks:
            target["precommit_hook"] = {"name": target["name"]}
        if target["name"] in gitlab_ci_jobs:
            target["gitlab_include"] = {"name": target["name"]}

        # merge groups into tags if groups contains anything tags does not have already
        tags = set(target.get("tags", []))
        groups = set(target.get("groups", []))
        target["tags"] = list(tags | groups)

    # convert dict -> typed File struct
    return msgspec.convert(data, cici_config.File)


def load(
    file: Union[str, Path],
    gitlab_ci_jobs: Optional[dict[str, Any]] = None,
    precommit_hooks: Optional[dict[str, Any]] = None,
) -> cici_config.File:
    return loads(
        open(file).read(),
        gitlab_ci_jobs=gitlab_ci_jobs,
        precommit_hooks=precommit_hooks,
    )
