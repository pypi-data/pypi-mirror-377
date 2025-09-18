# enelyzer-api-client
A client library for accessing Enelyzer API

## Usage

First Authenticate and get your access token:

```python

from enelyzer_api_client.auth import DeviceCodeAuthenticator, ServiceAccountAuthenticator

client_id = ""
client_secret = ""
username = ""
password = ""
environment = "production" # or "staging"

authenticator = ServiceAccountAuthenticator(client_id, client_secret, username, password, environment=environment)
token = authenticator.get_auth_token()
```

Then, create a client:

```python
from enelyzer_api_client import AuthenticatedClient

base_url_staging="https://client-api.enelyzer.com"
base_url_production="https://client-api.enelyzer.com"
client = AuthenticatedClient(base_url=base_url_staging, token="{token}")
```

Now call your endpoint and use your models:

```python
from enelyzer_api_client.api.units_categories_and_quantities import get_units


organisation_group = ""
organisation_id = ""

with client as client:
     response = get_units.sync(
         organisation_group=organisation_group,
         organisation_id=organisation_id,
         client=client,
     )

    print(response)
```