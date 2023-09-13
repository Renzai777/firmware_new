from Products.Lloydac.test_utils import execute_test_tcp, execute_cloud_test


def test_on_tcp(common_tcp_client):
    execute_test_tcp(common_tcp_client, "POWER_CONTROL_ON", "H1000")  # Passing the whole tuple


def test_temp_set_16(common_tcp_client):
    execute_test_tcp(common_tcp_client, "TEMPERATURE_CONTROL_16", "H1001")


def test_eco_mode(common_tcp_client):
    execute_test_tcp(common_tcp_client, "TURN_ON_ECO", "H3001")


def test_off_tcp(common_tcp_client):
    execute_test_tcp(common_tcp_client, "POWER_CONTROL_OFF", "H1000")


def test_on_cloud_(common_api_client):
    execute_cloud_test(common_api_client, {"H1000": 1}, "H1000")


def test_off_cloud_(common_api_client):
    execute_cloud_test(common_api_client, {"H1000": 0}, "H1000")

