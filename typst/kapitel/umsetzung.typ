#import "../lib.typ": *

= Umsetzung

== Camera Node

== KI Node

// Details zur Bilderkennung: Objekterkennung + Segmentierung, Ableitung von
// Bewegungskommandos.

Die KI-Node ist für die semantische Auswertung der von der Kamera-Node
publizierten Bilder zuständig. Sie abonniert den Bild-Topic, wertet jedes
eingehende Bild aus und publiziert daraus abgeleitete Bewegungskommandos, die
von der Motion-Node konsumiert werden. Für die eigentliche Objekterkennung
kommt eine Kombination aus Grounding DINO und dem Segment Anything Model
(SAM) zum Einsatz. Grounding DINO lokalisiert das Zielobjekt anhand eines
textuellen Prompts als Bounding Box, ohne dass hierfür ein objektspezifisches
Training notwendig ist. Die von Grounding DINO gelieferte Bounding Box wird
anschließend an SAM übergeben, welches daraus eine pixelgenaue
Segmentierungsmaske des Objekts erzeugt. Als Testobjekt diente ein
Tafelschwamm. @ki_node_erkennung zeigt ein Beispielbild, auf dem der
Tafelschwamm sowohl über die Bounding Box als auch pixelgenau über die
SAM-Maske korrekt identifiziert wurde; die Auswertung eines einzelnen Bildes
benötigte dabei etwa 0,5 Sekunden.

#figure(
  image("../bilder/image_detection.png", width: 70%),
  caption: [Erkennung des Tafelschwamms durch Grounding DINO (Bounding Box)
    und SAM (Segmentierungsmaske).],
) <ki_node_erkennung>

Die Formulierung des Prompts hatte einen deutlichen Einfluss auf die
Erkennungsqualität. Getestet wurden unter anderem ein einzelnes Schlagwort
("Tafelschwamm"), die englische Übersetzung ("sponge"), eine reine
Umgebungsbeschreibung ohne konkrete Suchanweisung sowie explizitere
Formulierungen, die den Suchauftrag direkt benennen und die Ausgabe eines
Ergebnisses bei Unsicherheit unterbinden sollten. Diese Varianten lieferten
insgesamt schlechtere oder inkonsistente Ergebnisse. Die besten Ergebnisse
wurden mit dem Prompt in @prompt erzielt, bei dem die Farbe des Objekts explizit bennent wird und der Fokus auch explizit nochmal auf dieses Objekt gesetzt wird.

#listing(
  caption: [Prompt zur Bilderkennung],
  ```python
  PROMPT = "Ein orange-brauner Tafelschwamm steht auf einer Oberfläche, suche nur den orange-braunen Tafelschwamm"
  ```,
) <prompt>

Bei der Erkennung traten mehrere Probleme auf, die im Projektverlauf gezielt
adressiert wurden. Auf farblich ähnlichem Untergrund sowie bei Tisch- oder
Stuhlbeinen im Bildhintergrund kam es teils zu Fehlerkennungen, bei denen
das Modell andere Objekte als den Tafelschwamm auswählte. Diesem Problem
wurde unter anderem durch die explizite Nennung der Farbe im Prompt sowie
durch die Wahl kontrastreicher Testumgebungen (z. B. roter oder grauer
Boden) begegnet. Ein weiteres wiederkehrendes Problem bestand darin, dass
die erkannte Bounding Box gelegentlich das gesamte Bild umrahmte, anstatt
sich auf den Tafelschwamm zu beschränken. Da eine derart große Bounding Box
kein sinnvolles Erkennungsergebnis darstellt, wird ein solcher Fall in der
Bewegungslogik gesondert behandelt, indem Ergebnisse ab einer bestimmten
Breite relativ zur Bildbreite verworfen werden.

Aus der Segmentierungsmaske werden mehrere Merkmale abgeleitet, die als
Grundlage für die Bewegungsentscheidung dienen: die mittlere Position des
Objekts im Bild, die Breite der Bounding Box sowie der Winkel der oberen
Objektkante. Letzterer wird bestimmt, indem aus der Maske die Kontur
extrahiert, ein minimal umschließendes Rechteck berechnet und dessen am
ehesten horizontale, oberste Kante ausgewählt wird. Der Winkel dieser Kante
dient als Näherung dafür, wie stark der Roboter relativ zum Objekt gedreht
steht.

Auf Basis dieser Merkmale wird ein einfaches regelbasiertes Entscheidungsschema
angewendet: Nimmt die Bounding Box nahezu die gesamte Bildbreite ein, wird das
Objekt als erreicht betrachtet (bzw. das Ergebnis als fehlerhaft verworfen).
Andernfalls wird zunächst der Kantenwinkel geprüft und bei Überschreiten
eines Toleranzwerts ein Rotationskommando ausgegeben, um den Roboter am
Objekt auszurichten. Ist der Winkel im Toleranzbereich, wird geprüft, ob
sich das Objekt hinreichend mittig im Bild befindet; bei seitlichem Versatz
werden entsprechende Seitwärtsschritte kommandiert. Befindet sich das Objekt
mittig, aber die Bounding Box ist noch klein, wird ein größerer
Vorwärtsschritt ausgelöst, andernfalls ein kleinerer, feiner dosierter
Schritt. Kann kein Objekt erkannt werden, wird kein Bewegungskommando
erzeugt. Auf diese Weise wird aus der kontinuierlichen Bildauswertung ein
diskretes Kommando (u. a. `rotate_left`, `rotate_right`, `left`, `right`,
`forward`, `none`) abgeleitet, das die Motion-Node schrittweise in Richtung
des Zielobjekts navigieren lässt.
== Motion Node (Bewegungen)

== Gesamtablauf
