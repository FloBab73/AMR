#import "../lib.typ": *

= System Design

== ROS-Nodes-Diagramm

Das Gesamtsystem besteht aus vier ROS-2-Nodes, die ausschließlich über Topics
miteinander kommunizieren und jeweils als eigener Prozess gestartet werden.
@ros_nodes zeigt die Nodes und die zwischen ihnen ausgetauschten Topics samt
Nachrichtentypen.

#figure(
  image("../bilder/ros-nodes.svg", width: 85%),
  caption: [ROS-Nodes des Gesamtsystems und die Topics, über die sie
    miteinander kommunizieren.],
) <ros_nodes>

Der `naoqi_driver` ist die Schnittstelle zur Roboterhardware und der einzige
Node, der nicht selbst implementiert wurde. Er übersetzt zwischen den
proprietären NAOqi-Diensten des Nao und der ROS-2-Welt. Er stellt die Bilder der
unteren Kamera, die Zustände der Fußtaster sowie die aktuellen Gelenkwinkel als
Topics bereit und nimmt umgekehrt Geschwindigkeits- und Gelenkbefehle entgegen.
Alle Datenflüsse zum und vom Roboter laufen damit über diesen einen Node.

Der Node `nao_camera_collector` abonniert die Rohbilder der unteren Kamera und
veröffentlicht sie unverändert auf einem zweiten Topic. Diese Zwischenstufe
entkoppelt die Bildverarbeitung vom Treiber und erlaubt es, den Bildstrom an
einer zentralen Stelle mitzuschneiden oder zu manipulieren, ohne die übrigen
Nodes anzupassen.

Die `KI_Node` bildet den wahrnehmenden Teil des Systems. Sie abonniert den
weitergereichten Bildstrom, wertet jedes Bild aus und
leitet daraus einen einzelnen diskreten Steuerbefehl ab. Dieser wird als
JSON-Objekt in einer String-Nachricht veröffentlicht.

Die `motion_control`-Node ist der ausführende Gegenpart. Sie abonniert die
Befehle der KI-Node und setzt Laufbefehle in Geschwindigkeitsvorgaben um. Zusätzlich
abonniert sie die Fußtaster, über die das Aufheben ausgelöst wird, sowie die
Gelenkzustände, aus denen vor jeder Aufhebesequenz die aktuelle Pose des
Roboters bestimmt wird.


== Betriebssystem-Setup

Die Wahl des Betriebssystems ergibt sich aus zwei unabhängigen Anforderungen,
die sich gegenseitig einschränken. Einerseits benötigt der `naoqi_driver2`
eine konkrete ROS-2-Distribution, für die das Paket und seine
Abhängigkeiten offiziell veröffentlicht sind. Andererseits erfordert die
KI-gestützte Bilderkennung mit GroundingDINO und SAM eine NVIDIA-GPU mit
CUDA-Unterstützung und damit aktuelle Grafikkartentreiber. Beide
Anforderungen lassen sich auf einer gemeinsamen Basis erfüllen.

Der `naoqi_driver2` unterstützt offiziell ausschließlich ROS2~Humble und
ROS2~Iron, die beide auf *Ubuntu~22.04~LTS* aufbauen @naoqi_driver2024.
Neuere Distributionen wie ROS2~Jazzy zielen auf Ubuntu~24.04 und werden
vom Treiber nicht unterstützt, weil die vorgelagerten Abhängigkeiten
(`naoqi_libqi` und `naoqi_bridge_msgs`) für diese Distributionen nicht
veröffentlicht wurden und die Portierung bislang aussteht.
Da ROS2~Iron bereits das Ende seines Support-Zeitraums erreicht
hat, fällt die Wahl auf ROS2~Humble als die aktive Long-Term-Support-Version.
Damit ist Ubuntu~22.04 als Betriebssystem vorgegeben.

Diese Festlegung erweist sich auch für die zweite Anforderung als
geeignet. Ubuntu~22.04 stellt aktuelle NVIDIA-Grafikkartentreiber
unmittelbar über die offiziellen Paketquellen bereit, ohne dass
zusätzliche Drittanbieter-Repositories oder manuelle Treiberinstallationen
notwendig sind. Die verfügbaren Treiber unterstützen aktuelle
CUDA-Versionen, unter denen GroundingDINO seine eigenen CUDA-Erweiterungen
kompiliert und SAM die GPU-Inferenz ausführt. Die Kombination aus
naoqi-bedingter OS-Wahl und modernen GPU-Treibern trifft sich damit
auf Ubuntu~22.04 als gemeinsamem Nenner.

