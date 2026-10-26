#!/usr/bin/env bash
# Run from a trusted local checkout: sudo bash scripts/install.sh
set -Eeuo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Bitte mit sudo bash scripts/install.sh starten." >&2
  exit 1
fi

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v systemctl >/dev/null || ! command -v apt-get >/dev/null; then
  echo "Dieser Installer ist für Ubuntu/Debian mit systemd vorgesehen." >&2
  exit 1
fi
if [[ -e /opt/rufpass/current && ! -L /opt/rufpass/current ]]; then
  echo "/opt/rufpass/current ist kein Symlink; Abbruch ohne Überschreiben." >&2
  exit 1
fi

old_release="$(readlink /opt/rufpass/current 2>/dev/null || true)"
switched=0
recover() {
  echo "Installation fehlgeschlagen. Konfiguration und Freigabedaten bleiben erhalten." >&2
  echo "Konfiguration bei Bedarf mit sudoedit /etc/rufpass/config.toml korrigieren." >&2
  if [[ "$switched" -eq 1 && -n "$old_release" && -d "$old_release" ]]; then
    ln -s "$old_release" "/opt/rufpass/.rollback-$$"
    mv -Tf "/opt/rufpass/.rollback-$$" /opt/rufpass/current
    systemctl restart rufpass.service || true
    echo "Vorherige Programmversion wieder ausgewählt." >&2
  fi
}
trap recover ERR

apt-get update
apt-get install -y python3-venv
python3 -c 'import sys; assert sys.version_info >= (3, 12), "Python 3.12 oder neuer erforderlich"'
if ! id -u rufpass >/dev/null 2>&1; then
  useradd --system --user-group --home-dir /var/lib/rufpass --shell /usr/sbin/nologin rufpass
fi
install -d -m 755 /opt/rufpass /opt/rufpass/releases
install -d -m 750 -o root -g rufpass /etc/rufpass
install -d -m 700 -o rufpass -g rufpass /var/lib/rufpass

# Build a new isolated environment while the installed service keeps running.
release_dir="$(mktemp -d /opt/rufpass/releases/XXXXXX)"
chmod 755 "$release_dir"
python3 -m venv "$release_dir"
install -d -m 755 "$release_dir/source"
cp -R "$project_root/pyproject.toml" "$project_root/README.md" "$project_root/src" "$release_dir/source/"
"$release_dir/bin/python" -m pip install "$release_dir/source"
if [[ ! -f /etc/rufpass/config.toml ]]; then
  "$release_dir/bin/rufpass" configure
fi
chown root:rufpass /etc/rufpass/config.toml
chmod 640 /etc/rufpass/config.toml
"$release_dir/bin/rufpass" validate

install -m 644 "$project_root/deploy/rufpass.service" /etc/systemd/system/rufpass.service
ln -s "$release_dir" "/opt/rufpass/.current-$$"
mv -Tf "/opt/rufpass/.current-$$" /opt/rufpass/current
switched=1
systemctl daemon-reload
systemctl enable rufpass.service
systemctl restart rufpass.service
sleep 2
systemctl is-active --quiet rufpass.service
trap - ERR

echo "Rufpass ist installiert und aktiv."
echo "Status: sudo systemctl status rufpass --no-pager"
echo "Logs:   sudo journalctl -u rufpass -n 30 --no-pager"
echo "Updates: git pull --ff-only und anschließend denselben Installer erneut ausführen."
