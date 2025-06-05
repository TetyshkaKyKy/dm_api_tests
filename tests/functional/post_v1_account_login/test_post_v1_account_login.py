import allure

from checkers.post_v1_account import PostV1Account


@allure.suite('Тесты на проверку метода POST v1/account')
@allure.sub_suite('Позитивные тесты')
class TestPostV1Account:
    @staticmethod
    @allure.title('Проверка регистрации нового пользователя')
    def test_post_v1_account_login(account_helper, prepare_user):
        login = prepare_user.login
        password = prepare_user.password
        email = prepare_user.email

        account_helper.register_new_user(login=login, password=password, email=email)
        account_helper.activate_user_email(login=login)
        user_login = account_helper.user_login(login=login, password=password, validate_response=True,
                                               validate_headers=False)
        login = user_login.resource.login
        PostV1Account.check_response_values(user_login, login)
