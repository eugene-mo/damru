# Bundled WSL Kernel Artifact

This directory contains the locally verified WSL2 kernel artifact used for Damru Redroid on WSL.

Included files:

- `wsl2-kernel-redroid-natfix-20260602`: WSL2 kernel binary with Android binderfs and Docker bridge/NAT options enabled.
- `wsl2-kernel-redroid-natfix-20260602.config`: exact kernel config captured from the build.
- `SHA256SUMS`: checksums for integrity verification.

Damru installs this safely by copying the kernel to the user's home directory under `.damru/wsl-kernels/`, backing up any existing `.wslconfig`, preserving unrelated `.wslconfig` settings, and writing the `[wsl2] kernel=...` entry.

The user must restart WSL after installing or changing a WSL kernel:

```powershell
wsl --shutdown
```

Then run:

```bash
python -m damru fix-wsl
python -m damru check-env --viewer
```
Source metadata:

- `source_metadata/damru-wsl-kernel-nat-build.config`: copied from the local WSL kernel build tree's `.config`.
- `source_metadata/damru-wsl-kernel-nat-build.config.old`: copied from the local WSL kernel build tree's `.config.old`.
- `source_metadata/damru-wsl-kernel-nat-build.kernel_config_data`: copied from the built kernel's embedded config data.
- `source_metadata/damru-wsl-kernel-nat-build.info`: source path, size, active kernel, and git metadata captured from WSL.

The full WSL kernel source tree was not copied into this repository because the local build tree is about 15 GB. The exact kernel config and installed binary are preserved here.