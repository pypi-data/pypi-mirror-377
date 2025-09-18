from dataclasses import dataclass, field

@dataclass
class AuthTokenResponse:
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__annotations__:
                setattr(self, key, value)