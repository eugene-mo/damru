# Fix: redroid image auto-pull on first run

Addresses Gap #1 (Image Management) from `docs/AUTOMATION_GAPS_PLAN.md`.

Branch: `wip/image-auto-pull` (off `main`).

## Problem

`RedroidManager.start_container()` ran `docker run ... REDROID_IMAGE` with no
existence check. `REDROID_IMAGE` defaults to the baked tag
`damru-redroid:latest`, which does not exist on a clean machine until
`scripts/bake_image.py` is run - so the first run crashed with
`docker: Error response from daemon: No such image: damru-redroid:latest`.

Current setup note: Windows/WSL Docker commands now run through `wsl -u root`
instead of piping a WSL sudo password through the shell. `WSL_PASSWORD` remains
in config only as a compatibility placeholder and is not required by the current
setup path.

## Changes

Implemented pieces:

1. **Auto-pull/tag the launch image** -
   - `config.py*`: add `REDROID_BASE_IMAGE = "redroid/redroid:14.0.0_64only-latest"`.
   - `docker.py`: add `RedroidManager._image_exists()` and `ensure_image()`:
     - present -> no-op
     - baked image (`REDROID_IMAGE`) missing -> pull `REDROID_BASE_IMAGE`, tag
       it as the launch image (unbaked but functional; warns to bake for
       faster cold starts)
     - any other image missing -> pull; **raise `DamruError`** on failure
       instead of letting `docker run` crash opaquely
   - `docker.py`: call `await self.ensure_image(REDROID_IMAGE)` at the top of
     `start_container()`.

2. **CLI verification path** -
   - `python -m damru check-env` reports Docker, binderfs, Chrome APKs, Redroid
     image state, and the Damru Playwright `crPage.js` patch.
   - `python -m damru install-deps` installs Linux/WSL dependencies and fails
     clearly when the WSL kernel lacks required Docker netfilter modules.
   - `python -m damru fix-wsl` retries safe WSL Docker, binderfs, and
     netfilter setup and explains when a kernel replacement is required.

## Scope / follow-ups (not done here)

- `bake_image()` starts the temp container from `REDROID_IMAGE` (the baked
  tag) rather than `REDROID_BASE_IMAGE`, which is circular on a clean machine.
  Left untouched by request; candidate for a separate change.
- Other gaps in `AUTOMATION_GAPS_PLAN.md` (storage location and deeper
  self-healing) remain future work.

## Tests

`pyproject.toml` gains `[tool.pytest.ini_options]` (asyncio auto mode,
`pythonpath = ["."]`).

| File | Type | Runs |
|------|------|------|
| `tests/test_images_unit.py` | Unit (mocks the `_run_cmd` subprocess boundary) | Anywhere |
| `tests/test_images_integration.py` | Integration (real local Docker, pulls `hello-world`) | Skipped unless `docker` CLI + daemon present |
| `tests/test_images_e2e.py` | E2E (real base-image pull + tag, no mocks) | Skipped unless `DAMRU_E2E=1` |

### Running

This repo's global Python env has unrelated broken pytest plugins
(`logfire`, `pytest_ansible`) due to a `typing_extensions`/`opentelemetry`
version clash, so plugin autoload must be disabled locally:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/test_images_unit.py tests/test_images_integration.py tests/test_images_e2e.py \
  -p pytest_asyncio.plugin
```

In a clean environment the project config is enough:

```bash
python -m pytest tests/test_images_unit.py
```

Last local result: **6 unit passed, 1 integration passed** (real Docker on
the dev box), **1 e2e skipped** (opt-in). The e2e is delivered but requires
the redroid host (WSL2/Linux) to execute - it has not been run here.
