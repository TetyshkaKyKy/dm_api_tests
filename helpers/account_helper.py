import time
from json import loads

from services.dm_api_account import DMApiAccount
from services.api_mailhog import MailHogApi
from retrying import retry


def retry_if_result_none(
        result
):
    """Return True if we should retry (in this case when result is None), False otherwise"""
    return result is None


def retrier(
        function
):
    def wrapper(
            *args,
            **kwargs,
    ):
        token = None
        count = 0
        while token is None:
            print(f'Попытка получения токена номер {count}!')
            token = function(*args, **kwargs)
            count += 1
            if count == 5:
                raise AssertionError('Превышено количество получения активационного токена!')
            if token:
                return token
            time.sleep(1)

    return wrapper


class AccountHelper:
    def __init__(
            self,
            dm_account_api: DMApiAccount,
            mailhog: MailHogApi
    ):
        self.dm_account_api = dm_account_api
        self.mailhog = mailhog

    def auth_client(
            self,
            login: str,
            password: str
    ):
        response = self.user_login(login=login, password=password)
        token = {
            'x-dm-auth-token': response.headers['x-dm-auth-token']
        }
        self.dm_account_api.account_api.set_headers(token)
        self.dm_account_api.login_api.set_headers(token)
        return token

    def register_new_user(
            self,
            login: str,
            password: str,
            email: str,
    ):
        json_data = {
            'login': login,
            'email': email,
            'password': password,
        }
        response = self.dm_account_api.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f'Пользователь не был создан {response.json()}'

        self.get_user_token(login=login)

    def user_login(
            self,
            login: str,
            password: str,
            remember_me: bool = True,
    ):
        json_data = {
            'login': login,
            'password': password,
            'rememberMe': remember_me,
        }
        response = self.dm_account_api.login_api.post_v1_account_login(json_data=json_data)
        return response

    def change_user_email(
            self,
            login: str,
            email: str,
            password: str,
    ):

        json_data = {
            'login': login,
            'email': email,
            'password': password,
        }

        response = self.dm_account_api.account_api.put_v1_account_email(json_data=json_data)
        assert response.status_code == 200, 'Пользователь не смог сменить почтовый адрес'

    def change_user_password(
            self,
            login: str,
            email: str,
            old_password: str,
            new_password: str,
    ):
        headers = self.auth_client(login=login, password=old_password)
        self.reset_user_password(login=login, email=email)
        token = self.get_user_token(login=login, token_type='reset')

        json_data = {
            'login': login,
            'token': token,
            'oldPassword': old_password,
            'newPassword': new_password
        }

        response = self.dm_account_api.account_api.put_v1_account_password(headers=headers, json_data=json_data)
        assert response.status_code == 200, 'Пользователь не смог сменить пароль'

    def reset_user_password(
            self,
            login: str,
            email: str,
    ):
        json_data = {
            'login': login,
            'email': email
        }

        response = self.dm_account_api.account_api.post_v1_account_password(json_data=json_data)
        assert response.status_code == 200, 'Не удалось сбросить пароль'

    def get_user_token(
            self,
            login: str,
            token_type: str = 'activation'
    ):

        token = self.get_activation_token_by_login(login, token_type)
        assert token is not None, f'Токен для пользователя {login} не был получен'
        return token

    def activate_user_email(
            self,
            login,
    ):
        token = self.get_user_token(login=login)
        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, 'Пользователь не был активирован'

    def delete_account_login(
            self
    ):
        response = self.dm_account_api.login_api.delete_v1_account_login()
        assert response.status_code == 204, 'Пользователь не был разлогинен'

    def delete_account_login_all(
            self
    ):
        response = self.dm_account_api.login_api.delete_v1_account_login_all()
        assert response.status_code == 204, 'Пользователь не был разлогинен на всех устройствах'

    @retry(stop_max_attempt_number=5, retry_on_result=retry_if_result_none, wait_fixed=1000)
    def get_activation_token_by_login(
            self,
            login,
            token_type: str = 'activation'
    ):
        token = None
        messages = self.mailhog.mailhog_api.get_api_v2_messages()

        for item in messages.json()['items']:
            user_data = loads(
                item['Content']['Body']
            )

            key = 'ConfirmationLinkUrl' if token_type == 'activation' else 'ConfirmationLinkUri'

            user_login = user_data['Login']
            if user_login == login:
                try:
                    token = user_data[key].split('/')[-1]
                except KeyError:
                    continue

            return token
