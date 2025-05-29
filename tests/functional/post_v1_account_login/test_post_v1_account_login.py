from datetime import datetime

from hamcrest import assert_that, all_of, has_property, has_properties, starts_with, instance_of, equal_to


def test_post_v1_account_login(account_helper, prepare_user):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email

    account_helper.register_new_user(login=login, password=password, email=email)
    account_helper.activate_user_email(login=login)
    user_login = account_helper.user_login(login=login, password=password, validate_response=True,
                                           validate_headers=False)

    assert_that(
        user_login,
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
            )
        )
    )
