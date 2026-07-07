import pandas as pd
import matplotlib.pyplot as plt
import norgatedata
from matplotlib.widgets import Button
from matplotlib.patches import Rectangle


INDEX_WATCHLIST_CANDIDATES = {
    "S&P 500": [
        "S&P 500",
        "S&P 500 Current",
    ],
    "NASDAQ 100": [
        "Nasdaq 100",
        "NASDAQ 100",
        "NASDAQ-100",
        "Nasdaq-100",
    ],
    "Russell 1000": [
        "Russell 1000",
        "Russell-1000",
        "Russell 1000 Current",
    ],
    "ASX 200": [
        "S&P/ASX 200",
        "ASX 200",
        "S&P ASX 200",
    ],
    "ASX 100": [
        "S&P/ASX 100",
        "ASX 100",
        "S&P ASX 100",
    ],
}


INDEX_BUTTON_LABELS = {
    "S&P 500": "S&P500",
    "NASDAQ 100": "NASDAQ100",
    "Russell 1000": "R1000",
    "ASX 200": "ASX200",
    "ASX 100": "ASX100",
}


START_DATE = "2000-01-01"

TOP_N = 10
ROC_LOOKBACK_DAYS = 252

# Default mode.
# Options: "ROC252", "YTD", "ROC1"
DEFAULT_MODE = "ROC252"

# False = only completed months for monthly-sampled ROC252/YTD.
# True = include current month-to-date.
INCLUDE_CURRENT_MONTH = False

# CAPITAL = split/capital-action adjusted price movement, but not dividend total return.
# TOTALRETURN = includes dividends.
# NONE = raw unadjusted price movement, usually not ideal for individual stocks.
PRICE_ADJUSTMENT = norgatedata.StockPriceAdjustmentType.CAPITAL


# Missing data policy:
# "omit" = skip unavailable symbols completely. Recommended.
# "blank" = keep unavailable columns as blank/NaN where possible.
# "zero" = fill calculated ranking tables with 0.0 where possible.
MISSING_DATA_POLICY = "omit"


def apply_ranking_data_policy(df: pd.DataFrame, expected_columns: list[str] | None = None) -> pd.DataFrame:
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


def normalize_watchlist_name(name: str) -> str:
    return "".join(ch.lower() for ch in name if ch.isalnum())


def resolve_watchlist(index_name: str) -> tuple[str, list[str]]:
    candidates = INDEX_WATCHLIST_CANDIDATES[index_name]
    errors = []

    # Try exact candidate names first.
    for watchlist_name in candidates:
        try:
            symbols = norgatedata.watchlist_symbols(watchlist_name)

            if symbols:
                print(f"Resolved {index_name} watchlist as: {watchlist_name}")
                return watchlist_name, symbols

        except Exception as e:
            errors.append(f"{watchlist_name}: {e}")

    # If exact names fail, try fuzzy matching against available watchlists.
    try:
        available_watchlists = norgatedata.watchlists()
        available_lookup = {
            normalize_watchlist_name(name): name
            for name in available_watchlists
        }

        for candidate in candidates:
            candidate_norm = normalize_watchlist_name(candidate)

            if candidate_norm in available_lookup:
                watchlist_name = available_lookup[candidate_norm]

                if "currentpast" not in normalize_watchlist_name(watchlist_name):
                    symbols = norgatedata.watchlist_symbols(watchlist_name)

                    if symbols:
                        print(f"Resolved {index_name} watchlist as: {watchlist_name}")
                        return watchlist_name, symbols

        # Last-chance fuzzy contains match, but still prefer not Current & Past.
        candidate_norms = [normalize_watchlist_name(c) for c in candidates]

        for watchlist_name in available_watchlists:
            watchlist_norm = normalize_watchlist_name(watchlist_name)

            if "currentpast" in watchlist_norm:
                continue

            for candidate_norm in candidate_norms:
                if candidate_norm in watchlist_norm or watchlist_norm in candidate_norm:
                    symbols = norgatedata.watchlist_symbols(watchlist_name)

                    if symbols:
                        print(f"Resolved {index_name} watchlist as: {watchlist_name}")
                        return watchlist_name, symbols

    except Exception as e:
        errors.append(f"watchlists() fuzzy lookup failed: {e}")

    raise ValueError(
        f"Could not resolve a Norgate watchlist for {index_name}.\n"
        f"Tried: {candidates}\n\n"
        f"Open Norgate Data Updater > Watchlist Library and check the exact watchlist name.\n"
        f"Recent errors:\n" + "\n".join(errors[-8:])
    )


