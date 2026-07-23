#import "../lib.typ": *

= Umsetzung

== Camera Node

Das NAOqi-SDK, auf das der `naoqi_driver` intern angewiesen ist, setzt
Python~2 voraus. Die KI-Node hingegen benötigt Python~3, da PyTorch und
die CUDA-Anbindung ausschließlich dort verfügbar sind. Eine direkte
Verarbeitung der Kamerabilder innerhalb derselben Umgebung ist daher nicht
möglich. Die Bilder müssen zunächst in ein Format überführt werden, das
ohne NAOqi-Abhängigkeiten auskommt.

Die Camera Node löst dieses Problem als einfache Zwischenschicht. Sie
abonniert das Rohbild des `naoqi_driver`, dekodiert es über `CvBridge` in
ein OpenCV-kompatibles BGR8-Array und verpackt es anschließend als
standardäßige `sensor_msgs/Image`-Nachricht neu. Das resultierende
Ausgabe-Topic ist damit frei von NAOqi-Abhängigkeiten und kann von der
KI-Node mit gängigen Bibliotheken konsumiert werden.

#listing(
  caption: [Bildkonvertierung in der Camera Node],
  ```python
  self.camera_sub = self.create_subscription(
      Image, '/camera/bottom/image_raw', self.get_camera_data, 10)
  self.camera_pub = self.create_publisher(
      Image, '/camera/bottom/image_republished', 10)

  def get_camera_data(self, msg):
      frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
      out_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
      self.camera_pub.publish(out_msg)
  ```,
)

== KI Node <ki_node>

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
SAM-Maske korrekt identifiziert wurde. Die Auswertung eines einzelnen Bildes
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

Aus der Segmentierungsmaske werden drei Merkmale abgeleitet, die als
Grundlage für die Bewegungsentscheidung dienen, nämlich die mittlere Position des
Objekts im Bild, die Breite der Bounding Box sowie der Winkel der oberen
Objektkante. Letzterer wird bestimmt, indem aus der Maske die Kontur
extrahiert, ein minimal umschließendes Rechteck berechnet und dessen am
ehesten horizontale, oberste Kante ausgewählt wird. Der Winkel dieser Kante
dient als Näherung dafür, wie stark der Roboter relativ zum Objekt gedreht
steht.

Auf Basis dieser Merkmale wird ein einfaches regelbasiertes Entscheidungsschema
angewendet. Nimmt die Bounding Box nahezu die gesamte Bildbreite ein, wird das
Objekt als erreicht betrachtet (bzw. das Ergebnis als fehlerhaft verworfen).
Andernfalls wird zunächst der Kantenwinkel geprüft und bei Überschreiten
eines Toleranzwerts ein Rotationskommando ausgegeben, um den Roboter am
Objekt auszurichten. Ist der Winkel im Toleranzbereich, wird geprüft, ob
sich das Objekt hinreichend mittig im Bild befindet. Bei seitlichem Versatz
werden entsprechende Seitwärtsschritte kommandiert. Befindet sich das Objekt
mittig, aber die Bounding Box ist noch klein, wird ein größerer
Vorwärtsschritt ausgelöst, andernfalls ein kleinerer, feiner dosierter
Schritt. Kann kein Objekt erkannt werden, wird kein Bewegungskommando
erzeugt. Auf diese Weise wird aus der kontinuierlichen Bildauswertung ein
diskretes Kommando (u. a. `rotate_left`, `rotate_right`, `left`, `right`,
`forward`, `none`) abgeleitet, das die Motion-Node schrittweise in Richtung
des Zielobjekts navigieren lässt.
== Motion Node <motion_node>

// Umsetzung der Bewegungssteuerung: Kommandoverarbeitung, Laufen, abgespielte
// Bewegungssequenzen, bumpergetriggerter Greifvorgang.

