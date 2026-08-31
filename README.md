# tlserver
tlserver is a small HTTP service that mimics Sugoi Offline.

## Requirements
- Python 3.11+
- Dependencies from `requirements.txt` (ctranslate2 and sentencepiece need their native libraries; install CUDA if you want GPU support for the offline translator)
- Optional:
  - `uv` for an easier experience

## Install
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```
If you use `uv`, run `uv sync` instead.

## Run
```powershell
uv run tlserver
# or:
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