def get_daily_ohlc(symbol: str, start_date: str) -> pd.DataFrame:
    df = norgatedata.price_timeseries(
        symbol,
        start_date=start_date,
        stock_price_adjustment_setting=PRICE_ADJUSTMENT,
        padding_setting=norgatedata.PaddingType.NONE,
        timeseriesformat="pandas-dataframe",
    )

    if df is None or df.empty:
        raise ValueError(
            f"No data returned for {symbol}. "
            f"This symbol may be unavailable, or the required Norgate data package may not be installed."
        )

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
    else:
        df.index = pd.to_datetime(df.index)

    required_columns = ["Open", "Close"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"No {col} column found for {symbol}. "
                f"This symbol may be unavailable, incomplete, or unsupported by the user's Norgate subscription. "
                f"Columns: {list(df.columns)}"
            )

    df = df[["Open", "Close"]].dropna()

    if df.empty:
        raise ValueError(
            f"OHLC data is empty for {symbol}. "
            f"This symbol may be unavailable in the user's Norgate subscription."
        )

    return df.sort_index()


def remove_current_month(monthly_data: pd.Series) -> pd.Series:
    if INCLUDE_CURRENT_MONTH:
        return monthly_data

    current_month = pd.Timestamp.today().to_period("M")

    return monthly_data[
        monthly_data.index.to_period("M") < current_month
    ]


def calculate_symbol_ytd(monthly_open: pd.Series, monthly_close: pd.Series) -> pd.Series:
    ytd = pd.Series(index=monthly_close.index, dtype=float)

    for month in monthly_close.index:
        january_months = monthly_open.index[
            (monthly_open.index.year == month.year) &
            (monthly_open.index.month == 1)
        ]

        if len(january_months) == 0:
            continue

        january_month = january_months[0]
        base_open = monthly_open.loc[january_month]
        current_close = monthly_close.loc[month]

        if pd.notna(base_open) and pd.notna(current_close) and base_open != 0:
            ytd.loc[month] = (current_close / base_open - 1) * 100

    return ytd


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

        self.title_text = self.ax.text(
            0,
            0.86,
            title,
            fontsize=12,
            fontweight="bold",
            va="center",
            ha="left"
        )

        self.status_text = self.ax.text(
            0,
            0.62,
            "Preparing...",
            fontsize=10,
            va="center",
            ha="left"
        )

        self.percent_text = self.ax.text(
            100,
            0.62,
            "0.0%",
            fontsize=10,
            va="center",
            ha="right"
        )

        self.skipped_text = self.ax.text(
            0,
            0.12,
            "",
            fontsize=8,
            va="center",
            ha="left"
        )

        self.bar_background = Rectangle(
            (0, 0.34),
            100,
            0.14,
            linewidth=0.8,
            edgecolor="black",
            facecolor="lightgray"
        )

        self.bar = Rectangle(
            (0, 0.34),
            0,
            0.14,
            linewidth=0,
            facecolor="steelblue"
        )

        self.ax.add_patch(self.bar_background)
        self.ax.add_patch(self.bar)

        plt.show(block=False)
        plt.pause(0.001)

    def update(self, current: int, total: int, symbol: str, skipped_count: int = 0):
        percent = (current / total) * 100 if total > 0 else 0

        self.status_text.set_text(f"[{current}/{total}] Loading {symbol}...")
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
        plt.pause(0.25)

    def close(self):
        plt.close(self.fig)
        plt.pause(0.001)


