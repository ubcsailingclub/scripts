"""
This module provides set of classes for working with WildApricot public API v2.
Public API documentation can be found here: http://help.wildapricot.com/display/DOC/API+Version+2

Example:
    from waapi import WildApricotClient
    api = WildApricotClient()
    api.authenticate_with_contact_credentials("admin@youraccount.com", "your_password")
    accounts = api.request("/v2/accounts")
    for account in accounts:
        print(account.PrimaryDomainName)
"""

__author__ = 'dsmirnov@wildapricot.com'

import datetime
import urllib.request
import urllib.response
import urllib.error
import urllib.parse
import json
import base64


class WildApricotClient:
    """Wild apricot API client."""
    auth_endpoint = "https://oauth.wildapricot.org/auth/token"
    api_endpoint = "https://api.wildapricot.org"
    _token = None

    def __init__(self, client_id=None, client_secret=None, *, api_key=None):
        """
        client_id -- client id from account settings
        client_secret -- client secret from account settings
        api_key -- secret api key from account settings (alternative for servers)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self._api_key_refresh_scope = None

    def request_token(self, data, authorization):
        encoded_data = urllib.parse.urlencode(data).encode()
        request = urllib.request.Request(self.auth_endpoint, encoded_data, method="POST")
        request.add_header("ContentType", "application/x-www-form-urlencoded")
        auth_header = base64.standard_b64encode(authorization.encode()).decode()
        request.add_header("Authorization", 'Basic ' + auth_header)
        response = urllib.request.urlopen(request)
        self._token = self._parse_response(response)
        self._token.retrieved_at = datetime.datetime.now()

    def authenticate_with_apikey(self, scope='auto'):
        """perform authentication by api key and store result for request method
        scope -- optional scope of authentication request. If `auto` full list of API scopes will be used.
        """
        if self.api_key is None:
            raise APIException("API key was not provided when initializing.")
        data = {
            "grant_type": "client_credentials",
            "scope": scope
        }
        self.request_token(data, 'APIKEY:' + self.api_key)
        self._api_key_refresh_scope = scope

    def authenticate_with_contact_credentials(self, username, password, scope='auto'):
        """perform authentication by contact credentials and store result for request method

        username -- typically a contact email
        password -- contact password
        scope -- optional scope of authentication request. If `auto` full list of API scopes will be used.
        """
        if self.client_id is None or self.client_secret is None:
            raise APIException("Client id or secret was not provided when initializing.")
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": scope
        }
        self.request_token(data, self.client_id + ':' + self.client_secret)

    def request(self, api_url, post_payload=None, method=None):
        """
        perform api request and return result as an instance of APIObject or list of APIObjects

        api_url -- absolute or relative api resource url
        post_payload -- any json serializable object to send to API
        method -- HTTP method of api request. Default: GET if post_payload is None else POST
        """
        if self._token is None:
            raise APIException("Access token is not abtained. "
                               "Call authenticate_with_apikey or authenticate_with_contact_credentials first.")

        if not api_url.startswith("http"):
            api_url = self.api_endpoint + api_url

        if method is None:
            if post_payload is None:
                method = "GET"
            else:
                method = "POST"

        request = urllib.request.Request(api_url, method=method)
        if post_payload is not None:
            request.data = json.dumps(post_payload, cls=_APIObjectEncoder).encode()

        request.add_header("Content-Type", "application/json")
        request.add_header("Accept", "application/json")
        request.add_header("Authorization", "Bearer " + self._get_access_token())

        try:
            response = urllib.request.urlopen(request)
            return self._parse_response(response)
        except urllib.error.HTTPError as http_err:
            if http_err.code == 400:
                raise APIException(http_err.read())
            else:
                raise

    def _get_access_token(self):
        expires_at = self._token.retrieved_at + datetime.timedelta(seconds=self._token.expires_in - 100)
        if datetime.datetime.now() > expires_at:
            self._refresh_auth_token()
        return self._token.access_token

    def _refresh_auth_token(self):
        if self.api_key is not None:
            self.authenticate_with_apikey(scope=self._api_key_refresh_scope)
        else:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self._token.refresh_token
            }
            self.request_token(data, self.client_id + ':' + self.client_secret)

    @staticmethod
    def _parse_response(http_response):
        decoded = json.loads(http_response.read().decode())
        if isinstance(decoded, list):
            result = []
            for item in decoded:
                result.append(APIObject(item))
            return result
        elif isinstance(decoded, dict):
            return APIObject(decoded)
        else:
            return None


class APIException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class APIObject:
    """Represent any api call input or output object"""

    def __init__(self, state):
        self.__dict__ = state
        for key, value in vars(self).items():
            if isinstance(value, dict):
                self.__dict__[key] = APIObject(value)
            elif isinstance(value, list):
                new_list = []
                for list_item in value:
                    if isinstance(list_item, dict):
                        new_list.append(APIObject(list_item))
                    else:
                        new_list.append(list_item)
                self.__dict__[key] = new_list

    def __getitem__(self, key):
        if not hasattr(self, 'FieldValues'):
            message = "This object does not have FieldValues attribute and cannot be indexed; try to access it as an attribute"
            raise ValueError(message)
        for field in self.FieldValues:
            if field.FieldName == key:
                return field.Value
        raise KeyError(key)

    def _jsons_massive_dump(self):
        return json.dumps(self.__dict__, default=lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else obj.__dict__, indent=4)

    def __str__(self):
        return 'JSON: ' + self._jsons_massive_dump()

    def __repr__(self):
        og = super().__repr__()
        return og + ': JSON: ' + self._jsons_massive_dump()

class _APIObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, APIObject):
            return obj.__dict__
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
