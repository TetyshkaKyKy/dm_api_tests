import allure

from checkers.get_v1_account import GetV1Account
from checkers.http_checkers import check_status_code_http


@allure.suite('Тесты на проверку метода GET /v1/account')
@allure.sub_suite('Позитивные тесты')
class TestGetV1Account:
    @staticmethod
    @allure.title('Проверка получения информации об авторизованном пользователе')
    def test_get_v1_account_auth(auth_account_helper):
        current_user = auth_account_helper.dm_account_api.account_api.get_v1_account()
        login = current_user.resource.login
        GetV1Account.check_response_values(current_user, login)

    @staticmethod
    @allure.title('Проверка получения информации о пользователе без авторизации')
    def test_get_v1_account_no_auth(account_helper):
        with check_status_code_http(expected_status_code=401, expected_message='User must be authenticated'):
            account_helper.dm_account_api.account_api.get_v1_account(validate_response=False)
