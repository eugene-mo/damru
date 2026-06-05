# Image and APK Readiness

Status: implemented. Current users should prefer the documented CLI flow instead of manually pulling Redroid images.

## Recommended Flow

```bash
python -m damru install-deps -y
python -m damru install-image
python -m damru check preflight
python -m damru check-env
```

`install-image` loads or downloads the baked `damru-redroid:latest` image. The baked image is the recommended path because Chrome, WebView/TTS assets, fonts, warm preferences, and native assets are already inside the container image.

## Raw/Unbaked Flow

Use this only for baking, debugging, or APK recovery:

```bash
python -m damru install-apks --download
python -m damru bake-image --image damru-redroid:latest
docker save damru-redroid:latest -o damru-redroid-latest.tar
sha256sum damru-redroid-latest.tar > damru-redroid-latest.tar.sha256
```

The APK installer extracts to `/home/damru/chrome-apks` by default and validates:

- Chrome split-APK version folders
- `TrichromeWebView.apk`
- `google_tts.apk`
- `espeak.apk`
- `rhvoice.apk`
- Damru's packaged `magisk.apk` when raw Redroid needs a local `resetprop` source

The current APK bundle contains 19 validated Chrome versions from `143.0.7499.52` through `148.0.7778.217`. Random profile actions can rotate Chrome versions when this bundle exists.

## Readiness Checks

`python -m damru check preflight` is fast and read-only. It does not install packages, pull/load images, mount binderfs, start containers, edit iptables, or change `.wslconfig`. Use `--json` for automation:

```bash
python -m damru check preflight --json --timeout 3
```

`python -m damru check-env` is slower and deeper. It verifies setup details such as Docker, binderfs, image/APK discovery, ADB, Playwright patching, and optional viewer tooling.

## Failure Handling

- Missing baked image: run `python -m damru install-image`.
- Missing raw APKs: run `python -m damru install-apks --download`.
- WSL Docker/binderfs/network issue: run `python -m damru fix-wsl`.
- Worker DNS/internet issue: run `python -m damru fix-internet --all`.
- Unsupported Debian/custom kernel: use Ubuntu 24.04 or a binderfs-enabled kernel.