// kürzerer titel
== Kommunikation zwischen Computer, NaoBridge und Roboter-Topics <kommunikation_kapitel>

Während @ros_nodes ausschließlich die logische Sicht auf die ROS-Nodes zeigt,
stellt @kommunikation das Gesamtbild dar, also welche Komponente auf welchem Gerät
läuft und über welchen Weg sie mit dem Roboter spricht. Sämtliche selbst
entwickelte Software läuft dabei auf einem einzigen Laptop, auf dem Nao selbst
wird kein eigener Code ausgeführt.

#figure(
  image("../bilder/kommunikation.svg", width: 95%),
  caption: [Gesamtbild der Kommunikation zwischen Laptop und Nao. Der
    `naoqi_driver` übersetzt zwischen ROS 2 und den NAOqi-Diensten. Die
    Werkzeuge zur Inbetriebnahme umgehen ROS vollständig. Die Topics der
    ROS-Nodes zeigt @ros_nodes.],
) <kommunikation>

Der Grund für diese Aufteilung liegt in der Rechenleistung. Die Objekterkennung
mit Grounding DINO und SAM benötigt eine GPU, über die der Nao nicht verfügt.
Die Bilder werden deshalb zum Laptop übertragen, dort ausgewertet, und
lediglich das Ergebnis der Auswertung, ein kurzer Steuerbefehl, wird
zurückgesendet. Der Roboter bleibt in dieser Architektur ein reiner Sensor- und
Aktorknoten.

Die vier ROS-Nodes kommunizieren untereinander über die Standardmechanismen von
ROS 2, also über DDS. Da alle Nodes auf demselben Rechner laufen, verlässt
dieser Datenverkehr das Gerät nicht. Voraussetzung ist allerdings, dass alle
Prozesse dieselbe `ROS_DOMAIN_ID` und dieselbe RMW-Implementierung verwenden,
da sie sich sonst gegenseitig schlicht nicht sehen.

Die eigentliche Systemgrenze verläuft am `naoqi_driver`. Er ist der einzige
Prozess, der beide Welten kennt. Nach innen spricht er ROS 2, nach außen das
proprietäre NAOqi-Protokoll. Auf dem Roboter läuft ein Broker, über den sämtliche
NAOqi-Dienste erreichbar sind. Jeder Zugriff von außen läuft über diesen einen
Einstiegspunkt. Der Treiber bezieht darüber den Bildstrom der unteren Kamera aus
`ALVideoDevice`, fragt die Zustände der Fußtaster über `ALMemory` ab und reicht
sowohl die Geschwindigkeits- als auch die Gelenkbefehle an `ALMotion` weiter. Die
ROS-Topics des Roboters sind damit keine nativen Topics, sondern eine vom Treiber
erzeugte Abbildung dieser Dienste. Der Roboter wird dem Treiber beim Start über
seine IP-Adresse bekannt gemacht.

Zwei Wege umgehen ROS vollständig und sind der Inbetriebnahme vorbehalten. Zum
einen sprechen die Skripte `wakup.py` und `shutdown.py` über das mitgelieferte
NAOqi-SDK und dessen `ALProxy`-Schnittstelle direkt mit den Diensten des
Roboters, um ihn in den Bereitschaftszustand zu versetzen oder wieder
abzuschalten. Da dieses SDK nur für Python 2.7 vorliegt, müssen diese beiden
Skripte mit dem beiliegenden Interpreter ausgeführt werden und lassen sich nicht
in die übrige, auf Python 3 basierende Codebasis integrieren. Zum anderen wird
per SSH das Kommandozeilenwerkzeug `qicli` auf dem Roboter selbst aufgerufen, um
`ALAutonomousLife` abzuschalten. Dieser Schritt ist notwendig, weil die
autonomen Verhaltensweisen des Nao andernfalls fortlaufend gegen die manuelle
Gelenkansteuerung arbeiten und die abgespielten Bewegungen verfälschen.
