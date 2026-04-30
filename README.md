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

## Results (snapshot)

AACT 2026-04-12 corpus = ~2,277 malaria trials (intentionally broad WHO-antimalarial inclusion; see design §5).

| Pilot | Title | Magnitude (95% CI) | n | Follow-up |
|---|---|---|---|---|
| P01 | Reporting compliance | 7.6% [6.3%, 9.1%] | 1,420 | 4/5 |
| P02 | Endpoint-family chaos | 28.5% [25.8%, 31.4%] | 997 | 5/5 |
| P03 | PCR-corrected reporting | 2.8% [2.0%, 3.9%] | 1,276 | 5/5 |
| P04 | Resistance-era pooling | 19.1% [14.8%, 24.4%] | 256 cells | 5/5 |
| P05 | Pediatric dose fragmentation | 17.0 doses/cell [9.18, 26.28] | 22 cells | 3/5 |
| P06 | Cross-registry coverage (probe) | — | 24/2,277 | 2/5 |
| P07 | Sponsor PDP misclass | 2.9% [2.3%, 3.7%] | 2,277 | 3/5 |
| P08 | Retro registration | 35.5% [33.5%, 37.5%] | 2,242 | 4/5 |
| P09 | Geographic transmission (probe) | — | top10 reported | 2/5 |
| P10 | CHMI vs field mixing | 22.9% [18.3%, 28.2%] | 271 | 4/5 |

Live dashboard: https://mahmood726-cyber.github.io/malaria-ct-recon/ (deployed via GitHub Pages on push)

Headline candidates for follow-up paper/atlas: P02 (endpoint chaos), P03 (PCR-corrected), P04 (K13 era).

## Output

`dashboard/data/signal-table.csv` ranks the 10 pilots by magnitude and follow-up potential.
