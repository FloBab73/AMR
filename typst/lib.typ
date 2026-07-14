// *******************************************************************
// HMA Thesis Template — Typst-Portierung der LaTeX-Vorlage der
// Technischen Hochschule Mannheim (Dokumentenklasse HMA).
//
// Ein einziges wiederverwendbares Template-Modul. Binden Sie es in
// Ihrem Hauptdokument ein:
//
//   #import "lib.typ": *
//   #show: thesis.with( ... )
//
// Alle bibliografischen Angaben werden als benannte Argumente an
// `thesis` uebergeben (siehe thesis.typ / docinfo).
// *******************************************************************

// -------------------------------------------------------------------
// Schriften
// -------------------------------------------------------------------
#let serif-font = "TeX Gyre Termes" // Fliesstext (Times-Aequivalent)
#let sans-font = "TeX Gyre Heros" // Ueberschriften, Beschriftungen (Helvetica)
#let mono-font = "DejaVu Sans Mono"

// -------------------------------------------------------------------
// Farben (aus hma.cls uebernommen)
// -------------------------------------------------------------------
#let HMA-linkblue = rgb(0, 0, 100)
#let HMA-linkblack = rgb(0, 0, 0)
#let HMA-comment = rgb(63, 127, 95)
#let HMA-darkgreen = rgb(14, 144, 102)
#let HMA-darkblue = rgb(0, 0, 168)
#let HMA-darkred = rgb(128, 0, 0)
#let HMA-javadoccomment = rgb(0, 0, 240)
#let backcolour = rgb(242, 242, 235) // 0.95, 0.95, 0.92

// -------------------------------------------------------------------
// Sprachabhaengige Textbausteine
// -------------------------------------------------------------------
#let strings-de = (
  abstract-title: "Abstrakt",
  contents: "Inhaltsverzeichnis",
  list-of-figures: "Abbildungsverzeichnis",
  list-of-tables: "Tabellenverzeichnis",
  list-of-listings: "Quellcodeverzeichnis",
  listing: "Quellcode",
  figure: "Abbildung",
  table: "Tabelle",
  abbreviations: "Abkürzungsverzeichnis",
  glossary: "Glossar",
  list-of-symbols: "Symbolverzeichnis",
  symb-sign: "Symbol",
  symb-description: "Beschreibung",
  symb-unit: "Einheit",
  bibliography: "Literaturverzeichnis",
  tutors: "Betreuer",
  course: "Studiengang",
  declaration: "Erklärung",
  gender-note: [
    Aus Gründen der besseren Lesbarkeit wird in dieser Arbeit auf die
    gleichzeitige Verwendung männlicher und weiblicher Sprachformen
    verzichtet. Sämtliche Personenbezeichnungen gelten gleichermaßen für
    alle Geschlechter.
  ],
  // Snowcard-Beschriftungen
  sc-anforderung: "Anforderung", sc-no: "Nr", sc-art: "Art", sc-prio: "Prio",
  sc-titel: "Titel", sc-herkunft: "Herkunft", sc-konflikt: "Konflikte",
  sc-beschreibung: "Beschreibung", sc-fitkriterium: "Fit-Kriterium",
  sc-material: "Weiteres Material",
  // QAS-Beschriftungen
  qas-anforderung: "QAS", qas-no: "Nr", qas-art: "Art", qas-prio: "Prio",
  qas-titel: "Titel", qas-quelle: "Quelle", qas-stimulus: "Stimulus",
  qas-artefakt: "Artefakt", qas-umgebung: "Umgebung", qas-antwort: "Antwort",
  qas-mass: "Maß für Antwort",
)

