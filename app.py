# app.py
from flask import Flask, request, render_template_string, abort
from pathlib import Path
import os

# CONFIG (env-driven)
BIND_IP = os.getenv("BIND_IP", "0.0.0.0")
PORT = int(os.getenv("PORT", 8085))
REQUIRE_TOKEN = os.getenv("REQUIRE_TOKEN", "true").lower() == "true"
TOKEN = os.getenv("PHONE_DROP_TOKEN", "token")

# New: dual targets from env
WINDOWS_TARGET_DIR = Path(
    os.getenv("WINDOWS_TARGET_DIR", "/mnt/c/Users/jon/Desktop/phone-drop")
)
WSL_TARGET_DIR = Path(os.getenv("WSL_TARGET_DIR", "/home/jon/phone-drop/files"))

# Ensure both exist (best-effort)
WINDOWS_TARGET_DIR.mkdir(parents=True, exist_ok=True)
WSL_TARGET_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

PAGE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>WSL Text Drop</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      body { font-family: system-ui, sans-serif; margin: 24px; max-width: 720px; }
      input, textarea, button, select { width: 100%; font-size: 16px; margin: 8px 0; }
      textarea { height: 40vh; }
      .ok { color: green; }
      .err { color: red; }
      .row { display: flex; gap: 8px; }
      .row > * { flex: 1; }
      label { font-weight: 600; display: block; margin-top: 8px; }
      small { color: #555; }
      code { background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
    </style>
  </head>
  <body>
    <h1>WSL Text Drop</h1>
    {% if message %}
      <p class="{{'ok' if ok else 'err'}}">{{ message }}</p>
    {% endif %}
    <form method="POST" action="/">
      {% if require_token %}
        <input type="password" name="token" placeholder="Token" required />
      {% endif %}

      <label for="target_choice">Save to:</label>
      <select name="target_choice" id="target_choice">
        <option value="windows" {{ 'selected' if target_choice == 'windows' else '' }}>Windows</option>
        <option value="wsl" {{ 'selected' if target_choice == 'wsl' else '' }}>WSL</option>
      </select>
      <small>
        Windows: <code>{{ windows_dir }}</code><br />
        WSL: <code>{{ wsl_dir }}</code>
      </small>

      <div class="row">
        <input name="filename" placeholder="filename.txt" required />
        <select name="mode">
          <option value="write">Write</option>
          <option value="append">Append</option>
        </select>
      </div>
      <textarea name="content" placeholder="Paste text here" required></textarea>
      <button type="submit">Save</button>
    </form>
    <hr />
    <p>Current selection target path: <code>{{ current_target_dir }}</code></p>
  </body>
</html>
"""

def sanitize_filename(name: str) -> str:
    # Simple, opinionated sanitizer to avoid path traversal and weird chars
    name = name.strip().replace("\\", "/")
    name = name.split("/")[-1]  # basename only
    allowed = "".join(ch for ch in name if ch.isalnum() or ch in "._- ")
    return allowed[:128] if allowed else "untitled.txt"

def resolve_target(choice: str) -> Path:
    if (choice or "").lower() == "wsl":
        return WSL_TARGET_DIR
    # default to windows
    return WINDOWS_TARGET_DIR

@app.get("/")
def index_get():
    # Default choice = windows
    choice = "windows"
    target_dir = resolve_target(choice)
    return render_template_string(
        PAGE,
        message=None,
        ok=True,
        require_token=REQUIRE_TOKEN,
        target_choice=choice,
        current_target_dir=str(target_dir),
        windows_dir=str(WINDOWS_TARGET_DIR),
        wsl_dir=str(WSL_TARGET_DIR),
    )

@app.post("/")
def index_post():
    if REQUIRE_TOKEN:
        token = request.form.get("token", "")
        if token != TOKEN:
            abort(403)

    filename = request.form.get("filename", "")
    content = request.form.get("content", "")
    mode = request.form.get("mode", "write")
    target_choice = request.form.get("target_choice", "windows")

    safe_name = sanitize_filename(filename)
    target_dir = resolve_target(target_choice)

    if not content.strip():
        return render_template_string(
            PAGE,
            message="Content is empty.",
            ok=False,
            require_token=REQUIRE_TOKEN,
            target_choice=target_choice,
            current_target_dir=str(target_dir),
            windows_dir=str(WINDOWS_TARGET_DIR),
            wsl_dir=str(WSL_TARGET_DIR),
        )

    dest = target_dir / safe_name
    try:
        if mode == "append" and dest.exists():
            dest.write_text(
                dest.read_text(encoding="utf-8") + content, encoding="utf-8"
            )
        else:
            dest.write_text(content, encoding="utf-8")
        msg = f"Saved to {dest}"
        ok = True
    except Exception as e:
        msg = f"Failed to write: {e}"
        ok = False

    return render_template_string(
        PAGE,
        message=msg,
        ok=ok,
        require_token=REQUIRE_TOKEN,
        target_choice=target_choice,
        current_target_dir=str(target_dir),
        windows_dir=str(WINDOWS_TARGET_DIR),
        wsl_dir=str(WSL_TARGET_DIR),
    )

if __name__ == "__main__":
    print(f"Windows target: {WINDOWS_TARGET_DIR}")
    print(f"WSL target:     {WSL_TARGET_DIR}")
    print(f"Open from phone: http://<WSL_IP>:{PORT}")
    if REQUIRE_TOKEN:
        print("Set PHONE_DROP_TOKEN env var to customize token.")
    app.run(host=BIND_IP, port=PORT, debug=False)
