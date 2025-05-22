from json import loads

from services.dm_api_account import DMApiAccount
from services.api_mailhog import MailHogApi


class AccountHelper:
    def __init__(
            self,
            dm_account_api: DMApiAccount,
            mailhog: MailHogApi
    ):
        self.dm_account_api = dm_account_api
        self.mailhog = mailhog

    def activate_new_user(
            self,
            login: str,
            password: str,
            email: str
    ):
        json_data = {
            'login': login,
            'email': email,
            'password': password,
        }
        response = self.dm_account_api.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f"Пользователь не был создан {response.json()}"

        self.activate_user_email(login=login)

    def register_new_user(
            self,
            login: str,
            password: str,
            email: str
    ):
        json_data = {
            'login': login,
            'email': email,
            'password': password,
        }
        response = self.dm_account_api.account_api.post_v1_account(json_data=json_data)
        assert response.status_code == 201, f"Пользователь не был создан {response.json()}"

        messages = self.mailhog.mailhog_api.get_api_v2_messages()
        assert messages.status_code == 200, "Письма не были получены"

        token = self.get_activation_token_by_login(login=login, response=messages)
        assert token is not None, f"Токен для пользователя {login} не был получен"

    def user_login(
            self,
            login: str,
            password: str,
            remember_me: bool = True
    ):
        json_data = {
            'login': login,
            'password': password,
            'rememberMe': remember_me,
        }

        response = self.dm_account_api.login_api.post_v1_account_login(json_data=json_data)
        assert response.status_code == 200, 'Пользователь не смог авторизоваться'

    def change_user_email(
            self,
            json_data: dict
    ):

        response = self.dm_account_api.account_api.put_v1_account_email(json_data)
        assert response.status_code == 200, 'Пользователь не смог сменить почтовый адрес'

    def user_login_without_activation(
            self,
            json_data: dict
    ):
        response = self.dm_account_api.login_api.post_v1_account_login(json_data=json_data)
        assert response.status_code == 403, 'Пользователь смог авторизоваться без активации токена'

    def activate_user_email(
            self,
            login: str,
    ):
        messages = self.mailhog.mailhog_api.get_api_v2_messages()
        assert messages.status_code == 200, 'Письма не были получены'

        token = self.get_activation_token_by_login(login, messages)
        assert token is not None, f'Токен для пользователя {login} не был получен'

        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        assert response.status_code == 200, 'Пользователь не был активирован'

    @staticmethod
    def get_activation_token_by_login(
        login,
        response
    ):
        token = None
        for item in response.json()['items']:
            user_data = loads(
                item['Content']['Body']
            )
            user_login = user_data['Login']
            if user_login == login:
                token = user_data['ConfirmationLinkUrl'].split('/')[-1]
        return token
