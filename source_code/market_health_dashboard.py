import pandas as pd
import matplotlib.pyplot as plt
import norgatedata
from matplotlib.widgets import Button
from matplotlib.patches import Patch
from matplotlib.backend_bases import MouseButton


START_DATE = "2000-01-01"

# Latest available EOD data is included by default.
# This script does not remove the current month because it is daily EOD-based.
PRICE_ADJUSTMENT = norgatedata.StockPriceAdjustmentType.NONE

DEFAULT_MODE = "1D"

MODE_OPTIONS = ["1D", "MTD", "1M", "3M", "6M", "12M", "YTD"]

MODE_LOOKBACK_DAYS = {
    "1D": 1,
    "1M": 21,
    "3M": 63,
    "6M": 126,
    "12M": 252,
}

MODE_LABELS = {
    "1D": "1-Day ROC",
    "MTD": "Month-to-Date",
    "1M": "1-Month (21D) ROC",
    "3M": "3-Month (63D) ROC",
    "6M": "6-Month (126D) ROC",
    "12M": "12-Month (252D) ROC",
    "YTD": "Year-to-Date",
}


GROUP_COLORS = {
    "Equity": "#1f77b4",
    "Growth": "#9467bd",
    "Small Caps": "#17becf",
    "Volatility": "#d62728",
    "Bonds": "#2ca02c",
    "Credit": "#ff7f0e",
    "Commodity": "#8c564b",
    "Currency": "#7f7f7f",
    "Sector": "#1f77b4",
    "Ratio": "#bcbd22",
    "Defensive": "#2ca02c",
    "Breadth": "#17becf",
    "Tech Breadth": "#9467bd",
    "ASX Breadth": "#ff7f0e",
    "Other": "#666666",
}


BREADTH_STATUS_COLORS = {
    "Strong": "#2ca02c",
    "Healthy": "#8bc34a",
    "Neutral": "#ffbf00",
    "Weak": "#ff7f0e",
    "Risk-off": "#d62728",
}


US_MACRO_MARKETS = {
    "VIX": {
        "candidates": ["$VIX", "VXX", "VIXY"],
        "group": "Volatility",
    },
    "S&P 500 Equal Weight": {
        "candidates": ["RSP"],
        "group": "Equity",
    },
    "S&P 500": {
        "candidates": ["$SPX", "SPY"],
        "group": "Equity",
    },
    "Nasdaq 100": {
        "candidates": ["$NDX", "QQQ"],
        "group": "Growth",
    },
    "Russell 1000": {
        "candidates": ["$RUI", "IWB"],
        "group": "Small Caps",
    },
    "Russell 2000": {
        "candidates": ["$RUT", "IWM"],
        "group": "Small Caps",
    },
    "20+ Year Treasuries": {
        "candidates": ["TLT"],
        "group": "Bonds",
    },
    "7-10 Year Treasuries": {
        "candidates": ["IEF"],
        "group": "Bonds",
    },
    "1-3 Year Treasuries": {
        "candidates": ["SHY"],
        "group": "Bonds",
    },
    "TIPS": {
        "candidates": ["TIP"],
        "group": "Bonds",
    },
    "Investment Grade Credit": {
        "candidates": ["LQD"],
        "group": "Credit",
    },
    "High Yield Credit": {
        "candidates": ["HYG", "JNK"],
        "group": "Credit",
    },
    "Gold": {
        "candidates": ["GLD"],
        "group": "Commodity",
    },
    "Oil": {
        "candidates": ["USO"],
        "group": "Commodity",
    },
    "Broad Commodities": {
        "candidates": ["DBC", "GSG"],
        "group": "Commodity",
    },
    "US Dollar": {
        "candidates": ["UUP"],
        "group": "Currency",
    },
}


