# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from pathlib import Path
from typing import Optional

from lisa import Node, TestCaseMetadata, TestSuite, TestSuiteMetadata
from lisa.environment import EnvironmentStatus
from lisa.features import SerialConsole
from lisa.testsuite import simple_requirement
from lisa.util import LisaException, PassedException
from lisa.util.perf_timer import create_timer
from lisa.util.shell import wait_tcp_port_ready


@TestSuiteMetadata(
    area="provisioning",
    category="functional",
    description="""
    This test suite uses to verify if an environment can be provisioned correct or not.

    - The basic smoke test can run on all images to determinate if a image can boot and
    reboot.
    - Other provisioning tests verify if an environment can be provisioned with special
    hardware configurations.
    """,
)
class Provisioning(TestSuite):
    TIME_OUT = 300

    @TestCaseMetadata(
        description="""
        This case verifies whether a node is operating normally.

        Steps,
        1. Connect to TCP port 22. If it's not connectable, failed and check whether
            there is kernel panic.
        2. Connect to SSH port 22, and reboot the node. If there is an error and kernel
            panic, fail the case. If it's not connectable, also fail the case.
        3. If there is another error, but not kernel panic or tcp connection, pass with
            warning.
        4. Otherwise, fully passed.
        """,
        priority=0,
        requirement=simple_requirement(
            environment_status=EnvironmentStatus.Deployed,
            supported_features=[SerialConsole],
        ),
    )
    def smoke_test(self, case_name: str, node: Node) -> None:
        case_path: Optional[Path] = None

        is_ready, tcp_error_code = wait_tcp_port_ready(
            node.public_address, node.public_port, log=self.log, timeout=self.TIME_OUT
        )
        if not is_ready:
            serial_console = node.features[SerialConsole]
            case_path = self._create_case_log_path(case_name)
            serial_console.check_panic(saved_path=case_path, stage="bootup")
            raise LisaException(
                f"cannot connect to [{node.public_address}:{node.public_port}], "
                f"error code: {tcp_error_code}, no panic found in serial log"
            )

        try:
            timer = create_timer()
            self.log.info(
                f"SSH port 22 is opened, connecting and rebooting '{node.name}'"
            )
            node.reboot()
            self.log.info(f"node '{node.name}' rebooted in {timer}")
        except Exception as identifier:
            if not case_path:
                case_path = self._create_case_log_path(case_name)
            serial_console = node.features[SerialConsole]
            # if there is any panic, fail before partial pass
            serial_console.check_panic(saved_path=case_path, stage="reboot")

            # if node cannot be connected after reboot, it should be failed.
            if isinstance(identifier, LisaException) and str(identifier).startswith(
                "cannot connect to TCP port"
            ):
                raise LisaException(f"after reboot, {identifier}")
            raise PassedException(identifier)
