from restclient.client import RestClient


class LoginApi(RestClient):

    def post_v1_account_login(
            self,
            json_data
    ):
        """
        Authenticate via credentials
        :param json_data:
        :return:
        """
        response = self.post(
            path='/v1/account/login',
            json=json_data
        )
        return response

    def delete_v1_account_login(
            self,
            **kwargs
    ):
        """
        Logout as current user
        :param kwargs:
        :return:
        """
        response = self.delete(
            path='/v1/account/login',
            **kwargs
        )
        return response

    def delete_v1_account_login_all(
            self,
    ):
        """
        Logout from every device
        :return:
        """
        response = self.delete(
            path='/v1/account/login/all'
        )
        return response
