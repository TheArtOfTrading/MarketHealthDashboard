import sys
import traceback
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import importlib
import threading
import queue
import time

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


def get_local_timestamp() -> str:
    """
    Return a timestamp in the user's local machine timezone.

    datetime.now() can be ambiguous in logs because it does not include a timezone.
    astimezone() attaches the local timezone/offset reported by Windows/macOS/Linux,
    so the log clearly shows local time instead of looking like UTC.
    """
    try:
        return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S LOCAL")


def write_error_log(title: str, error_text: str):
    with open(APP_LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"{get_local_timestamp()} - {title}\n")
        f.write("=" * 80 + "\n")
        f.write(error_text)
        f.write("\n")


def write_console_log_header():
    try:
        with open(APP_CONSOLE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"{get_local_timestamp()} - Trading Dashboard session started\n")
            f.write("=" * 80 + "\n")
    except Exception:
        pass


def log_uncaught_exception(exc_type, exc_value, exc_traceback):
    error_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    write_error_log("Uncaught crash", error_text)


def check_norgate_connection_worker(result_queue: queue.Queue):
    try:
        import norgatedata

        # Lightweight smoke test.
        # This can hang on some machines if Norgate is unavailable, so it runs
        # in a daemon background thread after the GUI has already appeared.
        norgatedata.watchlists()

        result_queue.put((True, ""))

    except Exception:
        error_text = traceback.format_exc()
        write_error_log("Norgate Data connection failed", error_text)
        result_queue.put((False, error_text))


# Must happen before any dashboard module imports norgatedata.
setup_safe_console_streams()
write_console_log_header()
sys.excepthook = log_uncaught_exception


class TradingDashboardApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("520x740")
        self.root.resizable(False, False)

        # Catch errors from Tkinter callbacks too.
        self.root.report_callback_exception = self.handle_tkinter_exception

        self.norgate_check_queue = queue.Queue()
        self.norgate_check_start_time = time.monotonic()

        self.build_loading_screen()

        # Start the Norgate check after the Tk window has had a chance to draw.
        # This prevents the EXE from appearing to do nothing if Norgate hangs.
        self.root.after(100, self.start_norgate_check)

    def handle_tkinter_exception(self, exc_type, exc_value, exc_traceback):
        error_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        write_error_log("Tkinter callback error", error_text)

        messagebox.showerror(
            "Application Error",
            f"Something went wrong:\n\n{exc_value}\n\n"
            f"The full error was saved here:\n\n{APP_LOG_PATH}"
        )

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def build_loading_screen(self):
        self.clear_root()

        title = tk.Label(
            self.root,
            text="Trading Dashboard",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(pady=(90, 10))

        status = tk.Label(
            self.root,
            text="Checking Norgate Data connection...",
            font=("Segoe UI", 11)
        )
        status.pack(pady=(0, 12))

        note = tk.Label(
            self.root,
            text="If this takes too long, Norgate Data may not be responding.",
            font=("Segoe UI", 9),
            fg="gray"
        )
        note.pack(pady=(0, 20))

        exit_button = tk.Button(
            self.root,
            text="Exit",
            font=("Segoe UI", 11),
            width=20,
            height=2,
            command=self.root.destroy
        )
        exit_button.pack(pady=(10, 0))

        log_label = tk.Label(
            self.root,
            text=f"Error log: {APP_LOG_PATH}",
            font=("Segoe UI", 8),
            fg="gray"
        )
        log_label.pack(pady=(30, 0))

    def start_norgate_check(self):
        worker = threading.Thread(
            target=check_norgate_connection_worker,
            args=(self.norgate_check_queue,),
            daemon=True
        )

        worker.start()

        self.root.after(250, self.poll_norgate_check)

    def poll_norgate_check(self):
        try:
            norgate_ok, norgate_error = self.norgate_check_queue.get_nowait()

        except queue.Empty:
            elapsed_seconds = time.monotonic() - self.norgate_check_start_time

            if elapsed_seconds >= 15:
                write_error_log(
                    "Norgate Data connection timed out",
                    "The startup Norgate Data connection check did not complete within 15 seconds."
                )

                messagebox.showerror(
                    "Norgate Data Connection Timed Out",
                    "This app could not confirm a Norgate Data connection within 15 seconds.\n\n"
                    "Please check that:\n\n"
                    "- Norgate Data is installed\n"
                    "- Norgate Data Updater can open normally\n"
                    "- Your subscription is active\n"
                    "- Your local Norgate database is available\n\n"
                    f"The timeout was saved here:\n\n{APP_LOG_PATH}"
                )

                self.root.destroy()
                return

            self.root.after(250, self.poll_norgate_check)
            return

        if not norgate_ok:
            messagebox.showerror(
                "Norgate Data Connection Failed",
                "This app could not connect to Norgate Data.\n\n"
                "Please check that:\n\n"
                "- Norgate Data is installed\n"
                "- Your Norgate Data subscription is active\n"
                "- The Norgate Python package is installed\n"
                "- Norgate Data Updater has successfully downloaded data\n\n"
                f"The full error was saved here:\n\n{APP_LOG_PATH}"
            )

            self.root.destroy()
            return

        self.build_home()

    def build_home(self):
        self.clear_root()

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
        self.add_button("Forex Dashboard", self.open_forex_dashboard)
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
                f"If this happened while loading market data, the most likely causes are:\n\n"
                f"- Missing Norgate data package\n"
                f"- Unavailable symbol/watchlist\n"
                f"- Norgate Data not updated\n"
                f"- Norgate Python API issue\n\n"
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


    def open_forex_dashboard(self):
        forex_dashboard = self.import_dashboard_module("forex_dashboard")

        viewer = forex_dashboard.ForexDashboardViewer()

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