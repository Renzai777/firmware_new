import pytest
from Library.tcp_communication import TcpWrap
from Library.cloud_api import ApiClient
from Utilities.utils import Config ,FileManager
from py.xml import html


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
    config_data = FileManager.manage_file("config.json", "r")
    ip = config_data['tcp_client']['ip']
    return next(tcp_client_factory(ip))


@pytest.fixture(scope='session')
def api_client_fixture():
    setup_status = 'Not attempted'
    api_client = None

    try:
        config_data = FileManager.manage_file("config.json", "r")

        environment = config_data['api_client_fixture']['environment']
        username = config_data['api_client_fixture']['username']
        password = config_data['api_client_fixture']['password']

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
        except Exception as e:
            pass


@pytest.fixture(scope='session')
def common_api_client(api_client_fixture):
    config_data = FileManager.manage_file("config.json", "r")

    device_id = config_data['api_client_fixture']['device_id']
    setup_status, api_client = api_client_fixture  # directly use api_client_fixture

    yield setup_status, api_client, device_id


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    cells.insert(2, html.th("Fixture"))
    cells.insert(3, html.th("Setup Status"))
    cells.insert(4, html.th("Teardown Status"))

@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    cells.insert(2, html.td(report.fixture))
    cells.insert(3, html.td(report.setup_status))
    cells.insert(4, html.td(report.teardown_status))


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if 'tcp_client' in item.funcargs:
        setup_status, _ = item.funcargs['tcp_client']
        report.setup_status = setup_status
        report.fixture = 'tcp_client'
    elif 'api_client_fixture' in item.funcargs:
        setup_status, _ = item.funcargs['api_client_fixture']
        report.setup_status = setup_status
        report.fixture = 'api_client_fixture'
    else:
        report.setup_status = 'N/A'
        report.fixture = 'None'

    report.teardown_status = 'Teardown successful'