def load_index_metric_tables(index_name: str) -> dict:
    watchlist_name, symbols = resolve_watchlist(index_name)

    # Keep symbols unique while preserving order.
    seen = set()
    symbols = [
        symbol for symbol in symbols
        if not (symbol in seen or seen.add(symbol))
    ]

    roc1_tables = {}
    roc252_tables = {}
    ytd_tables = {}
    skipped = []

    print(f"\nLoading {len(symbols)} symbols for {index_name}...\n")

    loading_window = LoadingProgressWindow(f"Loading {index_name} constituents")

    try:
        for i, symbol in enumerate(symbols, start=1):
            print(f"[{i}/{len(symbols)}] Loading {symbol}...")

            loading_window.update(
                current=i,
                total=len(symbols),
                symbol=symbol,
                skipped_count=len(skipped)
            )

            try:
                daily_ohlc = get_daily_ohlc(symbol, START_DATE)

                close = daily_ohlc["Close"]

                # Daily ROC(Close, 1), kept as true daily EOD data.
                # This powers the "yesterday's biggest movers" mode.
                roc1_daily = close.pct_change(1) * 100

                # Daily ROC(Close, 252), sampled at each completed month-end.
                roc252_daily = close.pct_change(ROC_LOOKBACK_DAYS) * 100
                roc252_monthly = roc252_daily.resample("ME").last()
                roc252_monthly = remove_current_month(roc252_monthly)

                # YTD = January first trading day open -> selected month-end close.
                monthly_open = daily_ohlc["Open"].resample("ME").first()
                monthly_close = daily_ohlc["Close"].resample("ME").last()

                monthly_open = remove_current_month(monthly_open)
                monthly_close = remove_current_month(monthly_close)

                ytd_monthly = calculate_symbol_ytd(monthly_open, monthly_close)

                roc1_tables[symbol] = roc1_daily
                roc252_tables[symbol] = roc252_monthly
                ytd_tables[symbol] = ytd_monthly

            except Exception as e:
                print(f"  SKIPPED: {symbol}")
                print(f"  Reason: {e}")
                skipped.append(symbol)

        loading_window.finish(f"Finished loading {index_name}")

    finally:
        loading_window.close()

    if skipped:
        print(f"\nSkipped {len(skipped)} symbols:")
        for symbol in skipped[:50]:
            print(f"  - {symbol}")

        if len(skipped) > 50:
            print(f"  ... plus {len(skipped) - 50} more")

    if not roc252_tables and not roc1_tables:
        raise ValueError(f"No stock data was loaded for {index_name}.")

    expected_columns = symbols

    roc1_df = apply_ranking_data_policy(pd.DataFrame(roc1_tables), expected_columns)
    roc252_df = apply_ranking_data_policy(pd.DataFrame(roc252_tables), expected_columns)
    ytd_df = apply_ranking_data_policy(pd.DataFrame(ytd_tables), expected_columns)

    return {
        "index_name": index_name,
        "watchlist_name": watchlist_name,
        "symbols": symbols,
        "roc1": roc1_df,
        "roc252": roc252_df,
        "ytd": ytd_df,
    }


