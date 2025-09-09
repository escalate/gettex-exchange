import re
from base64 import b64encode
from datetime import datetime
from typing import Optional

import jwt
import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests_cache import NEVER_EXPIRE, BaseCache, CacheMixin
from requests_ratelimiter import LimiterMixin


class CachedLimiterSession(CacheMixin, LimiterMixin, requests.Session):
    """Session class with caching and rate-limiting behavior.
    Accepts keyword arguments for both LimiterSession and CachedSession.
    """


class Api:
    def __init__(
        self, request_timeout: float = 10.0, cache_timeout: float = 2.0
    ) -> None:
        """
        Initializes the Api class with URLs and sane defaults.
        """
        self._auth_api: str = "https://lseg-widgets.financial.com/auth/api/v1"
        self._rest_api: str = "https://lseg-widgets.financial.com/rest/api"
        self._request_user_agent: str = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        )
        self._request_timeout: float = request_timeout
        self._session_id: str = Optional[str]
        self._session_expires_at: datetime = datetime.now()
        self._token: str = Optional[str]
        self._token_expires_at: datetime = datetime.now()
        self._cache_timeout: float = cache_timeout
        self._cache: CachedLimiterSession = CachedLimiterSession(
            cache_name="request_cache",
            backend=BaseCache(),
            stale_if_error=False,
            # Limit non-cached requests to 5 requests per second
            per_second=1,
        )

    def _get_saml_request(self) -> bytes:
        """
        Fetches the SAML Request from the Gettex website.

        Returns:
            bytes: The SAML Request.
        """
        logger.debug("Fetching SAML Request")

        headers = {"User-Agent": self._request_user_agent}

        r = requests.get(
            url="https://www.gettex.de/",
            headers=headers,
            timeout=self._request_timeout,
        )

        if r.status_code != requests.codes.ok:
            raise requests.exceptions.HTTPError(r.status_code)

        soup = BeautifulSoup(r.text, "html.parser")
        widget_script = soup.find_all("script")[3]
        saml_request_search = re.search(
            r"const samlRequest=`([\S\s.]+)`;", widget_script.text
        )

        if not saml_request_search:
            raise ValueError("No SAML Request found.")

        saml_request = saml_request_search.group(1).encode("utf-8")
        logger.debug(f"SAML Request: {saml_request}")

        return saml_request

    def _create_session_and_token(self) -> None:
        """
        Creates a session and token by sending a SAML request to the Gettex API.
        Stores the session ID, the session expiration time,
        the token, and the token expiration time as class attributes for later use.

        Returns:
            None
        """
        logger.debug("Creating session and token")

        base64_saml_request = b64encode(self._get_saml_request())
        data = {"SAMLResponse": base64_saml_request.decode("utf-8")}

        headers = {
            "User-Agent": self._request_user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
        }

        r = requests.post(
            url=f"{self._auth_api}/sessions/samllogin?fetchToken=true",
            headers=headers,
            timeout=self._request_timeout,
            data=data,
        )

        if r.status_code != requests.codes.created:
            raise requests.exceptions.HTTPError(r.status_code)

        self._session_id = r.json()["sid"]
        self._session_expires_at = datetime.fromtimestamp(r.json()["expiresAt"])
        logger.debug(
            f"Session ID: {self._session_id} Expires at: {self._session_expires_at}"
        )

        self._token = r.json()["token"]
        self._token_expires_at = datetime.fromtimestamp(
            jwt.decode(self._token, options={"verify_signature": False})["exp"]
        )
        logger.debug(
            f"Initial Token: {self._token} Expires at: {self._token_expires_at}"
        )

    def _is_session_expired(self) -> bool:
        """
        Checks if the session is expired.

        Returns:
            bool: True if the session is expired, False otherwise.
        """
        logger.debug("Checking if session is expired")

        if self._session_id is None or self._session_expires_at <= datetime.now():
            logger.debug("Session is expired")
            return True
        else:
            logger.debug("Session is valid")
            return False

    def _is_token_expired(self) -> bool:
        """
        Checks if the token is expired.

        Returns:
            bool: True if the token is expired, False otherwise.
        """
        logger.debug("Checking if token is expired")

        if self._token is None or self._token_expires_at <= datetime.now():
            logger.debug("Token is expired")
            return True
        else:
            logger.debug("Token is valid")
            return False

    def _refresh_token(self) -> str:
        """
        Refreshes the token if it is expired.

        Returns:
            str: The refreshed token.
        """
        logger.debug("Refreshing token")

        if self._is_session_expired():
            self._create_session_and_token()

        if self._is_token_expired():
            headers = {
                "Accept": "application/json",
                "User-Agent": self._request_user_agent,
                "sid": self._session_id,
            }

            r = requests.post(
                url=f"{self._auth_api}/tokens",
                headers=headers,
                timeout=self._request_timeout,
            )

            if r.status_code != requests.codes.ok:
                raise requests.exceptions.HTTPError(r.status_code)

            self._token = r.text
            logger.debug(f"Refreshed Token: {self._token}")

        return self._token

    def _get_ric(self, isin: str) -> str:
        """
        Fetches the RIC (Reuters Instrument Code) for a given
        ISIN (International Securities Identification Number).

        Returns:
            str: The RIC for the given ISIN
        """
        logger.debug(f"Fetching RIC for ISIN {isin}")

        if self._is_token_expired():
            self._refresh_token()

        headers = {
            "Accept": "application/json",
            "User-Agent": self._request_user_agent,
            "jwt": self._token,
            "x-component-id": "GettexInit",
        }

        r = self._cache.get(
            url=(
                f"{self._rest_api}/find/securities?"
                f"fids=x.RIC&search={isin}&searchFor=ISIN&exchanges=GTX&isNF=false"
            ),
            headers=headers,
            timeout=self._request_timeout,
            expire_after=NEVER_EXPIRE,
        )

        logger.debug(f"Request '/find/securities' is from cache: {r.from_cache}")
        logger.debug(f"Request cache for '/find/securities' is expired: {r.is_expired}")

        if r.status_code != requests.codes.ok:
            raise requests.exceptions.HTTPError(r.status_code)

        if r.json()["totalCount"] != 1:
            raise ValueError(f"No stock found for ISIN {isin}")

        ric = r.json()["data"][0]["x.RIC"]
        logger.debug(f"RIC for ISIN {isin}: {ric}")

        return ric

    def _translate_taxonomy(self, taxonomy: str) -> str:
        """
        Translates the taxonomy id from the API to a human-readable name.

        Returns:
            str: The translated taxonomy.
        """
        logger.debug(f"Translating taxonomy id {taxonomy}")

        taxonomies = {
            "50": "Energy",
            "51": "Basic Materials",
            "52": "Industrials",
            "53": "Consumer",
            "54": "Consumer",
            "55": "Financials",
            "56": "Healthcare",
            "57": "Technology",
            "59": "Utilities",
            "60": "Real Estate",
            "61": "Institutions",
            "62": "Government Activity",
            "63": "Education",
        }

        return taxonomies.get(taxonomy, "Unknown")
