# web_site

Quarto sources for <https://kengo-shinoda.github.io/>.

## Build

Run `quarto render` from this directory to build both languages into `docs/`.
The `scripts/localize-navigation.py` post-render hook sets navigation labels,
active links, privacy links, and the corresponding-page language switch.
It also runs after partial renders; do not edit generated HTML by hand.
Python 3.9 or later is required for the hook.

## Japanese and English pages

Japanese sources live at the repository root; matching English sources live
under `en/` with the same filenames. Both use the same `styles.css`, theme,
layout classes, images, section order, and list numbering. When updating a page,
update its counterpart as well. Add both files to `_quarto.yml` when adding a
new top-level page. Notes are discovered under `notes/` and `en/notes/`.

English translations of Japanese presentation titles and meeting names are
descriptive; keep any supplied official English wording when it is available.

PDFs and their QR codes live under `papers/` and are copied during rendering.
Keep published PDF filenames stable to preserve existing QR code links.
