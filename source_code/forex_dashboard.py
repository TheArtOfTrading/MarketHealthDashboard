import pandas as pd
import matplotlib.pyplot as plt
import norgatedata
from matplotlib.widgets import Button, CheckButtons
from matplotlib.patches import Patch


START_DATE = "2000-01-01"

# Missing data policy:
# "omit" = skip unavailable symbols completely. Recommended.
# "blank" = keep unavailable columns as NaN where possible.
# "zero" = fill missing calculated returns with 0.0 where possible.
MISSING_DATA_POLICY = "omit"

# Forex spot rates are usually best viewed as raw spot-price movement.
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


# Each row is displayed as that currency's performance versus USD.
# Example:
# - AUDUSD directly measures AUD versus USD.
# - USDJPY measures USD versus JPY, so it is inverted if used as a fallback.
FOREX_USD_MARKETS = {
    "Australian Dollar": {
        "code": "AUD",
        "group": "Major",
        "candidates": [("AUDUSD", False), ("USDAUD", True)],
    },
    "Brazilian Real": {
        "code": "BRL",
        "group": "Emerging",
        "candidates": [("BRLUSD", False), ("USDBRL", True)],
    },
    "Canadian Dollar": {
        "code": "CAD",
        "group": "Major",
        "candidates": [("CADUSD", False), ("USDCAD", True)],
    },
    "Swiss Franc": {
        "code": "CHF",
        "group": "Major",
        "candidates": [("CHFUSD", False), ("USDCHF", True)],
    },
    "Chilean Peso": {
        "code": "CLP",
        "group": "Emerging",
        "candidates": [("CLPUSD", False), ("USDCLP", True)],
    },
    "Chinese Yuan": {
        "code": "CNY",
        "group": "Emerging",
        "candidates": [("CNYUSD", False), ("USDCNY", True)],
    },
    "Czech Koruna": {
        "code": "CZK",
        "group": "Europe",
        "candidates": [("CZKUSD", False), ("USDCZK", True)],
    },
    "Danish Krone": {
        "code": "DKK",
        "group": "Europe",
        "candidates": [("DKKUSD", False), ("USDDKK", True)],
    },
    "Euro": {
        "code": "EUR",
        "group": "Major",
        "candidates": [("EURUSD", False), ("USDEUR", True)],
    },
    "British Pound": {
        "code": "GBP",
        "group": "Major",
        "candidates": [("GBPUSD", False), ("USDGBP", True)],
    },
    "Hong Kong Dollar": {
        "code": "HKD",
        "group": "Asia",
        "candidates": [("HKDUSD", False), ("USDHKD", True)],
    },
    "Hungarian Forint": {
        "code": "HUF",
        "group": "Europe",
        "candidates": [("HUFUSD", False), ("USDHUF", True)],
    },
    "Israeli Shekel": {
        "code": "ILS",
        "group": "Other",
        "candidates": [("ILSUSD", False), ("USDILS", True)],
    },
    "Indian Rupee": {
        "code": "INR",
        "group": "Emerging",
        "candidates": [("INRUSD", False), ("USDINR", True)],
    },
    "Japanese Yen": {
        "code": "JPY",
        "group": "Major",
        "candidates": [("JPYUSD", False), ("USDJPY", True)],
    },
    "South Korean Won": {
        "code": "KRW",
        "group": "Asia",
        "candidates": [("KRWUSD", False), ("USDKRW", True)],
    },
    "Mexican Peso": {
        "code": "MXN",
        "group": "Emerging",
        "candidates": [("MXNUSD", False), ("USDMXN", True)],
    },
    "Malaysian Ringgit": {
        "code": "MYR",
        "group": "Asia",
        "candidates": [("MYRUSD", False), ("USDMYR", True)],
    },
    "Norwegian Krone": {
        "code": "NOK",
        "group": "Europe",
        "candidates": [("NOKUSD", False), ("USDNOK", True)],
    },
    "New Zealand Dollar": {
        "code": "NZD",
        "group": "Major",
        "candidates": [("NZDUSD", False), ("USDNZD", True)],
    },
    "Polish Zloty": {
        "code": "PLN",
        "group": "Europe",
        "candidates": [("PLNUSD", False), ("USDPLN", True)],
    },
    "Russian Ruble": {
        "code": "RUB",
        "group": "Emerging",
        "candidates": [("RUBUSD", False), ("USDRUB", True)],
    },
    "Swedish Krona": {
        "code": "SEK",
        "group": "Europe",
        "candidates": [("SEKUSD", False), ("USDSEK", True)],
    },
    "Singapore Dollar": {
        "code": "SGD",
        "group": "Asia",
        "candidates": [("SGDUSD", False), ("USDSGD", True)],
    },
    "Turkish Lira": {
        "code": "TRY",
        "group": "Emerging",
        "candidates": [("TRYUSD", False), ("USDTRY", True)],
    },
    "Taiwan Dollar": {
        "code": "TWD",
        "group": "Asia",
        "candidates": [("TWDUSD", False), ("USDTWD", True)],
    },
    "South African Rand": {
        "code": "ZAR",
        "group": "Emerging",
        "candidates": [("ZARUSD", False), ("USDZAR", True)],
    },
    "Zimbabwean Dollar": {
        "code": "ZWL",
        "group": "Other",
        "candidates": [("ZWLUSD", False), ("USDZWL", True)],
    },
    "Bitcoin": {
        "code": "BTC",
        "group": "Crypto",
        "candidates": [("BTCUSD", False), ("USDBTC", True)],
    },
    "Ethereum": {
        "code": "ETH",
        "group": "Crypto",
        "candidates": [("ETHUSD", False), ("USDETH", True)],
    },
}