#let strings-en = (
  abstract-title: "Abstract",
  contents: "Contents",
  list-of-figures: "List of Figures",
  list-of-tables: "List of Tables",
  list-of-listings: "Listings",
  listing: "Source Code",
  figure: "Figure",
  table: "Table",
  abbreviations: "List of Abbreviations",
  glossary: "Glossary",
  list-of-symbols: "List of Symbols",
  symb-sign: "Sign",
  symb-description: "Description",
  symb-unit: "Unit",
  bibliography: "Bibliography",
  tutors: "Tutors",
  course: "Course of Studies",
  declaration: "Declaration",
  gender-note: [],
  sc-anforderung: "Requirement", sc-no: "#", sc-art: "Type", sc-prio: "Prio",
  sc-titel: "Title", sc-herkunft: "Origin", sc-konflikt: "Conflicts",
  sc-beschreibung: "Description", sc-fitkriterium: "Fit Criterion",
  sc-material: "Supporting Material",
  qas-anforderung: "QAS", qas-no: "#", qas-art: "Type", qas-prio: "Prio",
  qas-titel: "Title", qas-quelle: "Source", qas-stimulus: "Stimulus",
  qas-artefakt: "Artifact", qas-umgebung: "Environment", qas-antwort: "Response",
  qas-mass: "Response Measure",
)

// -------------------------------------------------------------------
// Fakultaeten der HS-Mannheim  (aus studiengaenge.tex)
// -------------------------------------------------------------------
#let faculties = (
  I: (de: "Fakultät für Informatik", en: "Department of Computer Science"),
  E: (de: "Fakultät für Elektrotechnik", en: "Department of Electrical Engineering"),
  S: (de: "Fakultät für Sozialwesen", en: "Department of Social Work"),
  B: (de: "Fakultät für Biotechnologie", en: "Department of Biotechnology"),
  D: (de: "Fakultät für Gestaltung", en: "Department of Design"),
  M: (de: "Fakultät für Maschinenbau", en: "Department of Mechanical Engineering"),
  N: (de: "Fakultät für Informationstechnik", en: "Department of Information Technology"),
  W: (de: "Fakultät für Wirtschaftsingenieurwesen", en: "Department of Engineering and Management"),
  V: (de: "Fakultät für Verfahrens- und Chemietechnik", en: "Department of Chemical Process Engineering"),
)

// -------------------------------------------------------------------
// Abschluesse
// -------------------------------------------------------------------
#let degrees = (
  bsc: "Bachelor of Science (B.Sc.)",
  ba: "Bachelor of Arts (B.A.)",
  msc: "Master of Science (M.Sc.)",
  ma: "Master of Arts (M.A.)",
  mba: "Master of Business Administration (MBA)",
)

