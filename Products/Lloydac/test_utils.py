from Products.Lloydac.lloydac import LloydAC
from Utilities.utils import CommonMethod
import pytest
import time
pytestmark = pytest.mark.skip
def execute_test_tcp(tcp_client, command_key, telemetry_key):
    setup_status, tcp_wrapper = tcp_client
    if setup_status == 'Success':
        command = LloydAC.get_command(command_key)  # Updated to use get_command
        print(f"Command: {command}")

        received_data = tcp_wrapper.tcp_communication(command, 0.1)  # No need to use commands[0] anymore
        status, rx_data = CommonMethod.compare_telemetry(received_data, command, telemetry_key)

        print(f'status: {status}')
        assert status == 0
    else:
        pytest.fail(f"Setup failed with status: {setup_status}")


def execute_cloud_test(common_api_client, command, telemetry_key):
    setup_status, api_client, device_id = common_api_client  # Unpacking here

    if setup_status == 'Success':
        print(f"Command: {command}")
        api_client.device_control(device_id, command)
        time.sleep(3)
        received_data = api_client.fetch_device_status(device_id)
        status, rx_data = CommonMethod.compare_telemetry(received_data, command, telemetry_key)

        print(f'status: {status}')
        assert status == 0
    else:
        pytest.fail(f"Setup failed with status: {setup_status}")

