import pandas as pd
import matplotlib.pyplot as plt
import norgatedata
from matplotlib.widgets import Button, CheckButtons
from matplotlib.patches import Patch


MARKET_INDEXES = {
    # Crypto
    "S&P Crypto MegaCap USD": {
        "region": "Crypto",
        "symbol": "$SPCMC",
    },
    
    # Global
    "Dow Jones Global": {
        "region": "Global",
        "symbol": "$W1DOW",
    },
    "Dow Jones Global ex-US": {
        "region": "Global",
        "symbol": "$W2DOW",
    },
    "S&P Global 100": {
        "region": "Global",
        "symbol": "$OOI",
    },

    # North America
    "S&P 500 (US)": {
        "region": "North America",
        "symbol": "$SPX",
    },
    "NASDAQ 100 (US)": {
        "region": "North America",
        "symbol": "$NDX",
    },
    "S&P/TSX Composite (Canada)": {
        "region": "North America",
        "symbol": "$SPTSX",
    },
    "S&P/TSX 60 (Canada)": {
        "region": "North America",
        "symbol": "$SPTSX60",
    },
    "IPC (Mexico)": {
        "region": "Latin America",
        "symbol": "$MXX",
    },

    # Latin America
    "Bovespa (Brazil)": {
        "region": "Latin America",
        "symbol": "$BVSP",
    },

    # Asia-Pacific
    "S&P/ASX 200 (Australia)": {
        "region": "Asia-Pacific",
        "symbol": "$XJO.au",
    },
    "Nikkei 225 (Japan)": {
        "region": "Asia-Pacific",
        "symbol": "$N225",
    },
    "KOSPI 200 (Korea)": {
        "region": "Asia-Pacific",
        "symbol": "$KO",
    },
    "MSCI Taiwan": {
        "region": "Asia-Pacific",
        "symbol": "$TWMSCI",
    },
    "Hang Seng (HK)": {
        "region": "Asia-Pacific",
        "symbol": "$HS",
    },
    "Shanghai Composite": {
        "region": "Asia-Pacific",
        "symbol": "$SSEC",
    },
    "FTSE China 50": {
        "region": "Asia-Pacific",
        "symbol": "$XIN0",
    },
    "FTSE China A50": {
        "region": "Asia-Pacific",
        "symbol": "$XIN9",
    },
    "NIFTY (India)": {
        "region": "Asia-Pacific",
        "symbol": "$NIF",
    },
    "Sensex (India)": {
        "region": "Asia-Pacific",
        "symbol": "$SEN",
    },
    "MSCI Singapore": {
        "region": "Asia-Pacific",
        "symbol": "$SIMSCI",
    },
    "Straits Times (Singapore)": {
        "region": "Asia-Pacific",
        "symbol": "$STI",
    },

    # Europe
    "FTSE 100 (UK)": {
        "region": "Europe",
        "symbol": "$FT100",
    },
    "DAX (Germany)": {
        "region": "Europe",
        "symbol": "$DAX",
    },
    "CAC 40 (France)": {
        "region": "Europe",
        "symbol": "$CAC",
    },
    "IBEX 35 (Spain)": {
        "region": "Europe",
        "symbol": "$IBEX",
    },
    "Euro STOXX 50": {
        "region": "Europe",
        "symbol": "$STOXX50",
    },
    "FTSEurofirst 300": {
        "region": "Europe",
        "symbol": "$E3X",
    },
    "FTSE MIB (Italy)": {
        "region": "Europe",
        "symbol": "$FTSEMIB",
    },
    "SMI (Switzerland)": {
        "region": "Europe",
        "symbol": "$SMI",
    },
    "TecDAX (Germany)": {
        "region": "Europe",
        "symbol": "$TDX",
    },
    "OMX Nordic 40": {
        "region": "Europe",
        "symbol": "$OMNX40",
    },
    "RTS (Russia)": {
        "region": "Europe",
        "symbol": "$RTS",
    },

    # Africa
    "Dow Jones South Africa": {
        "region": "Africa",
        "symbol": "$ZADOW",
    },
}


