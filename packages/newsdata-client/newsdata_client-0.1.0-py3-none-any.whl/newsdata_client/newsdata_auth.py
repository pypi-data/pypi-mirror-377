from requests.auth import AuthBase


class NewsDataAuth(AuthBase):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def __call__(self, request):
        request.headers.update(self.get_auth_header())
        return request

    def get_auth_header(self):
        return {"X-ACCESS-KEY": self.api_key}
