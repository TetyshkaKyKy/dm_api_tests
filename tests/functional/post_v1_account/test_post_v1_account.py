import allure
import pytest

from checkers.http_checkers import check_status_code_http


@allure.suite('Тесты на проверку метода POST /v1/account')
class TestPostV1Account:
    @staticmethod
    @allure.sub_suite('Позитивные тесты')
    @allure.title('Проверка регистрации нового пользователя')
    def test_post_v1_account(account_helper, prepare_user):
        login = prepare_user.login
        password = prepare_user.password
        email = prepare_user.email

        account_helper.register_new_user(login=login, password=password, email=email)

    @staticmethod
    @allure.sub_suite('Негативные тесты')
    @allure.title('Проверка регистрации нового пользователя с некорректными данными')
    @pytest.mark.parametrize(
        'login, email, password',
        [
            pytest.param('ek-n-pavlova', 'ek-n-pavlova@mail.ru', '12345', id='invalid_password'),
            pytest.param('ek-n-pavlova', 'ek-n-pavlovamail.ru', '123456789', id='invalid_email'),
            pytest.param('e', 'ek-n-pavlova@mail.ru', '123456789', id='invalid_login')
        ]
    )
    def test_post_v1_account_invalid_user_data(
            account_helper,
            prepare_user,
            login,
            email,
            password,
    ):
        with check_status_code_http(
                expected_status_code=400,
                expected_message='Validation failed'
        ):
            account_helper.register_new_user(login=login, password=password, email=email)
