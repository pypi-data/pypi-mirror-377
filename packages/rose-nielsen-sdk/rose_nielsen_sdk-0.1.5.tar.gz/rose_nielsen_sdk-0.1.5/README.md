
# Getting Started with Swagger Petstore

## Introduction

This is a sample server Petstore server.  You can find out more about Swagger at [http://swagger.io](http://swagger.io) or on [irc.freenode.net, #swagger](http://swagger.io/irc/).  For this sample, you can use the api key `special-key` to test the authorization filters.

Find out more about Swagger: [http://swagger.io](http://swagger.io)

## Install the Package

The package is compatible with Python versions `3.7+`.
Install the package from PyPi using the following pip command:

```bash
pip install rose-nielsen-sdk==0.1.5
```

You can also view the package at:
https://pypi.python.org/pypi/rose-nielsen-sdk/0.1.5

## Test the SDK

You can test the generated SDK and the server with test cases. `unittest` is used as the testing framework and `pytest` is used as the test runner. You can run the tests as follows:

Navigate to the root directory of the SDK and run the following commands


pip install -r test-requirements.txt
pytest


## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/client.md)

The following parameters are configurable for the API Client:

| Parameter | Type | Description |
|  --- | --- | --- |
| test_header | `str` | This is a test header<br>*Default*: `'TestHeaderDefaultValue'` |
| environment | `Environment` | The API environment. <br> **Default: `Environment.PRODUCTION`** |
| http_client_instance | `HttpClient` | The Http Client passed from the sdk user for making requests |
| override_http_client_configuration | `bool` | The value which determines to override properties of the passed Http Client from the sdk user |
| http_call_back | `HttpCallBack` | The callback value that is invoked before and after an HTTP call is made to an endpoint |
| timeout | `float` | The value to use for connection timeout. <br> **Default: 60** |
| max_retries | `int` | The number of times to retry an endpoint call if it fails. <br> **Default: 0** |
| backoff_factor | `float` | A backoff factor to apply between attempts after the second try. <br> **Default: 2** |
| retry_statuses | `Array of int` | The http statuses on which retry is to be done. <br> **Default: [408, 413, 429, 500, 502, 503, 504, 521, 522, 524]** |
| retry_methods | `Array of string` | The http methods on which retry is to be done. <br> **Default: ['GET', 'PUT']** |
| proxy_settings | [`ProxySettings`](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/proxy-settings.md) | Optional proxy configuration to route HTTP requests through a proxy server. |
| api_key_credentials | [`ApiKeyCredentials`](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/auth/custom-header-signature.md) | The credential object for Custom Header Signature |
| http_basic_credentials | [`HttpBasicCredentials`](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/auth/basic-authentication.md) | The credential object for Basic Authentication |
| petstore_auth_credentials | [`PetstoreAuthCredentials`](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/auth/oauth-2-implicit-grant.md) | The credential object for OAuth 2 Implicit Grant |

The API client can be initialized as follows:

```python
from swaggerpetstore.configuration import Environment
from swaggerpetstore.http.auth.api_key import ApiKeyCredentials
from swaggerpetstore.http.auth.http_basic import HttpBasicCredentials
from swaggerpetstore.http.auth.petstore_auth import PetstoreAuthCredentials
from swaggerpetstore.models.o_auth_scope_petstore_auth_enum import OAuthScopePetstoreAuthEnum
from swaggerpetstore.swaggerpetstore_client import SwaggerpetstoreClient

client = SwaggerpetstoreClient(
    test_header='TestHeaderDefaultValue',
    api_key_credentials=ApiKeyCredentials(
        api_key='api_key'
    ),
    http_basic_credentials=HttpBasicCredentials(
        username='username',
        passwprd='passwprd'
    ),
    petstore_auth_credentials=PetstoreAuthCredentials(
        o_auth_client_id='OAuthClientId',
        o_auth_redirect_uri='OAuthRedirectUri',
        o_auth_scopes=[
            OAuthScopePetstoreAuthEnum.READPETS,
            OAuthScopePetstoreAuthEnum.WRITEPETS
        ]
    ),
    environment=Environment.PRODUCTION
)
```

## Environments

The SDK can be configured to use a different environment for making API calls. Available environments are:

### Fields

| Name | Description |
|  --- | --- |
| production | **Default** |
| environment2 | - |
| environment3 | - |

## Authorization

This API uses the following authentication schemes.

* [`api_key (Custom Header Signature)`](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/auth/custom-header-signature.md)
* [`httpBasic (Basic Authentication)`](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/auth/basic-authentication.md)
* [`petstore_auth (OAuth 2 Implicit Grant)`](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/auth/oauth-2-implicit-grant.md)

## List of APIs

* [Pet](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/controllers/pet.md)
* [Store](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/controllers/store.md)
* [User](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/controllers/user.md)

## SDK Infrastructure

### Configuration

* [ProxySettings](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/proxy-settings.md)

### HTTP

* [HttpResponse](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/http-response.md)
* [HttpRequest](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/http-request.md)

### Utilities

* [ApiHelper](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/api-helper.md)
* [HttpDateTime](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/http-date-time.md)
* [RFC3339DateTime](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/rfc3339-date-time.md)
* [UnixDateTime](https://www.github.com/ZahraN444/rose-nielsen-python-sdk/tree/0.1.5/doc/unix-date-time.md)

