import allure


@allure.suite('Тесты на проверку метода PUT /v1/account/token')
@allure.sub_suite('Позитивные тесты')
class TestPutV1AccountToken:
    @staticmethod
    @allure.title('Тест на проверку активации пользователя')
    def test_put_v1_account_token(account_helper, prepare_user):
        login = prepare_user.login
        password = prepare_user.password
        email = prepare_user.email

        account_helper.register_new_user(login=login, password=password, email=email)
        account_helper.activate_user_email(login=login)
