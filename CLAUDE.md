# Toolkit — CLAUDE.md

Collezione di script Python standalone per elaborazione batch di immagini, PDF e video su Windows. Ogni script nella root è pensato per essere **avviato con doppio click** (associazione `.py` → `py.exe`): nessun argomento CLI, tutto interattivo.

## Architettura: `_core/`

Tutto il boilerplate condiviso vive nel package `_core/` (underscore = non è uno script cliccabile). Il flusso obbligatorio di ogni script root è garantito da `_core`:

1. **UTF-8 console fix** — automatico all'import di `_core` (la console Windows è cp1252 e rompe ✓/✗).
2. **Check dipendenze** — `require_pip(PIL="Pillow", ...)` (chiave = import name, valore = pip name) e `require_bin("ffmpeg", "ffprobe")`. Messaggio `⚠ MISSING DEPENDENCY` con comando di installazione, pausa, exit 1. **Va chiamato prima degli import reali** delle librerie.
3. **Banner + pausa finale garantita** — decoratore `@run("NOME SCRIPT")` su `main()`: stampa il banner, cattura ogni eccezione e fa **sempre** `input("Press ENTER to exit...")` in `finally`, così la finestra non si chiude mai su un errore non letto.
4. **Setup cartelle** — `iter_src({'.jpg', ...})` crea `src/` e `out/`, verifica che `out/` sia scrivibile e ritorna i file ordinati filtrati per estensione. `OUT_DIR` / `SRC_DIR` esportati da `_core`.
5. **Input interattivi** — `ask_choice(prompt, options, default)` (menu numerato, 1-based, input invalido → default), `ask_int`, `ask_float`, `ask_text`, `ask_yes_no`.
6. **Elaborazione** — loop sui file: `✓ nome -> out` o `✗ errore` per file, mai interrompere il batch per un file rotto. Per ffmpeg usare `run_ffmpeg(cmd, name)` che filtra lo stderr alle righe rilevanti.
7. **Riepilogo** — `done(processed, total, "images")` → `=== Done! N/M ... ===`. Se `src/` è vuota: `no_files_warning("images", SUPPORTED)`.

Scheletro di uno script:

```python
from _core import run, require_pip, iter_src, no_files_warning, done, ask_choice, OUT_DIR

require_pip(PIL="Pillow")
from PIL import Image

SUPPORTED = {'.jpg', '.png'}

@run("MY SCRIPT")
def main():
    level = ask_choice("Level", ["Light", "Heavy"], default=1)
    files = iter_src(SUPPORTED)
    if not files:
        no_files_warning("images", SUPPORTED)
        return
    processed = sum(process(f, OUT_DIR / f.name) for f in files)
    done(processed, len(files), "images")

main()
```

## Convenzioni

- **Lingua:** codice e output utente in **inglese**; README in inglese.
- **Naming:** `<categoria>_<azione>.py` (es. `images_resize.py`, `pdf_merge.py`). Categorie: `images_`, `pdf_`, `videos_`, altro.
- Dipendenze ammesse: stdlib + `Pillow`, `pillow-heif`, `pypdf`, `pypdfium2`, `reportlab`, `markdown`, `xhtml2pdf`, ffmpeg via subprocess. Non aggiungere librerie nuove senza motivo.
- Configurazione locale in `.env` (gitignored), template in `.env.example`. Parsing `.env` a mano con stdlib (vedi `hosts_add.py`), niente python-dotenv.

## Struttura

- Root: script doppio-click che lavorano su `src/` → `out/`, tutti basati su `_core`.
- `hosts_add.py`: caso speciale (auto-elevazione admin, modifica il file hosts di Windows, non usa `src/`/`out/` né `_core`).
- `themes/`: design system custom per `md_to_pdf.py` — un file `.css` per tema, elencati automaticamente nel menu. Limiti del renderer xhtml2pdf documentati in `themes/README.md` (no flexbox/grid/var(), sfondo pagina solo via `@page background-image`, font custom via `@font-face` + `.ttf` locale).
- `server-kit/`: script CLI da server, prendono la directory target come argomento (`argparse`), **non** usano `src/`/`out/` né `_core`, nessuna pausa interattiva.
- `src/` e `out/` sono gitignored.

## Quando modifichi o aggiungi uno script

- Usa `_core`: mai duplicare boilerplate (check dipendenze, pause, setup cartelle, prompt).
- Aggiorna sempre la sezione corrispondente del `README.md` (formati supportati, modi interattivi, dipendenze).
- Test manuale senza interattività: `printf '1\n\n' | py script.py` con file campione in `src/` (le risposte ai prompt vanno in ordine; l'ultimo `\n` è la pausa finale).
