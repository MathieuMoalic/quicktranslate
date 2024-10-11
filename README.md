# Deeplinux:

Using the Deepl API, this python script will grab the selected text with `xclip` and make a translate request to the API. It will show the translated text in a small popup window next to the mouse cursor. Left click to dismiss it.
You need to create a [Deepl account](https://www.deepl.com/pro-api?cta=header-pro-api), the API is free for 500 000 characters per months. If you have a pro plan, change the API endpoint accordingly in the configuration file.


## Configuration

You need to create a config file at `$XDG_CONFIG_HOME/deeplinux/deeplinux.toml` (usually `$HOME/.config/deeplinux/deeplinux.toml`) and add the following:

```toml
[quicktranslate]
DEEPL_AUTH_KEY = "api_key_here"
DEEPL_API_ENDPOINT = "https://api-free.deepl.com/v2/translate"
TARGET_LANG = "EN"
```

## Usage
For example, on Hyprland, you can bind it as:
`$mod, T, exec, quicktranslate`


### Logs
Logs are located in `$XDG_STATE_HOME/deeplinux/deeplinux.log` (usually `$HOME/.local/state/deeplinux/deeplinux.log`)