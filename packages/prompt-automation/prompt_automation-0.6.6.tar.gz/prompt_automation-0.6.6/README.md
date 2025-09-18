# prompt-automation

`prompt-automation` is a keyboard-driven prompt launcher for teams that rely on shared templates. Press one hotkey to open the selector, fill placeholders with guardrails, and copy a final response.

## Key capabilities
- Single-window workflow that combines template browsing, variable collection, and review.
- New Template Wizard and hierarchical folder support to organize large prompt libraries.
- Snapshot-aware globals plus reminders to keep safety guidance consistent across templates.
- Espanso sync tooling that validates snippets, mirrors files, and restarts the espanso service for you.

## Installation
### Quick install scripts
Use the provided scripts when you want an end-to-end setup that installs dependencies and assigns the default hotkey.

- **Windows**
  ```powershell
  install\install.ps1
  ```
- **macOS / Linux / WSL2**
  ```bash
  bash install/install.sh
  ```

### pip / pipx packages
Prefer a Python package manager? Install the published package and run the CLI directly.

```bash
pipx install prompt-automation
# or
python -m pip install prompt-automation
```

### Native installers (preview)
Want a packaged executable or `.dmg` instead of running the scripts directly? Use the packaging CLI to orchestrate the builds.

```
python -m pip install -e .[packaging]
python packagers/build_all.py --dry-run  # prints planned commands
python packagers/build_all.py            # builds Windows + macOS artifacts
```

Artifacts are written to `dist/packagers/<os>/...` and the workflow is documented in [docs/PACKAGING.md](docs/PACKAGING.md).

Prefer a guided experience? The in-app wizard under **Options → Packaging → Manual packaging** walks through tests, packaging, tagging, and GitHub release upload. See [docs/MANUAL_PACKAGING.md](docs/MANUAL_PACKAGING.md) for screenshots and troubleshooting tips.

### Developer setup
For editable installs that auto-configure development flags:

- **Windows**: `install/install-dev.ps1`
- **macOS / Linux / WSL2**: `pipx install --editable .` or `python -m pip install --user -e .`

After installation restart your terminal so `pipx` is on your `PATH`. The GUI depends on Tkinter; Debian/Ubuntu users may need `sudo apt install python3-tk`.

## Quickstart
1. Launch the app with **Ctrl+Shift+J** or run `prompt-automation` (aliases: `prompt_automation`, `pa`).
2. Browse or search for a template. Hierarchical navigation is available when enabled.
3. Fill in placeholders. Leave a field blank to fall back to defaults or remove the line entirely.
4. Review the rendered output, then press **Ctrl+Enter** to copy and close or **Ctrl+Shift+C** to copy without closing.
5. Need a new shortcut? Run `prompt-automation --assign-hotkey` to rebind the global hotkey.

More GUI shortcuts and CLI options live in [Single Window Keyboard Shortcuts](docs/SINGLE_WINDOW_KB.md) and [Hotkeys](docs/HOTKEYS.md).

## Espanso integration
`prompt-automation` keeps the versioned espanso package under `espanso-package/` as the source of truth. Use the app, CLI, or helper scripts to generate matches, validate them, and mirror the results into your espanso installation.

| Command or flag | Purpose |
| --- | --- |
| `prompt-automation --espanso-sync` | Generate snippets, validate, mirror to the espanso directory, install/update the package, and restart espanso. |
| `prompt-automation --espanso-sync --git-branch <name>` | Override the git branch when installing from a repository. |
| `scripts/espanso.sh sync` | Run the sync pipeline from a shell script (respects the same environment variables). |
| `PA_SKIP_INSTALL=1 scripts/espanso.sh sync` | Dry-run: generate, validate, and mirror without installing or restarting espanso. |
| `scripts/espanso.sh lint` | Validate YAML matches and check for duplicate triggers. |
| `prompt-automation --espanso-clean` | Backup and remove local espanso match files managed by this project. |
| `prompt-automation --espanso-clean-deep` | Extend clean-up to uninstall legacy/conflicting packages. |
| `prompt-automation --espanso-clean-list` | Show which files would be touched without making changes. |

Detailed workflows, CI notes, and packaging guidance are documented in [ESPANSO_PACKAGE.md](docs/ESPANSO_PACKAGE.md) and [ESPANSO_FIRST_RUN.md](docs/ESPANSO_FIRST_RUN.md).

## Template authoring
Templates live under `src/prompt_automation/prompts/`. Start with the New Template Wizard or create JSON manually. For directory conventions, metadata flags, multi-file placeholders, and override sync behavior, read the [Template Authoring and Management guide](docs/TEMPLATES.md).

Additional references:
- [Variables & Globals Reference](docs/VARIABLES_REFERENCE.md) explains placeholder schema, persistence, and formatting helpers.
- [Reminders Schema and Usage](docs/REMINDERS.md) covers instructional text blocks and feature flags.
- [Theme Extension Guide](docs/THEME_EXTENSION_GUIDE.md) describes how to customize the Tk theme system.

## Troubleshooting and maintenance
- `prompt-automation --troubleshoot` prints log locations, override files, and environment details.
- [Installation Troubleshooting](docs/INSTALLATION_TROUBLESHOOTING.md) covers platform-specific installer issues.
- [Python Troubleshooting](docs/PYTHON_TROUBLESHOOTING.md) helps resolve interpreter or dependency problems.
- [Hotkeys](docs/HOTKEYS.md) walks through repairing or manually configuring shortcuts.
- [Uninstall](docs/UNINSTALL.md) lists CLI flags and exit codes for the built-in uninstaller.

For espanso-specific checks see [ESPANSO_REMOTE_FIRST.md](docs/ESPANSO_REMOTE_FIRST.md) and the scripts in `scripts/`.

## Contributing and support
- Review [CONTRIBUTING.md](CONTRIBUTING.md) and [CODEBASE_REFERENCE.md](docs/CODEBASE_REFERENCE.md) before submitting a change.
- Run `pytest -q` to verify the test suite.
- Report bugs or request features via GitHub issues.

`prompt-automation` is licensed under the MIT License. See [LICENSE](LICENSE) for details.
