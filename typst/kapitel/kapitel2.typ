#import "../lib.typ": *

= Lorem Ipsum

== Lorem ipsum dolor

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod
tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At
vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren,
no sea takimata sanctus est Lorem ipsum dolor sit amet.

== Lorem ipsum dolor

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod
tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.

#figure(
  caption: [Ebenen der Kopplung und Beispiele für enge und lose Kopplung],
  table(
    columns: 3,
    align: left,
    table.hline(stroke: 1pt),
    table.header(
      [*Form der Kopplung*], [*enge Kopplung*], [*lose Kopplung*],
    ),
    table.hline(stroke: 0.5pt),
    [Physikalische Verbindung], [Punkt-zu-Punkt], [über Vermittler],
    [Kommunikationsstil], [synchron], [asynchron],
    [Datenmodell], [komplexe gemeinsame Typen], [nur einfache gemeinsame Typen],
    [Bindung], [statisch], [dynamisch],
    table.hline(stroke: 1pt),
  ),
) <Kap2:Kopplungsformen>

- Ein wichtiger Punkt
- Noch ein wichtiger Punkt
- Ein Punkt mit Unterpunkten
  - Unterpunkt 1
  - Unterpunkt 2
- Ein abschließender Punkt ohne Unterpunkte
