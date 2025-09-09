from datetime import datetime

import requests
from loguru import logger

from .api import Api


class Stock(Api):
    def __init__(self, isin: str) -> None:
        """
        Initializes the Stock class
        """
        super().__init__()
        self._isin: str = isin

        self._bid_price: float = 0.0
        self._ask_price: float = 0.0

        self._bid_size: int = 0
        self._ask_size: int = 0

        self._ticker: str = ""
        self._display_name: str = ""
        self._low_price: float = 0.0
        self._price_change: float = 0.0
        self._percent_change: float = 0.0
        self._country: str = ""
        self._trade_date_time: datetime = datetime.now()
        self._wkn: str = ""
        self._open_price: float = 0.0
        self._high_price: float = 0.0
        self._last_price: float = 0.0
        self._turnover: float = 0.0
        self._taxonomy: str = ""

    def _get_quote_info(self, fields: list, component_id: str) -> dict:
        """
        Fetches quote info for a stock.

        Returns:
            dict: A dictionary containing the fetched info.
        """
        logger.debug(f"Fetching quote info for stock with ISIN {self._isin}")

        ric = self._get_ric(self._isin)

        if self._is_token_expired():
            self._refresh_token()

        url = f"{self._rest_api}/quote/info?" f"rics={ric}&fids={",".join(fields)}"

        headers = {
            "Accept": "application/json",
            "User-Agent": self._request_user_agent,
            "jwt": self._token,
            "x-component-id": component_id,
        }

        r = self._cache.get(
            url=url,
            headers=headers,
            timeout=self._request_timeout,
            expire_after=self._cache_timeout,
        )

        logger.debug(f"Request {url} is from cache: {r.from_cache}")
        logger.debug(f"Request cache for {url} is expired: {r.is_expired}")

        if r.status_code != requests.codes.ok:
            raise requests.exceptions.HTTPError(r.status_code)

        data = r.json()["data"][0]

        logger.debug(f"Fetched quote info for stock with ISIN {self._isin}: {data}")

        return data

    def _get_quote_info_matrix_price(self) -> dict:
        """
        Fetches the bid and ask price for a stock.

        Returns:
            dict: A dictionary containing the bid and ask price.
        """
        logger.debug(f"Fetching bid and ask price for a stock with ISIN {self._isin}")

        component_id = "InfoMatrix"
        fields = [
            "q._BID",
            "q._ASK",
        ]
        return self._get_quote_info(fields, component_id)

    @property
    def isin(self) -> str:
        """
        Returns the ISIN for a stock.

        Returns:
            str: The ISIN.
        """
        return self._isin

    @property
    def bid_price(self) -> float:
        """
        Fetches the bid price for a stock.

        Returns:
            float: The bid price.
        """
        data = self._get_quote_info_matrix_price()
        self._bid_price = float(data.get("q._BID"))
        return self._bid_price

    @property
    def ask_price(self) -> float:
        """
        Fetches the ask price for a stock.

        Returns:
            float: The ask price.
        """
        data = self._get_quote_info_matrix_price()
        self._ask_price = float(data.get("q._ASK"))
        return self._ask_price

    def _get_quote_info_matrix_size(self) -> dict:
        """
        Fetches the bid and ask size for a stock.

        Returns:
            dict: A dictionary containing the bid size and ask size.
        """
        logger.debug(f"Fetching bid and ask size for stock with ISIN {self._isin}")

        component_id = "InfoMatrix"
        fields = [
            "q.BIDSIZE",
            "q.ASKSIZE",
        ]
        return self._get_quote_info(fields, component_id)

    @property
    def bid_size(self) -> int:
        """
        Fetches the bid size for a stock.

        Returns:
            int: The bid size.
        """
        data = self._get_quote_info_matrix_size()
        self._bid_size = int(data.get("q.BIDSIZE"))
        return self._bid_size

    @property
    def ask_size(self) -> int:
        """
        Fetches the ask size for a stock.

        Returns:
            int: The ask size.
        """
        data = self._get_quote_info_matrix_size()
        self._ask_size = int(data.get("q.ASKSIZE"))
        return self._ask_size

    def _get_quote_info_instrument_info(self) -> dict:
        """
        Fetches additional info for a stock.

        Returns:
            dict: A dictionary containing the additional info.
        """
        logger.debug(f"Fetching additional info for a stock with ISIN {self._isin}")

        component_id = "InstrumentInfo"
        fields = [
            "x._TICKER",
            "x._DSPLY_NAME",
            "q._TRDPRC_1",
            "q._NETCHNG_1",
            "q._PCTCHNG",
            "q._COUNTRY",
            "q._TRADE_DATE",
            "q._TRDTIM_1",
            "x._LOCAL_ID",
            "q._OPEN_PRC",
            "q._HIGH_1",
            "q._LOW_1",
            "q._TURNOVER",
            "rkd.COMP_TAXONOMY_TRBC_CD_L1",
        ]

        return self._get_quote_info(fields, component_id)

    @property
    def ticker(self) -> str:
        """
        Fetches the ticker for a stock.

        Returns:
            str: The ticker.
        """
        data = self._get_quote_info_instrument_info()
        self._ticker = data.get("x._TICKER")
        return self._ticker

    @property
    def display_name(self) -> str:
        """
        Fetches the display name for a stock.

        Returns:
            str: The display name.
        """
        data = self._get_quote_info_instrument_info()
        self._display_name = data.get("x._DSPLY_NAME")
        return self._display_name

    @property
    def low_price(self) -> float:
        """
        Fetches the low price for a stock.

        Returns:
            float: The low price.
        """
        data = self._get_quote_info_instrument_info()
        self._low_price = float(data.get("q._LOW_1"))
        return self._low_price

    @property
    def price_change(self) -> float:
        """
        Fetches the price change for a stock.

        Returns:
            float: The price change.
        """
        data = self._get_quote_info_instrument_info()
        self._price_change = float(data.get("q._NETCHNG_1"))
        return self._price_change

    @property
    def percent_change(self) -> float:
        """
        Fetches the percent change for a stock.

        Returns:
            float: The percent change.
        """
        data = self._get_quote_info_instrument_info()
        self._percent_change = float(data.get("q._PCTCHNG"))
        return self._percent_change

    @property
    def country(self) -> str:
        """
        Fetches the country for a stock.

        Returns:
            str: The country.
        """
        data = self._get_quote_info_instrument_info()
        self._country = data.get("q._COUNTRY")
        return self._country

    @property
    def trade_date_time(self) -> datetime:
        """
        Fetches the trade date and time for a stock.

        Returns:
            datetime: The trade date and time.
        """
        data = self._get_quote_info_instrument_info()
        # 12 MAY 2025
        trade_date = data.get("q._TRADE_DATE")
        # 08:12
        trade_time = data.get("q._TRDTIM_1")
        self._trade_date_time = datetime.strptime(
            f"{trade_date} {trade_time}+0000", "%d %b %Y  %H:%M%z"
        )
        return self._trade_date_time

    @property
    def wkn(self) -> str:
        """
        Fetches the WKN (Wertpapierkennnummer) for a stock.

        Returns:
            str: The WKN.
        """
        data = self._get_quote_info_instrument_info()
        self._wkn = data.get("x._LOCAL_ID")
        return self._wkn

    @property
    def open_price(self) -> float:
        """
        Fetches the open price for a stock.

        Returns:
            float: The open price.
        """
        data = self._get_quote_info_instrument_info()
        self._open_price = float(data.get("q._OPEN_PRC"))
        return self._open_price

    @property
    def high_price(self) -> float:
        """
        Fetches the high price for a stock.

        Returns:
            float: The high price.
        """
        data = self._get_quote_info_instrument_info()
        self._high_price = float(data.get("q._HIGH_1"))
        return self._high_price

    @property
    def last_price(self) -> float:
        """
        Fetches the last price for a stock.

        Returns:
            float: The last price.
        """
        data = self._get_quote_info_instrument_info()
        self._last_price = float(data.get("q._TRDPRC_1"))
        return self._last_price

    @property
    def turnover(self) -> float:
        """
        Fetches the turnover for a stock.

        Returns:
            float: The turnover.
        """
        data = self._get_quote_info_instrument_info()
        self._turnover = float(data.get("q._TURNOVER"))
        return self._turnover

    @property
    def taxonomy(self) -> str:
        """
        Fetches the taxonomy name for a stock.

        Returns:
            str: The taxonomy name.
        """
        data = self._get_quote_info_instrument_info()
        self._taxonomy = self._translate_taxonomy(
            data.get("rkd.COMP_TAXONOMY_TRBC_CD_L1")
        )
        return self._taxonomy
