# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional

import msgspec


class PreCommitHookTarget(msgspec.Struct, frozen=True, kw_only=True):
    name: str


class GitLabIncludeTarget(msgspec.Struct, frozen=True, kw_only=True):
    name: str


class Group(msgspec.Struct, frozen=True, kw_only=True):
    name: str
    brief: str = ""
    description: str = ""


class Target(msgspec.Struct, frozen=True, kw_only=True):
    name: str
    brief: str = ""
    description: str = ""

    groups: List[str] = msgspec.field(default_factory=list)
    tags: List[str] = msgspec.field(default_factory=list)

    precommit_hook: Optional[PreCommitHookTarget] = None
    gitlab_include: Optional[GitLabIncludeTarget] = None


class VariableExample(msgspec.Struct, frozen=True, kw_only=True):
    value: str
    brief: str = ""


class Variable(msgspec.Struct, frozen=True, kw_only=True):
    name: str
    brief: str = ""
    default: str = ""
    description: str = ""
    required: bool = False
    examples: List[VariableExample] = msgspec.field(default_factory=list)


class File(msgspec.Struct, frozen=True, kw_only=True):
    name: str

    repo_url: str = ""

    gitlab_project_path: str = ""

    brief: str = ""
    description: str = ""

    groups: list[Group] = msgspec.field(default_factory=list)
    targets: list[Target] = msgspec.field(default_factory=list)
    variables: dict[str, Variable] = msgspec.field(default_factory=dict)
