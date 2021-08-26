import base64
import json
import requests
import urllib3
from contextlib import contextmanager
from packaging.version import Version
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from mlflow import __version__
from mlflow.protos import databricks_pb2
from mlflow.protos.databricks_pb2 import INVALID_PARAMETER_VALUE
from mlflow.utils.proto_json_utils import parse_dict
from mlflow.utils.string_utils import strip_suffix
from mlflow.exceptions import MlflowException, RestException

RESOURCE_DOES_NOT_EXIST = "RESOURCE_DOES_NOT_EXIST"
_REST_API_PATH_PREFIX = "/api/2.0"
_DEFAULT_HEADERS = {"User-Agent": "mlflow-python-client/%s" % __version__}
# Response codes that generally indicate transient network failures and merit client retries,
# based on guidance from cloud service providers
# (https://docs.microsoft.com/en-us/azure/architecture/best-practices/retry-service-specific#general-rest-and-retry-guidelines)
_TRANSIENT_FAILURE_RESPONSE_CODES = frozenset(
    [
        408,  # Request Timeout
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
    ]
)


def _get_http_response_with_retries(
    method, url, max_retries, backoff_factor, retry_codes, **kwargs
):
    """
    Performs an HTTP request using Python's `requests` module with an automatic retry policy.

    :param method: a string indicating the method to use, e.g. "GET", "POST", "PUT".
    :param url: the target URL address for the HTTP request.
    :param max_retries: Maximum total number of retries.
    :param backoff_factor: a time factor for exponential backoff. e.g. value 5 means the HTTP
      request will be retried with interval 5, 10, 20... seconds. A value of 0 turns off the
      exponential backoff.
    :param retry_codes: a list of HTTP response error codes that qualifies for retry.
    :param kwargs: Additional keyword arguments to pass to `requests.Session.request()`

    :return: requests.Response object.
    """
    assert 0 <= max_retries < 10
    assert 0 <= backoff_factor < 120

    retry_kwargs = {
        "total": max_retries,
        "connect": max_retries,
        "read": max_retries,
        "redirect": max_retries,
        "status": max_retries,
        "status_forcelist": retry_codes,
        "backoff_factor": backoff_factor,
    }
    if Version(urllib3.__version__) >= Version("1.26.0"):
        retry_kwargs["allowed_methods"] = None
    else:
        retry_kwargs["method_whitelist"] = None

    retry = Retry(**retry_kwargs)
    adapter = HTTPAdapter(max_retries=retry)
    with requests.Session() as http:
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        response = http.request(method, url, **kwargs)
        return response


def http_request(
    host_creds,
    endpoint,
    method,
    max_retries=5,
    backoff_factor=2,
    retry_codes=_TRANSIENT_FAILURE_RESPONSE_CODES,
    timeout=10,
    **kwargs
):
    """
    Makes an HTTP request with the specified method to the specified hostname/endpoint. Transient
    errors such as Rate-limited (429), service unavailable (503) and internal error (500) are
    retried with an exponential back off with backoff_factor * (1, 2, 4, ... seconds).
    The function parses the API response (assumed to be JSON) into a Python object and returns it.

    :param host_creds: A :py:class:`mlflow.rest_utils.MlflowHostCreds` object containing
        hostname and optional authentication.
    :param endpoint: a string for service endpoint, e.g. "/path/to/object".
    :param method: a string indicating the method to use, e.g. "GET", "POST", "PUT".
    :param max_retries: maximum number of retries before throwing an exception.
    :param backoff_factor: a time factor for exponential backoff. e.g. value 5 means the HTTP
      request will be retried with interval 5, 10, 20... seconds. A value of 0 turns off the
      exponential backoff.
    :param retry_codes: a list of HTTP response error codes that qualifies for retry.
    :param timeout: wait for timeout seconds for response from remote server for connect and
      read request.
    :param kwargs: Additional keyword arguments to pass to `requests.Session.request()`

    :return: requests.Response object.
    """
    hostname = host_creds.host
    auth_str = None
    if host_creds.username and host_creds.password:
        basic_auth_str = ("%s:%s" % (host_creds.username, host_creds.password)).encode("utf-8")
        auth_str = "Basic " + base64.standard_b64encode(basic_auth_str).decode("utf-8")
    elif host_creds.token:
        auth_str = "Bearer %s" % host_creds.token

    from mlflow.tracking.request_header.registry import resolve_request_headers

    headers = dict({**_DEFAULT_HEADERS, **resolve_request_headers()})
    if auth_str:
        headers["Authorization"] = auth_str

    if host_creds.server_cert_path is None:
        verify = not host_creds.ignore_tls_verification
    else:
        verify = host_creds.server_cert_path

    if host_creds.client_cert_path is not None:
        kwargs["cert"] = host_creds.client_cert_path

    cleaned_hostname = strip_suffix(hostname, "/")
    url = "%s%s" % (cleaned_hostname, endpoint)
    try:
        return _get_http_response_with_retries(
            method,
            url,
            max_retries,
            backoff_factor,
            retry_codes,
            headers=headers,
            verify=verify,
            timeout=timeout,
            **kwargs
        )
    except Exception as e:
        raise MlflowException("API request to %s failed with exception %s" % (url, e))


def _can_parse_as_json(string):
    try:
        json.loads(string)
        return True
    except Exception:
        return False


def http_request_safe(host_creds, endpoint, method, **kwargs):
    """
    Wrapper around ``http_request`` that also verifies that the request succeeds with code 200.
    """
    response = http_request(host_creds=host_creds, endpoint=endpoint, method=method, **kwargs)
    return verify_rest_response(response, endpoint)


