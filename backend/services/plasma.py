import json
import shutil
import subprocess
from pathlib import Path


def _fallback_screens() -> list[dict]:
    return [
        {"id": 0, "name": "Desktop 0", "available": False},
        {"id": 1, "name": "Desktop 1", "available": False},
    ]


def _qdbus() -> str | None:
    for cmd in ("qdbus6", "qdbus"):
        if shutil.which(cmd):
            return cmd
    return None


def list_screens() -> list[dict]:
    qdbus = _qdbus()
    if not qdbus:
        return _fallback_screens()

    script = """
var result = [];
var ds = desktops();
for (var i = 0; i < ds.length; i++) {
  result.push({ id: i, name: 'Desktop ' + i, screen: ds[i].screen });
}
JSON.stringify(result);
""".strip()

    try:
        proc = subprocess.run(
            [qdbus, "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        payload = proc.stdout.strip()
        if not payload:
            raise RuntimeError("empty dbus response")
        screens = json.loads(payload)
        for screen in screens:
            screen["available"] = True
        return screens
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError, RuntimeError):
        return _fallback_screens()


def apply_wallpaper(screen_id: int, image_path: Path) -> None:
    qdbus = _qdbus()
    if not qdbus:
        raise RuntimeError("qdbus não encontrado — aplique wallpaper fora do container ou use network_mode: host")

    uri = image_path.resolve().as_uri()
    script = f"""
var d = desktops()[{screen_id}];
if (!d) throw new Error('screen not found');
d.wallpaperPlugin = 'org.kde.image';
d.currentConfigGroup = ['Wallpaper', 'org.kde.image', 'General'];
d.writeConfig('Image', '{uri}');
d.reloadConfig();
""".strip()

    subprocess.run(
        [qdbus, "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script],
        capture_output=True,
        text=True,
        check=True,
        timeout=5,
    )
