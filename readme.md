# FOU V2

FOU is a command-line cryptocurrency watchlist built with Python.

It allows users to search for cryptocurrency symbols, add them to a local portfolio, view live market prices, remove coins, and save the portfolio so it can be loaded again the next time FOU starts.

FOU V2 uses a hosted backend to communicate with CoinGecko while keeping the API key out of the distributed desktop application.

## Features

- Add valid cryptocurrency symbols to a portfolio
- Add multiple coins in a single session
- Prevent duplicate coins
- View live cryptocurrency prices
- Sort displayed coins by market-cap rank
- Handle very small cryptocurrency prices with readable formatting
- Remove coins from the portfolio
- Save portfolio data locally
- Automatically load saved portfolio data
- Validate save-file structure and recover safely from corrupted save data
- Handle backend/network errors without crashing
- Cross-platform builds for Windows, Linux, and macOS

## How It Works

FOU stores the user's portfolio locally inside `save_portfolio.json`.

When market information is needed, the desktop application sends requests to the FOU backend. The backend communicates with CoinGecko and returns cryptocurrency information to the application.

The CoinGecko API key is stored only on the backend and is not included inside the distributed FOU executable.

FOU also uses backend caching and rate limiting to reduce unnecessary external API requests.

## How to Run

### Run with Python

Requirements:

- Python 3
- `requests`

Install the required dependency:

`python -m pip install requests`

Steps:

1. Download or clone the project.
2. Open the project folder.
3. Install the required dependency.
4. Run `main.py`.
5. Use the numbered menu options shown in the terminal.

### Windows

1. Download `FOU.exe`.
2. Place it inside a folder where you want FOU to store its save data.
3. Run `FOU.exe`.
4. Use the numbered menu options shown in the terminal.

FOU stores `save_portfolio.json` beside `FOU.exe`.

### Linux

1. Download `FOU-Linux.tar.gz`.
2. Extract the archive.
3. Open a terminal inside the extracted folder.
4. Run:

`./FOU`

FOU stores `save_portfolio.json` beside the executable.

### macOS

1. Download `FOU-macOS.tar.gz`.
2. Extract the archive.
3. Open a terminal inside the extracted folder.
4. Run:

`./FOU`

FOU stores `save_portfolio.json` beside the executable.

The macOS build is produced through GitHub Actions. It has been build-verified, but the current V2 release has not been manually runtime-tested on a physical Mac.

## What's New in V2

FOU V2 expands the original local watchlist into a live cryptocurrency watchlist with real-time market data.

Major changes include:

- Live cryptocurrency prices
- Cryptocurrency symbol validation
- Multiple coins can be added in one session
- Market-cap-based portfolio sorting
- Improved formatting for very small cryptocurrency prices
- A hosted backend for CoinGecko requests
- CoinGecko API credentials are kept out of the distributed application
- Backend caching and rate limiting
- Improved network and backend error handling
- Save-file structure validation
- Recovery from malformed or corrupted save files
- Cross-platform builds for Windows, Linux, and macOS
- Automated cross-platform builds using GitHub Actions

## Save Data

FOU stores portfolio data locally inside:

`save_portfolio.json`

When running from Python, the save file is stored beside `main.py`.

When running a packaged version, the save file is stored beside the FOU executable.

The save file contains cryptocurrency symbols and their associated CoinGecko IDs.

If the save file is missing, corrupted, or contains an invalid structure, FOU creates an empty portfolio instead of crashing.

## Current Limitations

FOU is designed as a cryptocurrency watchlist and does not execute trades or manage real cryptocurrency assets.

FOU currently requires an internet connection and access to the hosted backend to start and retrieve cryptocurrency information.

Because the backend currently uses a free hosting service, the first startup after a period of inactivity may take longer while the backend wakes up.

Portfolio data is stored locally on each device and is not synchronized between devices.

The macOS build is generated successfully through GitHub Actions but has not yet been manually runtime-tested on a physical Mac.

## Future Plans

FOU will continue to improve after V2 based on testing, user reviews, and feedback.

### V2 Updates

After the V2 release, the immediate focus will be:

- Collect user reviews and feedback
- Fix bugs discovered after release
- Improve reliability and usability
- Refine the interface and existing features
- Make small improvements without changing the core V2 design

### V3

The next major version of FOU is planned to expand the project beyond the current command-line watchlist.

Current ideas for V3 include:

- Price alerts
- Cryptocurrency notifications
- Telegram bot integration
- Additional portfolio and market information
- Improvements based on V2 user feedback

The V3 plan may change based on testing, technical limitations, and feedback from V2.

## AI Usage

AI tools, mainly ChatGPT, were used during the development of FOU as a learning and development assistant.

AI was used for:

- Explaining Python concepts
- Reviewing code
- Helping identify bugs
- Suggesting code structure improvements
- Learning Git and GitHub workflows
- Understanding packaging and project-release concepts

The project code was written, modified, and tested by me while using AI mainly for guidance and feedback.

## Version

Current version: **FOU V2.0.0**

FOU is being developed as a learning project and will continue to improve in future versions.