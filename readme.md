# FOU v2.5 — Crypto Portfolio Tracker

**A little Python watchlist that slowly turned into a desktop app.**

FOU is my cryptocurrency watchlist and price tracker. You can add coins you want to follow, check their latest available prices, and keep your list saved for next time. There's no account to make, no wallet to connect, and no trading involved.

I started FOU while learning Python, mostly to see whether I could build something useful beyond small practice programs. I kept adding to it, breaking things, fixing them, and eventually turned the terminal version into a full desktop app for **Hack Club Stardance**.

The current version, **v2.5**, has three themes, three companions, and a bunch of small details I spent far too much time adjusting. The original CLI is still here too.

## Watch FOU in action

Here's a silent walkthrough of the actual desktop app: adding coins, checking prices, saving a watchlist, switching themes, and seeing the companions react.

https://github.com/user-attachments/assets/0a3a8ab3-f181-4bb7-b2a8-0bce8a2d00bb

**[Download FOU v2.5.0](https://github.com/FOU-SHREX/FOU/releases/tag/v2.5.0)** · **[Privacy](PRIVACY.md)** · **[Code Signing Policy](CODE_SIGNING_POLICY.md)** · **[Asset licenses](ASSET_LICENSES.md)** · **[MIT License](LICENSE)**

> **v2.5.0 is released!** You can download FOU for Windows, Linux, or macOS from the [official GitHub Release](https://github.com/FOU-SHREX/FOU/releases/tag/v2.5.0). I tested the Windows executable locally and also downloaded and ran the published ZIP on another Windows laptop, where it worked without a security warning. The Windows app is still **unsigned**, so other PCs may warn or block it. Linux and macOS builds passed GitHub Actions, but still need real-device runtime testing. I have submitted a code-signing application to SignPath Foundation; approval is pending.

## Before You Try FOU v2.5.0

Hey! Thanks for giving FOU a try. A few quick notes might make your first run smoother.

### First price load can take around 60 seconds ⏳

When you add your first coin, or reopen FOU with a saved portfolio, **the prices may take around a minute to appear**. FOU gets market prices from an online backend that I'm hosting on a free service. After a period of inactivity, that server can go to sleep, and the first request needs to wake it up.

Your coin list is saved locally on your computer; the wait is mainly for **fresh prices**, not for reading your saved portfolio. Once the server is awake, adding coins and refreshing should usually be quicker. If nothing loads after a minute or two, check your internet connection and try **Refresh** again.

### Windows might show a security warning 🛡️

FOU v2.5.0 is **not code-signed yet**. I've applied to SignPath Foundation, but approval is still pending. The published Windows ZIP worked on another laptop without any warning; that doesn't mean every Windows computer will behave the same way.

Some PCs may show **Windows protected your PC** through SmartScreen. If you've checked the official download and trust it, Windows may offer **More info → Run anyway**. Windows 11 Smart App Control can also block unsigned applications without offering an individual-app exception. **Please don't disable system-wide security just to test FOU.** You can watch the [demo video](#watch-fou-in-action) instead if your system blocks it.

### A couple of things to remember 📦

On Windows, **extract the whole ZIP before launching** and keep `FOU.exe` alongside its `_internal` folder. You don't need to install Python separately. The Linux and macOS packages are available, but I haven't yet tested them running on those systems.

If you find a bug or have trouble launching FOU, please [open an issue](https://github.com/FOU-SHREX/FOU/issues) with your OS and what happened. I really appreciate the feedback!

## Contents

- [Watch FOU in action](#watch-fou-in-action)
- [Before You Try FOU v2.5.0](#before-you-try-fou-v250)
- [See FOU](#see-fou)
- [Why I built it](#why-i-built-it)
- [The journey: CLI to GUI](#the-journey-cli-to-gui)
- [Features](#features)
- [How feedback shaped FOU](#how-feedback-shaped-fou)
- [Three themes, three companions](#three-themes-three-companions)
- [The six companion emotions](#the-six-companion-emotions)
- [Two tricky parts of the GUI](#two-tricky-parts-of-the-gui)
- [Download, installation, and running from source](#download-installation-and-running-from-source)
- [How FOU works](#how-fou-works)
- [Testing and reliability](#testing-and-reliability)
- [What I learned](#what-i-learned)
- [AI tools and credits](#ai-tools-and-credits)
- [Limitations and roadmap](#limitations-and-roadmap)
- [License and contributions](#license-and-contributions)

## See FOU

Three themes are available in the **v2.5** theme selector. Each one has its own colors, layout details, companion, and atmosphere; switching themes does not change which coins are in your portfolio.

<table>
  <tr>
    <th>FOU DEFAULT</th>
    <th>THE FOOL</th>
    <th>VOID</th>
  </tr>
  <tr>
    <td align="center"><img src="assets/reactions/fou_default/idle.png" alt="FOU, the default theme companion" width="215"></td>
    <td align="center"><img src="assets/reactions/the_fool/idle.png" alt="MR. FOOL, the antique-gold gothic companion" width="215"></td>
    <td align="center"><img src="assets/reactions/void/idle.png" alt="NØXAR, the deep-purple cosmic companion" width="215"></td>
  </tr>
  <tr>
    <td align="center"><strong>FOU</strong> · Modern / cosmic</td>
    <td align="center"><strong>MR. FOOL</strong> · Gothic / antique gold</td>
    <td align="center"><strong>NØXAR</strong> · Cosmic void / violet</td>
  </tr>
</table>

*These are the companions from the project assets. They change expression as you use the app.*

## Why I built it

FOU is one of the first projects where I started learning Python by actually building something, instead of just solving exercises.

I wanted to check a few crypto prices without opening an exchange and searching for the same coins every single time. I wanted something small that would remember my list and show me the prices when I came back.

The first idea was straightforward:

1. Add a symbol such as `BTC`, `ETH`, or `SOL`.
2. Fetch the latest available price.
3. Keep the list saved for the next session.
4. Make the experience faster and more enjoyable over time.

That is pretty much where FOU began. Just to be clear, it is **not a trading platform**: it does not hold funds, connect to a crypto wallet, execute orders, or require you to own the coins you track.

## The journey: CLI to GUI

### Stage 1 — My first Python CLI

FOU started as a terminal-based watchlist. It taught me how to put individual Python concepts together into an actual application: dictionaries, loops, functions, conditional logic, string handling, and reading and writing JSON.

The early CLI could add symbols, view a portfolio, remove coins, and save data. Repeated testing made it more reliable: empty inputs were ignored, symbols were normalized with `.strip().upper()`, and duplicate entries such as `BTC` and `btc` were treated as the same coin.

### Stage 2 — Making the data real

Once the basic list worked, I wanted it to show real information. That turned into a few new problems to solve:

- Symbol validation and market-price retrieval.
- Market-cap-ranked results and readable price formatting, including very small prices.
- A hosted backend that contacts CoinGecko so an API key does not need to be embedded in the desktop client.
- Network-error handling, backend caching, and rate limiting.
- JSON validation so a malformed save file does not crash the app.

This was also when I started thinking about how someone other than me would run the project: Windows releases, Linux archives, GitHub Actions, dependency management, and testing clean downloads rather than just running my own working directory.

### Stage 3 — Building a desktop GUI

After spending enough time in the terminal, I wanted FOU to feel like something you could open and use every day — not just a CLI with prettier output.

I moved the interface to **CustomTkinter**, used **Pillow** to prepare and render artwork, and kept the underlying portfolio logic in Python. The GUI introduced a visual coin list, search field, Add Coin button, Refresh and Save actions, activity indicator, theme selector, and companion panel.

The first GUI looked nothing like the current one. I would run it, spot a problem with a frame or some spacing, adjust the Python code, and try again. Getting it to look right while still working properly took much longer than I expected.

### Stage 4 — FOU v2.5: three finished themes

For v2.5, I decided to finish three themes properly instead of making lots of half-finished ones: **FOU DEFAULT**, **THE FOOL**, and **VOID**. Their characters, background illustrations, controls, text styles, frames, and reactions are deliberately different, while the underlying portfolio remains the same.

I also learned to lock completed designs instead of changing everything every time I improved one theme. Any time I changed VOID, I made sure FOU DEFAULT and THE FOOL still worked.

## Features

### Portfolio and market data

- Add a cryptocurrency by its symbol, with validation against available coins.
- Reject duplicate symbols and ignore blank input.
- View the latest available prices in USD and refresh them on demand.
- Display coins in market-cap-rank order, and show tiny prices with multipliers (like `BABYDOGE ×1,000`) so they do not just look like zero.
- Remove individual coins using an **×** control on their row.
- Save and reload the portfolio locally; **no wallet connection** required.
- Recover to an empty portfolio when the JSON save file is missing or invalid.
- Show selected-coin and last-updated information.
- Fetch coin logos, crop or mask inconsistent backgrounds, and tint them to suit the active theme.

### Desktop experience

- A themed **Companion** panel with six visual reaction states.
- Three selectable themes, with independent palettes, typography, illustrations, and ornamentation.
- A scrollable Portfolio area with compact, readable rows.
- Search icon that focuses the coin-entry field; Enter can also add a coin.
- Responsive resizing for different window and monitor sizes.
- Loading feedback and disabled controls while requests are in progress.
- A **Help** button that opens this GitHub README in your browser.
- A status/activity area that reports success, failures, and network activity.

## How feedback shaped FOU

A lot of FOU came from noticing small things that felt awkward and then going back to fix them. None of these changes is huge on its own, but together they made the app easier to use.

| What I noticed or wanted | What changed |
| --- | --- |
| “Watchlist” felt less suitable for the UI | Renamed the main panel **Portfolio**. |
| The extra Orbital Watchlist section made the layout busy | Removed it and focused on the primary coin list. |
| A separate Remove button took up room | Added a compact **×** on each coin row. |
| Rows needed a clearer focus state | Added a selected-row highlight and selection indicator. |
| The first coin shouldn't be chosen automatically | Left selection empty until the user selects a coin. |
| Refreshing shouldn't arbitrarily change the user's focus | Preserved the active selection when the selected symbol is still available. |
| Coin logos had different shapes and backgrounds | Added automated normalization, circular masking, and theme-based recoloring. |
| The search icon felt decorative instead of useful | Made clicking it focus the input box. |
| Users needed clearer progress while loading | Added **Loading** reactions, activity feedback, and temporary control disabling. |
| Status text alone felt disconnected from the companion | Linked **Idle, Loading, Happy, Angry, Confused, and Proud** to real app events. |
| People needed a way to learn the UI | Added a **Help** button that opens this README. |
| Save and Refresh buttons felt inconsistent between themes | Refined icons, fonts, button borders, and themed ornamental treatments. |
| The interface looked different when maximized or resized | Iterated on layout proportions, render sizes, backgrounds, and frame alignment. |
| Portfolio text and controls were hard to fit inside artwork | Adjusted padding, coin-row spacing, headings, scrollbar, and border geometry. |
| One theme's fixes could affect another | Kept the three completed themes isolated and ran cross-theme regression tests. |

The final UI is mostly the result of dozens of these little decisions.

## Three themes, three companions

### 1. FOU DEFAULT — FOU

The original desktop identity: dark, modern, restrained, with a space-inspired look. **FOU** is the default companion, providing reactions without distracting from the prices and controls.

<img src="assets/reactions/fou_default/idle.png" alt="FOU DEFAULT companion FOU in the Idle state" width="330">

### 2. THE FOOL — MR. FOOL

A very different atmosphere: **black, antique gold, parchment-like accents, gothic ornamentation, and occult/celestial details**. MR. FOOL belongs in this setting. The theme has a special companion frame and a highly detailed Portfolio border, built to stay aligned as the window size changes.

<img src="assets/reactions/the_fool/idle.png" alt="THE FOOL companion MR. FOOL in the Idle state" width="330">

### 3. VOID — NØXAR

VOID uses **deep purple, black, cold lavender, thorn-like metalwork, and a fractured cosmic-eclipse atmosphere**. NØXAR is a shadowy, quiet character with messy hair and glowing eyes. This theme also introduced the **New Rocker** display font and gothic button-frame artwork.

<img src="assets/reactions/void/idle.png" alt="VOID companion NØXAR in the Idle state" width="330">

## The six companion emotions

The companion is not just a static illustration. FOU changes its state in response to the app's actual behavior.

| Emotion | When it appears |
| --- | --- |
| **Idle** | The app is standing by or has returned to its normal state. |
| **Loading** | FOU is contacting the backend, refreshing prices, or checking a coin. |
| **Happy** | A coin is added or removed successfully. |
| **Angry** | You try to add a coin already in your portfolio. |
| **Confused** | A symbol is invalid, input is missing, or a network/data problem occurs. |
| **Proud** | Your portfolio is saved successfully. |

Every released theme has its own companion-art folder. Expand a gallery to see the artwork for each reaction.

<details>
<summary><strong>FOU DEFAULT — FOU's six reactions</strong></summary>

| Idle | Loading | Happy |
|:---:|:---:|:---:|
| <img src="assets/reactions/fou_default/idle.png" width="170" alt="FOU Idle"> | <img src="assets/reactions/fou_default/loading.png" width="170" alt="FOU Loading"> | <img src="assets/reactions/fou_default/happy.png" width="170" alt="FOU Happy"> |

| Angry | Confused | Proud |
|:---:|:---:|:---:|
| <img src="assets/reactions/fou_default/angry.png" width="170" alt="FOU Angry"> | <img src="assets/reactions/fou_default/confused.png" width="170" alt="FOU Confused"> | <img src="assets/reactions/fou_default/proud.png" width="170" alt="FOU Proud"> |

</details>

<details>
<summary><strong>THE FOOL — MR. FOOL's six reactions</strong></summary>

| Idle | Loading | Happy |
|:---:|:---:|:---:|
| <img src="assets/reactions/the_fool/idle.png" width="170" alt="MR. FOOL Idle"> | <img src="assets/reactions/the_fool/loading.png" width="170" alt="MR. FOOL Loading"> | <img src="assets/reactions/the_fool/happy.png" width="170" alt="MR. FOOL Happy"> |

| Angry | Confused | Proud |
|:---:|:---:|:---:|
| <img src="assets/reactions/the_fool/angry.png" width="170" alt="MR. FOOL Angry"> | <img src="assets/reactions/the_fool/confused.png" width="170" alt="MR. FOOL Confused"> | <img src="assets/reactions/the_fool/proud.png" width="170" alt="MR. FOOL Proud"> |

</details>

<details>
<summary><strong>VOID — NØXAR's six reactions</strong></summary>

| Idle | Loading | Happy |
|:---:|:---:|:---:|
| <img src="assets/reactions/void/idle.png" width="170" alt="NØXAR Idle"> | <img src="assets/reactions/void/loading.png" width="170" alt="NØXAR Loading"> | <img src="assets/reactions/void/happy.png" width="170" alt="NØXAR Happy"> |

| Angry | Confused | Proud |
|:---:|:---:|:---:|
| <img src="assets/reactions/void/angry.png" width="170" alt="NØXAR Angry"> | <img src="assets/reactions/void/confused.png" width="170" alt="NØXAR Confused"> | <img src="assets/reactions/void/proud.png" width="170" alt="NØXAR Proud"> |

</details>

*These galleries reference the reaction PNGs in the project assets.*

## Two tricky parts of the GUI

The part that surprised me most was how much code went into details that seem simple when you're just looking at the screen. Here are two functions from [`gui.py`](gui.py) that took some real figuring out.

### 1. `build_portfolio_border()` — making THE FOOL's gold frame resize properly

THE FOOL uses a detailed gold border around the Portfolio panel. I had the artwork as a transparent PNG, but stretching the whole image made the corners and ornaments look wrong. Worse, the frame didn't always line up with the companion panel after maximizing or resizing the window.

<img src="assets/ui/the_fool/portfolio_frame.png" alt="Transparent gold Portfolio frame used in THE FOOL" width="520">

The solution was to split the image into smaller regions instead of resizing everything together. The real function works with a **5 × 5 grid**. Some parts can grow more than others, so the corners and important ornaments keep much more of their original shape.

Here's a small part of the actual code:

```python
xs = (0, round(sw * 0.08), round(sw * 0.44),
      round(sw * 0.57), round(sw * 0.92), sw)
ys = (0, round(sh * 0.16), round(sh * 0.44),
      round(sh * 0.56), round(sh * 0.82), sh)

for row in range(5):
    for column in range(5):
        tile = source.crop((xs[column], ys[row],
                            xs[column + 1], ys[row + 1]))
        tile = tile.resize((tile_width, tile_height), Image.Resampling.LANCZOS)
        frame.alpha_composite(tile, (dx[column], dy[row]))
```

That loop cuts out the pieces, resizes them to their new positions, and recombines them on a transparent image. The surrounding code works out the destination sizes. Other helpers, such as `get_portfolio_border_vertical_bounds()` and `render_portfolio_border()`, measure the actual window and align the gold frame with the companion's visible border.

It still took plenty of comparing the running app against the target layout. I worked with **OpenAI Codex** on some of the border-rendering calculations, then kept testing the results and adjusting what didn't match. This was probably the hardest visual part of FOU for me.

### 2. `request_coin_logo()` — downloading and recoloring logos without freezing the app

I thought coin logos would be the easy part. Then I started seeing square backgrounds, odd proportions, and coins whose logos were almost invisible in a dark theme.

The GUI keeps a cache of downloaded logos. If an image is already available, it can reuse it. If not, `request_coin_logo()` starts a background download instead of making the whole window wait.

This is the key idea from the function:

```python
if image_url in coin_logo_loading:
    return

coin_logo_loading.add(image_url)

threading.Thread(
    target=worker,
    daemon=True
).start()
```

The loading set stops the same image from being downloaded several times at once. Inside the worker, FOU fetches the image and passes it to `normalize_coin_logo()`. Once the download finishes, the UI is updated using `app.after(...)` rather than directly changing widgets from the worker thread.

The rest of the image-processing code uses Pillow to crop, mask, and tint logos for the active theme. There's also a cache for the themed versions, so changing from FOU DEFAULT to VOID doesn't mean downloading all the images again.

Both of these taught me the same thing: getting a feature to *work* is only half the job. Making it look consistent and behave well when people resize the window or switch themes is another challenge.

## Download, installation, and running from source

### Download the published v2.5.0 release

The three packages below are available in the [FOU v2.5.0 GitHub Release](https://github.com/FOU-SHREX/FOU/releases/tag/v2.5.0). They were built through GitHub Actions.

| Platform | Download | Testing status |
| --- | --- | --- |
| Windows portable | [FOU-v2.5-Windows.zip](https://github.com/FOU-SHREX/FOU/releases/download/v2.5.0/FOU-v2.5-Windows.zip) | Launched successfully on my PC and on a second Windows laptop from the published download. **Unsigned**; some PCs may warn or block it. |
| Linux | [FOU-v2.5-Linux.tar.gz](https://github.com/FOU-SHREX/FOU/releases/download/v2.5.0/FOU-v2.5-Linux.tar.gz) | GitHub Actions build passed; Linux runtime testing still needed. |
| macOS | [FOU-v2.5-macOS.zip](https://github.com/FOU-SHREX/FOU/releases/download/v2.5.0/FOU-v2.5-macOS.zip) | GitHub Actions build passed; macOS runtime testing still needed. |

**Windows quick start:** Download the Windows ZIP, extract all files into one folder, then run `FOU.exe`. Keep `_internal` next to the EXE. You don't need to install Python. If you hit a first-time loading delay or Windows security warning, read [Before You Try FOU](#before-you-try-fou-v250) above. There isn't a Windows installer yet; this is a portable release.

### Run the desktop GUI with Python

This is the current path for developers and source-code testers. The v2.5 development environment uses Python **3.14.6**; a recent Python version supporting the project's syntax is recommended.

```powershell
# Run from the repository root in Windows PowerShell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install customtkinter pillow requests
.\.venv\Scripts\python.exe gui.py
```

On Linux/macOS, create and activate a virtual environment and use the equivalent `python3 -m pip install customtkinter pillow requests` / `python3 gui.py` commands. Linux users may need system Tk packages.

### Run the original CLI

```powershell
.\.venv\Scripts\python.exe main.py
```

The CLI uses a numbered terminal menu to add, view, remove, and save coins. It is still useful for understanding FOU's beginnings and testing the portfolio logic separately from the GUI.

### Beginner's quick start

In the **GUI**, type a symbol such as `BTC` into the entry field and click **+ Add Coin**. Once it appears in the Portfolio, try **Refresh**, switch between the three themes, and click **Save**. The companion responds to each operation. **Help** opens this README in your browser.

The CLI uses numbered menu options instead of GUI buttons. In that mode you can add multiple symbols, enter `DONE`, and select **View Portfolio** to display prices.

For example, the CLI can show data in a format like this (*illustrative values, not live quotes*):

```text
--------- PORTFOLIO --------
#    COIN     | PRICE
----------------------------
1.   BTC      | $81,000.00
2.   ETH      | $2,600.00
```

## How FOU works

```text
FOU GUI (gui.py) / FOU CLI (main.py)
             │
             ├── Local save_portfolio.json
             │
             └── HTTPS requests
                     │
                     ▼
                FOU backend
                     │
                     ▼
             CoinGecko market data
```

The desktop GUI imports portfolio logic from `main.py`. Market requests go through the hosted FOU backend rather than putting a private CoinGecko API credential into the desktop executable. The backend is intended to use caching and rate limiting to reduce unnecessary external requests.

**Your saved portfolio contains coin symbols and CoinGecko IDs—not purchased quantities, wallet keys, or assets.**

### Where saved portfolios live

- **Python source run:** `save_portfolio.json` in the project folder.
- **Packaged Windows application:** `%LOCALAPPDATA%\FOU\save_portfolio.json`.
- **Packaged Linux application:** `~/.local/share/FOU/save_portfolio.json` by default, or `$XDG_DATA_HOME/FOU/save_portfolio.json` when `XDG_DATA_HOME` is set.
- **Packaged macOS application:** `~/Library/Application Support/FOU/save_portfolio.json`.

Packaged builds use a user-writable data directory so that replacing the application files doesn't automatically remove your watchlist. An old portable release that saved beside the executable does **not** migrate automatically.

## Testing and reliability

I test both the **portfolio behavior** and the **interface behavior** because a pretty theme is not enough if the underlying app is unreliable.

### Portfolio regression checks

- Add multiple valid symbols; reject invalid and empty symbols.
- Attempt to add the same symbol twice and with different capitalization.
- Refresh and inspect price ordering, symbols, coin labels, and logos.
- Remove a coin and confirm it disappears without disturbing other rows.
- Save, close, reopen, and check persistence.
- Test malformed save structures (for example, a JSON list or an invalid/null coin ID) and recover without crashing.
- Check behavior when the backend cannot be reached.

### GUI and theme regression checks

- Switch **VOID → THE FOOL → FOU DEFAULT → VOID**.
- Verify correct companions, colors, fonts, frames, and button decoration for each theme.
- Resize and maximize/restore the window, checking panel alignment and readable rows.
- Test Add Coin, Refresh, Save, Help, and selection behavior.
- Confirm the current portfolio remains consistent while changing themes.

**v2.5.0 verification so far:** The three themes and companion reactions have been tested in the Python GUI. The Windows standalone EXE was also tested, including adding coins, tiny-price multipliers, and switching themes. I downloaded the published Windows ZIP onto another laptop and ran it successfully without a security warning. All three operating-system packaging jobs passed in GitHub Actions, but Linux and macOS still need actual runtime testing. The Windows app is unsigned, so a successful test on one device doesn't guarantee another device won't show a Windows security warning.

## What I learned

FOU became much bigger than my original plan. The biggest lessons weren't just about syntax—they came from trying to make something complete enough for other people to use.

| Area | What FOU taught me |
| --- | --- |
| **Python fundamentals** | Functions, loops, dictionaries, normalization, state, and breaking a big problem into small operations. |
| **JSON and local persistence** | Reading/writing data, checking structure, rejecting malformed inputs, and thinking about save paths. |
| **APIs and backends** | HTTP requests, timeouts, backend responsibilities, hosted services, caching, and keeping keys out of public desktop code. |
| **Error handling** | Distinguishing invalid symbols, duplicates, empty input, network failures, and corrupted files without crashing. |
| **GUI architecture** | Keeping backend logic separate from UI code and updating widgets in response to actions. |
| **Background work** | Threads and queues for network operations so the desktop interface stays responsive. |
| **Image processing** | Alpha masks, cropping, fit/contain behavior, tinting, compositing, and using PNG assets in Pillow. |
| **Responsive layout** | Pixel dimensions, UI scaling, alignment, widget geometry, and testing on different window sizes. |
| **Advanced frame rendering** | Splitting borders into regions, preserving ornaments, detecting visible rails, and coordinating artwork with content. |
| **User experience** | Making small choices—an × button, a clickable search icon, feedback animations, or a Help button—matter. |
| **Visual design** | Building three distinct, consistent identities rather than recoloring the same screen. |
| **Testing discipline** | Retesting old features after each design change and separating successful packaging from successful runtime behavior. |
| **Packaging and release engineering** | Virtual environments, PyInstaller specs, Windows binaries, Linux archives, GitHub, and signing/trust issues. |
| **Working with AI tools** | Explaining a problem clearly, reviewing generated solutions critically, testing the results, and knowing when to iterate. |

At first I was happy just to see a coin show up in the terminal. Now I'm thinking about whether the frames resize properly, whether saves work after reopening the EXE, and whether someone else can run the app. That shift has been one of the best parts of building FOU.

## AI tools and credits

I used AI as part of the **development process**, especially **ChatGPT** and **OpenAI Codex**, along with other AI image-generation tools.

- **ChatGPT:** Learning concepts, discussing features, troubleshooting Python errors, reviewing implementation ideas, preparing image prompts, planning the UI, and documenting the project.
- **Codex:** Assistance with code-level work, notably the difficult **THE FOOL Portfolio border** rendering and layout calculations.
- **AI image-generation tools:** Creating or refining theme artwork, companions, emotions, backgrounds, ornaments, logos, and icons.
- **My role:** Deciding the direction, giving feedback, comparing target and actual screenshots, modifying/integrating code, testing behavior, and choosing when a design was finished.

I'm mentioning the tools because they genuinely helped me learn and get past some difficult parts. But there was still a lot of going back into the app, seeing what looked wrong, changing things, and testing them again.

### Visual assets and licenses

FOU-controlled project artwork is documented in [`ASSET_LICENSES.md`](ASSET_LICENSES.md). The **New Rocker** typeface is distributed under the SIL Open Font License 1.1, with its text in [`assets/ui/void/OFL.txt`](assets/ui/void/OFL.txt). Third-party cryptocurrency symbols/logos retain their own owners' rights. AI-generated artwork is covered by the project's MIT grant only to the extent the creator controls licensable rights; redistribution also depends on the relevant generation services' terms.

## Limitations and roadmap

### Current limitations

- FOU is a watchlist, **not** a portfolio wallet or trading platform.
- Latest prices depend on internet access, the hosted backend, and third-party market-data availability.
- After inactivity, the free-hosted backend may need to wake up. The first coin or saved-portfolio price load can take **around 60 seconds**; later requests are usually faster.
- Saves are local to each device; FOU does not currently synchronize across devices.
- The published v2.5.0 Windows EXE has run successfully on two Windows laptops but is still **unsigned**. Windows SmartScreen or Smart App Control can warn or block users on other devices. I've submitted an application to **SignPath Foundation**; approval is not guaranteed.
- The v2.5 Linux and macOS GUI packages have been built successfully, but I haven't confirmed them running on real Linux or macOS machines yet.

### Future ideas (not released features)

- Price alerts and notifications.
- Telegram bot integration.
- More portfolio and market context.
- Additional planned themes such as Terminal, Frost, and Neon after they're complete and tested.
- More helpful tutorials and accessibility improvements.

## License and contributions

FOU's original source code is distributed under the [MIT License](LICENSE), subject to the separate rights and terms described in [ASSET_LICENSES.md](ASSET_LICENSES.md).

**Feedback is welcome.** If you find a bug, have a UI suggestion, or want to help improve the project, open an [issue](https://github.com/FOU-SHREX/FOU/issues). Include your operating system, what you expected, what happened, and a screenshot or steps to reproduce when possible.

**Repository:** https://github.com/FOU-SHREX/FOU  
**Creator:** FOU-SHREX  
**Version:** **2.5**

---

*It started with a few Python functions and a terminal menu. It took a lot of wrong turns to get here, but I learned something from most of them.*
