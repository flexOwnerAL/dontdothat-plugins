# dontdothat-plugins

Plugins for **DontDoThat** module (TETKO-UserBot).

## Install

From DontDoThat:

```

.dothat plugin install <name>

```

Or manually — reply to a `.py` file with:

```

.dothat install

```

## Repo structure

```

.
├── README.md
├── index.json          # plugin registry (DontDoThat reads this)
├── schemas/
│   └── plugin.schema.json
└── plugins/
├── LiteFlare.py
└── ...

```

## Available plugins

| Name | Version | Tags | Description |
|------|---------|------|-------------|
| _(none yet)_ | | | |

## Write your own plugin

A plugin is a single `.py` file placed in `plugins/`.

### 1. Metadata

At the top of the file — a `PLUGIN` dict:

```python
PLUGIN = {
    "name": "MyPlugin",
    "version": "1.0.0",
    "author": "@you",
    "description": "Short description shown in .dothat plugin info",
    "hooks": ["on_blocked", "after_fetch"],
    "min_core": "4.0.0",
    "tags": ["example"],
}
```

Required keys: name, version, hooks.
Optional: author, description, min_core, tags, signature.

2. Hooks

Implement only the hooks you declared:

Hook When called Can return
before_fetch(ctx) before HTTP request str (new URL), False (abort), None (continue)
after_fetch(ctx) after HTTP request str (replace HTML), None
on_blocked(ctx) captcha/Cloudflare detected str (HTML), None
on_js_required(ctx) JS-required page detected str (HTML), None
on_error(ctx) network error str (HTML), None
on_result(ctx) after successful parse None (mutate ctx["result"] in place)

ctx is a dict. Contents vary per hook:

· ctx["url"] — current URL
· ctx["name"] — source name
· ctx["query"] — search query
· ctx["site"] — source config dict
· ctx["html"] — response body (for after_fetch, on_blocked, on_js_required)
· ctx["reason"] — "captcha" / "cloudflare" (for on_blocked)
· ctx["error"] — exception string (for on_error)
· ctx["result"] — result dict (for on_result)

3. Example

```python
PLUGIN = {
    "name": "Example",
    "version": "1.0.0",
    "author": "@you",
    "description": "Does nothing useful.",
    "hooks": ["on_blocked"],
    "min_core": "4.0.0",
}

async def on_blocked(ctx):
    if ctx.get("reason") != "captcha":
        return None
    url = ctx["url"]
    # ... your logic ...
    return None
```

Sync functions are also accepted — DontDoThat awaits both.

4. Register in index

Add an entry to index.json:

```json
{
    "name": "Example",
    "file": "plugins/Example.py",
    "version": "1.0.0",
    "author": "@you",
    "description": "Does nothing useful.",
    "min_core": "4.0.0",
    "tags": ["example"],
    "sha256": ""
}
```

sha256 can be left empty. DontDoThat can refresh it later, or fill it manually:

```bash
sha256sum plugins/Example.py | cut -d' ' -f1
```

5. Test locally

Copy the .py to your bot and:

```
.dothat install     (reply to the file)
.dothat plugins
.dothat plugin info Example
```

Rules

· Do not import subprocess, os.system, ctypes, socket for outgoing connections outside of curl_cffi / httpx / urllib. The core will warn the owner.
· Do not write to paths outside data/dontdothat_plugins/.
· Hooks must return within 30 seconds or they will be killed.
· Keep PLUGIN["name"] unique across the registry.

License

MIT
