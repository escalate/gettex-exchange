[![Test](https://github.com/escalate/gettex-exchange/actions/workflows/test.yml/badge.svg?branch=master&event=push)](https://github.com/escalate/gettex-exchange/actions/workflows/test.yml)

# 📈 Gettex exchange

A Python client library for [Gettex exchange](https://www.gettex.de).

## ✨ Features

- Stock data from overview e.g. https://www.gettex.de/en/stock/US88160R1014/

## ⚠️ Disclaimer

This Python library is unofficial and not affiliated with, endorsed, or maintained by Gettex exchange.

Users are responsible for ensuring compliance with the legal terms and conditions of Gettex exchange when accessing, processing, or distributing any data obtained through this library.

Please review the official [legal notices](https://www.gettex.de/en/legal-notice/) of Gettex exchange before use.

## 📦 Installation

You can install [gettex-exchange](https://pypi.org/project/gettex-exchange/) using [pip](https://pypi.org/project/pip/):

```bash
pip install gettex-exchange
```

## 🚀 Quick Start

Here is a minimal example to get you started:

```python
from gettex_exchange import Stock

# Create an Stock instance
# URL: https://www.gettex.de/en/stock/US88160R1014/
isin = "US88160R1014"
s = Stock(isin)

# Print basic information of stock
print(s.bid_price)
print(s.ask_price)
print(s.bid_size)
print(s.ask_size)
print(s.ticker)
print(s.display_name)
print(s.wkn)
print(s.open_price)
print(s.high_price)
print(s.low_price)
print(s.last_price)
print(s.turnover)
print(s.percent_change)
print(s.price_change)
print(s.trade_date_time)
print(s.taxonomy)
```

## 🤝 Contributing

We welcome contributions of all kinds 🎉.

Please read our [CONTRIBUTING.md](https://github.com/escalate/gettex-exchange/blob/master/CONTRIBUTING.md) guide to learn how to get started, submit changes, and follow our contribution standards.

## 🌐 Code of Conduct

This project follows a [Code of Conduct](https://github.com/escalate/gettex-exchange/blob/master/CODE_OF_CONDUCT.md) to ensure a welcoming and respectful community.

By participating, you agree to uphold this standard.

# 🐛 Issues

Found a bug or want to request a feature?

Open an issue here: [GitHub Issues](https://github.com/escalate/gettex-exchange/issues)

## 🧪 Development

Development is possible via an interactive Docker container in VSCode.

1. Build and launch the [DevContainer](https://code.visualstudio.com/docs/devcontainers/containers) in VSCode.

2. Initiate the Python Virtual Environment via `poetry env activate` in the terminal.

3. Run test suite via `pytest` in the terminal.

## 📜 License

This project is licensed under the **MIT License**.

See the [LICENSE](https://github.com/escalate/gettex-exchange/blob/master/LICENSE) file for details.
