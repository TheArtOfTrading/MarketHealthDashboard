import pandas as pd
import matplotlib.pyplot as plt
import norgatedata
from matplotlib.widgets import Button


ASX_SECTOR_INDEXES = {
    "Communication Services ($XTJ)": "$XTJ.au",
    "Consumer Discretionary ($XDJ)": "$XDJ.au",
    "Consumer Staples ($XSJ)": "$XSJ.au",
    "Energy ($XEJ)": "$XEJ.au",
    "Financials ($XFJ)": "$XFJ.au",
    "Health Care ($XHJ)": "$XHJ.au",
    "Industrials ($XNJ)": "$XNJ.au",
    "Information Technology ($XIJ)": "$XIJ.au",
    "Materials ($XMJ)": "$XMJ.au",
    "Real Estate ($XRE)": "$XRE.au",
    "Utilities ($XUJ)": "$XUJ.au",
}


START_DATE = "2000-01-01"

# Default rolling window.
WINDOW_MONTHS = 12

# Hard limit.
MAX_WINDOW_MONTHS = 36

# False = only completed months.
# True = include current month-to-date.
INCLUDE_CURRENT_MONTH = False

# NONE = raw open-to-close price movement.
# For sector index rotation, NONE is usually the cleanest.
PRICE_ADJUSTMENT = norgatedata.StockPriceAdjustmentType.NONE


# Missing data policy:
# "omit" = skip unavailable symbols completely. Recommended.
# "blank" = keep unavailable columns as blank/NaN where possible.
# "zero" = fill calculated return tables with 0.0 where possible.
#
# Note: Open/Close price tables are never zero-filled because 0 is not a valid
# placeholder for a missing price. Zero-filling only applies to calculated returns.
MISSING_DATA_POLICY = "omit"


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


def get_monthly_open_close_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    monthly_opens = {}
    monthly_closes = {}
    monthly_returns = {}
    skipped = []

    for sector, symbol in ASX_SECTOR_INDEXES.items():
        print(f"Loading {sector} ({symbol})...")

        try:
            daily_ohlc = get_daily_ohlc(symbol, START_DATE)

            # First trading day's open inside each calendar month.
            monthly_open = daily_ohlc["Open"].resample("ME").first()

            # Last trading day's close inside each calendar month.
            monthly_close = daily_ohlc["Close"].resample("ME").last()

            # Drop current incomplete month unless enabled.
            monthly_open = remove_current_month(monthly_open)
            monthly_close = remove_current_month(monthly_close)

            # Monthly open-to-close return.
            monthly_ret = (monthly_close / monthly_open - 1) * 100

            monthly_opens[sector] = monthly_open
            monthly_closes[sector] = monthly_close
            monthly_returns[sector] = monthly_ret

        except Exception as e:
            print(f"  SKIPPED: {sector} ({symbol})")
            print(f"  Reason: {e}")
            skipped.append(f"{sector} ({symbol})")

    if skipped:
        print("\nSkipped sectors:")
        for item in skipped:
            print(f"  - {item}")

    if not monthly_returns:
        raise ValueError("No ASX sector data was loaded. Check the symbols in Norgate Data Viewer. This may mean the required Norgate data package is not installed.")

    expected_columns = list(ASX_SECTOR_INDEXES.keys())

    monthly_opens_df = apply_price_data_policy(pd.DataFrame(monthly_opens), expected_columns)
    monthly_closes_df = apply_price_data_policy(pd.DataFrame(monthly_closes), expected_columns)
    monthly_returns_df = apply_return_data_policy(pd.DataFrame(monthly_returns), expected_columns)

    return monthly_opens_df, monthly_closes_df, monthly_returns_df


def get_monthly_returns() -> pd.DataFrame:
    monthly_opens, monthly_closes, monthly_returns = get_monthly_open_close_data()
    return monthly_returns