GROUP_COLORS = {
    "Major": "#ff9f1c",
    "Europe": "#ff9f1c",
    "Asia": "#ff9f1c",
    "Emerging": "#000000",
    "Other": "#666666",
    "Crypto": "#ffe300",
}


class LoadingProgressWindow:
    def __init__(self, title: str):
        self.fig, self.ax = plt.subplots(figsize=(8.5, 2.4))

        try:
            self.fig.canvas.manager.set_window_title(title)
        except Exception:
            pass

        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 1)
        self.ax.axis("off")

        self.title_text = self.ax.text(0, 0.86, title, fontsize=12, fontweight="bold", va="center", ha="left")
        self.status_text = self.ax.text(0, 0.62, "Preparing...", fontsize=10, va="center", ha="left")
        self.percent_text = self.ax.text(100, 0.62, "0.0%", fontsize=10, va="center", ha="right")
        self.skipped_text = self.ax.text(0, 0.12, "", fontsize=8, va="center", ha="left")

        self.bar_background = plt.Rectangle((0, 0.34), 100, 0.14, linewidth=0.8, edgecolor="black", facecolor="lightgray")
        self.bar = plt.Rectangle((0, 0.34), 0, 0.14, linewidth=0, facecolor="steelblue")

        self.ax.add_patch(self.bar_background)
        self.ax.add_patch(self.bar)

        plt.show(block=False)
        plt.pause(0.001)

    def update(self, current: int, total: int, label: str, skipped_count: int = 0):
        percent = (current / total) * 100 if total > 0 else 0

        self.status_text.set_text(f"[{current}/{total}] Loading {label}...")
        self.percent_text.set_text(f"{percent:.1f}%")
        self.skipped_text.set_text(f"Skipped: {skipped_count}" if skipped_count > 0 else "")
        self.bar.set_width(percent)

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(0.001)

    def finish(self, message: str = "Done"):
        self.status_text.set_text(message)
        self.percent_text.set_text("100.0%")
        self.bar.set_width(100)

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(0.15)

    def close(self):
        plt.close(self.fig)
        plt.pause(0.001)


