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

## Output

`dashboard/data/signal-table.csv` ranks the 10 pilots by magnitude and follow-up potential.