REGION_COLORS = {
    "North America": "#1f77b4",
    "Europe": "#7b3fb2",
    "Asia-Pacific": "#d62728",
    "Latin America": "#2ca02c",
    "Africa": "#ff7f0e",
    "Global": "#666666",
    "Crypto": "#ffe300",
}


START_DATE = "2000-01-01"

# False = only completed months.
# True = include current month-to-date in monthly modes.
# Leave this False if you want monthly charts to use confirmed monthly closes only.
INCLUDE_CURRENT_MONTH = False

# Default startup mode.
# EOD = latest available daily end-of-day close-to-close move.
DEFAULT_RETURN_MODE = "EOD"

# For index rotation charts, price-only is cleaner.
# Do not mix normal price indexes with total return indexes unless intentional.
PRICE_ADJUSTMENT = norgatedata.StockPriceAdjustmentType.NONE


# Missing data policy:
# "omit" = skip unavailable symbols completely. Recommended.
# "blank" = keep unavailable columns as blank/NaN where possible.
# "zero" = fill calculated return tables with 0.0 where possible.
#
# Note: Open/Close price tables are never zero-filled because 0 is not a valid
# placeholder for a missing price. Zero-filling only applies to calculated returns.
MISSING_DATA_POLICY = "omit"


# Prevent 24/7 assets like crypto from forcing EOD mode onto dates
# where normal equity/index markets have no fresh bar.
#
# This keeps EOD mode anchored to normal global equity market dates.
EOD_ANCHOR_COLUMN = "S&P 500 (US)"


def apply_price_data_policy(df: pd.DataFrame, expected_columns: list[str] | None = None) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.sort_index()

    if expected_columns is not None and MISSING_DATA_POLICY in ["blank", "zero"]:
        df = df.reindex(columns=expected_columns)

    if MISSING_DATA_POLICY == "omit":
        return df.dropna(axis=1, how="all").dropna(how="all")

    return df.dropna(how="all")


def apply_return_data_policy(df: pd.DataFrame, expected_columns: list[str] | None = None) -> pd.DataFrame:
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


# These are filled by get_monthly_ohlc().
# This keeps compatibility with your main dashboard, which currently calls:
# monthly_opens, monthly_closes = get_monthly_ohlc()
_LAST_DAILY_OPENS = None
_LAST_DAILY_CLOSES = None


