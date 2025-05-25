import random
from json import loads

from helpers.account_helper import AccountHelper
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


def test_put_v1_account_email():
    # Подготовка тестовых данных
    mailhog_configuration = MailhogConfiguration(host='http://5.63.153.31:5025')
    dm_api_configuration = DmApiConfiguration(host='http://5.63.153.31:5051', disable_log=False)

    account = DMApiAccount(configuration=dm_api_configuration)
    mailhog = MailHogApi(configuration=mailhog_configuration)

    account_helper = AccountHelper(dm_account_api=account, mailhog=mailhog)

    login = f'ek-n-palvova-{random.random()}'
    password = '123456789'
    email = f'{login}@mail.ru'
    new_email = f'new-{login}@mail.ru'

    account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.activate_user_email(login=login)
    account_helper.user_login(login=login, password=password)

    # Смена почтового адреса пользователя
    account_helper.change_user_email(login=login, password=password, email=new_email)

    # Попытка авторизации с новым почтовым адресом
    user_login_without_activation = account_helper.user_login(login=login, password=password)
    assert user_login_without_activation.status_code == 403, 'Пользователь смог авторизоваться без активации токена'

    # Получение нового активационного токена и активация пользователя
    account_helper.get_user_token(login=login)
    account_helper.activate_user_email(login=login)

    # Авторизация с новой почтой
    account_helper.user_login(login=login, password=password)
