from datetime import datetime

from hamcrest import assert_that, all_of, has_property, starts_with, instance_of, has_properties, equal_to, has_items

from dm_api_account.models.user_details_envelope import UserRole, ColorSchema


def test_get_v1_account_auth(auth_account_helper):
    # assert response.status_code == 200, 'Не удалось получить информацию о пользователи'
    assert_that(
        current_user,
        has_property(
            'resource', all_of(
                has_property('login', starts_with('ek-n-pavlova')),
                has_property('registration', instance_of(datetime)),
                has_properties(
                    {
                        'rating': has_properties(
                            {
                                'enabled': equal_to(True),
                                'quality': equal_to(0),
                                'quantity': equal_to(0)
                            }
                        )
                    }
                ),
                has_property('roles', has_items(UserRole.GUEST, UserRole.PLAYER)),
                has_property('settings', all_of(
                    has_property('color_schema', equal_to(ColorSchema.MODERN))
                )
                             )
            )
        )
    )


def test_get_v1_account_no_auth(account_helper):
    response = account_helper.dm_account_api.account_api.get_v1_account(validate_response=False)
    assert response.status_code == 401, 'Получена информация о пользователе без авторизации'
    assert response.json()['title'] == 'User must be authenticated'
