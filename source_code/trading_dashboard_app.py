import sys
import traceback
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import importlib

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.widgets import Button as MplButton


APP_TITLE = "Trading Dashboard"

APP_LOG_PATH = Path.home() / "TradingDashboard_error_log.txt"
APP_CONSOLE_LOG_PATH = Path.home() / "TradingDashboard_console_log.txt"

_STDOUT_LOG_HANDLE = None
_STDERR_LOG_HANDLE = None


def setup_safe_console_streams():
    """
    PyInstaller --windowed can set sys.stdout / sys.stderr to None.
    Some libraries, including norgatedata/logbook, expect stderr to exist.
    This redirects missing console streams to a log file instead.
    """
    global _STDOUT_LOG_HANDLE
    global _STDERR_LOG_HANDLE

    try:
        if sys.stdout is None:
            _STDOUT_LOG_HANDLE = open(APP_CONSOLE_LOG_PATH, "a", encoding="utf-8", buffering=1)
            sys.stdout = _STDOUT_LOG_HANDLE

        if sys.stderr is None:
            _STDERR_LOG_HANDLE = open(APP_CONSOLE_LOG_PATH, "a", encoding="utf-8", buffering=1)
            sys.stderr = _STDERR_LOG_HANDLE

    except Exception:
        # Last-resort fallback. Do not allow logging setup to kill app startup.
        pass


def write_error_log(title: str, error_text: str):
    with open(APP_LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} - {title}\n")
        f.write("=" * 80 + "\n")
        f.write(error_text)
        f.write("\n")


def log_uncaught_exception(exc_type, exc_value, exc_traceback):
    error_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    write_error_log("Uncaught crash", error_text)


# Must happen before any dashboard module imports norgatedata.
setup_safe_console_streams()
sys.excepthook = log_uncaught_exception


class TradingDashboardApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("520x680")
        self.root.resizable(False, False)

        # Catch errors from Tkinter callbacks too.
        self.root.report_callback_exception = self.handle_tkinter_exception

        self.build_home()

    def handle_tkinter_exception(self, exc_type, exc_value, exc_traceback):
        error_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        write_error_log("Tkinter callback error", error_text)

        messagebox.showerror(
            "Application Error",
            f"Something went wrong:\n\n{exc_value}\n\n"
            f"The full error was saved here:\n\n{APP_LOG_PATH}"
        )

    def build_home(self):
        title = tk.Label(
            self.root,
            text="Trading Dashboard",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(pady=(28, 6))

        subtitle = tk.Label(
            self.root,
            text="Select a dashboard to open",
            font=("Segoe UI", 10)
        )
        subtitle.pack(pady=(0, 22))

        self.add_button("Market Health", self.open_market_health)
        self.add_button("US Sectors", self.open_us_sector_dashboard)
        self.add_button("ASX Sectors", self.open_asx_sector_dashboard)
        self.add_button("Global Indicies", self.open_global_indexes_monthly)
        self.add_button("Momentum Stocks", self.open_momentum_stocks)

        exit_button = tk.Button(
            self.root,
            text="Exit",
            font=("Segoe UI", 11),
            width=32,
            height=2,
            command=self.root.destroy
        )
        exit_button.pack(pady=(22, 0))

        log_label = tk.Label(
            self.root,
            text=f"Error log: {APP_LOG_PATH}",
            font=("Segoe UI", 8),
            fg="gray"
        )
        log_label.pack(pady=(14, 0))

        console_log_label = tk.Label(
            self.root,
            text=f"Console log: {APP_CONSOLE_LOG_PATH}",
            font=("Segoe UI", 8),
            fg="gray"
        )
        console_log_label.pack(pady=(4, 0))

    def add_button(self, text: str, command):
        button = tk.Button(
            self.root,
            text=text,
            font=("Segoe UI", 11),
            width=32,
            height=2,
            command=lambda: self.run_dashboard(command)
        )
        button.pack(pady=6)

    def import_dashboard_module(self, module_name: str):
        try:
            return importlib.import_module(module_name)

        except Exception:
            error_text = traceback.format_exc()
            write_error_log(f"Failed to import module: {module_name}", error_text)

            raise RuntimeError(
                f"Could not load dashboard module '{module_name}'.\n\n"
                f"This usually means one of these is missing:\n"
                f"- the Python file itself\n"
                f"- a bundled PyInstaller dependency\n"
                f"- norgatedata / Norgate Data components\n\n"
                f"Full error saved to:\n{APP_LOG_PATH}\n\n"
                f"Console output saved to:\n{APP_CONSOLE_LOG_PATH}"
            )

    def run_dashboard(self, dashboard_function):
        try:
            self.root.withdraw()
            dashboard_function()

        except Exception as e:
            error_text = traceback.format_exc()

            try:
                print(error_text)
            except Exception:
                pass

            write_error_log("Dashboard error", error_text)

            messagebox.showerror(
                "Dashboard Error",
                f"Something went wrong:\n\n{e}\n\n"
                f"The full error was saved here:\n\n{APP_LOG_PATH}\n\n"
                f"Console output was saved here:\n\n{APP_CONSOLE_LOG_PATH}"
            )

        finally:
            plt.close("all")
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()

    def add_home_button(self, fig):
        # Adds a Home button to the top-right of the Matplotlib chart.
        # Clicking it closes all Matplotlib figures, which returns to the Tkinter home menu.
        home_ax = fig.add_axes([0.875, 0.925, 0.095, 0.045])
        home_button = MplButton(home_ax, "Home")

        def go_home(event=None):
            plt.close("all")

        home_button.on_clicked(go_home)

        # Keep a strong reference so Matplotlib does not garbage-collect the button.
        fig._home_button = home_button

    def show_matplotlib_dashboard(self, viewer):
        self.add_home_button(viewer.fig)
        plt.show()

    # ------------------------------------------------------------
    # Dashboard launchers
    # ------------------------------------------------------------

    def open_market_health(self):
        market_health_dashboard = self.import_dashboard_module("market_health_dashboard")

        viewer = market_health_dashboard.MarketHealthDashboardViewer()

        self.show_matplotlib_dashboard(viewer)

    def open_us_sector_dashboard(self):
        us_sector_dashboard = self.import_dashboard_module("us_sector_dashboard")

        monthly_opens, monthly_closes, monthly_returns = us_sector_dashboard.get_monthly_open_close_data()

        viewer = us_sector_dashboard.USSectorDashboardViewer(
            monthly_opens,
            monthly_closes,
            monthly_returns,
            window_months=us_sector_dashboard.WINDOW_MONTHS
        )

        self.show_matplotlib_dashboard(viewer)

    def open_asx_sector_dashboard(self):
        asx_sector_dashboard = self.import_dashboard_module("asx_sector_dashboard")

        monthly_opens, monthly_closes, monthly_returns = asx_sector_dashboard.get_monthly_open_close_data()

        viewer = asx_sector_dashboard.ASXSectorDashboardViewer(
            monthly_opens,
            monthly_closes,
            monthly_returns,
            window_months=asx_sector_dashboard.WINDOW_MONTHS
        )

        self.show_matplotlib_dashboard(viewer)

    def open_global_indexes_monthly(self):
        global_indexes_monthly = self.import_dashboard_module("global_indexes_monthly")

        monthly_opens, monthly_closes = global_indexes_monthly.get_monthly_ohlc()

        monthly_returns, yearly_returns, ytd_returns = global_indexes_monthly.calculate_return_tables(
            monthly_opens,
            monthly_closes
        )

        viewer = global_indexes_monthly.MonthlyIndexBarViewer(
            monthly_returns,
            yearly_returns,
            ytd_returns
        )

        self.show_matplotlib_dashboard(viewer)

    def open_momentum_stocks(self):
        momentum_stocks = self.import_dashboard_module("momentum_stocks")

        viewer = momentum_stocks.TopStockRankingViewer()

        self.show_matplotlib_dashboard(viewer)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TradingDashboardApp()
    app.run()