# local-drop

Tiny Flask app to drop text from your phone to WSL or Windows Filesystem. Opens a form on your LAN with filename, content, and a target (Windows or WSL). Writes files to your chosen directory.

## Features
- Paste text, choose filename, Write/Append
- Save to Windows or WSL paths (configured via env)
- Optional token to prevent drive‑by writes

## Quick start

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

Run:
```bash
export BIND_IP="0.0.0.0"
export PORT="8085"
export WINDOWS_TARGET_DIR="/mnt/c/Users/jon/Desktop/phone-drop"
export WSL_TARGET_DIR="/home/jon/phone-drop/files"
export REQUIRE_TOKEN="true"
export PHONE_DROP_TOKEN="change-me"
python app.py
```

Open from phone:
- Find your WSL IP:
```bash
ip -4 addr show eth0 | grep -oP '(?<=inet\\s)\\d+(\\.\\d+){3}'
```
- Visit: `http://<WSL_IP>:8085`

## Systemd (optional, auto-start)

You can also keep local-drop running while WSL is up. Ensure systemd is enabled in WSL (/etc/wsl.conf -> systemd=true, then `wsl --shutdown` from Windows).

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
Environment=WINDOWS_TARGET_DIR=/mnt/c/Users/jon/Desktop/phone-drop
Environment=WSL_TARGET_DIR=/home/jon/phone-drop/files
Environment=REQUIRE_TOKEN=true
Environment=PHONE_DROP_TOKEN=change-me
Restart=on-failure

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now phone-drop.service
```

Handy helpers (add to ~/.bashrc):
```bash
start-phone-drop() { systemctl --user daemon-reload; systemctl --user start phone-drop.service; }
stop-phone-drop() { systemctl --user stop phone-drop.service; }
enable-phone-drop() { systemctl --user enable phone-drop.service; }
disable-phone-drop() { systemctl --user disable phone-drop.service; }
status-phone-drop() { systemctl --user --no-pager --full status phone-drop.service; }
```

## Security notes
- Keep it on your LAN; bind to `0.0.0.0` only if you need mobile access
- Use `REQUIRE_TOKEN=true` and set a non-default `PHONE_DROP_TOKEN`
- Restrict writes to known directories only

## License
MIT
