# malaria-ct-recon

10-pilot reconnaissance of bias sources in malaria trial data on ClinicalTrials.gov.

**Snapshot:** AACT 2026-04-12 (frozen).
**Status:** v0.1.4 shipped 2026-05-04 — multi-persona review fixes (5 P0 + most P1 closed). v0.1.3 swapped WHO mandate year 2008→2009 after the 2008 doc was identified as the wrong reference. v0.2.0 reserved for submission-ready (post user review).

See `docs/superpowers/specs/2026-04-30-malaria-ct-recon-design.md` for the design.

## Quickstart

1. Install: `pip install -e .[dev]`
2. Configure snapshot path: `cp aact_path.toml.example aact_path.toml` and edit
3. Run tests: `pytest -q`
4. Run preflight: `python -m pilots.preflight`
5. Run all pilots: `python -m pilots.run_all`
6. Open `dashboard/index.html` in a browser

## Methods Note paper draft

A Synthēsis Methods Note (≤400 words) is drafted in `paper/methods-note-draft.md`
and built to .docx by `paper/build_docx.py`. It hangs on the P01 (FDAAA
results-posting) and P03 (WHO PCR-correction declaration) trajectories. Both
mandates are undercomplied with by an order of magnitude; FDAAA compliance is
rising while WHO PCR-correction declaration is declining.

The §4 sensitivity analysis (uncomplicated-*P. falciparum* subset) is
implemented in `pilots/p03_sensitivity_uncomplicated_falciparum.py`; its
result automatically locks the body sentence variant via
`pilots/p03_decision_rule.py` (output: `pilots/results/decision_rule.json`).
Design spec: `docs/superpowers/specs/2026-05-03-methods-paper-design.md`,
OTS-anchored 2026-05-03.

## Preregistration

Framework + design soft-preregistered on 2026-04-30 against framework HEAD `26a3fb0a4610816382cf3024c748d508b3af1180`. See `.preregistration_commit.txt` for the pinned contents manifest. OpenTimestamps Bitcoin anchoring is applied post-push to GitHub (see release tag v0.1.0). Downstream consumers can verify the framework state by `git checkout 26a3fb0a4610816382cf3024c748d508b3af1180` and inspecting the pinned files.

## Integrity chain

The repo combines three integrity layers so a reviewer can verify both the data-pipeline state and the design spec without trusting the author:

1. **Per-pilot self-hash.** Each `pilots/p*.py` writes its own SHA-256 into `dashboard/data/signal-table.csv` (column `script_sha256`). This is *not* an external pin — it's a tamper-evident witness: if a pilot file is edited and re-run, the column changes.
2. **Framework HEAD pin.** Commit `26a3fb0` (2026-04-30) is the immutable framework reference. `.preregistration_commit.txt` lists the framework files; `.preregistration_commit.txt.ots` is the OpenTimestamps Bitcoin attestation against that commit. Tampering with any framework file would change the git tree hash, breaking the OTS receipt.
3. **Design spec OTS anchor.** `docs/superpowers/specs/2026-05-03-methods-paper-design.md.ots` anchors the methods-paper design (commit `535fa2e`) to Bitcoin block 947705. The §4 decision-rule ladder was committed before any data was seen; `pilots/p03_decision_rule.py` reads the sensitivity CSV and locks the body sentence deterministically — the paper's body-sentence is a function of the data, not the writer's interpretation.
4. **Per-tag commit anchor.** `.v013_commit.txt.ots` anchors the v0.1.3 release commit; same convention will apply to subsequent tags.

Verification: `ots-cli.js verify <file>.ots` against the upstream Bitcoin calendars. The chain closes from spec → framework HEAD → release commit → per-pilot SHA in CSV.

## Results (snapshot)

AACT 2026-04-12 corpus = ~2,277 malaria trials (intentionally broad WHO-antimalarial inclusion; see design §5).

| Pilot | Title | Magnitude (95% CI) | n | Follow-up |
|---|---|---|---|---|
| P01 | Reporting compliance | 7.6% [6.3%, 9.1%] | 1,420 | 4/5 |
| P02 | Endpoint-family chaos | 28.5% [25.8%, 31.4%] | 997 | 5/5 |
| P03 | PCR-corrected reporting | 2.8% [2.0%, 3.8%] strict / 7.5% [6.2%, 9.1%] broad | 1,270 | 5/5 |
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
