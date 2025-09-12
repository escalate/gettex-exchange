import pytest

from gettex_exchange.api import Api


@pytest.fixture
def api_instance():
    return Api()


def test_api_request_user_agent(api_instance):
    assert api_instance._request_user_agent == (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    )

    api_instance.api_request_user_agent("CustomUserAgent/1.0")
    assert api_instance._request_user_agent == "CustomUserAgent/1.0"


def test_api_request_timeout(api_instance):
    assert api_instance._request_timeout == pytest.approx(10.0)

    api_instance.api_request_timeout(5.0)
    assert api_instance._request_timeout == pytest.approx(5.0)


def test_api_cache_timeout(api_instance):
    assert api_instance._cache_timeout == pytest.approx(2.0)

    api_instance.api_cache_timeout(10.0)
    assert api_instance._cache_timeout == pytest.approx(10.0)