ASX_MACRO_MARKETS = {
    "ASX 200 Volatility": {
        "candidates": ["$XVI.au"],
        "group": "Volatility",
    },
    "All Ordinaries": {
        "candidates": ["$XAO.au"],
        "group": "Equity",
    },
    "S&P/ASX 100": {
        "candidates": ["$XTO.au"],
        "group": "Equity",
    },
    "S&P/ASX 200": {
        "candidates": ["$XJO.au"],
        "group": "Equity",
    },
    "S&P/ASX 300": {
        "candidates": ["$XKO.au"],
        "group": "Equity",
    },
    "ASX Resources": {
        "candidates": ["$XJR.au"],
        "group": "Commodity",
    },
    "ASX Gold Stocks": {
        "candidates": ["$XGD.au"],
        "group": "Commodity",
    },
    "Physical Gold": {
        "candidates": ["GOLD.au", "QAU.au"],
        "group": "Commodity",
    },
    "Australian Govt Bonds": {
        "candidates": ["GOVT.au"],
        "group": "Bonds",
    },
    "Australian Fixed Interest": {
        "candidates": ["VAF.au", "IAF.au"],
        "group": "Bonds",
    },
    "Cash / Bank Bills": {
        "candidates": ["AAA.au", "BILL.au"],
        "group": "Defensive",
    },
    "S&P 500 AUD": {
        "candidates": ["$SPXAUD.au"],
        "group": "Equity",
    },
    "US Dollar ETF": {
        "candidates": ["USD.au"],
        "group": "Currency",
    },
}


US_SECTOR_MARKETS = {
    "Technology": {
        "candidates": ["XLK"],
        "group": "Sector",
    },
    "Communication Services": {
        "candidates": ["XLC"],
        "group": "Sector",
    },
    "Consumer Discretionary": {
        "candidates": ["XLY"],
        "group": "Sector",
    },
    "Consumer Staples": {
        "candidates": ["XLP"],
        "group": "Sector",
    },
    "Health Care": {
        "candidates": ["XLV"],
        "group": "Sector",
    },
    "Financials": {
        "candidates": ["XLF"],
        "group": "Sector",
    },
    "Industrials": {
        "candidates": ["XLI"],
        "group": "Sector",
    },
    "Energy": {
        "candidates": ["XLE"],
        "group": "Sector",
    },
    "Materials": {
        "candidates": ["XLB"],
        "group": "Sector",
    },
    "Real Estate": {
        "candidates": ["XLRE"],
        "group": "Sector",
    },
    "Utilities": {
        "candidates": ["XLU"],
        "group": "Sector",
    },
}


ASX_SECTOR_MARKETS = {
    "Communication Services": {
        "candidates": ["$XTJ.au"],
        "group": "Sector",
    },
    "Consumer Discretionary": {
        "candidates": ["$XDJ.au"],
        "group": "Sector",
    },
    "Consumer Staples": {
        "candidates": ["$XSJ.au"],
        "group": "Sector",
    },
    "Energy": {
        "candidates": ["$XEJ.au"],
        "group": "Sector",
    },
    "Financials": {
        "candidates": ["$XFJ.au"],
        "group": "Sector",
    },
    "Health Care": {
        "candidates": ["$XHJ.au"],
        "group": "Sector",
    },
    "Industrials": {
        "candidates": ["$XNJ.au"],
        "group": "Sector",
    },
    "Information Technology": {
        "candidates": ["$XIJ.au"],
        "group": "Sector",
    },
    "Materials": {
        "candidates": ["$XMJ.au"],
        "group": "Sector",
    },
    "Real Estate": {
        "candidates": ["$XRE.au"],
        "group": "Sector",
    },
    "Utilities": {
        "candidates": ["$XUJ.au"],
        "group": "Sector",
    },
}


US_RATIO_MARKETS = {
    "Stocks vs Long Bonds": {
        "numerator": ["$SPX", "SPY"],
        "denominator": ["TLT"],
        "group": "Ratio",
    },
    "Stocks vs Intermediate Bonds": {
        "numerator": ["$SPX", "SPY"],
        "denominator": ["IEF"],
        "group": "Ratio",
    },
    "High Yield vs Treasuries": {
        "numerator": ["HYG", "JNK"],
        "denominator": ["IEF"],
        "group": "Ratio",
    },
    "Credit vs Long Bonds": {
        "numerator": ["LQD"],
        "denominator": ["TLT"],
        "group": "Ratio",
    },
    "Small Caps vs S&P 500": {
        "numerator": ["IWM", "$RUT"],
        "denominator": ["SPY", "$SPX"],
        "group": "Ratio",
    },
    "Nasdaq vs S&P 500": {
        "numerator": ["QQQ", "$NDX"],
        "denominator": ["SPY", "$SPX"],
        "group": "Ratio",
    },
    "Equal Weight vs Cap Weight": {
        "numerator": ["RSP"],
        "denominator": ["SPY", "$SPX"],
        "group": "Ratio",
    },
    "Consumer Discretionary vs Staples": {
        "numerator": ["XLY"],
        "denominator": ["XLP"],
        "group": "Ratio",
    },
    "Gold vs Stocks": {
        "numerator": ["GLD"],
        "denominator": ["SPY", "$SPX"],
        "group": "Ratio",
    },
    "Commodities vs Stocks": {
        "numerator": ["DBC", "GSG"],
        "denominator": ["SPY", "$SPX"],
        "group": "Ratio",
    },
}