def get_daily_ohlc(symbol: str, label: str) -> pd.DataFrame:
    df = norgatedata.price_timeseries(
        symbol,
        start_date=START_DATE,
        stock_price_adjustment_setting=PRICE_ADJUSTMENT,
        padding_setting=norgatedata.PaddingType.NONE,
        timeseriesformat="pandas-dataframe",
    )

    if df is None or df.empty:
        raise ValueError(
            f"No data returned for {label} / {symbol}. "
            f"This symbol may be unavailable, or the required Norgate data package may not be installed."
        )

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
    else:
        df.index = pd.to_datetime(df.index)

    if "Close" not in df.columns:
        raise ValueError(f"No Close column found for {label} / {symbol}. Columns: {list(df.columns)}")

    if "Open" not in df.columns:
        print(f"WARNING: No Open column for {label} / {symbol}; using Close as Open fallback.")
        df["Open"] = df["Close"]

    df = df[["Open", "Close"]].dropna()

    if df.empty:
        raise ValueError(
            f"OHLC data is empty for {label} / {symbol}. "
            f"This symbol may be unavailable in the user's Norgate subscription."
        )

    return df.sort_index()


def invert_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    inverted = pd.DataFrame(index=df.index)
    inverted["Open"] = 1.0 / df["Open"]
    inverted["Close"] = 1.0 / df["Close"]
    return inverted.replace([float("inf"), float("-inf")], pd.NA).dropna()


def resolve_currency_data(label: str, candidates: list[tuple[str, bool]], data_cache: dict) -> tuple[str, pd.DataFrame]:
    errors = []

    for symbol, invert in candidates:
        cache_key = f"{symbol}|invert={invert}"

        if cache_key in data_cache:
            return symbol, data_cache[cache_key]

        try:
            raw_df = get_daily_ohlc(symbol, label)
            df = invert_ohlc(raw_df) if invert else raw_df
            data_cache[cache_key] = df

            if invert:
                print(f"Resolved {label} as inverse of {symbol}")
            else:
                print(f"Resolved {label} as {symbol}")

            return symbol, df

        except Exception as e:
            errors.append(f"{symbol}: {e}")

    raise ValueError(
        f"Could not load data for {label}.\n"
        f"Tried: {[symbol for symbol, invert in candidates]}\n"
        f"Errors:\n" + "\n".join(errors)
    )


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


def apply_missing_data_policy(df: pd.DataFrame, expected_columns: list[str] | None = None) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.sort_index()

    if expected_columns is not None and MISSING_DATA_POLICY in ["blank", "zero"]:
        df = df.reindex(columns=expected_columns)

    if MISSING_DATA_POLICY == "zero":
        return df.fillna(0.0).dropna(how="all")

    if MISSING_DATA_POLICY == "blank":
        return df.dropna(how="all")

    return df.dropna(axis=1, how="all").dropna(how="all")


def calculate_metric_tables(open_df: pd.DataFrame, close_df: pd.DataFrame) -> dict:
    tables = {}

    for mode, lookback in MODE_LOOKBACK_DAYS.items():
        tables[mode] = close_df.pct_change(periods=lookback) * 100

    tables["MTD"] = calculate_mtd_returns(open_df, close_df)
    tables["YTD"] = calculate_ytd_returns(open_df, close_df)

    expected_columns = list(close_df.columns)

    return {
        mode: apply_missing_data_policy(table, expected_columns)
        for mode, table in tables.items()
    }


def load_forex_data() -> dict:
    open_tables = {}
    close_tables = {}
    groups = {}
    symbol_map = {}
    skipped = []
    data_cache = {}

    total = len(FOREX_USD_MARKETS)
    loading_window = LoadingProgressWindow("Loading Forex USD pairs")

    try:
        for i, (label, info) in enumerate(FOREX_USD_MARKETS.items(), start=1):
            print(f"[{i}/{total}] Loading Forex: {label}...")
            loading_window.update(i, total, label, skipped_count=len(skipped))

            try:
                resolved_symbol, df = resolve_currency_data(label, info["candidates"], data_cache)

                open_tables[label] = df["Open"]
                close_tables[label] = df["Close"]
                groups[label] = info.get("group", "Other")
                symbol_map[label] = resolved_symbol

            except Exception as e:
                print(f"  SKIPPED: {label}")
                print(f"  Reason: {e}")
                skipped.append(label)

        loading_window.finish("Finished loading Forex USD pairs")

    finally:
        loading_window.close()

    if skipped:
        print(f"\nSkipped {len(skipped)} Forex pairs:")
        for item in skipped:
            print(f"  - {item}")

    if not close_tables:
        raise ValueError("No Forex USD data was loaded. Check the symbols and your Norgate data package.")

    open_df = pd.DataFrame(open_tables).dropna(how="all").sort_index()
    close_df = pd.DataFrame(close_tables).dropna(how="all").sort_index()

    metric_tables = calculate_metric_tables(open_df, close_df)

    return {
        "open": open_df,
        "close": close_df,
        "metric_tables": metric_tables,
        "groups": groups,
        "symbol_map": symbol_map,
        "skipped": skipped,
    }


