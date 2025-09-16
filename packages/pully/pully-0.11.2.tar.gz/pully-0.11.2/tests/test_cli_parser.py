# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import contextlib
import io
import os

import pytest

from pully.cli.run_command import build_pully_run_command
from pully.main import parse_args


@contextlib.contextmanager
def temp_environment():
    current = dict(os.environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(current)


@pytest.mark.parametrize(
    "argv,funcname,expected,succeed",
    (
        ([], "pull_command", dict(), False),
        # init
        (["init"], "init_command", dict(), True),
        # add
        (["add", "-p", "70752539"], "add_command", dict(project_id=[70752539]), True),
        (
            ["add", "-P", "saferatday0/badgie"],
            "add_command",
            dict(project_path=["saferatday0/badgie"]),
            True,
        ),
        (
            ["add", "-p", "70752539", "70752540", "-g", "78192659", "70752539"],
            "add_command",
            dict(project_id=[70752539, 70752540], group_id=[78192659, 70752539]),
            True,
        ),
        (
            ["add", "-g", "78192659", "70752539"],
            "add_command",
            dict(group_id=[78192659, 70752539]),
            True,
        ),
        (
            ["add", "-G", "saferatday0"],
            "add_command",
            dict(group_path=["saferatday0"]),
            True,
        ),
        (
            ["add", "-G", "saferatday0", "dyff", "-g", "78192659", "70752539"],
            "add_command",
            dict(group_id=[78192659, 70752539], group_path=["saferatday0", "dyff"]),
            True,
        ),
        # ls
        (["ls"], "ls_command", dict(), True),
        (["ls", "-p", "safe"], "ls_command", dict(path_prefix="safe"), True),
        (["ls", "--path-prefix", "safe"], "ls_command", dict(path_prefix="safe"), True),
        # get
        (["get"], "get_command", dict(), True),
        (["get", "-p", "safe"], "get_command", dict(path_prefix="safe"), True),
        (
            ["get", "--path-prefix", "safe"],
            "get_command",
            dict(path_prefix="safe"),
            True,
        ),
        (
            ["get"],
            "get_command",
            dict(strategy="clone"),
            True,
        ),
        (
            ["get"],
            "get_command",
            dict(strategy="clone"),
            True,
        ),
        (
            ["get", "-s", "clone"],
            "get_command",
            dict(strategy="clone"),
            True,
        ),
        (
            ["get", "--strategy", "clone"],
            "get_command",
            dict(strategy="clone"),
            True,
        ),
        (
            ["get", "-s", "fetch"],
            "get_command",
            dict(strategy="fetch"),
            True,
        ),
        (
            ["get", "--strategy", "fetch"],
            "get_command",
            dict(strategy="fetch"),
            True,
        ),
        (
            ["get", "-s", "pull"],
            "get_command",
            dict(strategy="pull"),
            True,
        ),
        (
            ["get", "--strategy", "pull"],
            "get_command",
            dict(strategy="pull"),
            True,
        ),
        (
            ["get", "-s", "hmm"],
            "get_command",
            None,
            False,
        ),
        (
            ["get", "--strategy", "hmm"],
            "get_command",
            None,
            False,
        ),
        # run
        (["run"], "run_command", None, False),
        (["run", "-p", "safe"], "run_command", None, False),
        (
            ["run", "--path-prefix", "safe"],
            "run_command",
            None,
            False,
        ),
        (
            ["run", "-p", "safe", "ls"],
            "run_command",
            dict(path_prefix="safe", args=["ls"]),
            True,
        ),
        (
            ["run", "--path-prefix", "safe", "ls"],
            "run_command",
            dict(path_prefix="safe", args=["ls"]),
            True,
        ),
        (["run", "-c", "echo hello"], "run_command", dict(command="echo hello"), True),
        (["run", "-c", "echo", "hello"], "run_command", None, False),
        (["run", "-c", "-"], "run_command", dict(command="-"), True),
        (
            ["run", "-e", '["/bin/bash", "-c"]', "-c", "echo hello"],
            "run_command",
            dict(entrypoint=["/bin/bash", "-c"], command="echo hello"),
            True,
        ),
        (
            ["run", "-e", '["/bin/bash", "-c"]', "echo", "hello"],
            "run_command",
            dict(args=["echo", "hello"]),
            True,
        ),
        (["run", "echo", "hello"], "run_command", dict(args=["echo", "hello"]), True),
    ),
)
def test_parse_args(argv, funcname, expected, succeed):
    if succeed:
        args = parse_args(argv)
        assert args.func.__name__ == funcname
        for key, value in expected.items():
            assert getattr(args, key) == value
    else:
        with pytest.raises(SystemExit):
            args = parse_args(argv)


@pytest.mark.parametrize(
    "in_args,in_command,in_stdin,success,out_command,out_error",
    (
        (["run", "ls"], [], None, True, ["/bin/ls"], None),
        (["run", "--", "ls", "-l"], [], None, True, ["/bin/ls", "-l"], None),
        (
            ["run", "-c", "echo hello"],
            [],
            None,
            True,
            ["/bin/sh", "-euc", "echo hello"],
            None,
        ),
        (
            ["run", "-c", "-"],
            [],
            "echo hello",
            True,
            ["/bin/sh", "-euc", "echo hello"],
            None,
        ),
        (
            ["run", "-e", '["/bin/bash", "-c"]', "-c", "echo hello"],
            [],
            None,
            True,
            ["/bin/bash", "-c", "echo hello"],
            None,
        ),
        (
            ["run", "rochuoeuhet"],
            [],
            None,
            False,
            None,
            FileNotFoundError,
        ),
    ),
)
def test_build_run_command(
    in_args, in_command, in_stdin, success, out_command, out_error
):
    with temp_environment():
        os.environ["PATH"] = "/bin"
        input_file = None if in_stdin is None else io.StringIO(in_stdin)
        args = parse_args(in_args)
        if success:
            assert build_pully_run_command(args, input_file=input_file) == out_command
        else:
            with pytest.raises(out_error):
                build_pully_run_command(args, input_file=input_file)
