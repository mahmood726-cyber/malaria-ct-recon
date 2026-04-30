# malaria-ct-recon

10-pilot reconnaissance of bias sources in malaria trial data on ClinicalTrials.gov.

**Snapshot:** AACT 2026-04-12 (frozen).
**Status:** Sprint in progress.

See `docs/superpowers/specs/2026-04-30-malaria-ct-recon-design.md` for the design.

## Quickstart

1. Install: `pip install -e .[dev]`
2. Configure snapshot path: `cp aact_path.toml.example aact_path.toml` and edit
3. Run preflight: `python -m pilots.preflight`
4. Run all pilots: `python -m pilots.run_all`
5. Open `dashboard/index.html` in a browser

## Preregistration

Framework + design soft-preregistered on 2026-04-30 against framework HEAD `26a3fb0a4610816382cf3024c748d508b3af1180`. See `.preregistration_commit.txt` for the pinned contents manifest. OpenTimestamps Bitcoin anchoring is applied post-push to GitHub (see release tag v0.1.0). Downstream consumers can verify the framework state by `git checkout 26a3fb0a4610816382cf3024c748d508b3af1180` and inspecting the pinned files.

## Output

`dashboard/data/signal-table.csv` ranks the 10 pilots by magnitude and follow-up potential.
