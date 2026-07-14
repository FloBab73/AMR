#import "../lib.typ": *

= Lorem Ipsum

== Lorem ipsum dolor

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod
tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At
vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren,
no sea takimata sanctus est Lorem ipsum dolor sit amet.

Beispiel einer Anforderungskarte (Snowcard):

#snowcard(
  1, "F", "hoch", "Beispielanforderung",
  herkunft: "Stakeholder-Interview",
  beschreibung: "Das System soll Lorem ipsum dolor sit amet erfüllen.",
  fitkriterium: "Die Anforderung gilt als erfüllt, wenn ...",
)

Beispiel eines Quality Attribute Scenarios:

#qas(
  1, "hoch", "Performance", "Nutzer", "Anfrage senden", "Webserver",
  "Normalbetrieb", "Antwort wird ausgeliefert", "< 200 ms in 99 % der Fälle",
)

Harvey Balls: #harveyball(0) #harveyball(0.25) #harveyball(0.5) #harveyball(0.75) #harveyball(1)

Checkliste:
#checklist(
  [Erster zu erledigender Punkt],
  [Zweiter Punkt],
  [Dritter Punkt],
)