Die Motion-Node bildet das Gegenstück zur KI-Node und übersetzt deren abstrakte
Kommandos in konkrete Bewegungen des Roboters. Sie ist als persistente
ROS2-Node realisiert, die beim Start ihre Publisher für die Fahrbefehle und die
Gelenkansteuerung anlegt und anschließend auf eingehende Kommandos wartet. Da
ohne Abonnenten auf dem Gelenk-Topic alle Nachrichten verworfen würden, ohne
dass sich der Roboter bewegt, wartet die Node zunächst auf die Verbindung der
`naoqi_driver`-Brücke und weist andernfalls explizit darauf hin. Neben den
Kommandos abonniert sie die Fußtaster (#box[`/bumper`]) sowie die aktuellen
Gelenkstellungen (#box[`/joint_states`]), die fortlaufend zwischengespeichert werden.

Die Kommandos werden als JSON-Nachricht übertragen und enthalten neben dem
eigentlichen Kommando eine Dauer sowie einen Zeitstempel. Letzterer ist
notwendig, weil das Abspielen einer Bewegungssequenz mehrere Sekunden dauert,
während die KI-Node unabhängig davon weiter Bilder auswertet und Kommandos
publiziert. Diese beziehen sich dann auf eine bereits veraltete Situation und
würden den Roboter in die falsche Richtung schicken. Die Motion-Node verwirft
daher alle Kommandos, deren Zeitstempel älter als 1,5 Sekunden ist, und
arbeitet stets nur auf der aktuellsten Bildauswertung.

Für die Ausführung werden zwei unterschiedliche Mechanismen eingesetzt. Die
Fortbewegungskommandos (`forward`, `left`, `right`, `rotate_left`,
`rotate_right`) werden auf den Geschwindigkeitsbefehl #box[`/cmd_vel`] abgebildet:
Eine Twist-Nachricht mit der gewünschten Linear- oder Winkelgeschwindigkeit wird
publiziert, für die im Kommando angegebene Dauer gewartet und anschließend eine
Nullgeschwindigkeit gesendet, um den Roboter anzuhalten. Die Schrittlänge ergibt
sich damit implizit aus dem Produkt aus fester Geschwindigkeit und
vorgegebener Dauer, sodass die Korrektur umso größer ausfällt, je weiter der
Roboter vom Ziel entfernt oder je stärker er fehlausgerichtet ist. Das
Gangmuster selbst, also die Koordination der Beingelenke, übernimmt vollständig die
Laufsteuerung des Nao.

Alle übrigen Bewegungen, das Senken des Kopfes, das Hinsetzen, das Greifen und
das Aufstehen, werden dagegen als aufgezeichnete Sequenzen über das Topic
#box[`/joint_angles`] abgespielt. Sie entstanden, indem der Roboter von Hand in die
gewünschten Zwischenposen gebracht, die dabei über #box[`/joint_states`] gemeldeten
Gelenkwinkel aufgezeichnet und anschließend manuell nachbearbeitet wurden. Jede
Sequenz liegt als Textdatei aus wiederholten Blöcken von Gelenknamen und
zugehörigen Winkeln vor, wobei nicht zwingend alle 26 Gelenke angesteuert werden
müssen. Die Kopfbewegung etwa beschränkt sich auf die beiden Kopfgelenke, sodass
die übrige Körperhaltung unverändert bleibt. Beim Abspielen wird jede Pose als
Zielvorgabe gesendet, woraufhin der Roboter die betroffenen Gelenke
selbstständig anfährt. Da keine Rückmeldung über das Erreichen einer Pose
vorliegt, wird die Wartezeit bis zur nächsten Pose aus der größten
Winkeländerung aller beteiligten Gelenke und einer konfigurierten
Abspielgeschwindigkeit berechnet. Eine untere Schranke verhindert, dass sehr
kleine Änderungen zu einem sprunghaften Durchlauf führen. Große Umstellungen
erhalten so automatisch mehr Zeit als kleine Nachjustierungen.

Eine Besonderheit ist das Zurückführen in die Ausgangshaltung. Da die
aufgezeichneten Sequenzen von einer definierten Startpose ausgehen, würde ein
direkter Sprung aus einer beliebigen aktuellen Haltung dorthin ruckartig und
potenziell destabilisierend wirken. Daher wird vor jedem Greifvorgang die
aktuelle Gelenkstellung aus den zwischengespeicherten #box[`/joint_states`] ausgelesen
und zur Laufzeit eine Übergangsbewegung zur ersten Pose der Hinsetz-Sequenz
erzeugt. Diese besteht aus 80 Zwischenposen, die über eine Smoothstep-Funktion
statt linear interpoliert werden, sodass die Bewegung sanft beschleunigt und
wieder abbremst, und wird über denselben Mechanismus abgespielt wie die
aufgezeichneten Bewegungen.

Der Greifvorgang selbst wird nicht durch die Bilderkennung, sondern durch die
Fußtaster ausgelöst. Der Roboter läuft so lange auf den Tafelschwamm zu, bis er
physisch an diesen anstößt. Der Kontakt markiert einen eindeutigen und aus der
Bildauswertung allein nicht zuverlässig bestimmbaren Zustand, denn der Schwamm
befindet sich nun in einer bekannten, festen Position direkt vor den Füßen des
Roboters, auf die die aufgezeichnete Greifbewegung ausgelegt ist. Der
Taster-Zustand wird daher bei jedem eingehenden Kommando vorrangig geprüft, noch
bevor ein Fortbewegungskommando ausgeführt wird. Ist er gesetzt, wird die
Navigation abgebrochen und die feste Greifsequenz durchlaufen, bestehend aus der
Rückkehr in die Ausgangshaltung über die beschriebene Übergangsbewegung, dem
Hinsetzen, dem Greifen und dem Aufstehen. Je nachdem, welcher der beiden Taster ausgelöst hat, kommen dabei die
Varianten für die rechte oder die linke Hand zum Einsatz.


== Gesamtablauf

// Zusammenspiel der Nodes im Betrieb: Inbetriebnahme, Regelkreis, Abbruch durch
// den Bumper.

Nachdem die einzelnen Komponenten beschrieben sind, zeigt dieser Abschnitt, wie
sie im Betrieb zeitlich zusammenwirken, von der Inbetriebnahme des Roboters bis
zum aufgehobenen Tafelschwamm.

Am Anfang steht die Herstellung der Verbindung zum Roboter. Der Nao wird
eingeschaltet und mit demselben Netzwerk verbunden wie der Laptop. Anschließend
wird der `naoqi_driver` unter Angabe der IP-Adresse des Roboters gestartet. Erst
danach existieren die in @ros_nodes gezeigten Roboter-Topics, sodass alle
weiteren Nodes diesen Schritt voraussetzen. Sind die Topics verfügbar, werden die
drei selbst implementierten Nodes, also Kamera-, KI- und Motion-Node, als jeweils
eigene Prozesse gestartet. Ihre Reihenfolge untereinander ist unkritisch.

Als Letztes wird der Roboter in einen definierten Grundzustand versetzt. Dazu
dienen die beiden in @kommunikation_kapitel beschriebenen Skripte, die ROS
umgehen. Zunächst wird `shutdown.py` aufgerufen, das entgegen seinem Namen den
Roboter nicht abschaltet, sondern lediglich `ALAutonomousLife` deaktiviert.
Anschließend versetzt `wakup.py` ihn in den Bereitschaftszustand, in dem die
Gelenke bestromt sind und er stehen sowie Gelenkvorgaben ausführen kann.
@startbefehle fasst die Startsequenz zusammen.

#listing(
  caption: [Startsequenz des Gesamtsystems],
  ```sh
  # 1. Treiberbrücke zum Roboter
  ros2 launch naoqi_driver naoqi_driver.launch.py nao_ip:=192.168.0.193

  # 2. Die drei eigenen Nodes, jeweils in einem eigenen Terminal
  python3 Nao/camera_node.py
  python3 Nao/motionControl.py
  uv run KI_Node/main.py

  # 3. Grundzustand des Roboters herstellen
  ./pynaoqi-python2.7-2.8.6.23-linux64-20191127_152327/bin/python2 shutdown.py
  ./pynaoqi-python2.7-2.8.6.23-linux64-20191127_152327/bin/python2 wakup.py
  ```,
) <startbefehle>

Ab diesem Zeitpunkt läuft das System ohne weiteres Zutun. Der Roboter steht
aufrecht vor dem am Boden liegenden Tafelschwamm, und der Regelkreis aus
Bildauswertung (@ki_node) und Kommandoausführung (@motion_node) schließt sich.
Eine übergeordnete Ablaufsteuerung existiert nicht. Der gesamte Ablauf ergibt
sich allein daraus, dass jedes Bild auf den Zustand antwortet, den die
vorangegangene Bewegung erzeugt hat.

Faktisch zerfällt der Anlauf dabei in zwei Phasen. Zu Beginn blickt der Roboter
geradeaus und hat den Schwamm auch über größere Distanz im Bild. Je näher er
kommt, desto weiter wandert der Schwamm im Bild nach unten, bis er den
Sichtbereich schließlich verlässt und die Erkennung kein Ergebnis mehr liefert.
Die KI-Node wertet dies nicht als Fehler. Bleiben vier Auswertungen in Folge
ergebnislos, sendet sie das Kommando `look_down`, woraufhin die Motion-Node die
aufgezeichnete Kopfbewegung abspielt und der Schwamm wieder im Bild erscheint.
Gleichzeitig schaltet die KI-Node auf einen zweiten, auf den Nahbereich
zugeschnittenen Satz von Toleranz- und Dauerwerten um. Die Schritte werden
deutlich kürzer und die Winkeltoleranz größer, sodass der Roboter sich dem
Schwamm in feinen Korrekturen nähert, statt ihn mit großen Schritten zu
überlaufen. Dieser Wechsel erfolgt einmalig und wird nicht zurückgenommen. Die
ursprünglichen Werte gelten erst nach einem Neustart der Node wieder.

Beendet wird die Navigation nicht durch die Bilderkennung, sondern durch den
physischen Kontakt mit dem Schwamm, der die in @motion_node beschriebene
Greifsequenz auslöst. Die KI-Node läuft währenddessen unverändert weiter und
publiziert Kommandos, die jedoch aufgrund ihres Alters verworfen werden.

Mit dem Aufstehen ist der Durchlauf abgeschlossen. Der Roboter steht wieder
aufrecht und hält den Tafelschwamm in der Hand. Das ursprünglich angedachte
Zurücktragen des Schwamms zu einem Zielort wurde nicht mehr umgesetzt.
