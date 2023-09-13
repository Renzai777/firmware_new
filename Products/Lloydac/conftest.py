import json
import pytest
from Library.tcp_communication import TcpWrap
from Library.cloud_api import ApiClient
from Utilities.utils import Config ,FileManager


@pytest.fixture(scope='session')
def tcp_client_factory():
    def make_tcp_client(ip):
        client = None
        tcp_wrapper = None
        setup_status = 'Not attempted'
        teardown_status = 'Not attempted'

        try:
            port = 8888
            tcp_wrapper = TcpWrap()
            client = tcp_wrapper.tcp_config(ip, port)
            setup_status = 'Success'
        except Exception as e:
            setup_status = f'Failed: {e}'

        yield setup_status, tcp_wrapper

        if tcp_wrapper is not None:
            try:
                tcp_wrapper.tcp_close()
                teardown_status = 'Success'
            except Exception as e:
                teardown_status = f'Failed: {e}'
    return make_tcp_client

@pytest.fixture(scope='session')
def common_tcp_client(tcp_client_factory):
    with open("config.json", "r") as f:
        config_data = json.load(f)
    ip = config_data['tcp_client']['ip']
    return next(tcp_client_factory(ip))


@pytest.fixture(scope='session')
def api_client_fixture(request):
    environment, username, password = request.param  # Getting the parameterized values
    api_client = None
    setup_status = 'Not attempted'
    teardown_status = 'Not attempted'

    try:
        config = Config("QA")
        api_client = ApiClient(config, environment)
        api_client.login(username, password)
        setup_status = 'Success'
    except Exception as e:
        setup_status = f'Failed: {e}'

    yield setup_status, api_client

    if api_client is not None:
        try:
            api_client.close_connection()
            teardown_status = 'Success'
        except Exception as e:
            teardown_status = f'Failed: {e}'

    return setup_status, teardown_status
