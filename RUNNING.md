# How to run and test OpenRights Assistant

Three ways to see the MVP, fastest first. All of them use the same offline archive.

## 1. Fastest: a single HTML file on a computer

```bash
git clone https://github.com/Steel84/openrights-assistant.git
cd openrights-assistant
python -m openrights ingest      # downloads the public sources once
python -m openrights bundle      # writes dist/openrights-demo.html
```

Open `dist/openrights-demo.html` in any browser. The interface and the search index are inside that one file, so you can disconnect from the internet first and search still works. Only the "Open source" links need a connection.

## 2. On your own phone, without building an APK

On the computer, inside the repository:

```bash
python -m openrights ingest
python -m openrights export-web
python -m openrights serve
```

It prints two addresses, for example:

```text
Open on this computer:  http://localhost:8000/app/
Open on your phone:     http://192.168.1.42:8000/app/   (same Wi-Fi)
```

Open the phone address in Chrome or Safari on a phone joined to the **same Wi-Fi**, then:

1. Use the browser menu: "Add to Home screen" / "Install app".
2. Turn on airplane mode.
3. Open it from the home screen and search again. It still works, because the interface and the index are cached on the phone.

If the phone cannot reach the address, the usual causes are a firewall on the computer blocking port 8000, or the phone being on a different network such as a guest Wi-Fi.

## 3. Native Android APK

The APK is a thin WebView shell around the same offline app. It is built **on a computer**, not on the phone.

### What you need

- Android Studio, which installs the Android SDK and Gradle: https://developer.android.com/studio
- Or, without Android Studio: JDK 17, Android command-line tools, Gradle 8.5+.

### Option A: Android Studio

```bash
python -m openrights ingest
python -m openrights export-web
mkdir -p android/app/src/main/assets
cp -R app/. android/app/src/main/assets/
```

Then in Android Studio: **File → Open** → select the `android` folder → wait for the Gradle sync → **Run** with a phone connected over USB (enable "USB debugging" in Developer options), or **Build → Build Bundle(s)/APK(s) → Build APK(s)**.

### Option B: command line

```bash
export ANDROID_HOME="$HOME/Android/Sdk"     # Windows: point this at your SDK
python -m openrights ingest
scripts/build_android.sh
```

Result:

```text
android/app/build/outputs/apk/debug/app-debug.apk
```

### Install it on a phone

With USB debugging enabled:

```bash
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
```

Or copy the `.apk` to the phone, open it in the file manager and allow installation from unknown sources. This is a debug build; it is not signed for Google Play.

### What to check on the phone

1. The app opens with no login, and the manifest requests no `INTERNET` permission.
2. Turn on airplane mode, then search: results still appear with source names and scores.
3. Note the install size, the cold start time, and whether scrolling stays smooth.

Record those numbers in `benchmarks/`. On the computer, `python -m openrights benchmark` prints the comparable retrieval numbers.

## Why the archive is a script, not a JSON fetch

A WebView loaded from `file:///android_asset/index.html` cannot `fetch()` a neighbouring file: the request is treated as cross-origin against an opaque origin and is blocked. The archive is therefore exported as `app/data/index.js`, which assigns `window.OPENRIGHTS_INDEX`, and is loaded with a `<script>` tag. The same file works over `http://` and inside the single-file bundle.

## Known limitations

- The Android project has no committed Gradle wrapper; Android Studio or an installed Gradle supplies it.
- The debug APK is unsigned and meant for testing, not distribution.
- The optional local LLM (`--model`) runs on a computer through `llama.cpp`; it is not wired into the Android build yet.
- All benchmark numbers so far come from a development machine. No physical low-end Android measurement exists yet.