ASX_RATIO_MARKETS = {
    "ASX 200 vs AU Bonds": {
        "numerator": ["$XJO.au"],
        "denominator": ["VAF.au", "IAF.au"],
        "group": "Ratio",
    },
    "Resources vs Industrials": {
        "numerator": ["$XJR.au"],
        "denominator": ["$XJI.au", "$XNJ.au"],
        "group": "Ratio",
    },
    "Materials vs ASX 200": {
        "numerator": ["$XMJ.au"],
        "denominator": ["$XJO.au"],
        "group": "Ratio",
    },
    "Financials vs ASX 200": {
        "numerator": ["$XFJ.au"],
        "denominator": ["$XJO.au"],
        "group": "Ratio",
    },
    "Gold Stocks vs ASX 200": {
        "numerator": ["$XGD.au"],
        "denominator": ["$XJO.au"],
        "group": "Ratio",
    },
    "ASX 200 vs Cash": {
        "numerator": ["$XJO.au"],
        "denominator": ["AAA.au", "BILL.au"],
        "group": "Ratio",
    },
    "ASX 200 vs S&P 500 AUD": {
        "numerator": ["$XJO.au"],
        "denominator": ["$SPXAUD.au"],
        "group": "Ratio",
    },
}


BREADTH_MARKETS = {
    "NYSE Composite >200DMA": {
        "candidates": ["#NYA%MA200"],
        "group": "Breadth",
    },
    "Nasdaq Composite >200DMA": {
        "candidates": ["#COMP%MA200"],
        "group": "Tech Breadth",
    },
    "Nasdaq-100 >200DMA": {
        "candidates": ["#NDX%MA200"],
        "group": "Tech Breadth",
    },
    "S&P 500 >200DMA": {
        "candidates": ["#SPX%MA200"],
        "group": "Breadth",
    },
    "Russell 3000 >200DMA": {
        "candidates": ["#RUA%MA200"],
        "group": "Breadth",
    },
    "Russell 2000 >200DMA": {
        "candidates": ["#RUT%MA200"],
        "group": "Breadth",
    },
    "ASX All Ordinaries >200DMA": {
        "candidates": ["#XAO%MA200.au"],
        "group": "ASX Breadth",
    },
    "S&P/ASX 200 >200DMA": {
        "candidates": ["#XJO%MA200.au"],
        "group": "ASX Breadth",
    },
    "S&P/ASX 300 >200DMA": {
        "candidates": ["#XKO%MA200.au"],
        "group": "ASX Breadth",
    },
}


UNIVERSES = {
    "US Macro": {
        "type": "markets",
        "definitions": US_MACRO_MARKETS,
    },
    "ASX Macro": {
        "type": "markets",
        "definitions": ASX_MACRO_MARKETS,
    },
    "Market Breadth": {
        "type": "breadth",
        "definitions": BREADTH_MARKETS,
    },
    "US Sectors": {
        "type": "markets",
        "definitions": US_SECTOR_MARKETS,
    },
    "ASX Sectors": {
        "type": "markets",
        "definitions": ASX_SECTOR_MARKETS,
    },
    "US Ratios": {
        "type": "ratios",
        "definitions": US_RATIO_MARKETS,
    },
    "ASX Ratios": {
        "type": "ratios",
        "definitions": ASX_RATIO_MARKETS,
    },
}


UNIVERSE_BUTTON_LABELS = {
    "US Macro": "US Macro",
    "ASX Macro": "ASX Macro",
    "Market Breadth": "Breadth",
    "US Sectors": "US Sectors",
    "ASX Sectors": "ASX Sectors",
    "US Ratios": "US Ratios",
    "ASX Ratios": "ASX Ratios",
}


def get_daily_ohlc(symbol: str, label: str) -> pd.DataFrame:
    df = norgatedata.price_timeseries(
        symbol,
        start_date=START_DATE,
        stock_price_adjustment_setting=PRICE_ADJUSTMENT,
        padding_setting=norgatedata.PaddingType.NONE,
        timeseriesformat="pandas-dataframe",
    )

    if df is None or df.empty:
        raise ValueError(f"No data returned for {label} / {symbol}")

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
    else:
        df.index = pd.to_datetime(df.index)

    if "Close" not in df.columns:
        raise ValueError(f"No Close column found for {label} / {symbol}. Columns: {list(df.columns)}")

    # Some synthetic/index series may not have an Open column.
    # Fall back to Close so the dashboard still works.
    if "Open" not in df.columns:
        print(f"WARNING: No Open column for {label} / {symbol}; using Close as Open fallback.")
        df["Open"] = df["Close"]

    df = df[["Open", "Close"]].dropna()

    if df.empty:
        raise ValueError(f"OHLC data is empty for {label} / {symbol}")

    return df.sort_index()


