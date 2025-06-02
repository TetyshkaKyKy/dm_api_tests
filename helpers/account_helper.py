import time
from json import loads

from dm_api_account.models.change_email import ChangeEmail
from dm_api_account.models.change_password import ChangePassword
from dm_api_account.models.login_credentials import LoginCredentials
from dm_api_account.models.registration import Registration
from dm_api_account.models.reset_password import ResetPassword
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
        registration = Registration(
            login=login,
            email=email,
            password=password,
        )
        response = self.dm_account_api.account_api.post_v1_account(registration=registration)
        start_time = time.time()
        self.get_user_token(login=login)
        end_time = time.time()
        assert end_time - start_time < 3, 'Время ожидания активации превышено'
        return response

    def user_login(
            self,
            login: str,
            password: str,
            remember_me: bool = True,
            validate_response: bool = False,
            validate_headers: bool = True
    ):
        login_credentials = LoginCredentials(
            login=login,
            password=password,
            remember_me=remember_me,
        )
        response = self.dm_account_api.login_api.post_v1_account_login(
            login_credentials=login_credentials,
            validate_response=validate_response
        )
        if validate_headers:
            assert response.headers['x-dm-auth-token'], 'Токен для пользователя не был получен'
        return response

    def change_user_email(
            self,
            login: str,
            email: str,
            password: str,
    ):

        change_email = ChangeEmail(
            login=login,
            email=email,
            password=password
        )

        response = self.dm_account_api.account_api.put_v1_account_email(change_email=change_email)
        return response

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

        change_password = ChangePassword(
            login=login,
            token=token,
            old_password=old_password,
            new_password=new_password
        )

        response = self.dm_account_api.account_api.put_v1_account_password(headers=headers,
                                                                           change_password=change_password)
        return response

    def reset_user_password(
            self,
            login: str,
            email: str,
    ):
        reset_password = ResetPassword(
            login=login,
            email=email
        )

        response = self.dm_account_api.account_api.post_v1_account_password(reset_password=reset_password)
        return response

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
        return response

    def delete_account_login(
            self
    ):
        response = self.dm_account_api.login_api.delete_v1_account_login()
        return response

    def delete_account_login_all(
            self
    ):
        response = self.dm_account_api.login_api.delete_v1_account_login_all()
        return response

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
