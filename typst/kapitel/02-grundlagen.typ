#import "../lib.typ": *

= Grundlagen

== Nao Roboter (Choregraphe und NAOqi)

=== Hardware

Der NAO H25 V5 von Aldebaran-Robotics ist ein humanoider Roboter mit 25
Freiheitsgraden, einer Körpergröße von 57 cm und einem Gewicht von 5,4 kg
@Gouaillier2009. Als Recheneinheit dient ein Intel Atom Z530 mit 1,6 GHz // todo: überprüfen, ob die daten zu unserer nao-version passen
und 1 GB Arbeitsspeicher, auf dem das herstellereigene NAOqi OS (ein angepastes Linux-System) betrieben wird. Die begrenzten
Rechenressourcen machen es praktisch unmöglich, rechenintensive Aufgaben
wie Bildverarbeitung oder KI-Inferenz direkt auf dem Roboter auszuführen;
diese werden daher auf einen externen Rechner ausgelagert.

Für die Wahrnehmung der Umgebung verfügt der NAO über zwei Kameras im Kopf
-- eine nach vorne oben und eine nach vorne unten ausgerichtet -- die
jeweils eine Auflösung von bis zu 1280×960 Pixeln bei 30 fps liefern.
An den Fußsohlen sind binäre Bumpersensoren verbaut, die einen Kontakt
mit einem Objekt am Boden detektieren.

#figure(
  image("../bilder/Nao_vorstellung.jpg", width: 52%),
  caption: [NAO mit unmöglichem Testaufbau],
)

=== NAOqi-Framework und Choregraphe

NAOqi ist die zentrale Softwareplattform des NAO. Sie startet beim
Hochfahren des Roboters automatisch und stellt sämtliche
Hardwarefunktionen über ein modulares Broker/Proxy-Modell bereit
@AldNAOqi2024. Jedes NAOqi-Modul (z.B. `ALMotion` für die
Bewegungssteuerung, `ALVideoDevice` für den Kamerazugriff oder
`ALRobotPosture` für vordefinierte Körperhaltungen) ist über einen
Proxy sowohl lokal als auch über TCP/IP remote ansprechbar. Das
Python-SDK erlaubt dabei, direkt von einem externen Rechner aus
Funktionsaufrufe abzusetzen:
#listing(
  caption: [Direkter Aufruf über ALProxy],
  ```python
  from naoqi import ALProxy
  motion = ALProxy("ALMotion", "<robot-ip>", 9559)
  motion.wakeUp()
  ```,
)

Choregraphe ist die vom Hersteller mitgelieferte grafische
Entwicklungsumgebung für den NAO @Pot2009. Sie verbindet sich
direkt über NAOqi mit dem Roboter und stellt dessen vollständige
API über eine visuelle, flussbasierte Programmieroberfläche bereit:
Verhalten werden als Graphen aus vorgefertigten und eigenen
Skript-Boxen zusammengesetzt und können vor dem Einsatz in einem
eingebetteten Simulator erprobt werden. Choregraphe ist damit das
zuverlässigste Werkzeug, um alle Fähigkeiten des Roboters
unkompliziert zu nutzen, insbesondere, da nicht alle
NAOqi-Funktionen per Remote-Aufruf gleich stabil oder vollständig
erreichbar sind. Im vorliegenden Projekt wurde Choregraphe bewusst nicht
für die Entwicklung verwendet, damit die eigentliche Systemsteuerung über ROS
erfolgt.

=== ROS-Integration über den naoqi_driver

Die Einbindung des NAO in eine ROS-Umgebung erfolgt über das
Paket `naoqi_driver` @naoqi_driver2024. Dabei handelt es sich
um einen C++-ROS-Node, der gleichzeitig als NAOqi-Modul agiert und
bei Verbindungsaufbau automatisch in den laufenden NAOqi-Broker
des Roboters eingebunden wird. Der Treiber übersetzt
NAOqi-Sensordaten in Standard-ROS-Topics. Unter anderem werden die Kamerabilder
(`/nao_robot/camera/top/image_raw`), Gelenkzustände
(`/joint_states`) und IMU-Daten (Inertial Measurement Unit) verfügbar gemacht und umgekehrt
Geschwindigkeitsbefehle (`/cmd_vel`) sowie direkte
Gelenkvorgaben an die NAOqi-Bewegungsmodule weitergeleitet.