def resolve_symbol_data(label: str, candidates: list[str], data_cache: dict) -> tuple[str, pd.DataFrame]:
    errors = []

    for symbol in candidates:
        if symbol in data_cache:
            return symbol, data_cache[symbol]

        try:
            df = get_daily_ohlc(symbol, label)
            data_cache[symbol] = df
            return symbol, df

        except Exception as e:
            errors.append(f"{symbol}: {e}")

    raise ValueError(
        f"Could not load data for {label}.\n"
        f"Tried: {candidates}\n"
        f"Errors:\n" + "\n".join(errors)
    )


def calculate_ytd_returns(open_df: pd.DataFrame, close_df: pd.DataFrame) -> pd.DataFrame:
    ytd = pd.DataFrame(index=close_df.index, columns=close_df.columns, dtype=float)

    years = sorted(set(close_df.index.year))

    for year in years:
        year_open = open_df.loc[open_df.index.year == year]
        year_close = close_df.loc[close_df.index.year == year]

        if year_open.empty or year_close.empty:
            continue

        base_open = pd.Series(index=open_df.columns, dtype=float)

        for col in open_df.columns:
            valid_opens = year_open[col].dropna()

            if not valid_opens.empty:
                base_open[col] = valid_opens.iloc[0]

        ytd.loc[year_close.index] = (year_close / base_open - 1) * 100

    return ytd


def calculate_mtd_returns(open_df: pd.DataFrame, close_df: pd.DataFrame) -> pd.DataFrame:
    mtd = pd.DataFrame(index=close_df.index, columns=close_df.columns, dtype=float)

    months = sorted(set(close_df.index.to_period("M")))

    for month in months:
        month_open = open_df.loc[open_df.index.to_period("M") == month]
        month_close = close_df.loc[close_df.index.to_period("M") == month]

        if month_open.empty or month_close.empty:
            continue

        base_open = pd.Series(index=open_df.columns, dtype=float)

        for col in open_df.columns:
            valid_opens = month_open[col].dropna()

            if not valid_opens.empty:
                base_open[col] = valid_opens.iloc[0]

        mtd.loc[month_close.index] = (month_close / base_open - 1) * 100

    return mtd


def calculate_metric_tables(open_df: pd.DataFrame, close_df: pd.DataFrame) -> dict:
    tables = {}

    for mode, lookback in MODE_LOOKBACK_DAYS.items():
        tables[mode] = close_df.pct_change(periods=lookback) * 100

    tables["MTD"] = calculate_mtd_returns(open_df, close_df)
    tables["YTD"] = calculate_ytd_returns(open_df, close_df)

    return tables


def classify_breadth_value(value: float) -> str:
    if pd.isna(value):
        return "Unknown"

    if value >= 70:
        return "Strong"

    if value >= 55:
        return "Healthy"

    if value >= 45:
        return "Neutral"

    if value >= 30:
        return "Weak"

    return "Risk-off"


def clean_breadth_series(series: pd.Series) -> pd.Series:
    series = series.dropna().copy()

    if series.empty:
        return series

    # Some data vendors store percentages as 0-1 fractions.
    # Norgate usually stores these breadth readings as 0-100,
    # but this keeps the chart safe either way.
    if series.max() <= 1.5:
        series = series * 100

    return series.clip(lower=0, upper=100)


