#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "${ANDROID_HOME:-}" ]]; then printf '%s\n' "ANDROID_HOME is required" >&2; exit 2; fi
if ! command -v gradle >/dev/null 2>&1; then printf '%s\n' "gradle is required (or add a Gradle wrapper)" >&2; exit 2; fi
rm -rf "$root/android/app/src/main/assets"
mkdir -p "$root/android/app/src/main/assets"
cp -R "$root/app/." "$root/android/app/src/main/assets/"
gradle -p "$root/android" :app:assembleDebug
printf '%s\n' "APK: android/app/build/outputs/apk/debug/app-debug.apk"
