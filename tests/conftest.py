from collections import namedtuple
import datetime

from swagger_coverage_py.reporter import CoverageReporter

from helpers.account_helper import AccountHelper
import pytest
from pathlib import Path
from restclient.configuration import Configuration as DmApiConfiguration
from restclient.configuration import Configuration as MailhogConfiguration
import structlog
from vyper import v

from services.api_mailhog import MailHogApi
from services.dm_api_account import DMApiAccount

structlog.configure(
    processors=[
        structlog.processors.JSONRenderer(
            indent=4,
            ensure_ascii=True,
            # sort_keys=True
        )
    ]
)

options = (
    'service.dm_api_account',
    'service.mailhog',
    'user.login',
    'user.password',
)


@pytest.fixture(scope="session", autouse=True)
def setup_swagger_coverage():
    reporter = CoverageReporter(api_name="dm-api-account", host=v.get('service.dm_api_account'))
    reporter.setup("/swagger/Account/swagger.json")
    yield
    reporter.generate_report()
    reporter.cleanup_input_files()


@pytest.fixture(scope='session', autouse=True)
def set_config(request):
    config = Path(__file__).joinpath('../../').joinpath('config')
    config_name = request.config.getoption('--env')
    v.set_config_name(config_name)
    v.add_config_path(config)
    v.read_in_config()
    for option in options:
        v.set(f'{option}', request.config.getoption(f'--{option}'))


def pytest_addoption(parser):
    parser.addoption('--env', action='store', default='stg', help='run stg')
    for option in options:
        parser.addoption(f'--{option}', action='store', default=None)


@pytest.fixture(scope='session')
def mailhog_api():
    mailhog_configuration = MailhogConfiguration(host=v.get('service.mailhog'), disable_log=False)
    mailhog_client = MailHogApi(configuration=mailhog_configuration)
    return mailhog_client


@pytest.fixture(scope='session')
def account_api():
    dm_api_configuration = DmApiConfiguration(host=v.get('service.dm_api_account'), disable_log=False)
    account = DMApiAccount(configuration=dm_api_configuration)
    return account


@pytest.fixture(scope='session')
def account_helper(account_api, mailhog_api):
    account_helper = AccountHelper(dm_account_api=account_api, mailhog=mailhog_api)
    return account_helper


@pytest.fixture(scope='function')
def auth_account_helper(mailhog_api):
    dm_api_configuration = DmApiConfiguration(host=v.get('service.dm_api_account'), disable_log=False)
    account = DMApiAccount(configuration=dm_api_configuration)
    account_helper = AccountHelper(dm_account_api=account, mailhog=mailhog_api)
    account_helper.auth_client(
        login=v.get('user.login'),
        password=v.get('user.password')
    )
    return account_helper


@pytest.fixture
def prepare_user():
    now = datetime.datetime.now()
    data = now.strftime('%d_%m_%Y-%H_%M_%S')
    login = f'ek-n-pavlova-{data}'
    password = v.get('user.password')
    email = f'{login}@mail.ru'
    new_email = f'new_{login}@mail.ru'
    new_password = '987654321'
    User = namedtuple('User', ['login', 'password', 'email', 'new_email', 'new_password'])
    user = User(login=login, password=password, email=email, new_email=new_email, new_password=new_password)
    return user
