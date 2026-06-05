# Chrome APK Bundle (`chrome-apks/`)

Damru normally uses the baked `damru-redroid:latest` image. That image already contains Chrome, WebView/TTS assets, fonts, warm browser preferences, and native assets. Most users do not need to manage APKs manually.

This folder is for raw/unbaked Redroid, image baking, APK recovery, and Chrome version rotation.

## Automatic Install

```bash
python -m damru install-apks --download
```

The installer downloads the release APK bundle, extracts it to `/home/damru/chrome-apks` on Linux/WSL by default, validates Chrome/WebView/TTS APKs, and copies Damru's packaged `magisk.apk` into the bundle when raw Redroid needs a local `resetprop` source. Damru does not download Magisk, eSpeak, Google TTS, or RHVoice from third-party APK sites at runtime.

Manual fallback bundle: [Chrome/WebView/TTS APK assets](https://drive.google.com/file/d/1xh5Z-LXqUIEjO08KKjhaB_89KS2pBWZq/view?usp=sharing)

## Expected Layout

Keep one bundle root with Chrome split APK version folders and top-level support APKs:

```text
chrome-apks/
  143.0.7499.52/
  144.0.7559.132/
  145.0.7632.75/
  146.0.7680.31/
  146.0.7680.65/
  146.0.7680.119/
  146.0.7680.153/
  146.0.7680.154/
  146.0.7680.164/
  146.0.7680.166/
  146.0.7680.177/
  147.0.7727.49/
  147.0.7727.101/
  147.0.7727.138/
  148.0.7778.120/
  148.0.7778.168/
  148.0.7778.178/
  148.0.7778.180/
  148.0.7778.217/
  TrichromeWebView.apk
  google_tts.apk
  espeak.apk
  rhvoice.apk
  magisk.apk
```

Each Chrome version folder must contain its matching Trichrome library split plus the Chrome split APKs. Do not deduplicate `google_trichrome_library.apk` across versions; the file is version-matched and differs by build.

## Chrome Rotation

The current bundle has 19 validated Chrome versions from `143.0.7499.52` through `148.0.7778.217`. Random profile actions can rotate Chrome to another validated version when the bundle exists. The rotation is tied to the same setup path that clears stale Chrome tabs and suppresses first-run prompts.

Chrome 149 is not included yet. Available APKMirror bundles tested so far were missing the required English/x86/x86_64 split layout, so Damru skips them instead of shipping a folder that installs unreliably.

## Auto-Detection

Damru auto-searches these roots:

- `/home/damru/chrome-apks`
- package-local `chrome-apks/`
- current directory `chrome-apks/`
- parent directory `chrome-apks/`

If auto-detection fails, set `CHROME_APK` to a Chrome split-APK version directory such as:

```python
CHROME_APK = "/home/damru/chrome-apks/148.0.7778.217"
```

## Manual Extraction

```bash
sudo mkdir -p /home/damru
sudo chown "$USER:$USER" /home/damru
unzip damru-chrome-apks-latest.zip -d /home/damru/chrome-apks
find /home/damru/chrome-apks -maxdepth 2 -name '*.apk' | head
```

On Windows, extract with File Explorer or 7-Zip. If Damru runs inside WSL, use the WSL path (`/mnt/c/...`) or copy the bundle to `/home/damru/chrome-apks`.

## Deployment Notes

- **Baked image:** preferred. APKs are already installed in `damru-redroid:latest`.
- **Raw/unbaked image:** Damru installs Chrome/WebView/TTS APKs on cold start, which is slower and has more moving parts.
- **Image baking:** run `install-apks --download`, then `python -m damru bake-image --image damru-redroid:latest` inside Linux/WSL.
- **Release artifact:** `chrome-apks.zip` is generated from this folder for external hosting; the large zip is not meant to be committed.
