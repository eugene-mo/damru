# Chrome APK Bundle (`chrome-apks/`)

Damru normally uses the baked `damru-redroid:latest` image, which already contains Chrome, WebView/TTS APKs, fonts, warm browser preferences, and native assets. Most users do not need to manage APKs manually.

This folder is for raw/unbaked Redroid, image baking, or APK recovery.

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
  143.0.7499.52/*.apk
  144.0.7559.132/*.apk
  145.0.7632.75/*.apk
  TrichromeWebView.apk
  google_tts.apk
  espeak.apk
  rhvoice.apk
  magisk.apk
```

Damru auto-searches `/home/damru/chrome-apks`, package-local `chrome-apks/`, the current directory's `chrome-apks/`, and the parent directory's `chrome-apks/`. If auto-detection fails, set `CHROME_APK` to a Chrome split-APK version directory such as:

```python
CHROME_APK = "/home/damru/chrome-apks/144.0.7559.132"
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
