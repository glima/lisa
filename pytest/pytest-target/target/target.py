"""Provides the abstract base `Target` class."""
from __future__ import annotations

import platform
import typing
from abc import ABC, abstractmethod
from io import BytesIO
from uuid import uuid4

import fabric  # type: ignore
import invoke  # type: ignore
from invoke.runners import Result  # type: ignore
from schema import Schema  # type: ignore
from tenacity import retry, stop_after_attempt, wait_exponential  # type: ignore

if typing.TYPE_CHECKING:
    from typing import Any, Mapping, Set


class Target(ABC):
    """Extends 'fabric.Connection' with our own utilities."""

    # Typed instance attributes, not class attributes.
    parameters: Mapping[str, str]
    features: Set[str]
    name: str
    host: str
    conn: fabric.Connection

    # Setup a sane configuration for local and remote commands. Note
    # that the defaults between Fabric and Invoke are different, so we
    # use their Config classes explicitly later.
    config = {
        "run": {
            # Show each command as its run.
            "echo": True,
            # Disable stdin forwarding.
            "in_stream": False,
            # Don’t let remote commands take longer than five minutes
            # (unless later overridden). This is to prevent hangs.
            "command_timeout": 1200,
        }
    }

    def __init__(
        self,
        parameters: Mapping[str, str],
        features: Set[str],
        name: str = f"pytest-{uuid4()}",
    ):
        """If not given a name, generates one uniquely.

        Name is a unique identifier for the group of associated
        resources. Features is a list of requirements such as sriov,
        rdma, gpu, xdp.

        """
        # TODO: Do we need to re-validate the parameters here?
        self.parameters = parameters
        self.features = features
        self.name = name

        # TODO: Review this thoroughly as currently it depends on
        # parameters which is side-effecty.
        self.host = self.deploy()

        fabric_config = self.config.copy()
        fabric_config["run"]["env"] = {  # type: ignore
            # Set PATH since it’s not a login shell.
            "PATH": "/sbin:/usr/sbin:/usr/local/sbin:/bin:/usr/bin:/usr/local/bin"
        }
        self.conn = fabric.Connection(
            self.host,
            config=fabric.Config(overrides=fabric_config),
            inline_ssh_env=True,
        )

    # NOTE: This ought to be a property, but the combination of
    # @classmethod, @property, and @abstractmethod is only supported
    # in Python 3.9 and up.
    @classmethod
    @abstractmethod
    def schema(cls) -> Schema:
        """Must return a schema for expected instance parameters.

        TODO: This schema is used for each instance. We may want to
        define platform-level shared schemata too.

        """
        ...

    @abstractmethod
    def deploy(self) -> str:
        """Must deploy the target resources and return hostname."""
        ...

    @abstractmethod
    def delete(self) -> None:
        """Must delete the target resources."""
        ...

    # A class attribute because it’s defined.
    local_context = invoke.Context(config=invoke.Config(overrides=config))

    @classmethod
    def local(cls, *args: Any, **kwargs: Any) -> Result:
        """This patches Fabric's 'local()' function to ignore SSH environment."""
        return Target.local_context.run(*args, **kwargs)

    @retry(reraise=True, wait=wait_exponential(), stop=stop_after_attempt(3))
    def ping(self, **kwargs: Any) -> Result:
        """Ping the node from the local system in a cross-platform manner."""
        flag = "-c 1" if platform.system() == "Linux" else "-n 1"
        return self.local(f"ping {flag} {self.host}", **kwargs)

    def cat(self, path: str) -> str:
        """Gets the value of a remote file without a temporary file."""
        with BytesIO() as buf:
            self.conn.get(path, buf)
            return buf.getvalue().decode("utf-8").strip()


class Local(Target):
    @classmethod
    def schema(cls) -> Schema:
        return Schema(None)

    def deploy(self) -> str:
        return "localhost"

    def delete(self) -> None:
        pass
