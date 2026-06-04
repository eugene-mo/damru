#  Documentation (`docs/`)

Welcome to the Damru knowledge base. This directory holds project documentation, architecture plans, roadmaps, and research notes.

---

## Contents

*   **CLI setup**: Run `python -m damru setup` for guided first-run configuration, `python -m damru install-deps` for Linux/WSL dependencies, `python -m damru install-image` to load the baked Redroid image, `python -m damru install-apks --download` for raw Chrome/WebView/TTS APK assets plus Damru's shipped resetprop source when baking or using unbaked Redroid, `python -m damru fix-wsl`/`fix-internet` for safe Docker/binderfs/netfilter/DNS repair, `python -m damru check-env` to verify setup details, and `python -m damru check preflight --json` for fast read-only readiness checks across VPS/VM fleets. Preflight checks Docker, ADB, binder/binderfs, image/assets, resources, ports, config, and WSL kernel state without installing, mounting, starting containers, or editing networking.
*   **Local UI**: `python -m damru ui` starts the experimental localhost dashboard for setup health, worker actions, Work Lab URL/screenshot/quick-check flows, browser viewer, native viewer command copy, gallery cleanup, and inline logs. The backend is allowlisted and local-only by default.
*   **Current validation**: On June 4, 2026, disposable Ubuntu WSL2 with Damru's bundled WSL kernel and native Ubuntu 24.04 VPS were both tested with fresh/reset setup flows, preflight, unit tests, two Redroid workers, `quick-check`, and `open-url https://example.com`. Debian 13 VPS was tested separately; Docker worked, but Redroid multi-container support failed because the stock Debian VPS kernel had `CONFIG_ANDROID_BINDERFS` disabled.
*   **[`PROOF.md`](PROOF.md)**: Sanitized WSL/native Linux verification notes plus proof assets: [Android screen recording](assets/proof/ubuntu-redroid-proof.mp4), Example.com proof, and individual site screenshots for Amazon, Foot Locker/DataDome, Fingerprint Pro, Sannysoft, and CreepJS.
*   **[`DEVICE_PROFILES.md`](DEVICE_PROFILES.md)**: Full generated reference for the 49 Android device profiles available in `damru/devices.py`.
*   **[`VIEWER.md`](VIEWER.md)**: Optional screenshot, video recording, and scrcpy live-view workflows.
*   **[`WSL_KERNEL.md`](WSL_KERNEL.md)**: WSL2 kernel requirements for Docker bridge/NAT networking and Redroid binderfs.
*   **Image baking**: Use `python -m damru install-apks --download`, then `python -m damru bake-image --image damru-redroid:latest` inside Linux/WSL2, then `docker save damru-redroid:latest -o damru-redroid-latest.tar`. The tarball is ignored by Git; keep `damru-redroid-latest.tar.sha256` with the release artifact. The APK installer downloads the Chrome/WebView/TTS bundle to `/home/damru/chrome-apks` on Linux/WSL and copies Damru's shipped `magisk.apk` there when raw Redroid needs standalone `resetprop`.
*   **[`AUTOMATION_GAPS_PLAN.md`](AUTOMATION_GAPS_PLAN.md)**: Contains the "Big Plan" for future iterations of Damru. It outlines exactly what features are missing to make Damru a fully autonomous 1-click infrastructure tool (e.g., a CLI installer, automated Docker image baking, and self-healing health checks).
*   **`architecture/`**: (Coming Soon) Deep dives into the CDP overrides and Android binary patching mechanics.
*   **`CONTRIBUTING.md`**: Guidelines for contributing to the Damru ecosystem.

*More architectural diagrams and research papers regarding browser fingerprinting will be added here as the project evolves.*