def get_daily_ohlc(symbol: str, label: str, start_date: str) -> pd.DataFrame:
    df = norgatedata.price_timeseries(
        symbol,
        start_date=start_date,
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

    required_columns = ["Open", "Close"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"No {col} column found for {label} / {symbol}. "
                f"This symbol may be unavailable, incomplete, or unsupported by the user's Norgate subscription. "
                f"Columns: {list(df.columns)}"
            )

    df = df[["Open", "Close"]].dropna()

    if df.empty:
        raise ValueError(
            f"OHLC data is empty for {label} / {symbol}. "
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


def get_monthly_ohlc() -> tuple[pd.DataFrame, pd.DataFrame]:
    global _LAST_DAILY_OPENS
    global _LAST_DAILY_CLOSES

    daily_opens = {}
    daily_closes = {}
    monthly_opens = {}
    monthly_closes = {}
    skipped = []

    for label, info in MARKET_INDEXES.items():
        symbol = info["symbol"]

        print(f"Loading {label} ({symbol})...")

        try:
            daily_ohlc = get_daily_ohlc(symbol, label, START_DATE)

            daily_opens[label] = daily_ohlc["Open"]
            daily_closes[label] = daily_ohlc["Close"]

            # First trading day's open inside each calendar month.
            monthly_open = daily_ohlc["Open"].resample("ME").first()

            # Last trading day's close inside each calendar month.
            monthly_close = daily_ohlc["Close"].resample("ME").last()

            # Keep monthly modes based on confirmed completed monthly closes.
            monthly_open = remove_current_month(monthly_open)
            monthly_close = remove_current_month(monthly_close)

            monthly_opens[label] = monthly_open
            monthly_closes[label] = monthly_close

        except Exception as e:
            print(f"  SKIPPED: {label} ({symbol})")
            print(f"  Reason: {e}")
            skipped.append(f"{label} ({symbol})")

    if skipped:
        print("\nSkipped indexes:")
        for item in skipped:
            print(f"  - {item}")

    if not monthly_closes:
        raise ValueError("No index data was loaded. Check the symbols in Norgate Data Viewer.")

    expected_columns = list(MARKET_INDEXES.keys())

    _LAST_DAILY_OPENS = apply_price_data_policy(pd.DataFrame(daily_opens), expected_columns)
    _LAST_DAILY_CLOSES = apply_price_data_policy(pd.DataFrame(daily_closes), expected_columns)

    monthly_opens_df = apply_price_data_policy(pd.DataFrame(monthly_opens), expected_columns)
    monthly_closes_df = apply_price_data_policy(pd.DataFrame(monthly_closes), expected_columns)

    return monthly_opens_df, monthly_closes_df


def calculate_eod_returns(daily_closes: pd.DataFrame, anchor_column: str | None = EOD_ANCHOR_COLUMN) -> pd.DataFrame:
    if daily_closes is None or daily_closes.empty:
        return pd.DataFrame()

    eod_returns = {}

    for column in daily_closes.columns:
        close = daily_closes[column].dropna()

        if close.empty:
            continue

        # Close-to-close daily move based on each market's own previous available EOD close.
        eod_returns[column] = close.pct_change() * 100

    if not eod_returns:
        return pd.DataFrame()

    eod_df = pd.DataFrame(eod_returns).dropna(how="all").sort_index()

    # For global indices, different markets have different holidays and data timestamps.
    # Forward filling keeps the dashboard populated when one market is closed and another has updated.
    eod_df = eod_df.ffill()

    # Important:
    # Crypto can have weekend / holiday / 24-7 dates that normal equity indices do not have.
    # If we allow those dates, the chart can be pulled onto a crypto-only date.
    #
    # So EOD mode is anchored to the S&P 500 date index by default.
    if anchor_column is not None and anchor_column in daily_closes.columns:
        anchor_dates = daily_closes.index[daily_closes[anchor_column].notna()]
        common_dates = eod_df.index.intersection(anchor_dates)

        if len(common_dates) > 0:
            eod_df = eod_df.loc[common_dates]

    return eod_df.dropna(how="all")


def calculate_ytd_returns(monthly_opens: pd.DataFrame, monthly_closes: pd.DataFrame) -> pd.DataFrame:
    ytd_returns = pd.DataFrame(
        index=monthly_closes.index,
        columns=monthly_closes.columns,
        dtype=float
    )

    for month in monthly_closes.index:
        january_months = monthly_opens.index[
            (monthly_opens.index.year == month.year) &
            (monthly_opens.index.month == 1)
        ]

        if len(january_months) == 0:
            continue

        january_month = january_months[0]

        # First trading day's OPEN in January.
        base_open = monthly_opens.loc[january_month]

        # Selected month's confirmed month-end CLOSE.
        current_close = monthly_closes.loc[month]

        ytd_returns.loc[month] = (current_close / base_open - 1) * 100

    return ytd_returns


def calculate_return_tables(monthly_opens: pd.DataFrame, monthly_closes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Month-over-month close-to-close return using confirmed month-end closes only.
    monthly_returns = monthly_closes.pct_change() * 100

    # Rolling 12-month close-to-close return using confirmed month-end closes only.
    yearly_returns = monthly_closes.pct_change(periods=12) * 100

    # Year-to-date return:
    # January first trading day open -> selected confirmed month-end close.
    ytd_returns = calculate_ytd_returns(monthly_opens, monthly_closes)

    expected_columns = list(monthly_closes.columns)

    monthly_returns = apply_return_data_policy(monthly_returns, expected_columns)
    yearly_returns = apply_return_data_policy(yearly_returns, expected_columns)
    ytd_returns = apply_return_data_policy(ytd_returns, expected_columns)

    return monthly_returns, yearly_returns, ytd_returns


def is_crypto_index(name: str) -> bool:
    return MARKET_INDEXES.get(name, {}).get("region") == "Crypto"


class MonthlyIndexBarViewer:
    def __init__(
        self,
        monthly_returns: pd.DataFrame,
        yearly_returns: pd.DataFrame,
        ytd_returns: pd.DataFrame,
        eod_returns: pd.DataFrame | None = None
    ):
        if eod_returns is None:
            eod_returns = calculate_eod_returns(_LAST_DAILY_CLOSES)

        self.return_tables = {}

        if eod_returns is not None and not eod_returns.empty:
            self.return_tables["EOD"] = eod_returns.dropna(how="all").sort_index()

        self.return_tables["Monthly"] = monthly_returns.dropna(how="all").sort_index()
        self.return_tables["Yearly"] = yearly_returns.dropna(how="all").sort_index()
        self.return_tables["YTD"] = ytd_returns.dropna(how="all").sort_index()

        if self.return_tables["Monthly"].empty:
            raise ValueError("No monthly return data available.")

        self.return_modes = [mode for mode in ["EOD", "Monthly", "Yearly", "YTD"] if mode in self.return_tables and not self.return_tables[mode].empty]

        if DEFAULT_RETURN_MODE in self.return_modes:
            self.return_mode = DEFAULT_RETURN_MODE
        else:
            self.return_mode = "Monthly"

        self.returns = self.return_tables[self.return_mode]
        self.periods = list(self.returns.index)

        self.static_order = list(self.return_tables["Monthly"].columns)
        self.period_index = len(self.periods) - 1
        self.sort_by_gain = False
        self.include_crypto = True

        # Prevent one mouse click from firing twice.
        self.last_click_time = 0

        self.fig, self.ax = plt.subplots(figsize=(14, 10))

        self.fig.subplots_adjust(
            left=0.25,
            right=0.96,
            bottom=0.15,
            top=0.90,
        )

        crypto_ax = self.fig.add_axes([0.015, 0.935, 0.12, 0.045])
        prev_ax = self.fig.add_axes([0.22, 0.045, 0.12, 0.045])
        mode_ax = self.fig.add_axes([0.38, 0.045, 0.16, 0.045])
        sort_ax = self.fig.add_axes([0.58, 0.045, 0.16, 0.045])
        next_ax = self.fig.add_axes([0.78, 0.045, 0.12, 0.045])

        self.prev_button = Button(prev_ax, "Previous")
        self.mode_button = Button(mode_ax, f"Mode: {self.return_mode}")
        self.sort_button = Button(sort_ax, "Sort: On")
        self.next_button = Button(next_ax, "Next")
        self.crypto_checkbox = CheckButtons(crypto_ax, ["Crypto"], [self.include_crypto])

        self.prev_button.on_clicked(self.previous_period)
        self.mode_button.on_clicked(self.toggle_return_mode)
        self.sort_button.on_clicked(self.toggle_sort)
        self.next_button.on_clicked(self.next_period)
        self.crypto_checkbox.on_clicked(self.toggle_crypto)

        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)

        self.draw()

    def is_double_click_event(self):
        now = pd.Timestamp.now().timestamp()

        if now - self.last_click_time < 0.25:
            return True

        self.last_click_time = now
        return False

    def get_current_period(self) -> pd.Timestamp:
        return self.periods[self.period_index]

    def set_return_mode(self, mode: str):
        if mode not in self.return_tables:
            return False

        if self.return_tables[mode].empty:
            print(f"No {mode} data available.")
            return False

        old_mode = self.return_mode
        current_period = self.get_current_period()

        self.return_mode = mode
        self.returns = self.return_tables[mode]
        self.periods = list(self.returns.index)

        # Important:
        # When switching INTO EOD, always jump to the latest available daily EOD date.
        # Otherwise it may preserve the last confirmed monthly date, which is usually
        # the final day of the previous month.
        if mode == "EOD":
            self.period_index = len(self.periods) - 1
            return True

        # When switching FROM EOD into a monthly-based mode, use the nearest confirmed
        # monthly period at or before the current EOD date.
        if old_mode == "EOD":
            earlier_periods = [p for p in self.periods if p <= current_period]

            if earlier_periods:
                nearest_period = earlier_periods[-1]
                self.period_index = self.periods.index(nearest_period)
            else:
                self.period_index = len(self.periods) - 1

            return True

        # Monthly/Yearly/YTD mode switching can preserve the same month when possible.
        if current_period in self.periods:
            self.period_index = self.periods.index(current_period)
        else:
            earlier_periods = [p for p in self.periods if p <= current_period]

            if earlier_periods:
                nearest_period = earlier_periods[-1]
                self.period_index = self.periods.index(nearest_period)
            else:
                self.period_index = len(self.periods) - 1

        return True

    def toggle_crypto(self, label=None):
        self.include_crypto = not self.include_crypto
        self.draw()

    def get_latest_values(self) -> tuple[pd.Timestamp, pd.Series]:
        period = self.get_current_period()
        latest = self.returns.loc[period].dropna()

        if not self.include_crypto:
            latest = latest[[name for name in latest.index if not is_crypto_index(name)]]

        if self.sort_by_gain:
            latest = latest.sort_values(ascending=False)
        else:
            latest = latest.reindex([name for name in self.static_order if name in latest.index])

        return period, latest

    def draw(self):
        self.ax.clear()

        period, latest = self.get_latest_values()

        if latest.empty:
            self.ax.set_title(f"No data available for {period:%d %b %Y}")
            self.fig.canvas.draw_idle()
            return

        colors = [
            REGION_COLORS.get(MARKET_INDEXES[name]["region"], "gray")
            for name in latest.index
        ]

        bars = self.ax.barh(latest.index, latest.values, color=colors)

        self.ax.invert_yaxis()
        self.ax.axvline(0, color="black", linewidth=1)

        if self.return_mode == "EOD":
            title = (
                f"Global Equity Indices EOD Returns\n"
                f"Latest available close-to-close move as of {period:%d %b %Y}"
            )
            x_label = "Daily EOD return %"

        elif self.return_mode == "Monthly":
            title = (
                f"Global Equity Indices Monthly Returns\n"
                f"{period:%B %Y} confirmed month-end close"
            )
            x_label = "Monthly close-to-close return %"

        elif self.return_mode == "Yearly":
            start_month = period - pd.DateOffset(months=12)
            title = (
                f"Global Equity Indices Rolling 12-Month Returns\n"
                f"{start_month:%B %Y} to {period:%B %Y} confirmed month-end closes"
            )
            x_label = "Rolling 12-month return %"

        else:
            title = (
                f"Global Equity Indices YTD Returns\n"
                f"January {period.year} open to {period:%B %Y} confirmed month-end close"
            )
            x_label = "Year-to-date return %"

        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.tick_params(axis="y", labelsize=8)
        self.ax.tick_params(axis="x", labelsize=9)

        min_x = min(0, latest.min())
        max_x = max(0, latest.max())
        max_abs = max(abs(min_x), abs(max_x))
        padding = max_abs * 0.18 if max_abs > 0 else 1

        self.ax.set_xlim(min_x - padding, max_x + padding)

        x_min, x_max = self.ax.get_xlim()
        offset = (x_max - x_min) * 0.008

        for bar, value in zip(bars, latest.values):
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

        visible_regions = []

        for name in latest.index:
            region = MARKET_INDEXES.get(name, {}).get("region", "Other")

            if region not in visible_regions:
                visible_regions.append(region)

        legend_items = [
            Patch(facecolor=REGION_COLORS.get(region, "gray"), label=region)
            for region in visible_regions
        ]

        self.ax.legend(
            handles=legend_items,
            title="Region",
            loc="lower right",
            fontsize=8,
            title_fontsize=9,
            frameon=True,
        )

        self.ax.grid(axis="x", alpha=0.25)

        self.mode_button.label.set_text(f"Mode: {self.return_mode}")
        self.sort_button.label.set_text("Sort: On" if self.sort_by_gain else "Sort: Off")

        if self.return_mode == "EOD":
            print(f"Showing: {self.return_mode} | {period:%Y-%m-%d}")
        else:
            print(f"Showing: {self.return_mode} | {period:%B %Y}")

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

    def toggle_return_mode(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        current_pos = self.return_modes.index(self.return_mode)

        for step in range(1, len(self.return_modes) + 1):
            new_mode = self.return_modes[(current_pos + step) % len(self.return_modes)]

            if self.set_return_mode(new_mode):
                self.draw()
                return

    def toggle_sort(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        self.sort_by_gain = not self.sort_by_gain
        self.draw()

    def on_key_press(self, event):
        if event.key in ["left", "down"]:
            if self.period_index > 0:
                self.period_index -= 1
                self.draw()

        elif event.key in ["right", "up"]:
            if self.period_index < len(self.periods) - 1:
                self.period_index += 1
                self.draw()

        elif event.key == "s":
            self.sort_by_gain = not self.sort_by_gain
            self.draw()

        elif event.key == "e":
            if self.set_return_mode("EOD"):
                self.draw()

        elif event.key == "m":
            if self.set_return_mode("Monthly"):
                self.draw()

        elif event.key == "y":
            if self.set_return_mode("Yearly"):
                self.draw()

        elif event.key == "t":
            if self.set_return_mode("YTD"):
                self.draw()


def plot_latest_month(
    monthly_returns: pd.DataFrame,
    yearly_returns: pd.DataFrame,
    ytd_returns: pd.DataFrame,
    eod_returns: pd.DataFrame | None = None
):
    viewer = MonthlyIndexBarViewer(
        monthly_returns,
        yearly_returns,
        ytd_returns,
        eod_returns=eod_returns
    )

    plt.show()
    return viewer


def plot_monthly_heatmap(returns: pd.DataFrame, months: int = 12):
    recent = returns.tail(months).T

    fig, ax = plt.subplots(figsize=(14, 9))
    im = ax.imshow(recent.values, aspect="auto")

    ax.set_title(f"Global Equity Indices Monthly Returns - Last {months} Completed Months")
    ax.set_yticks(range(len(recent.index)))
    ax.set_yticklabels(recent.index, fontsize=8)

    ax.set_xticks(range(len(recent.columns)))
    ax.set_xticklabels([d.strftime("%b %Y") for d in recent.columns], rotation=45, ha="right")

    for y in range(recent.shape[0]):
        for x in range(recent.shape[1]):
            val = recent.iloc[y, x]

            if pd.notna(val):
                ax.text(x, y, f"{val:+.1f}", ha="center", va="center", fontsize=7)

    fig.colorbar(im, ax=ax, label="Monthly return %")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    monthly_opens, monthly_closes = get_monthly_ohlc()
    monthly_returns, yearly_returns, ytd_returns = calculate_return_tables(monthly_opens, monthly_closes)
    eod_returns = calculate_eod_returns(_LAST_DAILY_CLOSES)

    print("\nLatest EOD returns:")
    print(eod_returns.tail(5).round(2))

    print("\nMonthly returns:")
    print(monthly_returns.tail(12).round(2))

    print("\nRolling 12-month returns:")
    print(yearly_returns.tail(12).round(2))

    print("\nYTD returns:")
    print(ytd_returns.tail(12).round(2))

    viewer = plot_latest_month(monthly_returns, yearly_returns, ytd_returns, eod_returns=eod_returns)
    plot_monthly_heatmap(monthly_returns, months=12)