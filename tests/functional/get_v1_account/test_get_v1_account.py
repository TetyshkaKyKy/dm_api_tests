def test_get_v1_account_auth(auth_account_helper):
    auth_account_helper.dm_account_api.account_api.get_v1_account()
    # assert response.status_code == 200, 'Не удалось получить информацию о пользователи'


def test_get_v1_account_no_auth(account_helper):
    response = account_helper.dm_account_api.account_api.get_v1_account(validate_response=False)
    assert response.status_code == 401, 'Получена информация о пользователе без авторизации'
    assert response.json()['title'] == 'User must be authenticated'
