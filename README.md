# local-drop

Tiny Flask app to drop text from your phone to your machine over LAN. Opens a form with filename, content, and a target (Windows or WSL on WSL setups; on Linux they’re just two configurable dirs). Writes files to your chosen directory.

## Features

- Paste text, choose filename, write/append to chosen file
- Two target directories selectable via dropdown (configured via env)
- Optional token to prevent drive‑by writes
- Works on Linux and WSL

---

## General Linux setup

Prereqs (Ubuntu/Debian-like):

```bash
sudo apt update
sudo apt install -y python3-venv
```

Setup:

```bash
git clone https://github.com/heyjonbray/local-drop.git
cd local-drop
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install flask
```

Run (Linux defaults keep data in your home; change envs as you like):

```bash
export BIND_IP="0.0.0.0"
export PORT="8085"
# Safe defaults inside your home if unset:
#   WINDOWS_TARGET_DIR -> ~/share/windows
#   WSL_TARGET_DIR     -> ~/share/wsl
# Override if desired:
# export WINDOWS_TARGET_DIR="$HOME/share/windows"
# export WSL_TARGET_DIR="$HOME/share/wsl"
export REQUIRE_TOKEN="true"
export PHONE_DROP_TOKEN="change-me"
python app.py
```

Open from phone (same Wi‑Fi/LAN):
- Find your machine’s LAN IP (choose your interface, e.g., `enp3s0`, `wlan0`):

```bash
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n1
```

- Visit: `http://<LAN_IP>:8085`

> For convenience, bookmark this in your mobile browser.

### Systemd user service (Linux, optional, auto-start)

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

Firewall (if applicable):
```bash
# Ubuntu with ufw:
sudo ufw allow 8085/tcp
```

---

## WSL setup (Windows Subsystem for Linux)

This is identical to Linux setup with a couple of WSL tips. You can target Windows paths via `/mnt/c/...` if desired.
The `WINDOWS_TARGET_DIR` was built with WSL in mind to write to the Windows filesystem but you can point it to another directory in WSL if you want.

Prereqs (WSL Ubuntu 24.04):
```bash
sudo apt update
sudo apt install -y python3-venv
```

Setup:
```bash
git clone https://github.com/heyjonbray/local-drop.git
cd local-drop
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install flask
```

Run (example with a Windows destination):
```bash
export BIND_IP="0.0.0.0"
export PORT="8085"
# Optional: write to Windows filesystem
export WINDOWS_TARGET_DIR="/mnt/c/Users/jon/Desktop/phone-drop"
# Optional: WSL target dir (default will be $HOME/share/wsl)
export WSL_TARGET_DIR="/home/jon/share/wsl"
export REQUIRE_TOKEN="true"
export PHONE_DROP_TOKEN="change-me"
python app.py
```

Open from phone:
- Find your WSL IP:

```bash
ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'
```

- Visit: `http://<WSL_IP>:8085`

### Systemd user service on WSL

Ensure systemd is enabled in WSL: in `/etc/wsl.conf` set:

```sh
[boot]
systemd=true
```

Then from Windows:
- Close WSL: `wsl --shutdown`
- Reopen your distro

Create the unit:

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
Environment=WINDOWS_TARGET_DIR=/mnt/c/Users/jon/Desktop/phone-drop
Environment=WSL_TARGET_DIR=/home/jon/share/wsl
Environment=REQUIRE_TOKEN=true
Environment=PHONE_DROP_TOKEN=change-me
Restart=on-failure

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now phone-drop.service
```

Optionally you can keep it running without an interactive login:

```bash
loginctl enable-linger "$USER"
```

Windows firewall/visibility:
- Easiest is to browse to the WSL IP directly from your phone and bookmark it.
- If you prefer using the Windows host IP or hostname, ensure Windows Defender Firewall allows inbound traffic to the chosen port.

## Helpers

Useful functions for managing the server are available in `helpers/.bash_functions` and can be added to your `~/.bashrc` or `~/.bash_functions`.

## Configuration

Environment variables (all optional, app has safe defaults):

- `BIND_IP`: interface to bind (default: `0.0.0.0`)
- `PORT`: port to serve on (default: `8085`)
- `WINDOWS_TARGET_DIR`: path for "Windows" option (WSL only, default: `$HOME/share/wsl`)
- `REQUIRE_TOKEN`: `true` or `false` to require token and display input (default: `true`)
- `PHONE_DROP_TOKEN`: token string required when `REQUIRE_TOKEN=true`
- `DEFAULT_TARGET`: `windows` or `wsl` for dropdown default (default: `wsl`)

## Security Notes

- Keep this on your LAN; bind to `0.0.0.0` only for devises you trust on your network
- Use `REQUIRE_TOKEN=true` and set a non-default `PHONE_DROP_TOKEN`

## License

[MIT](LICENSE)
