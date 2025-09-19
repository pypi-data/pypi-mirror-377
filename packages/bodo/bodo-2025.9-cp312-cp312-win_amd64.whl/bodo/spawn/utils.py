"""Utilities for Spawn Mode.
This file should import JIT lazily to avoid slowing down non-JIT code paths.
"""

from __future__ import annotations

import logging
import os
import sys
import typing as pt
import uuid
from enum import Enum
from time import sleep

import bodo.user_logging
from bodo.mpi4py import MPI


class CommandType(str, Enum):
    """
    Enum of the different types of commands that the spawner
    can send to the workers.
    """

    EXEC_FUNCTION = "exec"
    EXIT = "exit"
    BROADCAST = "broadcast"
    SCATTER = "scatter"
    GATHER = "gather"
    DELETE_RESULT = "delete_result"
    REGISTER_TYPE = "register_type"
    SET_CONFIG = "set_config"
    SPAWN_PROCESS = "spawn_process"
    STOP_PROCESS = "stop_process"


def poll_for_barrier(comm: MPI.Comm, poll_freq: float | None = 0.1):
    """
    Barrier that doesn't busy-wait, but instead polls on a defined interval.
    The poll_freq kwarg controls the rate of polling. When set to None it will
    busy-wait.
    """
    # Start a non-blocking barrier operation
    req = comm.Ibarrier()
    if not poll_freq:
        # If polling is disabled, just wait for the barrier synchronously
        req.Wait()
    else:
        # Check if the barrier has completed and sleep if not.
        # TODO Add exponential backoff (e.g. start with 0.01 and go up
        # to 0.1). This could provide a faster response in many cases.
        while not req.Test():
            sleep(poll_freq)


def debug_msg(logger: logging.Logger, msg: str):
    """Send debug message to logger if Bodo verbose level 2 is enabled"""
    if bodo.user_logging.get_verbose_level() >= 2:
        logger.debug(msg)


class ArgMetadata(str, Enum):
    """Argument metadata to inform workers about other arguments to receive separately.
    E.g. broadcast or scatter a dataframe from spawner to workers.
    Used for DataFrame/Series/Index/array arguments.
    """

    BROADCAST = "broadcast"
    SCATTER = "scatter"
    LAZY = "lazy"


def set_global_config(config_name: str, config_value: pt.Any):
    """Set global configuration value by name (for internal testing use only)
    (e.g. "bodo.hiframes.boxing._use_dict_str_type")
    """
    # Get module and attribute sections of config_name
    # (e.g. "bodo.hiframes.boxing._use_dict_str_type" -> "bodo.hiframes.boxing"
    # and "_use_dict_str_type")
    c_split = config_name.split(".")
    attr = c_split[-1]
    mod_name = ".".join(c_split[:-1])
    locs = {}
    exec(f"import {mod_name}; mod = {mod_name}", globals(), locs)
    mod = locs["mod"]
    setattr(mod, attr, config_value)


class WorkerProcess:
    _uuid: uuid.UUID
    _rank_to_pid: dict[int, int] = {}

    def __init__(self, rank_to_pid: dict[int, int] = {}):
        """Initialize WorkerProcess with a mapping of ranks to PIDs."""
        self._uuid = uuid.uuid4()
        self._rank_to_pid = rank_to_pid


def is_jupyter_on_windows() -> bool:
    """Returns True if running in Jupyter on Windows"""

    # Flag for testing purposes
    if os.environ.get("BODO_OUTPUT_REDIRECT_TEST", "0") == "1":
        return True

    return sys.platform == "win32" and (
        "JPY_SESSION_NAME" in os.environ
        or "PYDEVD_IPYTHON_COMPATIBLE_DEBUGGING" in os.environ
    )


def is_jupyter_on_bodo_platform() -> bool:
    """Returns True if running in Jupyter on Bodo Platform"""

    platform_cloud_provider = os.environ.get("BODO_PLATFORM_CLOUD_PROVIDER", None)
    return (platform_cloud_provider is not None) and (
        "JPY_SESSION_NAME" in os.environ
        or "PYDEVD_IPYTHON_COMPATIBLE_DEBUGGING" in os.environ
    )


def sync_and_reraise_error(
    err,
    _is_parallel=False,
    bcast_lowest_err: bool = True,
    default_generic_err_msg: str | None = None,
):  # pragma: no cover
    """
    If `err` is an Exception on any rank, raise an error on all ranks.
    If 'bcast_lowest_err' is True, we will broadcast the error from the
    "lowest" rank that has an error and raise it on all the ranks without
    their own error. If 'bcast_lowest_err' is False, we will raise a
    generic error on ranks without their own error. This is useful in
    cases where the error could be something that's not safe to broadcast
    (e.g. not pickle-able).
    This is a no-op if all ranks are exception-free.

    Args:
        err (Exception or None): Could be None or an exception
        _is_parallel (bool): Whether this is being called from many ranks
        bcast_lowest_err (bool): Whether to broadcast the error from the
            lowest rank. Only applicable in the _is_parallel case.
        default_generic_err_msg (str, optional): If bcast_lowest_err = False,
            this message will be used for the exception raised on
            ranks without their own error. Only applicable in the
            _is_parallel case.
    """
    comm = MPI.COMM_WORLD

    if _is_parallel:
        # If any rank raises an exception, re-raise that error on all non-failing
        # ranks to prevent deadlock on future MPI collective ops.
        # We use allreduce with MPI.MAXLOC to communicate the rank of the lowest
        # failing process, then broadcast the error backtrace across all ranks.
        err_on_this_rank = int(err is not None)
        err_on_any_rank, failing_rank = comm.allreduce(
            (err_on_this_rank, comm.Get_rank()), op=MPI.MAXLOC
        )
        if err_on_any_rank:
            if comm.Get_rank() == failing_rank:
                lowest_err = err
            else:
                lowest_err = None
            if bcast_lowest_err:
                lowest_err = comm.bcast(lowest_err, root=failing_rank)
            else:
                err_msg = (
                    default_generic_err_msg
                    if (default_generic_err_msg is not None)
                    else "Exception on some ranks. See other ranks for error."
                )
                lowest_err = Exception(err_msg)

            # Each rank that already has an error will re-raise their own error, and
            # any rank that doesn't have an error will re-raise the lowest rank's error.
            if err_on_this_rank:
                raise err
            else:
                raise lowest_err
    else:
        if err is not None:
            raise err


def import_compiler_on_workers():
    """Import the JIT compiler on all workers. Done as necessary since import time
    can be significant.
    """

    def import_compiler():
        import bodo.decorators  # isort:skip # noqa

    bodo.spawn.spawner.submit_func_to_workers(lambda: import_compiler(), [])
