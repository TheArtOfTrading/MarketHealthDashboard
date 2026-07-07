## Download

Download the pre-compiled .exe file under [releases](https://github.com/TheArtOfTrading/MarketHealthDashboard/releases/tag/release) - make sure Norgate Data is running when you open this software.

# Macro Market Trading Dashboard - What is this?

A lightweight Python desktop dashboard for exploring market data, sector rotation, market health, global indices, and momentum rankings using Norgate Data.

<img width="384" height="205" alt="image" src="https://github.com/user-attachments/assets/e6333fe9-d84c-4101-9413-6cca0d3777f3" />

The app provides a simple GUI launcher for multiple Matplotlib-based dashboards, including:

* Market Health dashboard
* US sector dashboard
* ASX sector dashboard
* Global indices dashboard
* Momentum stock rankings

It is intended as a personal research and visualization tool for traders, investors, and developers who want to explore market behaviour using local Norgate Data.

## Features

* Interactive chart screens
* Market health views across multiple universes
* US and ASX sector rotation dashboards
* Global index performance dashboard
* Momentum stock ranking tools
* Keyboard and button navigation
* Packagable as a Windows `.exe` with PyInstaller

## Requirements

This project depends on:

* Python
* pandas
* matplotlib
* norgatedata
* tkinter
* Norgate Data installed and configured locally

## Norgate Data

You must have Norgate Data for this tool to function: https://norgatedata.com/stockmarketpackages.php

I use it with the following data plans. If you are missing a data plan then the tool will obviously not be able to load data for that market - any data plan tier will work with this tool as it only uses market data for currently listed assets and does not reference historical constituents:

* US Stocks
* Australian Stocks
* Canadian Stocks
* Forex
* I do not use Futures with this tool.

## Usage

Download the pre-compiled .exe file under [releases](https://github.com/TheArtOfTrading/MarketHealthDashboard/releases/tag/release) - make sure Norgate Data is running when you open this software.

Or run the main launcher script:

```bash
python trading_dashboard_app.py
```

Or package it into a Windows executable using PyInstaller / `build.bat`.

## Disclaimer

This software is provided for educational and research purposes only.

It is not financial advice, investment advice, trading advice, or a recommendation to buy or sell any financial product.

Use at your own risk. The author is not responsible for trading losses, software errors, incorrect data, data provider issues, or any other damages arising from use of this software.

## License

This project is released under the MIT License.

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the terms of the MIT License.

See the `LICENSE` file for full details.