class TopStockRankingViewer:
    def __init__(self):
        self.index_names = list(INDEX_WATCHLIST_CANDIDATES.keys())
        self.index_position = 0

        self.mode_options = ["ROC252", "YTD", "ROC1"]
        self.mode = DEFAULT_MODE if DEFAULT_MODE in self.mode_options else "ROC252"

        self.index_cache = {}
        self.symbol_label_cache = {}

        self.metric_table = None
        self.periods = []
        self.period_index = 0

        self.last_click_time = 0

        self.fig, self.ax = plt.subplots(figsize=(13, 7))

        self.fig.subplots_adjust(
            left=0.34,
            right=0.96,
            bottom=0.20,
            top=0.88,
        )

        prev_ax = self.fig.add_axes([0.14, 0.055, 0.12, 0.055])
        mode_ax = self.fig.add_axes([0.31, 0.055, 0.16, 0.055])
        index_ax = self.fig.add_axes([0.52, 0.055, 0.18, 0.055])
        next_ax = self.fig.add_axes([0.75, 0.055, 0.12, 0.055])

        self.prev_button = Button(prev_ax, "Previous")
        self.mode_button = Button(mode_ax, f"Mode: {self.mode}")
        self.index_button = Button(index_ax, "Index: S&P500")
        self.next_button = Button(next_ax, "Next")

        self.prev_button.on_clicked(self.previous_period)
        self.mode_button.on_clicked(self.toggle_mode)
        self.index_button.on_clicked(self.next_index)
        self.next_button.on_clicked(self.next_period)

        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)

        self.load_current_index()
        self.draw()

    def is_double_click_event(self):
        now = pd.Timestamp.now().timestamp()

        if now - self.last_click_time < 0.25:
            return True

        self.last_click_time = now
        return False

    def get_current_index_name(self) -> str:
        return self.index_names[self.index_position]

    def get_current_period(self) -> pd.Timestamp:
        return self.periods[self.period_index]

    def get_current_index_data(self) -> dict:
        index_name = self.get_current_index_name()

        if index_name not in self.index_cache:
            self.index_cache[index_name] = load_index_metric_tables(index_name)

        return self.index_cache[index_name]

    def get_current_metric_table(self) -> pd.DataFrame:
        data = self.get_current_index_data()

        if self.mode == "ROC1":
            return data["roc1"].dropna(how="all").sort_index()

        if self.mode == "ROC252":
            return data["roc252"].dropna(how="all").sort_index()

        return data["ytd"].dropna(how="all").sort_index()

    def load_current_index(self, preserve_period: pd.Timestamp | None = None, jump_to_latest: bool = False):
        self.metric_table = self.get_current_metric_table()
        self.periods = list(self.metric_table.index)

        if not self.periods:
            raise ValueError(
                f"No {self.mode} data available for {self.get_current_index_name()}."
            )

        if jump_to_latest or preserve_period is None:
            self.period_index = len(self.periods) - 1
            return

        if preserve_period in self.periods:
            self.period_index = self.periods.index(preserve_period)
            return

        earlier_periods = [period for period in self.periods if period <= preserve_period]

        if earlier_periods:
            nearest_period = earlier_periods[-1]
            self.period_index = self.periods.index(nearest_period)
        else:
            self.period_index = len(self.periods) - 1

    def get_symbol_label(self, symbol: str) -> str:
        if symbol in self.symbol_label_cache:
            return self.symbol_label_cache[symbol]

        label = symbol

        try:
            name = norgatedata.security_name(symbol)

            if name:
                name = str(name).strip()

                if len(name) > 36:
                    name = name[:33] + "..."

                label = f"{symbol} - {name}"

        except Exception:
            label = symbol

        self.symbol_label_cache[symbol] = label
        return label

    def get_ranking(self, period: pd.Timestamp) -> pd.Series:
        ranking = self.metric_table.loc[period].dropna()

        if ranking.empty:
            return ranking

        if self.mode == "ROC1":
            # Top daily gainers only = highest positive ROC(Close, 1).
            ranking = ranking.sort_values(ascending=False).head(TOP_N)
            return ranking

        ranking = ranking.sort_values(ascending=False).head(TOP_N)
        return ranking

    def draw(self):
        self.ax.clear()

        index_name = self.get_current_index_name()
        data = self.get_current_index_data()

        period = self.get_current_period()
        ranking = self.get_ranking(period)

        if ranking.empty:
            if self.mode == "ROC1":
                self.ax.set_title(f"No daily ROC1 data available for {index_name} on {period:%d %b %Y}")
            else:
                self.ax.set_title(f"No ranking data available for {index_name} in {period:%B %Y}")

            self.fig.canvas.draw_idle()
            return

        labels = [self.get_symbol_label(symbol) for symbol in ranking.index]

        bars = self.ax.barh(labels, ranking.values)

        self.ax.invert_yaxis()
        self.ax.axvline(0, linewidth=1)

        if self.mode == "ROC1":
            title = (
                f"{index_name} Top {TOP_N} Biggest Daily Gains\n"
                f"As of latest selected EOD: {period:%d %b %Y} | Watchlist: {data['watchlist_name']}"
            )
            x_label = "ROC(Close, 1) %"

        elif self.mode == "ROC252":
            title = (
                f"{index_name} Top {TOP_N} Current Constituents\n"
                f"As of {period:%B %Y} | Watchlist: {data['watchlist_name']}"
            )
            x_label = f"ROC(Close, {ROC_LOOKBACK_DAYS}) %"

        else:
            title = (
                f"{index_name} Top {TOP_N} Current Constituents by YTD Return\n"
                f"January {period.year} open to {period:%B %Y} close | Watchlist: {data['watchlist_name']}"
            )
            x_label = "YTD return %"

        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.tick_params(axis="y", labelsize=8)
        self.ax.tick_params(axis="x", labelsize=9)

        min_x = min(0, ranking.min())
        max_x = max(0, ranking.max())
        max_abs = max(abs(min_x), abs(max_x))
        padding = max_abs * 0.15 if max_abs > 0 else 1

        self.ax.set_xlim(min_x - padding, max_x + padding)

        x_min, x_max = self.ax.get_xlim()
        offset = (x_max - x_min) * 0.01

        for bar, value in zip(bars, ranking.values):
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

        index_button_label = INDEX_BUTTON_LABELS.get(index_name, index_name)

        self.mode_button.label.set_text(f"Mode: {self.mode}")
        self.index_button.label.set_text(f"Index: {index_button_label}")

        self.ax.grid(axis="x", alpha=0.25)

        if self.mode == "ROC1":
            print(f"Showing: {index_name} | {self.mode} | {period:%Y-%m-%d}")
        else:
            print(f"Showing: {index_name} | {self.mode} | {period:%B %Y}")

        self.fig.canvas.draw_idle()

    def previous_period(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        if self.period_index > 0:
            self.period_index -= 1
            self.draw()

    def next_period(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        if self.period_index < len(self.periods) - 1:
            self.period_index += 1
            self.draw()

    def toggle_mode(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        old_mode = self.mode
        current_period = self.get_current_period()

        current_pos = self.mode_options.index(self.mode)
        self.mode = self.mode_options[(current_pos + 1) % len(self.mode_options)]

        # When switching into daily ROC1 mode, jump to the latest available EOD date.
        if self.mode == "ROC1":
            self.load_current_index(jump_to_latest=True)

        # When switching from daily ROC1 into monthly modes, use the nearest completed month.
        elif old_mode == "ROC1":
            self.load_current_index(preserve_period=current_period)

        # Monthly-to-monthly mode switching should preserve the selected month.
        else:
            self.load_current_index(preserve_period=current_period)

        self.draw()

    def set_mode(self, mode: str):
        if mode not in self.mode_options:
            return

        old_mode = self.mode
        current_period = self.get_current_period()

        self.mode = mode

        if self.mode == "ROC1":
            self.load_current_index(jump_to_latest=True)

        elif old_mode == "ROC1":
            self.load_current_index(preserve_period=current_period)

        else:
            self.load_current_index(preserve_period=current_period)

        self.draw()

    def next_index(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        current_period = self.get_current_period()

        self.index_position = (self.index_position + 1) % len(self.index_names)

        print(f"\nSwitching to {self.get_current_index_name()}...\n")

        if self.mode == "ROC1":
            self.load_current_index(jump_to_latest=True)
        else:
            self.load_current_index(preserve_period=current_period)

        self.draw()

    def on_key_press(self, event):
        if event.key in ["left", "down"]:
            self.previous_period()

        elif event.key in ["right", "up"]:
            self.next_period()

        elif event.key == "m":
            self.toggle_mode()

        elif event.key == "r":
            self.set_mode("ROC252")

        elif event.key == "y":
            self.set_mode("YTD")

        elif event.key in ["d", "1"]:
            self.set_mode("ROC1")

        elif event.key == "i":
            self.next_index()


def plot_top_stock_rankings():
    viewer = TopStockRankingViewer()
    plt.show()
    return viewer


if __name__ == "__main__":
    viewer = plot_top_stock_rankings()