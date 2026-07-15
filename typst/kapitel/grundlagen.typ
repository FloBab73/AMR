#import "../lib.typ": *

= Grundlagen

== Nao Roboter (Choregraphe und NAOqi)

== Objekterkennung

// Kurzer Überblick über gängige Ansätze der Objekterkennung, ohne auf die
// konkrete Umsetzung im Projekt einzugehen.

Objekterkennung beschreibt die Aufgabe, in einem Bild vorhandene Objekte zu
lokalisieren und zu klassifizieren. Klassische Ansätze basierten auf
handgefertigten Bildmerkmalen und erreichten bei komplexen, variablen Szenen
nur begrenzte Genauigkeit. Mit dem Aufkommen von Convolutional Neural
Networks (CNNs) hat sich dieses Feld stark weiterentwickelt, wobei sich
insbesondere einstufige Verfahren wie die YOLO-Familie (You Only Look Once)
aufgrund ihrer hohen Verarbeitungsgeschwindigkeit für Echtzeitanwendungen
durchgesetzt haben. Ein zentrales Merkmal solcher Ansätze ist jedoch, dass
sie auf einem festen, vorab definierten Satz an Objektklassen trainiert
werden. Sollen neue oder projektspezifische Objekte erkannt werden, ist ein
erneutes Training bzw. Finetuning mit entsprechend annotierten Daten
notwendig.

In den letzten Jahren haben sich zunehmend promptbasierte bzw.
Open-Vocabulary-Ansätze etabliert, die auf großen, vortrainierten
Foundation Models basieren. Diese Modelle koppeln Bild- und
Textrepräsentationen und erlauben es, Objekte anhand einer natürlichsprachlichen
Beschreibung zu lokalisieren, ohne dass eine klassenspezifische
Trainingsphase erforderlich ist. Ergänzend existieren Segmentierungsmodelle,
die – ausgehend von groben Lokalisierungen wie Bounding Boxes – präzise
Objektkonturen extrahieren können. Die Kombination beider Modelltypen
ermöglicht eine flexible, promptgesteuerte Objekterkennung mit
anschließender pixelgenauer Segmentierung, ohne dass für jedes neue
Zielobjekt ein eigener Trainingsprozess nötig ist.

Die Wahl zwischen klassentrainierten und promptbasierten Verfahren stellt
somit einen Trade-off dar: Klassische, trainierte Detektoren bieten in der
Regel eine höhere Verarbeitungsgeschwindigkeit, benötigen dafür jedoch
annotierte Trainingsdaten. Promptbasierte Foundation-Model-Ansätze bieten
hingegen hohe Flexibilität bei neuen Zielobjekten, sind jedoch
typischerweise rechenintensiver und stärker von der Formulierung des
Prompts sowie den Umgebungsbedingungen abhängig.

== ROS
