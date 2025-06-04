import allure

from checkers.http_checkers import check_status_code_http


@allure.suite('Тесты на проверку метода PUT /v1/account/email')
@allure.sub_suite('Позитивные тесты')
class TestPutV1AccountEmail:
    @staticmethod
    @allure.title('Проверка смены почтового адреса пользователя')
    def test_put_v1_account_email(account_helper, prepare_user):
        login = prepare_user.login
        password = prepare_user.password
        email = prepare_user.email
        new_email = prepare_user.new_email

        account_helper.register_new_user(login=login, password=password, email=email)
        account_helper.activate_user_email(login=login)
        account_helper.user_login(login=login, password=password)

        # Смена почтового адреса пользователя
        account_helper.change_user_email(login=login, password=password, email=new_email)

        # Попытка авторизации с новым почтовым адресом
        with check_status_code_http(
                expected_status_code=403,
                expected_message='User is inactive. Address the technical support for more details'
        ):
            account_helper.user_login(login=login, password=password, validate_headers=False)

        # Получение нового активационного токена и активация пользователя
        account_helper.get_user_token(login=login)
        account_helper.activate_user_email(login=login)

        # Авторизация с новой почтой
        account_helper.user_login(login=login, password=password)
