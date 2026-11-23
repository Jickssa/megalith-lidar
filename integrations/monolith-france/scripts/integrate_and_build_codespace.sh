#!/usr/bin/env bash
set -Eeuo pipefail

PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_REPO="${1:-}"
if [[ -z "$TARGET_REPO" || ! -d "$TARGET_REPO" ]]; then
  echo "Usage: $0 /workspace/megalith-lidar" >&2
  exit 2
fi
TARGET_REPO="$(cd "$TARGET_REPO" && pwd)"

[[ -f "$TARGET_REPO/android/gradlew" ]] || { echo "Gradle Wrapper Android absent" >&2; exit 2; }
command -v java >/dev/null || { echo "JDK requis" >&2; exit 3; }
command -v python3 >/dev/null || { echo "Python 3 requis" >&2; exit 3; }
command -v node >/dev/null || { echo "Node.js requis" >&2; exit 3; }

# All preflight checks happen before editing the target checkout.
VENV_DIR="${TMPDIR:-/tmp}/monolith-france-build-venv"
python3 -m venv "$VENV_DIR"
PYTHON="$VENV_DIR/bin/python"
"$PYTHON" -m pip install --disable-pip-version-check "Pillow>=10,<13"
"$PYTHON" "$PACKAGE_ROOT/scripts/validate_package.py"
node --check "$PACKAGE_ROOT/web/app.js"
"$PYTHON" -m py_compile "$PACKAGE_ROOT"/scripts/*.py
"$PYTHON" "$PACKAGE_ROOT/scripts/test_android_installer.py"

INSTALL_ARGS=("$TARGET_REPO")
if [[ "${FORCE_INTEGRATION:-0}" == "1" ]]; then INSTALL_ARGS+=(--force); fi
"$PYTHON" "$PACKAGE_ROOT/scripts/install_into_megalith_lidar_android.py" "${INSTALL_ARGS[@]}"

SDK_ROOT="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
[[ -n "$SDK_ROOT" && -d "$SDK_ROOT" ]] || {
  echo "ANDROID_HOME ou ANDROID_SDK_ROOT absent." >&2
  exit 4
}
export ANDROID_HOME="$SDK_ROOT" ANDROID_SDK_ROOT="$SDK_ROOT"
SDKMANAGER="$SDK_ROOT/cmdline-tools/latest/bin/sdkmanager"
if [[ "${SKIP_SDK_INSTALL:-0}" != "1" ]]; then
  [[ -x "$SDKMANAGER" ]] || { echo "sdkmanager absent : installer Android Command-line Tools." >&2; exit 4; }
  yes | "$SDKMANAGER" --licenses >/dev/null || true
  "$SDKMANAGER" "platforms;android-35" "build-tools;35.0.0"
fi
for required in "$SDK_ROOT/platforms/android-35/android.jar" \
                "$SDK_ROOT/build-tools/35.0.0/zipalign" \
                "$SDK_ROOT/build-tools/35.0.0/apksigner"; do
  [[ -e "$required" ]] || { echo "SDK incomplet : $required" >&2; exit 4; }
done

chmod +x "$TARGET_REPO/android/gradlew"
(cd "$TARGET_REPO/android" && ./gradlew assembleDebug --no-daemon --stacktrace)
BUILT="$TARGET_REPO/android/app/build/outputs/apk/debug/app-debug.apk"
[[ -s "$BUILT" ]] || { echo "APK Debug absent après Gradle." >&2; exit 5; }

# Assert that all France WebView assets are included in the actual APK.
python3 - "$BUILT" <<'PY'
from pathlib import Path
from zipfile import ZipFile
import sys
apk = Path(sys.argv[1])
required = (
    "assets/web/france/web/index.html",
    "assets/web/france/web/app.js",
    "assets/web/france/config/france-config.json",
    "assets/web/leaflet/leaflet.js",
    "assets/web/leaflet/leaflet.css",
)
with ZipFile(apk) as archive:
    bad = archive.testzip()
    if bad:
        raise SystemExit(f"APK ZIP CRC failure: {bad}")
    names = set(archive.namelist())
    missing = [name for name in required if name not in names]
    if missing:
        raise SystemExit("APK missing required assets:\n" + "\n".join(missing))
print("APK ZIP and France/Leaflet assets: OK")
PY

mkdir -p "$TARGET_REPO/dist"
OUT="$TARGET_REPO/dist/megalith-lidar-france-debug.apk"
cp "$BUILT" "$OUT"
(cd "$TARGET_REPO/dist" && sha256sum "$(basename "$OUT")" > "$(basename "$OUT").sha256")
"$SDK_ROOT/build-tools/35.0.0/zipalign" -c -v 4 "$OUT" >/dev/null
"$SDK_ROOT/build-tools/35.0.0/apksigner" verify --verbose "$OUT"
echo "APK Debug : $OUT"
cat "$OUT.sha256"
