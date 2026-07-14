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
  gender: true, // Genderhinweis anzeigen (nur Deutsch)

  // ---------- Verzeichnisse ----------
  show-toc: true,
  show-list-of-figures: true,
  show-list-of-tables: true,
  show-list-of-listings: true,

  // ---------- Titel ----------
  title-de: "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod",
  title-en: "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod",

  // ---------- Autor:innen  ((Vorname, Nachname, ORCID)) ----------
  authors: (
    ("Max", "Musterman", "0009-0009-7381-894X"),
    ("Erika", "Musterman", none),
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
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy
    eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam
    voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet
    clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit
    amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam
    nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed
    diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum.
    Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor
    sit amet.
  ],
  abstract-en: [
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy
    eirmod tempor invidunt ut labore et dolore magna aliquyam erat.
  ],

  // ---------- Optionale Nachschlage-Verzeichnisse ----------
  // Auf `none` setzen, um sie auszublenden.
  acronym-entries: (
    ("HTML", "Hypertext Markup Language"),
    ("PDF", "Portable Document Format"),
    ("THMA", "Technische Hochschule Mannheim"),
  ),
  glossary-entries: (
    ("Kopplung", "Grad der Abhängigkeit zwischen zwei Komponenten."),
    ("Rover", "Ein mobiles Erkundungsfahrzeug."),
  ),
  symbol-entries: (
    ($a$, "Beschleunigung", $upright("m")/upright("s")^2$),
    ($F$, "Kraft", $upright("N")$),
    ($rho$, "Dichte", $upright("kg")/upright("m")^3$),
  ),

  // ---------- Literatur ----------
  bib: bibliography("literatur.bib", style: "ieee", title: "Literaturverzeichnis"),
)

// ---------- Kapitel (aus dem Ordner /kapitel) ----------
#include "kapitel/kapitel1.typ"
#include "kapitel/kapitel2.typ"
#include "kapitel/kapitel3.typ"
#include "kapitel/kapitel4.typ"
#include "kapitel/kapitel5.typ"
#include "kapitel/kapitel6.typ"

// ---------- Anhang ----------
// Ab hier werden Kapitel mit Buchstaben (A, B, ...) nummeriert.
// #show: appendix
// = Ein Anhang
