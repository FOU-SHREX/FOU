# FOU v2.5 — Privacy Policy (Draft)

**Last updated:** October 12, 2026  
**Project:** [FOU — Crypto Portfolio Tracker](https://github.com/FOU-SHREX/FOU)  
**Maintainer:** FOU-SHREX

> This notice describes the reviewed desktop and backend source code. Hosting-provider logs, runtime settings, and whether the reviewed backend matches the current deployment have not been independently verified.

## Overview

FOU is a desktop cryptocurrency watchlist and price tracker, **not** a trading platform or wallet. It does not need wallet access, seed phrases, private keys, or exchange login credentials.

## Data stored locally

FOU saves cryptocurrency symbols and their associated coin IDs in `save_portfolio.json`. It loads this file on startup and updates it when the user saves. No cross-device watchlist synchronization is currently provided.

For packaged applications, the intended locations are:

- **Windows:** `%LOCALAPPDATA%\FOU\save_portfolio.json`
- **Linux:** `$XDG_DATA_HOME/FOU/save_portfolio.json`, or `~/.local/share/FOU/save_portfolio.json` by default
- **macOS:** `~/Library/Application Support/FOU/save_portfolio.json`

When launched from Python source, the file is saved in the project directory.

## Internet and third-party services

FOU contacts the hosted backend at `https://fou-backend.onrender.com` to fetch cryptocurrency lists and prices. When requesting prices, the application sends the relevant cryptocurrency IDs to the backend; it does **not** upload the local `save_portfolio.json` file as such. The backend requests cryptocurrency information from CoinGecko. The GUI may also download cryptocurrency logos from external image URLs. Opening **Help** may take users to an external tutorial in a browser.

Network providers may receive technical request data, such as IP addresses, requested URLs, and timestamps. Handling and retention of these details depend on the provider and the backend deployment configuration.

## Accounts and credentials

FOU's watchlist does not require an account, wallet connection, trading credentials, payment information, or private keys. Do not submit such secrets in bug reports.

## Logging and retention

FOU's desktop watchlist is stored locally rather than synced to an FOU user account. Based on the reviewed backend source:

- **Rate limiting:** The server reads the network address reported by the web framework as `request.client.host` and keeps that value alongside a request count and a time-window start timestamp in an in-memory dictionary. Depending on proxy configuration, this may represent a proxy address rather than the end user's IP address. The code resets counters after a rate-limit window but does not explicitly remove address entries; entries may remain in server memory until the backend process restarts.
- **Market-data caching:** The server caches combinations of requested cryptocurrency IDs and their market-data responses in memory. Cached responses are treated as fresh for 30 seconds, but an expired cache entry is only deleted when that same combination of IDs is requested again. Other stale entries may remain until process restart. The coin-list response is also cached in memory.
- **No persistent application database is defined:** The reviewed backend code does not define a database or write request data to a file. This does not rule out logs or monitoring outside the application code.

The hosting provider and application server may maintain access, diagnostic, or operational logs containing request metadata. Their actual logging configuration and retention have **not** been verified from the supplied code or private deployment dashboard. FOU therefore does not promise that no server-side request information is processed or retained.

## Delete local watchlist data

Close FOU and delete `save_portfolio.json` at the appropriate path to erase your locally saved watchlist. This does not remove any in-memory rate-limit or cache entries on the backend, or logs maintained by network providers. Those server-memory entries normally disappear when the backend process restarts.

## Changes and questions

This notice may change as FOU adds features or changes providers. Updates will be posted in this repository.

For questions, open an issue at [FOU GitHub Issues](https://github.com/FOU-SHREX/FOU/issues). Avoid publishing personal details, API keys, or wallet secrets in public issues.
