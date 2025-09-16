# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path

import gitlab
from gitlab.exceptions import GitlabGetError
from termcolor import colored

from .. import pullyfile
from ..constants import BASE_DIR
from ..pullyfile import PullyGroup, PullyProject


def get_gitlab_group_id_from_full_path(gl: gitlab.Gitlab, group_path: str) -> int:
    groups = gl.groups.list(search=group_path, get_all=True)
    for group in groups:
        if group.full_path == group_path:
            return group.id
    raise ValueError("group id not found")


def get_gitlab_project_id_from_full_path(glgroup, project_path: str) -> int:
    glprojects = glgroup.projects.list(search=project_path)
    for glproject in glprojects:
        if glproject.path == project_path:
            return glproject.id
    raise ValueError("project id not found")


def add_command(args):
    if not (args.group_id or args.group_path or args.project_id or args.project_path):
        print("projects or groups to add must be specified.")
        exit(1)
    base_dir = Path(args.directory) if args.directory else BASE_DIR
    if not base_dir.exists():
        print(f"{base_dir} does not exist")
        exit(1)

    gl = gitlab.Gitlab(private_token=os.environ.get("GITLAB_PRIVATE_TOKEN"))

    group_ids = []
    project_ids = []
    skipped_groups = []
    skipped_projects = []

    if args.group_path:
        print(
            "searching for group ids by full path: {paths}".format(
                paths=", ".join(args.group_path)
            )
        )
        for group in args.group_path:
            try:
                group_ids.append(get_gitlab_group_id_from_full_path(gl, group))
            except ValueError:
                skipped_groups.append(group)
                print(f"Unable to find group {group}")
    if args.group_id:
        group_ids.extend(args.group_id)
    if args.project_path:
        print(
            "searching for project ids by full path: {paths}".format(
                paths=", ".join(args.project_path)
            )
        )
        for project in args.project_path:
            try:
                project_path = Path(project)
                group_path = str(project_path.parent)
                group_id = get_gitlab_group_id_from_full_path(gl, group_path)
                glgroup = gl.groups.get(group_id)
                project_ids.append(
                    get_gitlab_project_id_from_full_path(
                        glgroup, str(project_path.name)
                    )
                )
            except ValueError:
                skipped_projects.append(project)
                print(f"Unable to find project {project}")
    if args.project_id:
        project_ids.extend(args.project_id)

    if group_ids:
        print("found group ids:", group_ids)
    if project_ids:
        print("found project ids:", project_ids)

    glprojects = []
    glgroups = []
    for group_id in group_ids:
        try:
            glgroup = gl.groups.get(id=group_id)
            glgroups.append(glgroup)
            glprojects.extend(
                glgroup.projects.list(
                    archived=False,
                    include_subgroups=True,
                    order_by="name",
                    sort="asc",
                    limit=3,
                    all=True,
                )
            )
        except GitlabGetError:
            skipped_groups.append(group_id)
            print(f"Unable to find group {group_id}")
    for project_id in project_ids:
        try:
            glprojects.append(gl.projects.get(id=project_id))
        except GitlabGetError:
            skipped_projects.append(project_id)
            print(f"Unable to find project {project_id}")

    with pullyfile.project_context(base_dir, search=not args.directory) as context:
        config_dir, projects, groups = context
        for glgroup in glgroups:
            if glgroup.id in groups:
                continue
            groups[glgroup.id] = PullyGroup(
                group_id=glgroup.id,
                local_path=glgroup.full_path,
            )
        for glproject in glprojects:
            if hasattr(glproject, "empty_repo") and glproject.empty_repo:
                continue
            if glproject.id in projects:
                continue
            projects[glproject.id] = PullyProject(
                project_id=glproject.id,
                local_path=glproject.path_with_namespace,
                ssh_url=glproject.ssh_url_to_repo,
            )
            print(colored("adding", "green"), glproject.path_with_namespace)
        if skipped_groups:
            print(colored("skipped", "red"), f"groups: {skipped_groups}")
        if skipped_projects:
            print(colored("skipped", "red"), f"projects: {skipped_projects}")


def add_command_parser(subparsers):
    parser = subparsers.add_parser("add")
    parser.set_defaults(func=add_command)

    parser.add_argument("-g", "--group-id", action="extend", nargs="*", type=int)
    parser.add_argument("-G", "--group-path", action="extend", nargs="*", type=str)
    parser.add_argument("-p", "--project-id", action="extend", nargs="*", type=int)
    parser.add_argument("-P", "--project-path", action="extend", nargs="*", type=str)