def verify_rest_response(response, endpoint):
    """Verify the return code and format, raise exception if the request was not successful."""
    if response.status_code != 200:
        if _can_parse_as_json(response.text):
            raise RestException(json.loads(response.text))
        else:
            base_msg = "API request to endpoint %s failed with error code " "%s != 200" % (
                endpoint,
                response.status_code,
            )
            raise MlflowException("%s. Response body: '%s'" % (base_msg, response.text))

    # Skip validation for endpoints (e.g. DBFS file-download API) which may return a non-JSON
    # response
    if endpoint.startswith(_REST_API_PATH_PREFIX) and not _can_parse_as_json(response.text):
        base_msg = (
            "API request to endpoint was successful but the response body was not "
            "in a valid JSON format"
        )
        raise MlflowException("%s. Response body: '%s'" % (base_msg, response.text))

    return response


def _get_path(path_prefix, endpoint_path):
    return "{}{}".format(path_prefix, endpoint_path)


def extract_api_info_for_service(service, path_prefix):
    """ Return a dictionary mapping each API method to a tuple (path, HTTP method)"""
    service_methods = service.DESCRIPTOR.methods
    res = {}
    for service_method in service_methods:
        endpoints = service_method.GetOptions().Extensions[databricks_pb2.rpc].endpoints
        endpoint = endpoints[0]
        endpoint_path = _get_path(path_prefix, endpoint.path)
        res[service().GetRequestClass(service_method)] = (endpoint_path, endpoint.method)
    return res


def call_endpoint(host_creds, endpoint, method, json_body, response_proto):
    # Convert json string to json dictionary, to pass to requests
    if json_body:
        json_body = json.loads(json_body)
    if method == "GET":
        response = http_request(
            host_creds=host_creds, endpoint=endpoint, method=method, params=json_body
        )
    else:
        response = http_request(
            host_creds=host_creds, endpoint=endpoint, method=method, json=json_body
        )
    response = verify_rest_response(response, endpoint)
    js_dict = json.loads(response.text)
    parse_dict(js_dict=js_dict, message=response_proto)
    return response_proto


@contextmanager
def cloud_storage_http_request(
    method,
    url,
    max_retries=5,
    backoff_factor=2,
    retry_codes=_TRANSIENT_FAILURE_RESPONSE_CODES,
    timeout=10,
    **kwargs
):
    """
    Performs an HTTP PUT/GET request using Python's `requests` module with automatic retry.

    :param method: string of 'PUT' or 'GET', specify to do http PUT or GET
    :param url: the target URL address for the HTTP request.
    :param max_retries: maximum number of retries before throwing an exception.
    :param backoff_factor: a time factor for exponential backoff. e.g. value 5 means the HTTP
      request will be retried with interval 5, 10, 20... seconds. A value of 0 turns off the
      exponential backoff.
    :param retry_codes: a list of HTTP response error codes that qualifies for retry.
    :param timeout: wait for timeout seconds for response from remote server for connect and
      read request.
    :param kwargs: Additional keyword arguments to pass to `requests.Session.request()`

    :return requests.Response object.
    """
    if method.lower() not in ("put", "get"):
        raise ValueError("Illegal http method: " + method)
    try:
        with _get_http_response_with_retries(
            method, url, max_retries, backoff_factor, retry_codes, timeout=timeout, **kwargs
        ) as response:
            yield response
    except Exception as e:
        raise MlflowException("API request failed with exception %s" % e)


class MlflowHostCreds(object):
    """
    Provides a hostname and optional authentication for talking to an MLflow tracking server.
    :param host: Hostname (e.g., http://localhost:5000) to MLflow server. Required.
    :param username: Username to use with Basic authentication when talking to server.
        If this is specified, password must also be specified.
    :param password: Password to use with Basic authentication when talking to server.
        If this is specified, username must also be specified.
    :param token: Token to use with Bearer authentication when talking to server.
        If provided, user/password authentication will be ignored.
    :param ignore_tls_verification: If true, we will not verify the server's hostname or TLS
        certificate. This is useful for certain testing situations, but should never be
        true in production.
        If this is set to true ``server_cert_path`` must not be set.
    :param client_cert_path: Path to ssl client cert file (.pem).
        Sets the cert param of the ``requests.request``
        function (see https://requests.readthedocs.io/en/master/api/).
    :param server_cert_path: Path to a CA bundle to use.
        Sets the verify param of the ``requests.request``
        function (see https://requests.readthedocs.io/en/master/api/).
        If this is set ``ignore_tls_verification`` must be false.
    """

    def __init__(
        self,
        host,
        username=None,
        password=None,
        token=None,
        ignore_tls_verification=False,
        client_cert_path=None,
        server_cert_path=None,
    ):
        if not host:
            raise MlflowException(
                message="host is a required parameter for MlflowHostCreds",
                error_code=INVALID_PARAMETER_VALUE,
            )
        if ignore_tls_verification and (server_cert_path is not None):
            raise MlflowException(
                message=(
                    "When 'ignore_tls_verification' is true then 'server_cert_path' "
                    "must not be set! This error may have occurred because the "
                    "'MLFLOW_TRACKING_INSECURE_TLS' and 'MLFLOW_TRACKING_SERVER_CERT_PATH' "
                    "environment variables are both set - only one of these environment "
                    "variables may be set."
                ),
                error_code=INVALID_PARAMETER_VALUE,
            )
        self.host = host
        self.username = username
        self.password = password
        self.token = token
        self.ignore_tls_verification = ignore_tls_verification
        self.client_cert_path = client_cert_path
        self.server_cert_path = server_cert_path
