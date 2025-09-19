from json import JSONDecodeError

import requests
import urllib3

from pybt.api_wrapper import models
from pybt.api_wrapper.exceptions import BigTimeAPIException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RestAdapter:
    def __init__(
        self,
        hostname: str,
        api_key: str,
        firm: str,
        ver: str = "v2",
        ssl_verify: bool = False,
    ):
        self.url = f"https://{hostname}/{ver}/"
        self._api_key = api_key
        self._firm = firm
        self._ssl_verify = ssl_verify

    def _do(
        self, http_method: str, endpoint: str, ep_params=None, data=None
    ) -> models.Result:
        full_url = self.url + endpoint
        headers = {"X-auth-ApiToken": self._api_key, "X-auth-realm": self._firm}
        try:
            response = requests.request(
                method=http_method,
                url=full_url,
                verify=self._ssl_verify,
                headers=headers,
                params=ep_params,
                json=data,
            )
        except requests.exceptions.RequestException as e:
            raise BigTimeAPIException("Request Failed") from e
        if 299 >= response.status_code >= 200:  # OK
            try:
                data_out = response.json()
            except (ValueError, JSONDecodeError) as e:
                raise BigTimeAPIException("Bad JSON in response", response) from e
            return models.Result(
                response.status_code, message=response.reason, data=data_out
            )
        raise BigTimeAPIException(f"{response.status_code}: {response.reason}")

    def get(self, endpoint: str, params=None) -> models.Result:
        return self._do(http_method="GET", endpoint=endpoint, ep_params=params)

    def post(self, endpoint: str, params=None, data=None) -> models.Result:
        return self._do(
            http_method="POST", endpoint=endpoint, ep_params=params, data=data
        )

    def delete(self, endpoint: str, params=None, data=None) -> models.Result:
        return self._do(
            http_method="DELETE", endpoint=endpoint, ep_params=params, data=data
        )
