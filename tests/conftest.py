from collections import namedtuple
import datetime

from helpers.account_helper import AccountHelper
import pytest
from restclient.configuration import Configuration as DmApiConfiguration
from restclient.configuration import Configuration as MailhogConfiguration
import structlog

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


@pytest.fixture(scope='session')
def mailhog_api():
    mailhog_configuration = MailhogConfiguration(host='http://5.63.153.31:5025')
    mailhog_client = MailHogApi(configuration=mailhog_configuration)
    return mailhog_client


@pytest.fixture(scope='session')
def account_api():
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)
    account = DMApiAccount(configuration=dm_api_configuration)
    return account


@pytest.fixture(scope='session')
def account_helper(account_api, mailhog_api):
    account_helper = AccountHelper(dm_account_api=account_api, mailhog=mailhog_api)
    return account_helper


@pytest.fixture(scope='function')
def auth_account_helper(mailhog_api):
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)
    account = DMApiAccount(configuration=dm_api_configuration)
    account_helper = AccountHelper(dm_account_api=account, mailhog=mailhog_api)
    account_helper.auth_client(
        login='ek-n-pavlova',
        password='123456789'
    )
    return account_helper


@pytest.fixture
def prepare_user():
    now = datetime.datetime.now()
    data = now.strftime('%d_%m_%Y-%H_%M_%S')
    login = f'ek-n-pavlova-{data}'
    password = '123456789'
    email = f'{login}@mail.ru'
    new_email = f'new_{login}@mail.ru'
    new_password = '987654321'
    User = namedtuple('User', ['login', 'password', 'email', 'new_email', 'new_password'])
    user = User(login=login, password=password, email=email, new_email=new_email, new_password=new_password)
    return user
