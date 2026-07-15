#import "../lib.typ": *

= Ergebnisse

== Finale Ergebnisse

== Einschränkungen

// Grenzen des Systems: Objekterkennung, Bewegungsqualität, Laufverhalten.

Trotz der grundsätzlich funktionierenden Gesamtpipeline zeigten sich mehrere
Einschränkungen, die eine durchgängig zuverlässige Ausführung der Aufgabe
erschwerten. Ein zentrales Problem war die Zuverlässigkeit der
Schwammerkennung: Je nach Lichtverhältnissen variierte die Erkennungsqualität
merklich, sodass ein vollständig fehlerfreier Durchlauf schwer zu erreichen
war. Unabhängig von den Lichtbedingungen deutet die Erkennungsleistung
insgesamt darauf hin, dass das promptgesteuerte Open-Vocabulary-Modell an
seine Grenzen stößt und ein auf das Zielobjekt trainiertes, klassenbasiertes
Modell voraussichtlich robustere und konsistentere Ergebnisse geliefert
hätte, allerdings auf Kosten der Flexibilität und des Trainingsaufwands.
Erschwerend kommt hinzu, dass ein Tafelschwamm als Objekt kaum ausgeprägte,
charakteristische Merkmale besitzt – er verfügt weder über eine markante
Form noch über Textur- oder Strukturdetails, anhand derer er sich eindeutig
von anderen Objekten oder dem Hintergrund abgrenzen lässt. Diese
Merkmalsarmut dürfte die promptbasierte Erkennung zusätzlich erschwert
haben.

Auch die Bewegungssteuerung des Roboters unterlag deutlichen Einschränkungen.
Insbesondere die selbst programmierten Bewegungssequenzen – das Hinsetzen und
das Greifen – wirkten stockend und wenig fließend, da sie nicht durch eine
natürliche Interpolation zwischen den Gelenkstellungen, sondern aus einzeln
angefahrenen Zwischenpositionen zusammengesetzt waren. Dies erhöhte das
Risiko eines Umfallens während der Bewegungsausführung. Beim Greifen selbst
bestand zudem keine Flexibilität hinsichtlich der genauen Position des
Schwamms: Die Greifbewegung war auf eine feste relative Position ausgelegt
und konnte sich nicht dynamisch an leicht abweichende Objektlagen anpassen.

Ein weiteres, laufbedingtes Problem ergab sich aus dem grundlegenden
Gangverhalten des Nao. Durch ein leichtes Wackeln während des Laufens hielt
der Roboter keine exakt gerade Linie, sondern lief tendenziell eine leichte
Kurve. Dies machte den Prozess des Hinlaufens zum Objekt spürbar langwieriger,
da wiederholt kleinere Korrekturbewegungen (Drehungen und seitliche Schritte)
notwendig waren, um den Roboter erneut auf das Ziel auszurichten.
