#!/usr/bin/env bash
set -Eeuo pipefail
PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_REPO="${1:-}"
if [[ -z "$TARGET_REPO" || ! -d "$TARGET_REPO" ]]; then echo "Usage: $0 /workspace/megalith-lidar" >&2; exit 2; fi
TARGET_REPO="$(cd "$TARGET_REPO" && pwd)"
[[ -f "$TARGET_REPO/android/gradlew" ]] || { echo "Gradle Wrapper Android absent" >&2; exit 2; }
command -v java >/dev/null || { echo "JDK 17 requis" >&2; exit 3; }
command -v python3 >/dev/null || { echo "Python 3 requis" >&2; exit 3; }
command -v node >/dev/null || { echo "Node.js requis" >&2; exit 3; }
python3 "$PACKAGE_ROOT/scripts/validate_package.py"
node --check "$PACKAGE_ROOT/web/app.js"
python3 -m py_compile "$PACKAGE_ROOT/scripts"/*.py "$PACKAGE_ROOT/tests"/*.py
python3 "$PACKAGE_ROOT/tests/test_android_installer.py"
python3 "$PACKAGE_ROOT/scripts/install_into_megalith_lidar_android.py" "$TARGET_REPO" ${FORCE_INTEGRATION:+--force}
python3 -c 'import PIL' >/dev/null 2>&1 || python3 -m pip install --user 'Pillow>=10.0'
SDK_ROOT="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
[[ -n "$SDK_ROOT" && -d "$SDK_ROOT" ]] || { echo "ANDROID_HOME / ANDROID_SDK_ROOT requis" >&2; exit 4; }
SDKMANAGER="$SDK_ROOT/cmdline-tools/latest/bin/sdkmanager"
if [[ -x "$SDKMANAGER" && "${SKIP_SDK_INSTALL:-0}" != 1 ]]; then
  yes | "$SDKMANAGER" --licenses >/dev/null || true
  "$SDKMANAGER" "platforms;android-35" "build-tools;35.0.0"
fi
for f in "$SDK_ROOT/platforms/android-35/android.jar" "$SDK_ROOT/build-tools/35.0.0/zipalign" "$SDK_ROOT/build-tools/35.0.0/apksigner"; do [[ -e "$f" ]] || { echo "SDK incomplet: $f" >&2; exit 4; }; done
chmod +x "$TARGET_REPO/android/gradlew"
(cd "$TARGET_REPO/android" && ./gradlew assembleDebug --no-daemon --stacktrace)
BUILT="$TARGET_REPO/android/app/build/outputs/apk/debug/app-debug.apk"
[[ -s "$BUILT" ]] || { echo "APK debug absent" >&2; exit 5; }
mkdir -p "$TARGET_REPO/dist"
OUT="$TARGET_REPO/dist/megalith-lidar-france-debug.apk"
cp "$BUILT" "$OUT"
(cd "$TARGET_REPO/dist" && sha256sum "$(basename "$OUT")" > "$(basename "$OUT").sha256")
"$SDK_ROOT/build-tools/35.0.0/zipalign" -c -v 4 "$OUT" >/dev/null
"$SDK_ROOT/build-tools/35.0.0/apksigner" verify --verbose "$OUT"
echo "APK: $OUT"; cat "$OUT.sha256"
