# ITAT 2026 / CEUR-WS — Submission Checklist

Paper: *Automated Conjecturing Pipeline for Graph Theory* (`itat_pipeline.tex`)
Venue: ITAT 2026, 25–29 Sep 2026, Vršatec, Slovakia · CEUR-WS (indexed in Scopus)

## Status of the source (verified)

- One-column `ceurart` class — correct ITAT/CEUR template.
- All 29 `\cite` keys are present in `sample-ceur.bib` — no citation orphans.
- No LaTeX errors in the body; document typesets end-to-end.
- "Declaration on Generative AI" section present (required by CEUR camera-ready).
- `\conference` line updated to the official string (dates + Vršatec venue).
- `orcid=` field added to the author block (placeholder).
- `itat_pipeline.xmpdata` being empty is harmless — the class regenerates it on
  every compile, and this `ceurart` build does not load `pdfx`.

## You must do before submitting

1. **Author block** (`itat_pipeline.tex`, ~lines 28–34): replace the placeholders
   `Author One`, `author.one@example.org`, `0000-0000-0000-0000`, and
   `Affiliation, City, Country` with real values. ITAT review is **not**
   double-blind, so named authors are expected in the review PDF.
2. **Compile with Libertinus fonts.** CEUR explicitly requires the Libertinus
   font family. Your `Makefile` uses `lualatex`, which is correct — just run
   `make` on a TeX install that has the `libertinus` package. Do **not** submit a
   PDF built with a fallback font.
3. **Pick the workshop track** on EasyChair. For graph-theory conjecturing, CADM
   (Computational Aspects of Large-Scale Problems in Discrete Mathematics) is the
   natural fit. Page limits are set per workshop — confirm yours (paper is ~6 pp).

## Review submission (now)

- Submit the **PDF only** via EasyChair: https://www.easychair.org/conferences/?conf=itat2026

## Camera-ready (if accepted) — ZIP containing

- All LaTeX source files + the compiled PDF.
- The "Declaration on Generative AI" section (already present).
- Scan of the **signed CEUR author agreement** — use the **NTP** variant
  (no third-party copyrighted material): `ceur-author-agreement-ccby-ntp.pdf`.
  - Event field: *ITAT 2026: Information Technologies – Applications and Theory, 2026*
  - Editors: Ciencialová, Holeňa, Jajcay, Jajcayová, Mačaj, Mráz, Ostertág,
    Pardubská, Plátek, Stanek.

## Optional polish

- `sample-ceur.bib` has one unused entry (`jacobs2020graph`) — harmless; remove if
  you want a tidy bib.