class ASXSectorDashboardViewer:
    def __init__(
        self,
        monthly_opens: pd.DataFrame,
        monthly_closes: pd.DataFrame,
        monthly_returns: pd.DataFrame,
        window_months: int = 12
    ):
        self.monthly_opens = monthly_opens.dropna(how="all").sort_index()
        self.monthly_closes = monthly_closes.dropna(how="all").sort_index()
        self.monthly_returns = monthly_returns.dropna(how="all").sort_index()

        if self.monthly_returns.empty:
            raise ValueError("No monthly open-to-close return data available.")

        available_months = len(self.monthly_returns.index)

        self.view_modes = ["Monthly", "Rolling"]
        self.view_mode = "Monthly"

        self.period_options = [3, 6, 12, 24, 36, "YTD"]
        self.period = max(1, min(int(window_months), MAX_WINDOW_MONTHS, available_months))

        self.months = list(self.monthly_returns.index)
        self.month_index = len(self.months) - 1
        self.end_index = len(self.monthly_returns.index) - 1

        self.static_order = list(self.monthly_returns.columns)

        # Change this to True if you want monthly bar charts sorted by gain by default.
        self.sort_by_gain = False

        # Prevent one mouse click from firing twice.
        self.last_click_time = 0

        self.fig, self.ax = plt.subplots(figsize=(14, 8))

        self.fig.subplots_adjust(
            left=0.31,
            right=0.78,
            bottom=0.18,
            top=0.88
        )

        prev_ax = self.fig.add_axes([0.12, 0.045, 0.12, 0.05])
        view_ax = self.fig.add_axes([0.28, 0.045, 0.14, 0.05])
        period_ax = self.fig.add_axes([0.46, 0.045, 0.14, 0.05])
        sort_ax = self.fig.add_axes([0.64, 0.045, 0.12, 0.05])
        next_ax = self.fig.add_axes([0.80, 0.045, 0.12, 0.05])

        self.prev_button = Button(prev_ax, "Previous")
        self.view_button = Button(view_ax, self.get_view_label())
        self.period_button = Button(period_ax, self.get_period_label())
        self.sort_button = Button(sort_ax, "Sort: Off")
        self.next_button = Button(next_ax, "Next")

        self.prev_button.on_clicked(self.previous)
        self.view_button.on_clicked(self.toggle_view_mode)
        self.period_button.on_clicked(self.cycle_period)
        self.sort_button.on_clicked(self.toggle_sort)
        self.next_button.on_clicked(self.next)

        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)

        self.sync_indices_to_latest()
        self.draw()

    def is_double_click_event(self):
        now = pd.Timestamp.now().timestamp()

        if now - self.last_click_time < 0.25:
            return True

        self.last_click_time = now
        return False

    def sync_indices_to_latest(self):
        latest_index = len(self.monthly_returns.index) - 1
        self.month_index = latest_index
        self.end_index = latest_index

    def sync_month_index_from_end_index(self):
        current_month = self.monthly_returns.index[self.end_index]

        if current_month in self.months:
            self.month_index = self.months.index(current_month)
        else:
            self.month_index = len(self.months) - 1

    def sync_end_index_from_month_index(self):
        current_month = self.months[self.month_index]

        if current_month in self.monthly_returns.index:
            self.end_index = list(self.monthly_returns.index).index(current_month)
        else:
            self.end_index = len(self.monthly_returns.index) - 1

    def get_view_label(self) -> str:
        return f"View: {self.view_mode}"

    def get_period_label(self) -> str:
        if self.view_mode == "Monthly":
            return "Period: N/A"

        if self.period == "YTD":
            return "YTD"

        return f"{self.period}M"

    def get_end_month(self) -> pd.Timestamp:
        return self.monthly_returns.index[self.end_index]

    # ------------------------------------------------------------
    # Monthly bar chart
    # ------------------------------------------------------------

    def draw_monthly_bar(self):
        month = self.months[self.month_index]
        latest = self.monthly_returns.loc[month].dropna()

        if latest.empty:
            self.ax.set_title(f"No data available for {month:%B %Y}")
            self.fig.canvas.draw_idle()
            return

        if self.sort_by_gain:
            latest = latest.sort_values(ascending=False)
        else:
            latest = latest.reindex([sector for sector in self.static_order if sector in latest.index])

        bars = self.ax.barh(latest.index, latest.values)

        self.ax.invert_yaxis()
        self.ax.axvline(0, linewidth=1)
        self.ax.set_title(f"S&P/ASX 200 Sector Index Monthly Open-to-Close Returns\n{month:%B %Y}")
        self.ax.set_xlabel("Monthly open-to-close return %")
        self.ax.tick_params(axis="y", labelsize=8)
        self.ax.tick_params(axis="x", labelsize=9)

        min_x = min(0, latest.min())
        max_x = max(0, latest.max())
        max_abs = max(abs(min_x), abs(max_x))
        padding = max_abs * 0.15 if max_abs > 0 else 1

        self.ax.set_xlim(min_x - padding, max_x + padding)

        x_min, x_max = self.ax.get_xlim()
        offset = (x_max - x_min) * 0.01

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

        self.ax.grid(axis="x", alpha=0.25)

        print(f"Showing: Monthly | {month:%B %Y}")

    # ------------------------------------------------------------
    # Rolling/YTD line chart
    # ------------------------------------------------------------

    def get_rolling_window_returns(self) -> pd.DataFrame:
        window_months = int(self.period)

        # For open-to-close monthly returns, a 12M window contains 12 monthly returns.
        start_index = max(0, self.end_index - window_months + 1)

        window = self.monthly_returns.iloc[start_index:self.end_index + 1].copy()

        # Drop sectors with incomplete data inside this window.
        window = window.dropna(axis=1, how="any")

        return window

    def get_rolling_performance(self) -> tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
        window_returns = self.get_rolling_window_returns()

        if window_returns.empty:
            return pd.DataFrame(), None, None

        # Compound the monthly open-to-close returns through the rolling window.
        performance = ((1 + window_returns / 100).cumprod() - 1) * 100

        # Add a 0% baseline just before the first month so each line starts from 0.
        baseline_month = window_returns.index[0] - pd.offsets.MonthEnd(1)
        baseline = pd.DataFrame(
            0.0,
            index=[baseline_month],
            columns=performance.columns
        )

        performance = pd.concat([baseline, performance])

        start_month = window_returns.index[0]
        end_month = window_returns.index[-1]

        return performance, start_month, end_month

    def get_ytd_performance(self) -> tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
        end_month = self.get_end_month()

        january_months = self.monthly_opens.index[
            (self.monthly_opens.index.year == end_month.year) &
            (self.monthly_opens.index.month == 1)
        ]

        if len(january_months) == 0:
            return pd.DataFrame(), None, None

        january_month = january_months[0]

        closes = self.monthly_closes.loc[
            (self.monthly_closes.index >= january_month) &
            (self.monthly_closes.index <= end_month)
        ].copy()

        if closes.empty:
            return pd.DataFrame(), None, None

        base_open = self.monthly_opens.loc[january_month]

        # Only keep sectors with a January open and complete closes through the displayed YTD period.
        valid_columns = base_open.dropna().index
        closes = closes[closes.columns.intersection(valid_columns)]
        closes = closes.dropna(axis=1, how="any")
        base_open = base_open[closes.columns]

        if closes.empty:
            return pd.DataFrame(), None, None

        # True YTD: January first trading day open -> each month-end close.
        performance = (closes / base_open - 1) * 100

        # Add a 0% baseline before January so the line starts at Jan open.
        baseline_month = january_month - pd.offsets.MonthEnd(1)
        baseline = pd.DataFrame(
            0.0,
            index=[baseline_month],
            columns=performance.columns
        )

        performance = pd.concat([baseline, performance])

        return performance, january_month, end_month

    def draw_rolling_line(self):
        if self.period == "YTD":
            performance, start_month, end_month = self.get_ytd_performance()
        else:
            performance, start_month, end_month = self.get_rolling_performance()

        if performance.empty or start_month is None or end_month is None:
            self.ax.set_title("Not enough data for this period")
            self.fig.canvas.draw_idle()
            return

        for sector in performance.columns:
            self.ax.plot(performance.index, performance[sector], label=sector, linewidth=1.8)

        self.ax.axhline(0, linewidth=1)

        if self.period == "YTD":
            title = (
                f"S&P/ASX 200 Sector Rotation - YTD\n"
                f"January {end_month.year} open to {end_month:%b %Y} close"
            )
            y_label = "YTD return %"
        else:
            title = (
                f"S&P/ASX 200 Sector Rotation - {self.period} Month Rolling Open-to-Close Window\n"
                f"{start_month:%b %Y} to {end_month:%b %Y}"
            )
            y_label = "Compounded monthly open-to-close return %"

        self.ax.set_title(title)
        self.ax.set_ylabel(y_label)
        self.ax.set_xlabel("Month")

        self.ax.legend(
            loc="center left",
            bbox_to_anchor=(1.01, 0.5),
            fontsize=7,
            frameon=False,
            borderaxespad=0.0
        )

        self.ax.grid(True, alpha=0.25)

        print(f"Showing: Rolling | {self.get_period_label()} | {start_month:%B %Y} to {end_month:%B %Y}")

    # ------------------------------------------------------------
    # Shared draw/navigation
    # ------------------------------------------------------------

    def draw(self):
        self.ax.clear()

        if self.view_mode == "Monthly":
            self.fig.subplots_adjust(
                left=0.31,
                right=0.96,
                bottom=0.18,
                top=0.88
            )

            self.draw_monthly_bar()

        else:
            self.fig.subplots_adjust(
                left=0.11,
                right=0.74,
                bottom=0.18,
                top=0.88
            )

            self.draw_rolling_line()

        self.view_button.label.set_text(self.get_view_label())
        self.period_button.label.set_text(self.get_period_label())
        self.sort_button.label.set_text("Sort: On" if self.sort_by_gain else "Sort: Off")

        self.fig.canvas.draw_idle()

    def previous(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        if self.view_mode == "Monthly":
            if self.month_index > 0:
                self.month_index -= 1
                self.sync_end_index_from_month_index()
                self.draw()

            return

        if self.period == "YTD":
            if self.end_index > 0:
                self.end_index -= 1
                self.sync_month_index_from_end_index()
                self.draw()

            return

        min_end_index = int(self.period) - 1

        if self.end_index > min_end_index:
            self.end_index -= 1
            self.sync_month_index_from_end_index()
            self.draw()

    def next(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        if self.view_mode == "Monthly":
            if self.month_index < len(self.months) - 1:
                self.month_index += 1
                self.sync_end_index_from_month_index()
                self.draw()

            return

        max_end_index = len(self.monthly_returns.index) - 1

        if self.end_index < max_end_index:
            self.end_index += 1
            self.sync_month_index_from_end_index()
            self.draw()

    def toggle_view_mode(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        current_pos = self.view_modes.index(self.view_mode)
        self.view_mode = self.view_modes[(current_pos + 1) % len(self.view_modes)]

        if self.view_mode == "Monthly":
            self.sync_month_index_from_end_index()
        else:
            self.sync_end_index_from_month_index()

        self.draw()

    def cycle_period(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        # Period only applies to Rolling mode.
        if self.view_mode == "Monthly":
            self.view_mode = "Rolling"

        current_pos = self.period_options.index(self.period) if self.period in self.period_options else 2
        new_period = self.period_options[(current_pos + 1) % len(self.period_options)]

        if new_period == "YTD":
            self.period = "YTD"
        else:
            available_months = len(self.monthly_returns.index)
            self.period = max(1, min(int(new_period), MAX_WINDOW_MONTHS, available_months))

            min_end_index = int(self.period) - 1

            if self.end_index < min_end_index:
                self.end_index = min_end_index

        self.sync_month_index_from_end_index()
        self.draw()

    def set_period(self, period):
        if period == "YTD":
            self.period = "YTD"
            self.view_mode = "Rolling"
            self.draw()
            return

        available_months = len(self.monthly_returns.index)
        self.period = max(1, min(int(period), MAX_WINDOW_MONTHS, available_months))
        self.view_mode = "Rolling"

        min_end_index = int(self.period) - 1

        if self.end_index < min_end_index:
            self.end_index = min_end_index

        self.sync_month_index_from_end_index()
        self.draw()

    def toggle_sort(self, event=None):
        if event is not None and self.is_double_click_event():
            return

        self.sort_by_gain = not self.sort_by_gain
        self.draw()

    def on_key_press(self, event):
        if event.key in ["left", "down"]:
            self.previous()

        elif event.key in ["right", "up"]:
            self.next()

        elif event.key == "v":
            self.toggle_view_mode()

        elif event.key == "w":
            self.cycle_period()

        elif event.key == "s":
            self.toggle_sort()

        elif event.key == "m":
            self.view_mode = "Monthly"
            self.sync_month_index_from_end_index()
            self.draw()

        elif event.key == "3":
            self.set_period(3)

        elif event.key == "6":
            self.set_period(6)

        elif event.key == "1":
            self.set_period(12)

        elif event.key == "2":
            self.set_period(24)

        elif event.key == "4":
            self.set_period(36)

        elif event.key == "y":
            self.set_period("YTD")


# Backwards-compatible alias if anything imports the old rolling viewer class name.
ASXSectorRotationLineViewer = ASXSectorDashboardViewer


class MonthlyASXSectorBarViewer(ASXSectorDashboardViewer):
    def __init__(self, returns: pd.DataFrame):
        monthly_returns = returns.dropna(how="all").sort_index()
        monthly_opens, monthly_closes, full_monthly_returns = get_monthly_open_close_data()

        # Use the caller-provided returns for compatibility with your old monthly script.
        aligned_opens = monthly_opens.reindex(monthly_returns.index)
        aligned_closes = monthly_closes.reindex(monthly_returns.index)

        super().__init__(
            aligned_opens,
            aligned_closes,
            monthly_returns,
            window_months=WINDOW_MONTHS
        )

        self.view_mode = "Monthly"
        self.draw()


def plot_asx_sector_dashboard(
    monthly_opens: pd.DataFrame,
    monthly_closes: pd.DataFrame,
    monthly_returns: pd.DataFrame,
    window_months: int = 12
):
    viewer = ASXSectorDashboardViewer(
        monthly_opens,
        monthly_closes,
        monthly_returns,
        window_months=window_months
    )

    plt.show()
    return viewer


def plot_latest_month(returns: pd.DataFrame):
    viewer = MonthlyASXSectorBarViewer(returns)
    plt.show()
    return viewer


def plot_sector_rotation(
    monthly_opens: pd.DataFrame,
    monthly_closes: pd.DataFrame,
    monthly_returns: pd.DataFrame,
    window_months: int = 12
):
    viewer = ASXSectorDashboardViewer(
        monthly_opens,
        monthly_closes,
        monthly_returns,
        window_months=window_months
    )

    viewer.view_mode = "Rolling"
    viewer.draw()

    plt.show()
    return viewer


def plot_monthly_heatmap(returns: pd.DataFrame, months: int = 12):
    recent = returns.tail(months).T

    fig, ax = plt.subplots(figsize=(13, 6))
    im = ax.imshow(recent.values, aspect="auto")

    ax.set_title(f"S&P/ASX 200 Sector Index Monthly Open-to-Close Returns - Last {months} Completed Months")
    ax.set_yticks(range(len(recent.index)))
    ax.set_yticklabels(recent.index, fontsize=8)

    ax.set_xticks(range(len(recent.columns)))
    ax.set_xticklabels([d.strftime("%b %Y") for d in recent.columns], rotation=45, ha="right")

    for y in range(recent.shape[0]):
        for x in range(recent.shape[1]):
            val = recent.iloc[y, x]

            if pd.notna(val):
                ax.text(x, y, f"{val:+.1f}", ha="center", va="center", fontsize=8)

    fig.colorbar(im, ax=ax, label="Monthly open-to-close return %")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    monthly_opens, monthly_closes, monthly_returns = get_monthly_open_close_data()

    print("\nMonthly open-to-close returns:")
    print(monthly_returns.tail(12).round(2))

    viewer = plot_asx_sector_dashboard(
        monthly_opens,
        monthly_closes,
        monthly_returns,
        window_months=WINDOW_MONTHS
    )