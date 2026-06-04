# Tools & Assets (`tools/`)

This directory contains external tools, assets, and third-party binaries used for Android environment research and development.

---

## Contents

### `magisk.apk`

Provided for developers who want to manually explore the Redroid container, debug root access, or install custom Magisk modules during research phases.

> **Note:** Users do not need to provide Magisk separately for normal setup. Damru ships `magisk.apk` as a package asset, copies it into the local APK bundle when needed, and raw/unbaked Redroid uses it only as a local source for extracting standalone `resetprop`. Damru does not download Magisk from third-party APK sites at runtime.

---

Do not commit sensitive keys or large unmodified third-party binaries here unless they are required for the build or release pipeline.