def load_market_universe(universe_name: str, definitions: dict, data_cache: dict) -> dict:
    open_tables = {}
    close_tables = {}
    groups = {}
    symbol_map = {}
    skipped = []

    total = len(definitions)

    for i, (label, info) in enumerate(definitions.items(), start=1):
        candidates = info["candidates"]

        print(f"[{i}/{total}] Loading {universe_name}: {label}...")

        try:
            resolved_symbol, df = resolve_symbol_data(label, candidates, data_cache)

            open_tables[label] = df["Open"]
            close_tables[label] = df["Close"]
            groups[label] = info.get("group", "Other")
            symbol_map[label] = resolved_symbol

        except Exception as e:
            print(f"  SKIPPED: {label}")
            print(f"  Reason: {e}")
            skipped.append(label)

    if skipped:
        print(f"\nSkipped {len(skipped)} markets in {universe_name}:")
        for item in skipped:
            print(f"  - {item}")

    if not close_tables:
        raise ValueError(f"No data loaded for {universe_name}.")

    open_df = pd.DataFrame(open_tables).dropna(how="all").sort_index()
    close_df = pd.DataFrame(close_tables).dropna(how="all").sort_index()

    metric_tables = calculate_metric_tables(open_df, close_df)

    return {
        "universe_name": universe_name,
        "open": open_df,
        "close": close_df,
        "metric_tables": metric_tables,
        "groups": groups,
        "symbol_map": symbol_map,
        "skipped": skipped,
    }


def load_ratio_universe(universe_name: str, definitions: dict, data_cache: dict) -> dict:
    ratio_open_tables = {}
    ratio_close_tables = {}
    groups = {}
    symbol_map = {}
    skipped = []

    total = len(definitions)

    for i, (label, info) in enumerate(definitions.items(), start=1):
        print(f"[{i}/{total}] Loading {universe_name}: {label}...")

        try:
            numerator_symbol, numerator_df = resolve_symbol_data(f"{label} numerator", info["numerator"], data_cache)
            denominator_symbol, denominator_df = resolve_symbol_data(f"{label} denominator", info["denominator"], data_cache)

            numerator_open, denominator_open = numerator_df["Open"].align(denominator_df["Open"], join="outer")
            numerator_close, denominator_close = numerator_df["Close"].align(denominator_df["Close"], join="outer")

            ratio_open = numerator_open / denominator_open
            ratio_close = numerator_close / denominator_close

            ratio_open_tables[label] = ratio_open
            ratio_close_tables[label] = ratio_close
            groups[label] = info.get("group", "Ratio")
            symbol_map[label] = f"{numerator_symbol} / {denominator_symbol}"

        except Exception as e:
            print(f"  SKIPPED: {label}")
            print(f"  Reason: {e}")
            skipped.append(label)

    if skipped:
        print(f"\nSkipped {len(skipped)} ratios in {universe_name}:")
        for item in skipped:
            print(f"  - {item}")

    if not ratio_close_tables:
        raise ValueError(f"No ratio data loaded for {universe_name}.")

    open_df = pd.DataFrame(ratio_open_tables).dropna(how="all").sort_index()
    close_df = pd.DataFrame(ratio_close_tables).dropna(how="all").sort_index()

    metric_tables = calculate_metric_tables(open_df, close_df)

    return {
        "universe_name": universe_name,
        "open": open_df,
        "close": close_df,
        "metric_tables": metric_tables,
        "groups": groups,
        "symbol_map": symbol_map,
        "skipped": skipped,
    }


def load_breadth_universe(universe_name: str, definitions: dict, data_cache: dict) -> dict:
    close_tables = {}
    groups = {}
    symbol_map = {}
    skipped = []

    total = len(definitions)

    for i, (label, info) in enumerate(definitions.items(), start=1):
        candidates = info["candidates"]

        print(f"[{i}/{total}] Loading {universe_name}: {label}...")

        try:
            resolved_symbol, df = resolve_symbol_data(label, candidates, data_cache)

            breadth_series = clean_breadth_series(df["Close"])

            if breadth_series.empty:
                raise ValueError(f"No usable breadth values found for {label}")

            close_tables[label] = breadth_series
            groups[label] = info.get("group", "Breadth")
            symbol_map[label] = resolved_symbol

        except Exception as e:
            print(f"  SKIPPED: {label}")
            print(f"  Reason: {e}")
            skipped.append(label)

    if skipped:
        print(f"\nSkipped {len(skipped)} breadth indicators in {universe_name}:")
        for item in skipped:
            print(f"  - {item}")

    if not close_tables:
        raise ValueError(f"No breadth data loaded for {universe_name}.")

    close_df = pd.DataFrame(close_tables).dropna(how="all").sort_index()

    return {
        "type": "breadth",
        "universe_name": universe_name,
        "close": close_df,
        "metric_tables": {
            "Breadth": close_df,
        },
        "groups": groups,
        "symbol_map": symbol_map,
        "skipped": skipped,
    }


