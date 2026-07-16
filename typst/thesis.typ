// *******************************************************************
// Hauptdokument der Abschlussarbeit
//
// Bauen mit:   typst compile thesis.typ
//
// Hier tragen Sie Ihre Angaben ein (entspricht docinfo.tex) und binden
// die Kapitel ein. Das gesamte Layout steckt in lib.typ und muss
// normalerweise nicht angepasst werden.
// *******************************************************************

#import "lib.typ": *

#show: thesis.with(
  // ---------- Sprache & Format ----------
  language: "de", // "de" fuer Deutsch, "en" fuer Englisch
  submission: "digital", // "digital" (einseitig, zentriert) oder "papier" (zweiseitig, Fenster)
  license: "opensource", // opensource | hs | stud | vertraulich
  gender: false, // Genderhinweis anzeigen (nur Deutsch)

  // ---------- Verzeichnisse ----------
  show-toc: true,
  show-list-of-figures: false,
  show-list-of-tables: false,
  show-list-of-listings: false,

  // ---------- Titel ----------
  title-de: "TODO: Titel der Arbeit",
  title-en: "TODO: Title of the thesis",

  // ---------- Autor:innen  ((Vorname, Nachname, ORCID)) ----------
  authors: (
    ("Florian", "Babel", "0009-0004-8006-7762"),
    ("Johannes", "Pielmeier", none),
    ("Jaronim", "Pracht", "0009-0003-2539-0666"),
  ),

  // ---------- Weitere Angaben ----------
  city: "Mannheim",
  date: datetime(year: 2026, month: 7, day: 24),
  supervisor: "Prof. Thomas Ihme",
  second-examiner: "",
  faculty: "I", // I, E, S, B, D, M, N, W, V
  course: "IM", // IB IMB UIB CSB IM MTB ... (siehe lib.typ)

  // ---------- Abstract ----------
  abstract-de: [
    TODO: Deutsche Kurzfassung.
  ],
  abstract-en: [
    TODO: English abstract.
  ],

  // ---------- Optionale Nachschlage-Verzeichnisse ----------
  // Auf `none` setzen, um sie auszublenden.
  acronym-entries: (
    none
  ),
  glossary-entries: (
    none
  ),
  symbol-entries: (
    none
  ),

  // ---------- Literatur ----------
  bib: bibliography("literatur.bib", style: "ieee", title: "Literaturverzeichnis"),
)

// ---------- Kapitel (aus dem Ordner /kapitel) ----------
#include "kapitel/01-einleitung.typ"
#include "kapitel/02-grundlagen.typ"
#include "kapitel/03-system-design.typ"
#include "kapitel/04-umsetzung.typ"
#include "kapitel/05-ergebnisse.typ"
#include "kapitel/06-fazit.typ"

// ---------- Anhang ----------
// Ab hier werden Kapitel mit Buchstaben (A, B, ...) nummeriert.
// #show: appendix
// = Ein Anhang
