import allure


@allure.suite('Тесты на проверку метода DELETE /v1/account/login')
@allure.sub_suite('Позитивные тесты')
class TestDeleteV1AccountLogin:
    @staticmethod
    @allure.title('Проверка выхода из аккаунта пользователя')
    def test_delete_v1_account_login(auth_account_helper):
        auth_account_helper.delete_account_login()