// -------------------------------------------------------------------
// Studiengaenge der HS-Mannheim  (aus studiengaenge.tex)
//   (de, en, typ-de, typ-en, grad)
// -------------------------------------------------------------------
#let courses = (
  IB: ("Informatik", "Computer Science", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  IMB: ("Medizinische Informatik", "Medical Informatics", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  UIB: ("Unternehmens- und Wirtschaftsinformatik", "Enterprise Computing", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  CSB: ("Cyber Security", "Cyber Security", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  IM: ("Informatik", "Computer Science", "Master-Thesis", "Master Thesis", "msc"),
  MEB: ("Mechatronik", "Mechatronic", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  UB: ("Automatisierungstechnik", "Automation Technology", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  ELB: ("Elektro- und Informationstechnik/Ingenieurpädagogik", "Elektro- und Informationstechnik/Ingenieurpädagogik", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  EBE: ("Energietechnik und erneuerbare Energien", "Power Engineering and Renewable Energies", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  TS: ("Translation Studies", "Translation Studies", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  EM: ("Automatisierungs- und Energiesysteme", "Automation and Energy Systems", "Master-Thesis", "Master Thesis", "msc"),
  ELM: ("Lehramt Ingenieurpädagogik", "Lectureship Educational Engineering", "Master-Thesis", "Master Thesis", "msc"),
  SAB: ("Soziale Arbeit", "Social Labour", "Bachelor-Thesis", "Bachelor Thesis", "ba"),
  SAM: ("Soziale Arbeit", "Social Labour", "Master-Thesis", "Master Thesis", "ma"),
  BB: ("Biotechnology", "Biotechnology", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  BCB: ("Biologische Chemie", "Biological Chemics", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  BMEBST: ("Biotechnology - Biomedical Science and Technology", "Biotechnology - Biomedical Science and Technology", "Master-Thesis", "Master Thesis", "msc"),
  BMEBPD: ("Biotechnology - Bioprocess Development", "Biotechnology - Bioprocess Development", "Master-Thesis", "Master Thesis", "msc"),
  BLSM: ("Life Science Management", "Life Science Management", "Master-Thesis", "Master Thesis", "msc"),
  KDB: ("Kommunikationsdesign", "Communication Design", "Bachelor-Thesis", "Bachelor Thesis", "ba"),
  KDM: ("Kommunikationsdesign", "Communication Design", "Master-Thesis", "Master Thesis", "ma"),
  MB: ("Maschinenbau", "Mechanical Engineering", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  MM: ("Maschinenbau", "Mechanical Engineering", "Master-Thesis", "Master Thesis", "msc"),
  NEB: ("Elektronik", "Electronics", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  TIB: ("Technische Informatik", "Technical Information Technology", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  MTB: ("Medizintechnik", "Medical Technology", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  MTM: ("Medizintechnik", "Medical Technology", "Master-Thesis", "Master Thesis", "msc"),
  NM: ("Informationstechnik", "Informationstechnik", "Master-Thesis", "Master Thesis", "msc"),
  WB: ("Wirtschaftsingenieurwesen", "Engineering and Management", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  WM: ("Wirtschaftsingenieurwesen", "Engineering and Management", "Master-Thesis", "Master Thesis", "msc"),
  VB: ("Verfahrenstechnik", "Process Engineering", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  CB: ("Chemische Technik", "Chemical Engineering", "Bachelor-Thesis", "Bachelor Thesis", "bsc"),
  CM: ("Chemieingenieurwesen", "Chemical Engineering", "Master-Thesis", "Master Thesis", "msc"),
)

// -------------------------------------------------------------------
// Zustaende (fuer die roemische Seitennummerierung im backmatter)
// -------------------------------------------------------------------
#let frontmatter-end = state("hma-frontmatter-end", 1)
// Dokumentteil: "front" (roemisch), "main" (arabisch), "back" (roemisch)
#let matter = state("hma-matter", "front")

// ===================================================================
// Autoren-Helfer: ORCID-Link
// ===================================================================
#let orcid(id) = box(baseline: 15%)[#text(size: 0.85em)[ID: #id]]

// ===================================================================
// bild — Bild einbinden (entspricht \bild aus preambel.tex)
//   #bild("kapitel3/nasa_rover.jpg", 60%, [Ein Nasa Rover], label: <fig:rover>)
// ===================================================================
#let bild(path, width, caption, label: none) = {
  let f = figure(image(path, width: width), caption: caption)
  if label != none { [#f #label] } else { f }
}

// ===================================================================
// Quellcode-Listing  (entspricht listings / lstlisting)
//   Hintergrund backcolour, Zeilennummern, Bildunterschrift "Quellcode N".
// ===================================================================
#let listing(body, caption: none, label: none) = {
  let content = {
    show raw.line: it => box(width: 100%)[
      #box(width: 1.6em, align(right, text(size: 0.7em, fill: gray)[#it.number]))
      #h(0.6em)
      #it.body
    ]
    set text(size: 9pt, font: mono-font)
    block(
      fill: backcolour,
      width: 100%,
      inset: (x: 0.4cm, y: 0.5em),
      radius: 1pt,
      body,
    )
  }
  let f = figure(
    content,
    caption: caption,
    kind: "listing",
    supplement: context (if text.lang == "en" { strings-en.listing } else { strings-de.listing }),
  )
  if label != none { [#f #label] } else { f }
}

// ===================================================================
// Harvey Balls  (entspricht harveyballs)
//   #harveyball(0.5)  -> Fuellgrad 0..1  (0, 0.25, 0.5, 0.75, 1)
// ===================================================================
#let harveyball(fraction) = {
  let glyphs = ("○", "◔", "◑", "◕", "●")
  let idx = int(calc.round(fraction * 4))
  idx = calc.max(0, calc.min(4, idx))
  text(size: 1.1em, glyphs.at(idx))
}

// ===================================================================
// Checkliste (entspricht dem checklist-Environment)
//   #checklist([Punkt 1], [Punkt 2])
// ===================================================================
#let checklist(..items) = {
  for it in items.pos() [
    #box(sym.ballot) #h(0.4em) #it \
  ]
}

// ===================================================================
// Nachschlage-Umgebungen (Abkuerzungen / Glossar / Symbole)
// ===================================================================

// Abkuerzungsverzeichnis: entries = ((kurz, lang), ...)
#let acronyms(entries, lang: "de") = {
  let s = if lang == "en" { strings-en } else { strings-de }
  heading(level: 1, numbering: none, s.abbreviations)
  table(
    columns: (auto, 1fr),
    stroke: none,
    column-gutter: 1em,
    row-gutter: 0.6em,
    ..entries.map(e => (strong(e.at(0)), e.at(1))).flatten(),
  )
}

// Glossar: entries = ((begriff, erklaerung), ...)
#let glossary(entries, lang: "de") = {
  let s = if lang == "en" { strings-en } else { strings-de }
  heading(level: 1, numbering: none, s.glossary)
  for e in entries [
    *#e.at(0)*#h(0.5em)#e.at(1)

  ]
}

// Symbolverzeichnis: entries = ((symbol, beschreibung, einheit), ...)
// entspricht dem 3-spaltigen "symbunitlong"-Stil
#let symbols(entries, lang: "de") = {
  let s = if lang == "en" { strings-en } else { strings-de }
  heading(level: 1, numbering: none, s.list-of-symbols)
  table(
    columns: (auto, 1fr, 2cm),
    stroke: (x, y) => if y == 0 { (bottom: 0.5pt) },
    align: (left, left, center),
    column-gutter: 1em,
    row-gutter: 0.6em,
    table.header(strong(s.symb-sign), strong(s.symb-description), strong(s.symb-unit)),
    ..entries.map(e => (e.at(0), e.at(1), e.at(2))).flatten(),
  )
}

// Verzeichnis fuer Abbildungen / Tabellen / Quellcode.
// Nummer und Seitenzahl werden am ORT der jeweiligen Gleitumgebung
// ausgewertet, damit die kapitelweise Nummerierung (N.M) auch im
// Verzeichnis korrekt erscheint.
#let list-of(target, title) = context {
  let items = query(target)
  heading(level: 1, numbering: none, title)
  for it in items {
    let loc = it.location()
    let ch = counter(heading).at(loc).first()
    let n = counter(target).at(loc).first()
    block(above: 0.55em, below: 0.55em, {
      set text(font: sans-font)
      link(loc)[
        #strong[#it.supplement #str(ch).#str(n)]#h(0.6em)#it.caption.body
        #box(width: 1fr, inset: (x: 3pt), repeat[.])
        #counter(page).at(loc).first()
      ]
    })
  }
}

// ===================================================================
// Snowcard — Anforderungskarte (entspricht \snowcard, 9 Argumente)
// ===================================================================
#let snowcard(
  nr, art, prio, titel,
  herkunft: none, konflikt: none, beschreibung: none,
  fitkriterium: none, material: none, lang: "de", label: none,
) = {
  let s = if lang == "en" { strings-en } else { strings-de }
  let full = cell => table.cell(colspan: 6, cell)
  let f = figure(
    kind: table,
    caption: [#s.sc-anforderung #nr -- #titel],
    {
      set text(font: sans-font, size: 9pt)
      table(
        columns: (auto, 1fr, auto, 1fr, auto, 1fr),
        stroke: none,
        table.hline(stroke: 1pt),
        strong(s.sc-no), [#nr], strong(s.sc-art), [#art], strong(s.sc-prio), [#prio],
        table.hline(stroke: 0.5pt),
        table.cell(colspan: 2, strong(s.sc-titel)), table.cell(colspan: 4, titel),
        ..if herkunft != none {(table.cell(colspan: 2, strong(s.sc-herkunft)), table.cell(colspan: 4, herkunft))} else {()},
        ..if konflikt != none {(table.cell(colspan: 2, strong(s.sc-konflikt)), table.cell(colspan: 4, konflikt))} else {()},
        full(strong(s.sc-beschreibung)), full(beschreibung),
        ..if fitkriterium != none {(full(strong(s.sc-fitkriterium)), full(fitkriterium))} else {()},
        ..if material != none {(full(strong(s.sc-material)), full(material))} else {()},
        table.hline(stroke: 1pt),
      )
    },
  )
  if label != none { [#f #label] } else { f }
}

// ===================================================================
// QAS — Quality Attribute Scenario (entspricht \qas, 9 Argumente)
// ===================================================================
#let qas(
  nr, prio, titel, quelle, stimulus, artefakt,
  umgebung, antwort, mass, lang: "de", label: none,
) = {
  let s = if lang == "en" { strings-en } else { strings-de }
  let full = cell => table.cell(colspan: 6, cell)
  let f = figure(
    kind: table,
    caption: [#s.qas-anforderung #nr -- #titel],
    {
      set text(font: sans-font, size: 9pt)
      table(
        columns: (auto, 1fr, auto, 1fr, auto, 1fr),
        stroke: none,
        table.hline(stroke: 1pt),
        strong(s.qas-no), [#nr], strong(s.qas-art), [QAS], strong(s.qas-prio), [#prio],
        table.hline(stroke: 0.5pt),
        table.cell(colspan: 2, strong(s.qas-titel)), table.cell(colspan: 4, titel),
        table.cell(colspan: 2, strong(s.qas-quelle)), table.cell(colspan: 4, quelle),
        table.cell(colspan: 2, strong(s.qas-stimulus)), table.cell(colspan: 4, stimulus),
        table.cell(colspan: 2, strong(s.qas-artefakt)), table.cell(colspan: 4, artefakt),
        full(strong(s.qas-umgebung)), full(umgebung),
        full(strong(s.qas-antwort)), full(antwort),
        full(strong(s.qas-mass)), full(mass),
        table.hline(stroke: 1pt),
      )
    },
  )
  if label != none { [#f #label] } else { f }
}

// ===================================================================
// Anhang — schaltet die Kapitelnummerierung auf Buchstaben (A, B, ...)
//   #show: appendix
// ===================================================================
#let appendix(body) = {
  counter(heading).update(0)
  set heading(numbering: "A.1")
  body
}

// ===================================================================
// HAUPT-TEMPLATE
// ===================================================================
#let thesis(
  // --- Sprache & Format ---
  language: "de", // "de" oder "en"
  submission: "digital", // "digital" oder "papier"
  license: "opensource", // opensource | hs | stud | vertraulich
  gender: true,
  show-toc: true,
  show-list-of-figures: true,
  show-list-of-tables: true,
  show-list-of-listings: true,
  // --- Bibliografische Angaben ---
  title-de: "",
  title-en: "",
  authors: (), // ((vorname, nachname, orcid), ...)
  city: "Mannheim",
  date: datetime.today(),
  supervisor: "",
  second-examiner: "",
  faculty: "I",
  course: "IB",
  // --- Abstract ---
  abstract-de: [],
  abstract-en: [],
  // --- Optionale Verzeichnisse (Inhalte) ---
  acronym-entries: none,
  glossary-entries: none,
  symbol-entries: none,
  // --- Literatur ---
  bib: none,
  body,
) = {
  let en = language == "en"
  let s = if en { strings-en } else { strings-de }
  let paper = submission == "papier"
  let twoside = paper
  let fenster = if paper { 4mm } else { 0mm }

  // Studiengang / Fakultaet aufloesen
  let c = courses.at(course, default: courses.IB)
  let course-de = c.at(0)
  let course-en = c.at(1)
  let typ = if en { c.at(3) } else { c.at(2) }
  let course-name = if en [Course of Studies: #course-en] else [#course-de]
  let fak = faculties.at(faculty, default: faculties.I)
  let fak-name = if en { fak.en } else { fak.de }
  let institution = if en { "University of Applied Sciences Mannheim" } else { "Technische Hochschule Mannheim" }
  let title = if en { title-en } else { title-de }

  // Autoren formatieren
  let author-block = authors.map(a => {
    let n = a.at(0) + " " + a.at(1)
    if a.len() > 2 and a.at(2) != none and a.at(2) != "" {
      n + "  " + "(ORCID: " + a.at(2) + ")"
    } else { n }
  }).join("\n")

  // ---------------- Dokument-Metadaten ----------------
  set document(
    title: title,
    author: authors.map(a => a.at(0) + " " + a.at(1)),
  )

  // ---------------- Seiten-Layout ----------------
  set page(
    paper: "a4",
    margin: (top: 30mm, bottom: 40mm, inside: 30mm, outside: 30mm),
    binding: if twoside { left } else { auto },
  )

  // ---------------- Basis-Typografie ----------------
  set text(
    font: serif-font,
    size: 12pt,
    lang: if en { "en" } else { "de" },
    region: if en { "US" } else { "DE" },
    hyphenate: true,
  )
  // setstretch{1.2}, parindent 0, parskip 1ex
  set par(leading: 0.85em, spacing: 1.0em, first-line-indent: 0pt, justify: true)

  // ---------------- Ueberschriften ----------------
  // Alle Ueberschriften serifenlos & fett (KOMA-Default),
  // Nummerierung bis Ebene 3 (secnumdepth=2 im book), keine Endpunkte.
  set heading(numbering: (..n) => {
    let nums = n.pos()
    if nums.len() <= 3 { numbering("1.1", ..nums) }
  })

  // Kapitel (Ebene 1): serifenlos fett LARGE, beginnt auf neuer (rechter)
  // Seite; setzt die Abbildungs-/Tabellen-/Listing-Zaehler zurueck.
  show heading.where(level: 1): it => {
    pagebreak(weak: true, to: if twoside { "odd" })
    counter(figure.where(kind: image)).update(0)
    counter(figure.where(kind: table)).update(0)
    counter(figure.where(kind: "listing")).update(0)
    counter(math.equation).update(0)
    set text(font: sans-font, weight: "bold", size: 20.74pt)
    block(above: 2.5em, below: 1.2em)[
      #if it.numbering != none {
        context {
          let n = counter(heading).display(it.numbering)
          if n != none and n != "" [#n#h(0.6em)]
        }
      }
      #it.body
    ]
  }
  // Section (Ebene 2)
  show heading.where(level: 2): it => {
    set text(font: sans-font, weight: "bold", size: 14.4pt)
    block(above: 1.6em, below: 0.8em, it)
  }
  // Subsection (Ebene 3)
  show heading.where(level: 3): it => {
    set text(font: sans-font, weight: "bold", size: 12pt)
    block(above: 1.4em, below: 0.7em, it)
  }
  // Subsubsection (Ebene 4): serifenlos, kursiv, fett, small
  show heading.where(level: 4): it => {
    set text(font: sans-font, weight: "bold", style: "italic", size: 10.95pt)
    block(above: 1.2em, below: 0.6em, it)
  }

  // ---------------- Links & Zitate ----------------
  show link: set text(fill: HMA-linkblue)
  show ref: set text(fill: HMA-linkblue)
  show cite: set text(fill: HMA-linkblue)

  // ---------------- Abbildungen / Tabellen ----------------
  // Nummerierung kapitelweise (N.M) — wie in scrbook
  set figure(numbering: n => context {
    let ch = counter(heading).get()
    let c = if ch.len() > 0 { ch.first() } else { 0 }
    [#c.#n]
  })
  // Beschriftungen: serifenlos, footnotesize, Label fett
  show figure.caption: it => {
    set text(font: sans-font, size: 10pt)
    [#strong[#it.supplement #context it.counter.display(it.numbering)#it.separator]#it.body]
  }
  set figure(gap: 0.8em)
  show figure.where(kind: table): set figure.caption(position: top)
  show figure.where(kind: "listing"): set figure.caption(position: bottom)

  // Formeln kapitelweise nummerieren (N.M)
  set math.equation(numbering: n => context {
    let ch = counter(heading).get()
    let c = if ch.len() > 0 { ch.first() } else { 0 }
    [(#c.#n)]
  })

  // Tabellen: booktabs-aehnlicher Stil
  set table(stroke: none, inset: (x: 0.6em, y: 0.45em))

  // Kopf-/Fusszeile — EINMAL global gesetzt (kein spaeteres `set page`,
  // sonst erzeugt Typst unerwuenschte Leerseiten). Die Seitennummerierung
  // (roemisch/arabisch) und die laufende Kopfzeile werden ueber den
  // Zustand `matter` gesteuert.
  let page-number = () => context {
    let m = matter.get()
    let pg = counter(page).get().first()
    if m == "main" { numbering("1", pg) } else { numbering("i", pg) }
  }
  set page(
    header: context {
      if matter.get() != "main" { return }
      // Aktuelles Kapitel: letzte Ueberschrift der Ebene 1, deren Seite
      // <= aktueller Seite liegt (funktioniert auch, wenn das Kapitel auf
      // der aktuellen Seite beginnt).
      let cur = none
      for h in query(heading.where(level: 1)) {
        if h.location().page() <= here().page() and h.numbering != none { cur = h }
      }
      if cur != none {
        set text(font: sans-font, size: 10pt)
        align(if twoside and calc.even(here().page()) { left } else { right })[#cur.body]
      }
    },
    footer: context {
      set text(font: sans-font, size: 10pt)
      let al = if twoside and calc.even(here().page()) { left } else { right }
      align(al)[#(page-number())]
    },
  )

  // ===============================================================
  // FRONTMATTER  (roemische Seitenzahlen)
  // ===============================================================

  // ---- Titelseite (ohne Kopf-/Fusszeile, ohne Raender) ----
  // Die Positionen werden – wie im LaTeX-Original (TikZ, current page.north) –
  // ab der physischen Papierkante gemessen. Dafuer werden auf der Titelseite
  // die Seitenraender auf 0 gesetzt.
  {
    set page(header: none, footer: none, margin: 0pt)
    // Logo oben links
    place(top + left, dx: 24mm, dy: 23mm, image("bilder/hsma-logo.svg", width: 48mm))

    // gemeinsame Positionierungshilfe: horizontal auf der Seite zentrierter
    // 128mm-Block (bei Papierabgabe um das Umschlagfenster verschoben).
    let field(dy, content) = place(
      top + center,
      dx: fenster,
      dy: dy,
      block(width: 128mm, content),
    )

    field(62mm, align(center)[
      #set text(font: sans-font, weight: "bold", size: 17.28pt)
      #title
    ])
    field(103mm, align(center)[
      #set text(font: sans-font, size: 14.4pt)
      #author-block
    ])
    field(130mm, align(center)[
      #set text(font: sans-font, size: 14.4pt)
      #typ \
      #v(2mm)
      #course-name
    ])
    field(165mm, align(center)[
      #set text(font: sans-font, size: 14.4pt)
      #fak-name \
      #v(2mm)
      #institution
    ])
    field(190mm, align(center)[
      #set text(font: sans-font, size: 14.4pt)
      #date.display("[day].[month].[year]")
    ])
    field(240mm, align(center)[
      #set text(font: sans-font, size: 14.4pt)
      #s.tutors \
      #v(2mm)
      #supervisor
      #if second-examiner != "" [\ #v(2mm) #second-examiner]
    ])
  }
  pagebreak()

  // ---- Abstract-Seite ----
  counter(page).update(1) // roemische Zaehlung beginnt bei der Abstract-Seite
  {
    set page(header: none)
    set par(justify: true)
    if en {
      text(font: sans-font, weight: "bold", size: 17.28pt, s.abstract-title)
      v(0.75cm)
      text(font: sans-font, weight: "bold", style: "italic")[#title-en] ; linebreak()
      v(0.25cm)
      abstract-en
      v(1.5cm)
      text(font: sans-font, weight: "bold", size: 17.28pt, "Abstrakt")
      v(0.75cm)
      text(font: sans-font, weight: "bold", style: "italic", lang: "de")[#title-de] ; linebreak()
      v(0.25cm)
      abstract-de
    } else {
      text(font: sans-font, weight: "bold", size: 17.28pt, s.abstract-title)
      v(0.75cm)
      text(font: sans-font, weight: "bold", style: "italic")[#title-de] ; linebreak()
      v(0.25cm)
      abstract-de
    }
  }

  // ---- Genderhinweis (nur Deutsch) ----
  if gender and not en {
    pagebreak(weak: true)
    v(2cm)
    text(font: sans-font, style: "italic", s.gender-note)
  }

  // ---- Verzeichnisse ----
  show outline.entry.where(level: 1): it => {
    set text(font: sans-font, weight: "bold")
    it
  }
  if show-toc {
    pagebreak(weak: true)
    show outline: set text(font: sans-font)
    outline(title: s.contents, depth: 3)
  }
  if show-list-of-figures {
    list-of(figure.where(kind: image), s.list-of-figures)
  }
  if show-list-of-tables {
    list-of(figure.where(kind: table), s.list-of-tables)
  }
  if show-list-of-listings {
    list-of(figure.where(kind: "listing"), s.list-of-listings)
  }

  // ---- Optionale Nachschlage-Verzeichnisse ----
  if acronym-entries != none {
    pagebreak(weak: true)
    acronyms(acronym-entries, lang: language)
  }
  if glossary-entries != none {
    pagebreak(weak: true)
    glossary(glossary-entries, lang: language)
  }
  if symbol-entries != none {
    pagebreak(weak: true)
    symbols(symbol-entries, lang: language)
  }

  // Letzte roemische Seitenzahl des Frontmatters merken (fuer den Backmatter)
  context frontmatter-end.update(counter(page).get().first())

  // ===============================================================
  // MAINMATTER  — arabische Seitenzahlen, laufende Kolumnentitel
  // ===============================================================
  // Erst die letzte Frontmatter-Seite verlassen, DANN umschalten, damit die
  // Umstellung nicht auf der letzten Frontmatter-Seite wirkt (Leerseite).
  pagebreak(weak: true)
  matter.update("main")
  counter(page).update(1)
  counter(heading).update(0) // Kapitel bei 1 beginnen (Frontmatter-Ueberschriften ignorieren)

  body

  // ===============================================================
  // BACKMATTER — roemische Seitenzahlen (Fortsetzung des Frontmatters)
  // ===============================================================
  pagebreak(weak: true)
  matter.update("back")
  context counter(page).update(frontmatter-end.get() + 1)

  // ---- Literaturverzeichnis ----
  if bib != none {
    set text(font: serif-font)
    show bibliography: set heading(numbering: none)
    bib
  }
}
