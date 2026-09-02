# FOU V1.1

FOU is a simple command-line cryptocurrency watchlist-style portfolio made with Python.

It allows users to add cryptocurrency symbols, view their portfolio, remove coins, and save their portfolio so it can be loaded again the next time the program starts.

## Features

- Add cryptocurrency symbols to your portfolio
- View your saved portfolio
- Remove coins from your portfolio
- Prevent duplicate coin symbols
- Save portfolio data locally
- Automatically load saved portfolio data when the program starts
- Handle missing or corrupted save files without crashing

## How It Works

FOU stores the cryptocurrency symbols entered by the user in a local JSON save file.

When the program starts, it automatically checks for previously saved portfolio data and loads it if available.

## How to Run

### Run with Python

Requirements:

- Python 3
- No external Python libraries are required

Steps:

1. Download or clone the project.
2. Open the project folder.
3. Run `main.py`.
4. Use the numbered menu options shown in the terminal.

### Windows Executable

A standalone Windows executable is available for FOU V1.1.

To run it:

1. Download `FOU.exe`.
2. Place it in a folder where you want FOU to store its save data.
3. Double-click `FOU.exe`.
4. Use the numbered menu options shown in the terminal.

FOU stores `save_portfolio.json` beside the executable, so keep that file in the same folder if you want your saved portfolio to remain available.

## What's New in V1.1

V1.1 focuses on improving the structure, reliability, and usability of the original FOU V1 project.

Changes include:

- Refactored the program into separate functions
- Added a standard Python entry point
- Improved the save-file location system
- Added support for detecting packaged executable mode
- Improved code readability and consistency
- Packaged and tested FOU as a standalone Windows executable

## Save Data

FOU stores portfolio data inside:

`save_portfolio.json`

When running from Python, the save file is stored beside `main.py`.

When running the packaged Windows version, the save file is stored beside `FOU.exe`.

## Current Limitations

FOU V1.1 currently works as a watchlist rather than a real cryptocurrency tracker.

Current limitations include:

- FOU only stores cryptocurrency symbols
- It does not display live cryptocurrency prices
- It does not verify whether a cryptocurrency symbol actually exists
- Invalid symbols can currently be added to the portfolio
- Portfolio data is stored locally on the user's device

## Future Plans

The current plans for FOU V2 include:

- Fetch live cryptocurrency prices
- Validate cryptocurrency symbols before adding them
- Display additional cryptocurrency information
- Improve the portfolio tracking system

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

Current version: **FOU V1.1**

FOU is currently being developed as a learning project and will continue to improve in future versions.
