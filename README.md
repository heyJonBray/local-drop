# local-drop

Extremely lightweight Flask app to drop text from your phone to your machine over LAN. Opens a form with filename, content, and a target (two selectable directories). Writes files to your chosen directory. Works on Linux and WSL.

## Features
- Paste text, choose filename, write/append
- Two target directories via dropdown (configured with env vars)
- Optional token to prevent drive‑by writes
- Single Python process with negligible resource usage

---

## Setup

Prereqs (Ubuntu/Debian-like):

```bash
sudo apt update
sudo apt install -y python3-venv
```

Install:

```bash
git clone https://github.com/heyjonbray/local-drop.git
cd local-drop
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install flask
```

Set optional env vars (app uses safe defaults, override as needed):

```bash
export BIND_IP="0.0.0.0"
export PORT="8085"
# Defaults if unset (inside your home):
#   WINDOWS_TARGET_DIR -> $HOME/share/windows
#   WSL_TARGET_DIR     -> $HOME/share/wsl
# Override if desired:
# export WINDOWS_TARGET_DIR="$HOME/share/windows"
# export WSL_TARGET_DIR="$HOME/share/wsl"

# Auth (recommended on shared LANs)
export REQUIRE_TOKEN="true"
export PHONE_DROP_TOKEN="change-me"
```

Run:

```bash
python app.py
```

Open from phone (same Wi‑Fi/LAN):
- Find your IP (generic):

```bash
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n1
```

- Visit: `http://<LAN_IP>:8085`, bookmark for convenience.

---

## Systemd user service (optional, auto-start)

Create a user unit:

```bash
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/phone-drop.service <<'EOF'
[Unit]
Description=Phone text drop (Flask)

[Service]
ExecStart=%h/local-drop/.venv/bin/python %h/local-drop/app.py
WorkingDirectory=%h/local-drop
Environment=BIND_IP=0.0.0.0
Environment=PORT=8085
# Defaults fall back to $HOME/share/{windows,wsl} if unset:
# Environment=WINDOWS_TARGET_DIR=%h/share/windows
# Environment=WSL_TARGET_DIR=%h/share/wsl
Environment=REQUIRE_TOKEN=true
Environment=PHONE_DROP_TOKEN=change-me
Restart=on-failure

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now phone-drop.service
```

Helpers to start/stop/restart and check status/logs are in `helpers/.bash_functions` and can be added to your `~/.bashrc` or `~/.bash_functions`

Firewall (if applicable):
```bash
# Ubuntu with ufw:
sudo ufw allow 8085/tcp
```

---

## WSL Notes

WSL uses pretty much the same setup as Linux, with a few minor differences.

- Enable systemd in WSL
  - Edit `/etc/wsl.conf`:
    ```
    [boot]
    systemd=true
    ```
  - From Windows PowerShell: `wsl --shutdown`, then reopen your distro.

- Target Windows filesystem by setting:
  ```bash
  export WINDOWS_TARGET_DIR="/mnt/c/Users/<you>/Desktop/phone-drop"
  ```
  Otherwise, defaults stay inside your WSL home.

- Find the WSL IP:
  ```bash
  ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'
  ```
  Visit `http://<WSL_IP>:8085` from your phone. If you prefer using the Windows host IP/hostname instead, ensure Windows Defender Firewall allows inbound traffic on that port.

### Windows Firewall Rules

If you can't connect to the site from your phone, make sure Windows Defender Firewall allows connections on that port:

1. Open "Windows Defender Firewall with Advanced Security"
2. Go to "Inbound Rules"
3. "New Rule..."
4. Select "Port" > "TCP" > "Specific local ports: `8085`" > "Allow the connection" > check all boxes
5. Give it a descriptive name like "Local Drop Port 8085"

After saving changes you should be able to open your browser to `http://<WSL_IP>:8085` and start using local-drop

---

## Configuration

Environment variables (optional; shown with defaults):
- BIND_IP: 0.0.0.0
- PORT: 8085
- WINDOWS_TARGET_DIR: `$HOME/share/windows`
- WSL_TARGET_DIR: `$HOME/share/wsl`
- REQUIRE_TOKEN: true
- PHONE_DROP_TOKEN: (string, required if REQUIRE_TOKEN=true)
- DEFAULT_TARGET: wsl (or windows) for dropdown default

---

## Security notes

- Keep it on your LAN; binding to 0.0.0.0 exposes it to your network.
- Use `REQUIRE_TOKEN=true` with a non-default `PHONE_DROP_TOKEN`.
- Filenames are sanitized; writes are constrained to chosen directories.

## License

MIT
