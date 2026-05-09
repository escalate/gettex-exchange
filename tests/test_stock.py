import json
import uuid
from datetime import datetime, timedelta, timezone
from time import sleep

import jwt
import pytest
import responses
from responses import matchers

from gettex_exchange import Stock


def unique_id():
    return str(uuid.uuid4())


def timestamp(seconds: int = 0):
    return int((datetime.now() + timedelta(seconds=seconds)).timestamp())


def jwt_token(seconds: int = 0):
    payload = {
        "lgn": "WG_GETTEX",
        "nbf": timestamp(),
        "prt": "wlib_gettex",
        "iss": "fincom",
        "prm": ["a:streaming", "c:api_documentation", "c:bbag", "c:wm_data", "USER"],
        "ety": "WG_GETTEX",
        "exp": timestamp(seconds=seconds),
        "iat": timestamp(),
        "jti": unique_id(),
        "did": "WG_GETTEX",
        "sea": unique_id(),
    }
    token = jwt.encode(payload, "secret", algorithm="HS256")
    return token


def gettex_homepage():
    with open("tests/fixtures/api/gettex_homepage.html", "r") as f:
        return f.read()


def saml_login():
    return {
        "sid": unique_id(),
        "expiresAt": timestamp(seconds=60),
        "token": jwt_token(seconds=1),
    }


def securities_ric():
    with open("tests/fixtures/api/securities_ric.json", "r") as f:
        return json.loads(f.read())


def stock_info_matrix_price():
    with open("tests/fixtures/stock/stock_info_matrix_price.json", "r") as f:
        return json.loads(f.read())


def stock_info_matrix_size():
    with open("tests/fixtures/stock/stock_info_matrix_size.json", "r") as f:
        return json.loads(f.read())


def stock_instrument_info():
    with open("tests/fixtures/stock/stock_instrument_info.json", "r") as f:
        return json.loads(f.read())


def stock_price_chart():
    with open("tests/fixtures/stock/stock_price_chart.json", "r") as f:
        return json.loads(f.read())


def stock_time_sales():
    with open("tests/fixtures/stock/stock_time_sales.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:

        rsps.add(
            method=responses.GET,
            url="https://www.gettex.de/",
            body=gettex_homepage(),
            status=200,
        )

        rsps.add(
            method=responses.POST,
            url="https://lseg-widgets.financial.com/auth/api/v1/sessions/samllogin",
            match=[
                matchers.query_param_matcher(
                    {
                        "fetchToken": "true",
                    }
                )
            ],
            json=saml_login(),
            status=201,
        )

        rsps.add(
            method=responses.POST,
            url="https://lseg-widgets.financial.com/auth/api/v1/tokens",
            json=jwt_token(),
            status=200,
        )

        rsps.add(
            method=responses.GET,
            url="https://lseg-widgets.financial.com/rest/api/find/securities",
            match=[
                matchers.query_param_matcher(
                    {
                        "fids": "x.RIC",
                        "search": "US88160R1014",
                        "searchFor": "ISIN",
                        "exchanges": "GTX",
                        "isNF": "false",
                    }
                )
            ],
            json=securities_ric(),
            status=200,
        )

        rsps.add(
            method=responses.GET,
            url="https://lseg-widgets.financial.com/rest/api/quote/info",
            match=[
                matchers.query_param_matcher(
                    {
                        "rics": "TSLA.GTX",
                        "fids": "q._BID,q._ASK",
                    }
                )
            ],
            json=stock_info_matrix_price(),
            status=200,
        )

        rsps.add(
            method=responses.GET,
            url="https://lseg-widgets.financial.com/rest/api/quote/info",
            match=[
                matchers.query_param_matcher(
                    {
                        "rics": "TSLA.GTX",
                        "fids": "q.BIDSIZE,q.ASKSIZE",
                    }
                )
            ],
            json=stock_info_matrix_size(),
            status=200,
        )

        rsps.add(
            method=responses.GET,
            url="https://lseg-widgets.financial.com/rest/api/quote/info",
            match=[
                matchers.query_param_matcher(
                    {
                        "rics": "TSLA.GTX",
                        "fids": (
                            "x._TICKER,x._DSPLY_NAME,x._LOCAL_ID,x._ISIN,x._CURRENCY,"
                            "q._TRDPRC_1,q._NETCHNG_1,q._PCTCHNG,q._BID,q._ASK,"
                            "q._BIDSIZE,q._ASKSIZE,q._ACVOL_1,q._TURNOVER,q._VWAP,"
                            "q._TRDVOL_1,q._OPEN_PRC,q._HIGH_1,q._LOW_1,q._HST_CLOSE,"
                            "q._COUNTRY,q._TRADE_DATE,q._TRDTIM_1,q._HSTCLSDATE,"
                            "rkd.COMP_TAXONOMY_TRBC_CD_L1,"
                            "rkd.COMP_TAXONOMY_TRBC_CD_L2,"
                            "rkd.COMP_TAXONOMY_TRBC_CD_L3"
                        ),
                    }
                )
            ],
            json=stock_instrument_info(),
            status=200,
        )

        yield rsps


def test_stock(mocked_responses):

    s = Stock("US88160R1014")
    assert s.isin == "US88160R1014"

    assert s.bid_price == 363.05
    assert s.ask_price == 363.45

    assert s.bid_size == 375
    assert s.ask_size == 375

    sleep(2.5)

    assert s.ticker == "TL0"
    assert s.display_name == "TESLA MOTORS"
    assert s.low_price == 350.55
    assert s.price_change == 13.1
    assert s.percent_change == 3.741
    assert s.country == "DE"
    assert s.trade_date_time == datetime(
        year=2026,
        month=5,
        day=8,
        hour=20,
        minute=56,
        second=10,
        tzinfo=timezone.utc,
    )
    assert s.wkn == "A1CX3T"
    assert s.open_price == 351.05
    assert s.high_price == 366
    assert s.last_price == 363.3
    assert s.turnover == 5112392.25
    assert s.taxonomy == "Consumer"
    assert s.taxonomy_level_2 == 5310
    assert s.taxonomy_level_3 == 531010
    assert s.currency == "EUR"
    assert s.accumulated_intraday_volume == 14201
    assert s.vwap == 360.00227
    assert s.last_trade_volume == 1
    assert s.previous_close_price == 350.2
    assert s.previous_close_date == datetime(
        year=2026,
        month=5,
        day=7,
        tzinfo=timezone.utc,
    )

    assert False, s._get_quote_info_instrument_info()
