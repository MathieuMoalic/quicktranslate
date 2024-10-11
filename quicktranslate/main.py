#!/usr/bin/env python3
import argparse
import logging
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Dict

import requests
import tomllib as tomli  # For Python 3.11+
from xdg_base_dirs import xdg_config_home, xdg_state_home


class QuickTranslateApp:
    def __init__(self) -> None:
        self.setup_logging()
        self.load_config()
        self.args: argparse.Namespace = self.parse_arguments()
        self.target_lang: str = (
            self.args.lang.upper() if self.args.lang else self.TARGET_LANG
        )

    def setup_logging(self) -> None:
        log_dir: Path = xdg_state_home().joinpath("quicktranslate")
        log_dir.mkdir(parents=True, exist_ok=True)
        LOG_FILE: Path = log_dir.joinpath("quicktranslate.log")
        logging.basicConfig(
            filename=str(LOG_FILE),
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def load_config(self) -> None:
        config_path: Path = xdg_config_home().joinpath(
            "quicktranslate/quicktranslate.toml"
        )
        try:
            with open(config_path, "rb") as f:
                config: Dict[str, Any] = tomli.load(f)
        except FileNotFoundError as e:
            logging.error(f"Configuration file not found at '{config_path}'")
            print(f"Error: {e}")
            sys.exit(1)
        except tomli.TOMLDecodeError as e:
            logging.error(f"Error parsing configuration file: {e}")
            print(f"Configuration Error: {e}")
            sys.exit(1)
        try:
            self.DEEPL_AUTH_KEY: str = config["quicktranslate"]["DEEPL_AUTH_KEY"]
            self.DEEPL_API_ENDPOINT: str = config["quicktranslate"][
                "DEEPL_API_ENDPOINT"
            ]
            self.TARGET_LANG: str = config["quicktranslate"]["TARGET_LANG"]
        except KeyError as e:
            logging.error(f"Missing configuration key: {e}")
            print(f"Configuration Error: Missing key {e}")
            sys.exit(1)

    def parse_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="QuickTranslate")
        parser.add_argument(
            "--lang", type=str, help="Target language code (e.g., DE, FR)"
        )
        parser.add_argument("--version", action="version", version="QuickTranslate 1.0")
        return parser.parse_args()

    def get_selected_text(self) -> str:
        try:
            # Use xclip to get the selected text from the primary selection buffer
            text: str = subprocess.check_output(
                ["xclip", "-o", "-selection", "primary"]
            ).decode("utf-8")
            if not text.strip():
                logging.error("No text is selected or the selection is empty.")
                self.display_error("No text found in the current selection.")
                sys.exit(1)
            return text
        except subprocess.CalledProcessError as e:
            logging.error(f"xclip command failed: {e}")
            self.display_error(
                "Failed to get selected text. Ensure xclip is installed."
            )
            sys.exit(1)
        except FileNotFoundError:
            logging.error("xclip is not installed or not found in PATH.")
            self.display_error(
                "xclip is not installed. Please install it and try again."
            )
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error when getting selected text: {e}")
            self.display_error(f"Error: {e}")
            sys.exit(1)

    def translate_text(self, text: str) -> str:
        headers: Dict[str, str] = {
            "Authorization": f"DeepL-Auth-Key {self.DEEPL_AUTH_KEY}"
        }
        data: Dict[str, str] = {"text": text, "target_lang": self.target_lang}

        try:
            response: requests.Response = requests.post(
                self.DEEPL_API_ENDPOINT, headers=headers, data=data
            )
            response.raise_for_status()
            return response.json()["translations"][0]["text"]
        except requests.exceptions.HTTPError as e:
            response = e.response
            if response.status_code == 429:
                message = "Rate limit exceeded. Please try again later."
            elif response.status_code == 456:
                message = "Quota exceeded. Upgrade your plan."
            else:
                message = f"HTTP error {response.status_code}: {response.reason}"
            logging.error(message)
            self.display_error(message)
            sys.exit(1)
        except Exception as e:
            logging.error(f"Translation failed: {e}")
            self.display_error("Translation failed due to an unexpected error.")
            sys.exit(1)

    def display_translation(self, text: str) -> None:
        # Dracula color theme
        BG_COLOR = "#282a36"
        FG_COLOR = "#f8f8f2"
        BORDER_COLOR = "#6272a4"

        root: tk.Tk = tk.Tk()
        root.title("Translation")
        root.overrideredirect(True)
        root.configure(bg=BORDER_COLOR)

        # Create label
        label: ttk.Label = ttk.Label(
            root,
            text=text,
            padding=10,
            wraplength=400,
            background=BG_COLOR,
            foreground=FG_COLOR,
        )
        label.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)

        # Position window
        root.update_idletasks()
        width: int = label.winfo_width() + 4
        height: int = label.winfo_height() + 4
        screen_width: int = root.winfo_screenwidth()
        screen_height: int = root.winfo_screenheight()
        x: int = (screen_width - width) // 2
        y: int = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")

        # Bind events for closing window
        root.bind("<Escape>", lambda _: root.destroy())
        root.bind("<KeyPress-q>", lambda _: root.destroy())
        root.bind("<Button-3>", lambda _: root.destroy())
        root.after(100000, root.destroy)  # Auto-close after 100 seconds

        self.root = root
        root.bind("<ButtonPress-1>", self.start_move)
        root.bind("<B1-Motion>", self.do_move)

        root.mainloop()

    def start_move(self, event: tk.Event) -> None:
        # Store the offset when the dragging starts
        self._x = event.x
        self._y = event.y

    def do_move(self, event: tk.Event) -> None:
        # Calculate new window position using root coordinates and the initial click offset
        x = event.x_root - self._x
        y = event.y_root - self._y
        self.root.geometry(f"+{x}+{y}")

    def copy_to_clipboard(self, event: tk.Event) -> None:
        root: tk.Tk = event.widget.master
        text: str = event.widget.cget("text")
        root.clipboard_clear()
        root.clipboard_append(text)
        logging.info("Translation copied to clipboard.")

    def display_error(self, message: str) -> None:
        root: tk.Tk = tk.Tk()
        root.title("Error")
        label: ttk.Label = ttk.Label(root, text=message, padding=10)
        label.pack()
        root.after(5000, root.destroy)
        root.mainloop()

    def run(self) -> None:
        selected_text: str = self.get_selected_text()
        translated_text: str = self.translate_text(selected_text)
        self.display_translation(translated_text)