class MarketHealthDashboardViewer:
    def __init__(self):
        self.universe_names = list(UNIVERSES.keys())
        self.universe_position = 0

        self.mode = DEFAULT_MODE if DEFAULT_MODE in MODE_OPTIONS else "1M"
        self.sort_by_gain = False

        self.data_cache = {}
        self.universe_cache = {}

        self.metric_table = None
        self.groups = {}
        self.symbol_map = {}
        self.dates = []
        self.date_index = 0
        self.static_order = []

        self.last_click_time = 0

        self.fig, self.ax = plt.subplots(figsize=(14, 9))

        self.fig.subplots_adjust(
            left=0.31,
            right=0.96,
            bottom=0.16,
            top=0.89,
        )

        prev_ax = self.fig.add_axes([0.12, 0.045, 0.12, 0.05])
        mode_ax = self.fig.add_axes([0.28, 0.045, 0.13, 0.05])
        universe_ax = self.fig.add_axes([0.45, 0.045, 0.18, 0.05])
        sort_ax = self.fig.add_axes([0.67, 0.045, 0.12, 0.05])
        next_ax = self.fig.add_axes([0.83, 0.045, 0.12, 0.05])

        self.prev_button = Button(prev_ax, "Previous")
        self.mode_button = Button(mode_ax, f"Mode: {self.mode}")
        self.universe_button = Button(universe_ax, self.get_universe_button_text())
        self.sort_button = Button(sort_ax, "Sort: On")
        self.next_button = Button(next_ax, "Next")

        self.prev_button.on_clicked(self.previous_date)
        self.universe_button.on_clicked(self.cycle_universe_button)
        self.sort_button.on_clicked(self.toggle_sort)
        self.next_button.on_clicked(self.next_date)

        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)

        self.load_current_universe()
        self.draw()

    def is_double_click_event(self):
        now = pd.Timestamp.now().timestamp()

        if now - self.last_click_time < 0.25:
            return True

        self.last_click_time = now
        return False

    def get_current_universe_name(self) -> str:
        return self.universe_names[self.universe_position]

    def get_universe_button_text(self) -> str:
        universe_name = self.get_current_universe_name()
        return UNIVERSE_BUTTON_LABELS.get(universe_name, universe_name)

    def get_current_universe_data(self) -> dict:
        universe_name = self.get_current_universe_name()

        if universe_name in self.universe_cache:
            return self.universe_cache[universe_name]

        config = UNIVERSES[universe_name]

        print(f"\nLoading universe: {universe_name}\n")

        if config["type"] == "ratios":
            data = load_ratio_universe(universe_name, config["definitions"], self.data_cache)

        elif config["type"] == "breadth":
            data = load_breadth_universe(universe_name, config["definitions"], self.data_cache)

        else:
            data = load_market_universe(universe_name, config["definitions"], self.data_cache)

        self.universe_cache[universe_name] = data

        return data

    def load_current_universe(self, preserve_date: pd.Timestamp | None = None):
        data = self.get_current_universe_data()

        self.groups = data["groups"]
        self.symbol_map = data["symbol_map"]
        self.static_order = list(data["close"].columns)

        if data.get("type") == "breadth":
            self.metric_table = data["metric_tables"]["Breadth"].dropna(how="all").sort_index()
        else:
            if self.mode not in data["metric_tables"]:
                self.mode = "1M"

            self.metric_table = data["metric_tables"][self.mode].dropna(how="all").sort_index()

        self.dates = list(self.metric_table.index)

        if not self.dates:
            raise ValueError(f"No data available for {self.get_current_universe_name()}.")

        if preserve_date is None:
            self.date_index = len(self.dates) - 1
            return

        if preserve_date in self.dates:
            self.date_index = self.dates.index(preserve_date)
            return

        earlier_dates = [date for date in self.dates if date <= preserve_date]

        if earlier_dates:
            nearest_date = earlier_dates[-1]
            self.date_index = self.dates.index(nearest_date)
        else:
            self.date_index = len(self.dates) - 1

    def get_current_date(self) -> pd.Timestamp:
        return self.dates[self.date_index]

    def draw_breadth(self, data: dict):
        universe_name = self.get_current_universe_name()
        current_date = self.get_current_date()

        values = self.metric_table.loc[current_date].dropna()

        if values.empty:
            self.ax.set_title(f"No breadth data available on {current_date:%d %b %Y}")
            self.fig.canvas.draw_idle()
            return

        if self.sort_by_gain:
            values = values.sort_values(ascending=False)
        else:
            values = values.reindex([name for name in self.static_order if name in values.index])

        statuses = {
            name: classify_breadth_value(value)
            for name, value in values.items()
        }

        colors = [
            BREADTH_STATUS_COLORS.get(statuses[name], GROUP_COLORS["Other"])
            for name in values.index
        ]

        labels = []

        for name in values.index:
            symbol = self.symbol_map.get(name, "")
            labels.append(f"{name} ({symbol})" if symbol else name)

        bars = self.ax.barh(labels, values.values, color=colors)

        self.ax.invert_yaxis()
        self.ax.set_xlim(0, 100)

        # Human-readable zones.
        self.ax.axvline(30, color="black", linewidth=1, alpha=0.35)
        self.ax.axvline(50, color="black", linewidth=1, alpha=0.35)
        self.ax.axvline(70, color="black", linewidth=1, alpha=0.35)

        self.ax.text(30, -0.55, "Weak <30", ha="center", va="bottom", fontsize=8)
        self.ax.text(50, -0.55, "Neutral 45-55", ha="center", va="bottom", fontsize=8)
        self.ax.text(70, -0.55, "Strong >70", ha="center", va="bottom", fontsize=8)

        self.ax.set_title(
            f"Market Breadth - % of Stocks Above 200-Day Moving Average\n"
            f"Latest selected EOD: {current_date:%d %b %Y}"
        )

        self.ax.set_xlabel("% of stocks above 200-day moving average")
        self.ax.tick_params(axis="y", labelsize=8)
        self.ax.tick_params(axis="x", labelsize=9)

        for bar, value, name in zip(bars, values.values, values.index):
            status = statuses[name]
            label_x = min(value + 1.5, 98)

            self.ax.text(
                label_x,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.0f}% • {status}",
                va="center",
                ha="left" if value < 92 else "right",
                fontsize=8,
            )

        legend_order = ["Strong", "Healthy", "Neutral", "Weak", "Risk-off"]

        legend_items = [
            Patch(facecolor=BREADTH_STATUS_COLORS[status], label=status)
            for status in legend_order
        ]

        self.ax.legend(
            handles=legend_items,
            loc="lower right",
            fontsize=8,
            frameon=True,
        )

        self.ax.grid(axis="x", alpha=0.25)

        self.mode_button.label.set_text("Mode: Breadth")
        self.universe_button.label.set_text(self.get_universe_button_text())
        self.sort_button.label.set_text("Sort: On" if self.sort_by_gain else "Sort: Off")

        print(f"Showing: {universe_name} | Breadth | {current_date:%Y-%m-%d}")

        self.fig.canvas.draw_idle()

    def draw(self):
        self.ax.clear()

        universe_name = self.get_current_universe_name()
        current_date = self.get_current_date()
        data = self.get_current_universe_data()

        if data.get("type") == "breadth":
            self.draw_breadth(data)
            return

        values = self.metric_table.loc[current_date].dropna()

        if values.empty:
            self.ax.set_title(f"No data available for {universe_name} on {current_date:%d %b %Y}")
            self.fig.canvas.draw_idle()
            return

        if self.sort_by_gain:
            values = values.sort_values(ascending=False)
        else:
            values = values.reindex([name for name in self.static_order if name in values.index])

        colors = [
            GROUP_COLORS.get(self.groups.get(name, "Other"), GROUP_COLORS["Other"])
            for name in values.index
        ]

        labels = []

        for name in values.index:
            symbol = self.symbol_map.get(name, "")
            labels.append(f"{name} ({symbol})" if symbol else name)

        bars = self.ax.barh(labels, values.values, color=colors)

        self.ax.invert_yaxis()
        self.ax.axvline(0, color="black", linewidth=1)

        if self.mode == "MTD":
            title = (
                f"Market Health - {universe_name} - Month-to-Date\n"
                f"Current month first trading-day open to {current_date:%d %b %Y} EOD close"
            )
            x_label = "Month-to-date return %"

        elif self.mode == "YTD":
            title = (
                f"Market Health - {universe_name} - YTD\n"
                f"January {current_date.year} first trading-day open to {current_date:%d %b %Y} EOD close"
            )
            x_label = "YTD return %"

        else:
            lookback = MODE_LOOKBACK_DAYS[self.mode]
            title = (
                f"Market Health - {universe_name} - {MODE_LABELS[self.mode]}\n"
                f"As of latest selected EOD: {current_date:%d %b %Y} | ROC(Close, {lookback})"
            )
            x_label = f"{MODE_LABELS[self.mode]} %"

        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.tick_params(axis="y", labelsize=8)
        self.ax.tick_params(axis="x", labelsize=9)

        min_x = min(0, values.min())
        max_x = max(0, values.max())
        max_abs = max(abs(min_x), abs(max_x))
        padding = max_abs * 0.18 if max_abs > 0 else 1

        self.ax.set_xlim(min_x - padding, max_x + padding)

        x_min, x_max = self.ax.get_xlim()
        offset = (x_max - x_min) * 0.008

        for bar, value in zip(bars, values.values):
            x = bar.get_width()
            label_x = x + offset if value >= 0 else x - offset

            self.ax.text(
                label_x,
                bar.get_y() + bar.get_height() / 2,
                f"{value:+.1f}%",
                va="center",
                ha="left" if value >= 0 else "right",
                fontsize=8,
            )

        legend_groups = []

        for name in values.index:
            group = self.groups.get(name, "Other")

            if group not in legend_groups:
                legend_groups.append(group)

        legend_items = [
            Patch(facecolor=GROUP_COLORS.get(group, GROUP_COLORS["Other"]), label=group)
            for group in legend_groups
        ]

        self.ax.legend(
            handles=legend_items,
            loc="lower right",
            fontsize=8,
            frameon=True,
        )

        self.ax.grid(axis="x", alpha=0.25)

        self.mode_button.label.set_text(f"Mode: {self.mode}")
        self.universe_button.label.set_text(self.get_universe_button_text())
        self.sort_button.label.set_text("Sort: On" if self.sort_by_gain else "Sort: Off")

        print(f"Showing: {universe_name} | {self.mode} | {current_date:%Y-%m-%d}")

        self.fig.canvas.draw_idle()

    def previous_date(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        if self.date_index > 0:
            self.date_index -= 1
            self.draw()

    def next_date(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        if self.date_index < len(self.dates) - 1:
            self.date_index += 1
            self.draw()

    def cycle_mode(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        data = self.get_current_universe_data()

        # Breadth uses raw % above 200DMA readings.
        # It does not use ROC/YTD modes.
        if data.get("type") == "breadth":
            return

        current_date = self.get_current_date()

        current_pos = MODE_OPTIONS.index(self.mode)
        self.mode = MODE_OPTIONS[(current_pos + 1) % len(MODE_OPTIONS)]

        self.load_current_universe(preserve_date=current_date)
        self.draw()

    def set_mode(self, mode: str):
        if mode not in MODE_OPTIONS:
            return

        data = self.get_current_universe_data()

        # Breadth uses raw % above 200DMA readings.
        # Ignore numeric return-mode shortcuts while viewing breadth.
        if data.get("type") == "breadth":
            return

        current_date = self.get_current_date()

        self.mode = mode

        self.load_current_universe(preserve_date=current_date)
        self.draw()

    def next_universe(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        current_date = self.get_current_date()

        self.universe_position = (self.universe_position + 1) % len(self.universe_names)

        self.load_current_universe(preserve_date=current_date)
        self.draw()

    def previous_universe(self):
        current_date = self.get_current_date()

        self.universe_position = (self.universe_position - 1) % len(self.universe_names)

        self.load_current_universe(preserve_date=current_date)
        self.draw()

    def cycle_universe_button(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        current_date = self.get_current_date()

        button = getattr(event, "button", None)
        is_right_click = button == MouseButton.RIGHT or button == 3

        if is_right_click:
            self.universe_position = (self.universe_position - 1) % len(self.universe_names)
        else:
            self.universe_position = (self.universe_position + 1) % len(self.universe_names)

        self.load_current_universe(preserve_date=current_date)
        self.draw()

    def toggle_sort(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        self.sort_by_gain = not self.sort_by_gain
        self.draw()

    def on_key_press(self, event):
        if event.key in ["left", "down"]:
            self.previous_date()

        elif event.key in ["right", "up"]:
            self.next_date()

        elif event.key == "m":
            self.cycle_mode()

        elif event.key == "u":
            self.next_universe()

        elif event.key == "shift+u":
            self.previous_universe()

        elif event.key == "s":
            self.toggle_sort()

        elif event.key == "1":
            self.set_mode("1D")

        elif event.key == "t":
            self.set_mode("MTD")

        elif event.key == "2":
            self.set_mode("1M")

        elif event.key == "3":
            self.set_mode("3M")

        elif event.key == "4":
            self.set_mode("6M")

        elif event.key == "5":
            self.set_mode("12M")

        elif event.key == "y":
            self.set_mode("YTD")


def plot_market_health_dashboard():
    viewer = MarketHealthDashboardViewer()
    plt.show()
    return viewer


if __name__ == "__main__":
    viewer = plot_market_health_dashboard()