class ForexDashboardViewer:
    def __init__(self):
        self.mode = DEFAULT_MODE if DEFAULT_MODE in MODE_OPTIONS else "1D"
        self.sort_by_gain = True
        self.include_crypto = True

        self.data = load_forex_data()
        self.metric_table = None
        self.dates = []
        self.date_index = 0
        self.static_order = list(self.data["close"].columns)
        self.groups = self.data["groups"]
        self.symbol_map = self.data["symbol_map"]

        self.last_click_time = 0

        self.fig, self.ax = plt.subplots(figsize=(14, 10))

        try:
            self.fig.canvas.manager.set_window_title("Forex Dashboard")
        except Exception:
            pass

        self.fig.patch.set_facecolor("white")
        self.ax.set_facecolor("white")

        self.fig.subplots_adjust(
            left=0.30,
            right=0.96,
            bottom=0.16,
            top=0.86,
        )

        prev_ax = self.fig.add_axes([0.12, 0.045, 0.12, 0.05])
        mode_ax = self.fig.add_axes([0.28, 0.045, 0.16, 0.05])
        sort_ax = self.fig.add_axes([0.48, 0.045, 0.14, 0.05])
        next_ax = self.fig.add_axes([0.66, 0.045, 0.12, 0.05])
        crypto_ax = self.fig.add_axes([0.015, 0.935, 0.12, 0.045])

        self.prev_button = Button(prev_ax, "Previous")
        self.mode_button = Button(mode_ax, f"Mode: {self.mode}")
        self.sort_button = Button(sort_ax, "Sort: On")
        self.next_button = Button(next_ax, "Next")
        self.crypto_checkbox = CheckButtons(crypto_ax, ["Crypto"], [self.include_crypto])

        self.prev_button.on_clicked(self.previous_date)
        self.mode_button.on_clicked(self.cycle_mode)
        self.sort_button.on_clicked(self.toggle_sort)
        self.next_button.on_clicked(self.next_date)
        self.crypto_checkbox.on_clicked(self.toggle_crypto)

        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)

        self.load_current_mode()
        self.draw()

    def is_double_click_event(self):
        now = pd.Timestamp.now().timestamp()

        if now - self.last_click_time < 0.25:
            return True

        self.last_click_time = now
        return False

    def load_current_mode(self, preserve_date: pd.Timestamp | None = None):
        self.metric_table = self.data["metric_tables"][self.mode].dropna(how="all").sort_index()
        self.dates = list(self.metric_table.index)

        if not self.dates:
            raise ValueError(f"No Forex data available for {self.mode}.")

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

    def get_title_and_xlabel(self, current_date: pd.Timestamp) -> tuple[str, str]:
        if self.mode == "MTD":
            title = (
                "World Currencies vs U.S. Dollar - Month-to-Date\n"
                f"Current month first trading-day open to {current_date:%d %b %Y} EOD close"
            )
            x_label = "MTD spot return vs USD %"

        elif self.mode == "YTD":
            title = (
                "World Currencies vs U.S. Dollar - Year-to-Date\n"
                f"January {current_date.year} first trading-day open to {current_date:%d %b %Y} EOD close"
            )
            x_label = "YTD spot return vs USD %"

        else:
            lookback = MODE_LOOKBACK_DAYS[self.mode]
            title = (
                f"World Currencies vs U.S. Dollar - {MODE_LABELS[self.mode]}\n"
                f"As of latest selected EOD: {current_date:%d %b %Y} | ROC(Close, {lookback})"
            )
            x_label = f"Spot return vs USD %"

        return title, x_label

    def filter_crypto_values(self, values: pd.Series) -> pd.Series:
        if self.include_crypto:
            return values

        return values[
            [
                name for name in values.index
                if self.groups.get(name, "Other") != "Crypto"
            ]
        ]

    def toggle_crypto(self, label=None):
        self.include_crypto = not self.include_crypto
        self.draw()

    def draw(self):
        self.ax.clear()
        self.ax.set_facecolor("white")

        current_date = self.get_current_date()
        values = self.metric_table.loc[current_date].dropna()
        values = self.filter_crypto_values(values)

        if values.empty:
            self.ax.set_title(f"No non-crypto Forex data available on {current_date:%d %b %Y}")
            self.fig.canvas.draw_idle()
            return

        if self.sort_by_gain:
            values = values.sort_values(ascending=False)
        else:
            values = values.reindex([name for name in self.static_order if name in values.index])

        labels = []
        colors = []

        for name in values.index:
            symbol = self.symbol_map.get(name, "")
            code = FOREX_USD_MARKETS.get(name, {}).get("code", "")
            group = self.groups.get(name, "Other")
            label = f"{name} ({code})" if code else name

            if symbol and symbol.startswith("USD"):
                label = f"{label}*"

            labels.append(label)
            colors.append(GROUP_COLORS.get(group, GROUP_COLORS["Other"]))

        bars = self.ax.barh(labels, values.values, color=colors)

        self.ax.invert_yaxis()
        self.ax.axvline(0, color="black", linewidth=1)

        title, x_label = self.get_title_and_xlabel(current_date)
        self.ax.set_title(title, loc="left", fontsize=17, fontweight="bold", pad=18)
        self.ax.set_xlabel(x_label, fontsize=12)
        self.ax.tick_params(axis="y", labelsize=9)
        self.ax.tick_params(axis="x", labelsize=9)

        min_x = min(0, values.min())
        max_x = max(0, values.max())
        max_abs = max(abs(min_x), abs(max_x))
        padding = max_abs * 0.20 if max_abs > 0 else 1

        self.ax.set_xlim(min_x - padding, max_x + padding)

        x_min, x_max = self.ax.get_xlim()
        offset = (x_max - x_min) * 0.01

        for bar, value in zip(bars, values.values):
            x = bar.get_width()
            label_x = x + offset if value >= 0 else x - offset

            self.ax.text(
                label_x,
                bar.get_y() + bar.get_height() / 2,
                f"{value:+.2f}%",
                va="center",
                ha="left" if value >= 0 else "right",
                fontsize=9,
            )

        for spine in ["top", "right", "left"]:
            self.ax.spines[spine].set_visible(False)

        self.ax.grid(axis="x", alpha=0.18)

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

        skipped_count = len(self.data.get("skipped", []))
        source_text = "Source: Norgate Data"

        if skipped_count > 0:
            source_text += f" | Skipped unavailable pairs: {skipped_count}"

        self.fig.text(0.015, 0.018, source_text, fontsize=10, ha="left", va="bottom")
        self.fig.text(0.50, 0.018, "* Inverted from USD base pair", fontsize=8, ha="center", va="bottom", color="gray")

        self.mode_button.label.set_text(f"Mode: {self.mode}")
        self.sort_button.label.set_text("Sort: On" if self.sort_by_gain else "Sort: Off")

        print(f"Showing: Forex | {self.mode} | {current_date:%Y-%m-%d}")

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

        current_date = self.get_current_date()
        current_pos = MODE_OPTIONS.index(self.mode)
        self.mode = MODE_OPTIONS[(current_pos + 1) % len(MODE_OPTIONS)]

        self.load_current_mode(preserve_date=current_date)
        self.draw()

    def set_mode(self, mode: str):
        if mode not in MODE_OPTIONS:
            return

        current_date = self.get_current_date()
        self.mode = mode

        self.load_current_mode(preserve_date=current_date)
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


def plot_forex_dashboard():
    viewer = ForexDashboardViewer()
    plt.show()
    return viewer


if __name__ == "__main__":
    viewer = plot_forex_dashboard()
