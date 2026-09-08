# tlserver

> [!IMPORTANT]
> This is the developer documentation.
> If you are a user looking for the downloads: [Releases](https://github.com/de-odex/tlserver/releases/)

tlserver is a small HTTP service that mimics Sugoi Offline.

## Requirements

Easiest:

- uv

Alternative:

- Python 3.11+
- Dependencies from `requirements.txt`
  - ctranslate2 and sentencepiece need their native libraries.
    Install CUDA if you want GPU support for the offline translator

## Install

Easiest:

```powershell
uv sync
```

Alternative:

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Run

Easiest:

```powershell
uv run tlserver
```

Alternative:

```powershell
python -m tlserver
```

## Configure

tlserver loads settings in this order:

1. TLSERVER_CONFIG_PATH environment variable
2. `XDG_CONFIG_HOME/tlserver/config.toml` or `%APPDATA%\tlserver\config.toml`
3. The directory containing `tlserver.exe` when using a frozen executable
4. Current working directory (`./config.toml`)

A sample configuration file can be found in `config.sample.toml`

## Troubleshooting

- Keep `debug = true` while testing to see detailed logs.
- If ports collide or config is invalid, tlserver will crash with a validation error.
- Ensure the referenced model/tokenizer files exist; the offline translator will fail to start if they are missing.
- For LLM translators, confirm the API server is reachable and the API key is correct.
