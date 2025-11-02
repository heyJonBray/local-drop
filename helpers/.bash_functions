#-----------------------------------------------------------------------#
# PHONE DROP HELPERS (systemd user service)                             #
#-----------------------------------------------------------------------#

_phone_drop_service="phone-drop.service"

start-phone-drop() {
  systemctl --user daemon-reload
  systemctl --user start "$_phone_drop_service"
  systemctl --user --no-pager --full status "$_phone_drop_service" | sed -n '1,15p'
}

stop-phone-drop() {
  systemctl --user stop "$_phone_drop_service"
  systemctl --user --no-pager --full status "$_phone_drop_service" | sed -n '1,15p'
}

enable-phone-drop() {
  systemctl --user enable "$_phone_drop_service"
  echo "Enabled auto-start for ${_phone_drop_service}"
  systemctl --user is-enabled "$_phone_drop_service"
}

disable-phone-drop() {
  systemctl --user disable "$_phone_drop_service"
  echo "Disabled auto-start for ${_phone_drop_service}"
  systemctl --user is-enabled "$_phone_drop_service" || true
}

restart-phone-drop() {
  systemctl --user daemon-reload
  systemctl --user restart phone-drop.service
}

config-phone-drop() {
  nano ~/.config/systemd/user/phone-drop.service
}

status-phone-drop() {
  systemctl --user --no-pager --full status "$_phone_drop_service"
}

logs-phone-drop() {
  journalctl --user -u "$_phone_drop_service" -f
}
