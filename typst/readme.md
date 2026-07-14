# Vorlage für Abschlussarbeiten mit Typst

Typst-Portierung der LaTeX-Vorlage der Technischen Hochschule Mannheim
(Dokumentenklasse `HMA`). Design, Schriften, Farben, Titelseite und
Verzeichnisse entsprechen der LaTeX-Vorlage.

## Bauen

```sh
typst compile thesis.typ        # erzeugt thesis.pdf
typst watch thesis.typ          # baut bei jeder Änderung neu
```

Benötigt Typst ≥ 0.12 sowie die Schriften **TeX Gyre Termes** und
**TeX Gyre Heros** (in TeX-Live enthalten). Zusätzliche Pakete oder
externe Tools (biber, makeglossaries) sind nicht nötig – Literatur,
Verzeichnisse und Nummerierung sind nativ umgesetzt.

## Aufbau

| Datei | Zweck |
|-------|-------|
| `thesis.typ` | Hauptdokument – hier tragen Sie Ihre Angaben ein (entspricht `docinfo.tex`) und binden die Kapitel ein. |
| `lib.typ` | Template-Modul mit dem gesamten Layout (entspricht `hma.cls` + `preambel.tex` + `titlepage.sty` + `studiengaenge.tex`). Muss normalerweise nicht verändert werden. |
| `kapitel/kapitel*.typ` | Ihre einzelnen Kapitel. |
| `bilder/` | Bilder (das Logo `hsma-logo.svg`, Beispielbilder). |
| `src/` | Beispiel-Quelltexte. |
| `literatur.bib` | Literaturdatenbank im BibTeX-Format (wie in LaTeX). |

## Optionen (in `thesis.typ`)

- `language`: `"de"` oder `"en"`
- `submission`: `"digital"` (einseitig, Titel zentriert) oder `"papier"`
  (zweiseitig, Titel für das Fenster des offiziellen Umschlags versetzt)
- `license`: `opensource` | `hs` | `stud` | `vertraulich`
- `gender`: Genderhinweis anzeigen (nur Deutsch)
- `show-toc`, `show-list-of-figures`, `show-list-of-tables`,
  `show-list-of-listings`: Verzeichnisse an-/abschalten
- `acronym-entries`, `glossary-entries`, `symbol-entries`: Inhalte der
  Nachschlage­verzeichnisse (`none` = ausblenden)

## Hilfsbefehle (aus `lib.typ`)

- `#bild("pfad", breite, [Beschriftung], label: <ref>)` – Bild einbinden
- `#listing(caption: [...], ```lang ... ```)` – Quellcode mit Zeilennummern
- `#snowcard(...)` – Anforderungskarte
- `#qas(...)` – Quality Attribute Scenario
- `#harveyball(0.5)` – Harvey Ball (0…1)
- `#checklist([...], [...])` – Checkliste
- `#show: appendix` – ab hier Kapitelnummerierung mit Buchstaben (A, B, …)

## Unterschiede zur LaTeX-Vorlage

- Syntax-Highlighting von Quellcode nutzt Typsts eingebauten Highlighter
  (Farbschema weicht leicht vom LaTeX-`listings`-Schema ab).
- Ein Stichwortverzeichnis (Index, `imakeidx`) ist nicht enthalten, da
  Typst dafür (noch) keine native Unterstützung bietet.
- Zitate: `@key` (numerisch), `#cite(<key>, form: "prose"/"author"/"year"/"full")`.
