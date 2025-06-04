import allure


@allure.suite('Тесты на проверку метода DELETE /v1/account/login/all')
@allure.sub_suite('Позитивные тесты')
class TestDeleteV1AccountLoginAll:
    @staticmethod
    @allure.title('Проверка выхода из аккаунта пользователя со всех устройств')
    def test_delete_v1_account_login_all(auth_account_helper):
        auth_account_helper.delete_account_login_all()
