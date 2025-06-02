from datetime import datetime

from hamcrest import assert_that, all_of, has_property, starts_with, instance_of, has_properties, equal_to, has_items

from dm_api_account.models.user_details_envelope import UserRole, ColorSchema


class GetV1Account:
    @classmethod
    def check_response_values(cls, response):
        assert_that(
            response,
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
