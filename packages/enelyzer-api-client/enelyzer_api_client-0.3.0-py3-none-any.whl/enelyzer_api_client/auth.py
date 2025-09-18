import time

import httpx

from enelyzer_api_client.models.auth_models import AuthTokenResponse


class DeviceCodeAuthenticator:
    def __init__(self, client_id: str, client_secret: str, organisation_group: str, environment: str = "production"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.organisation_group = organisation_group

        if environment == "staging":
            self.keycloak_url = "https://staging-idp.enelyzer.com/realms/Enprove"
            self.login_url = "https://staging-webapp.enelyzer.com/v/"
        else:
            self.keycloak_url = "https://idp.enelyzer.com/realms/Enprove"
            self.login_url = "https://app.enelyzer.com/v/"

    def get_auth_token(self) -> AuthTokenResponse | None:
        device_endpoint = f"{self.keycloak_url}/protocol/openid-connect/auth/device"
        data = {"client_id": self.client_id, "client_secret": self.client_secret, "grant_type": "client_credentials"}
        r = httpx.post(device_endpoint, data=data)
        r.raise_for_status()
        resp = r.json()

        verification_uri = resp["verification_uri_complete"]
        device_code = resp["device_code"]
        interval = resp.get("interval", 10)

        print(f"First make sure you are logged in here {self.login_url}{self.organisation_group}")
        print(f"Once you are logged in authenticate here {verification_uri}")

        # Poll for auth completion and get the access token
        token_endpoint = f"{self.keycloak_url}/protocol/openid-connect/token"
        while True:
            try:
                time.sleep(interval)
                token_data = {
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "client_id": self.client_id,
                    "device_code": device_code,
                    "client_secret": self.client_secret,
                }
                token_resp = httpx.post(token_endpoint, data=token_data)
                if token_resp.status_code == 200:
                    return AuthTokenResponse(**token_resp.json())
                elif token_resp.status_code == 400 or token_resp.status_code == 401:
                    # Need some better logic here to detect failures
                    continue
                else:
                    token_resp.raise_for_status()
            except Exception as e:
                print(f"An error occurred: {e}")
                continue


class ServiceAccountAuthenticator:
    def __init__(
        self, client_id: str, client_secret: str, username: str, password: str, environment: str = "production"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password

        if environment == "staging":
            self.keycloak_url = "https://staging-idp.enelyzer.com/realms/Enprove"
            self.login_url = "https://staging-webapp.enelyzer.com/v/"
        else:
            self.keycloak_url = "https://idp.enelyzer.com/realms/Enprove"
            self.login_url = "https://app.enelyzer.com/v/"

    def get_auth_token(self) -> AuthTokenResponse | None:
        token_endpoint = f"{self.keycloak_url}/protocol/openid-connect/token"
        token_data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
        }

        token_resp = httpx.post(token_endpoint, data=token_data)

        if token_resp.status_code == 200:
            return AuthTokenResponse(**token_resp.json())
        else:
            token_resp.raise_for_status()
            return None
