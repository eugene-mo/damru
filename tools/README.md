# 🧰 Tools & Assets (`tools/`)

This directory contains external tools, assets, and third-party binaries used exclusively for debugging or managing the Android environment during research and development.

---

## 🛠️ Contents

### `magisk.apk`

Provided for developers who wish to manually explore the Redroid container, debug root access, or install custom Magisk modules during research phases.

> **Note:** Users do not need to provide Magisk for normal setup. Damru uses Redroid's native `su` binary, and raw/unbaked Redroid automatically downloads the official Magisk APK to `/home/damru/tools/magisk.apk` only when it needs a source for extracting standalone `resetprop`. The APK is kept out of Git because it is a large third-party binary.

---

*Do not commit sensitive keys or large unmodified third-party binaries here unless absolutely necessary for the build pipeline.*