Ein wesentliches Ziel des Projekts war es, diese ROS-Integration
exemplarisch einzusetzen und deren praktische Grenzen zu erproben.
Der `naoqi_driver` deckt dabei nur einen Teil der NAOqi-API ab;
für Funktionen wie das direkte Ansteuern einzelner Gelenke oder
die Kontrolle von Körperhaltungen sind ergänzende direkte
NAOqi-Aufrufe notwendig. Hinzu kommen architekturbedingte
Einschränkungen: Remote-Aufrufe über TCP/IP unterliegen einer
Latenz von mindestens 100 ms und die Gelenkzustände werden nur
mit ca. 15 Hz publiziert.
Diese Limitierungen bestimmten maßgeblich das System-Design und
werden in den folgenden Kapiteln weiter ausgeführt.

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
die ausgehend von groben Lokalisierungen wie Bounding Boxes präzise
Objektkonturen extrahieren können. Die Kombination beider Modelltypen
ermöglicht eine flexible, promptgesteuerte Objekterkennung mit
anschließender pixelgenauer Segmentierung, ohne dass für jedes neue
Zielobjekt ein eigener Trainingsprozess nötig ist.

Die Wahl zwischen klassentrainierten und promptbasierten Verfahren stellt
somit einen Trade-off dar. Klassische, trainierte Detektoren bieten in der
Regel eine höhere Verarbeitungsgeschwindigkeit, benötigen dafür jedoch
annotierte Trainingsdaten. Promptbasierte Foundation-Model-Ansätze bieten
hingegen hohe Flexibilität bei neuen Zielobjekten, sind jedoch
typischerweise rechenintensiver und stärker von der Formulierung des
Prompts sowie den Umgebungsbedingungen abhängig.

== ROS

Das Robot Operating System (ROS) ist kein eigenständiges Betriebssystem,
sondern ein quelloffenes Middleware-Framework für die Entwicklung von
Robotersoftware @Quigley2009. Es stellt eine einheitliche
Kommunikationsinfrastruktur bereit, über die unabhängige Softwaremodule (sogenannte _Nodes_) miteinander interagieren können. Jeder Node ist ein
eigenständiger Prozess, der eine klar abgegrenzte Aufgabe übernimmt, etwa
die Bildverarbeitung, die Bewegungssteuerung oder die Sensorauswertung.
Diese modulare Architektur fördert Wiederverwendbarkeit und erlaubt es,
einzelne Komponenten unabhängig voneinander zu entwickeln, zu testen und
auszutauschen.

Die Kommunikation zwischen Nodes erfolgt über zwei grundlegende Mechanismen.
Topics implementieren ein asynchrones Publish/Subscribe-Prinzip: Ein Node
veröffentlicht Nachrichten eines bestimmten Typs auf einem benannten Kanal,
während beliebige andere Nodes diesen Kanal abonnieren können. Typische
Beispiele im Robotikkontext sind Kamerabilder (`sensor_msgs/Image`) oder
Geschwindigkeitsbefehle (`geometry_msgs/Twist`). Services hingegen
ermöglichen synchrone Kommunikation nach dem Request/Response-Prinzip und
eigenen sich für einmalige, zustandsbehaftete Operationen. Sämtliche
Nachrichtentypen sind stark typisiert und sprachunabhängig definiert. ROS
unterstützt primär C++ und Python als Implementierungssprachen.

Für das vorliegende Projekt bietet ROS den entscheidenden Vorteil, dass
Kameraverarbeitung, KI-Inferenz und Bewegungssteuerung als separate Nodes
realisiert und über standardisierte Topics entkoppelt werden können.
Gleichzeitig ermöglicht der `naoqi_driver` die Anbindung des NAO als
reguläre ROS-Komponente. Ein erklärtes Projektziel war es dabei, diese
Architektur nicht nur einzusetzen, sondern deren Grenzen aufgrund von
Latenz und unvollständiger NAOqi-Abdeckung im praktischen Betrieb zu erproben.
// der letzte satz ist doppelt mit zeile 70 in 2.1.3
