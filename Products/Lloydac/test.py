from Products.Lloydac.test_utils import execute_test_tcp, execute_cloud_test
import time
import pytest
def test_on_tcp(common_tcp_client):
    execute_test_tcp(common_tcp_client, "POWER_CONTROL_ON", "H1000")  # Passing the whole tuple


def test_temp_set_16(common_tcp_client):
    execute_test_tcp(common_tcp_client, "TEMPERATURE_CONTROL_16", "H1001")

def test_eco_mode(common_tcp_client):
    execute_test_tcp(common_tcp_client, "TURN_ON_ECO", "H3001")

def test_off_tcp(common_tcp_client):
    execute_test_tcp(common_tcp_client, "POWER_CONTROL_OFF", "H1000")


@pytest.mark.parametrize("api_client_fixture", [("QA", "+917387342890", "986040")], indirect=True)
def test_on_cloud(api_client_fixture):
    setup_status, api_client = api_client_fixture
    if setup_status == 'Success':
        command = {"H1000": 1}
        print(command)
        api_client.device_control("63DA0043EC70649000910C630000198CDAC9BD258", command)



