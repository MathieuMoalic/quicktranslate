#!/usr/bin/env python3
import subprocess
import requests
import tkinter as tk
from tkinter import ttk
from xdg_base_dirs import xdg_config_home
import sys
import configparser
from pathlib import Path

def xdg_config_home():
    # Implementation of xdg_config_home
    return Path.home() / ".config"

try:
    config = configparser.ConfigParser()
    config_path = xdg_config_home().joinpath("quicktranslate/quicktranslate.toml")

    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found at '{config_path}'")

    config.read(config_path)

    DEEPL_AUTH_KEY = config['quicktranslate'].get('deepl_auth_key')
    if DEEPL_AUTH_KEY is None:
        raise KeyError("Missing 'deepl_auth_key' in 'quicktranslate' section of the configuration file.")

    DEEPL_API_ENDPOINT = config['quicktranslate'].get('deepl_api_endpoint')
    if DEEPL_API_ENDPOINT is None:
        raise KeyError("Missing 'deepl_api_endpoint' in 'quicktranslate' section of the configuration file.")

    TARGET_LANG = config['quicktranslate'].get('TARGET_LANG')
    if TARGET_LANG is None:
        raise KeyError("Missing 'TARGET_LANG' in 'quicktranslate' section of the configuration file.")

    # Your logic here

except FileNotFoundError as e:
    print(f"Error: {e}")
    sys.exit(1)
except KeyError as e:
    print(f"Configuration Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)

def get_selected_text():
    return subprocess.check_output(["xclip", "-o", "-selection", "primary"]).decode(
        "utf-8"
    )


def translate_text(text):
    headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_AUTH_KEY}"}
    data = {"text": text, "target_lang": TARGET_LANG}

    response = requests.post(DEEPL_API_ENDPOINT, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["translations"][0]["text"]
    else:
        raise Exception(f"Error: {response.text}")


def display_translation(text):
    root = tk.Tk()
    root.title("Translation")

    # Dracula color theme
    BG_COLOR = "#282a36"
    FG_COLOR = "#f8f8f2"
    BORDER_COLOR = "#6272a4"

    # Remove window decorations to make it lightweight
    root.overrideredirect(True)
    root.configure(bg=BORDER_COLOR)

    # Set the window near the mouse cursor
    x, y = root.winfo_pointerx(), root.winfo_pointery()

    # Create a label to display the translation
    label = ttk.Label(
        root,
        text=text,
        padding=10,
        background=BG_COLOR,
        foreground=FG_COLOR,
        wraplength=200,
    )
    label.pack(
        padx=2, pady=2, fill=tk.BOTH, expand=True
    )  # padding for the border effect

    # Adjust window size to fit text
    root.update_idletasks()
    width = label.winfo_width() + 4  # 4 for the border effect
    height = label.winfo_height() + 4

    # Ensure the tooltip does not extend beyond screen boundaries
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = x if x + width < screen_width else screen_width - width
    y = y if y + height < screen_height else screen_height - height

    root.geometry(f"{width}x{height}+{x}+{y}")

    # Close the window on any keypress or mouse click
    root.bind("<Key>", lambda e: root.destroy())
    root.bind("<Button>", lambda e: root.destroy())

    root.mainloop()


def main():
    selected_text = get_selected_text()
    translated_text = translate_text(selected_text)
    display_translation(translated_text)


