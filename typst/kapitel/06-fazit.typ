#import "../lib.typ": *

= Fazit

== Zusammenfassung

Im Rahmen des Projekts wurde ein Prototyp entwickelt, der es dem NAO-Roboter
ermöglicht, einen Tafelschwamm selbstständig zu finden, anzulaufen und
aufzuheben. Als Integrationsplattform diente ROS~2, über das Bilderkennung,
Bewegungssteuerung und die Anbindung an den Roboter als entkoppelte Nodes
realisiert wurden. Die Objekterkennung kombiniert GroundingDINO zur
promptbasierten Lokalisierung mit SAM zur pixelgenauen Segmentierung und
ermöglicht so eine flexible Erkennung ohne objektspezifisches Training.
Eigene Bewegungssequenzen wurden durch Aufzeichnung manuell angeführter
Posen erstellt und über die Gelenkschnittstelle des `naoqi_driver`
abgespielt. Das Gesamtsystem durchläuft die Aufgabe, von der ersten
Bilderkennung bis zum aufgehobenen Schwamm, vollständig autonom und
ohne manuelle Eingriffe während der Ausführung.

Ein zentrales Ergebnis des Projekts ist die praktische Erfahrung mit den
Grenzen der NAO-ROS-Integration. Der `naoqi_driver` deckt nur einen Teil
der NAOqi-API ab, sodass ergänzende Direktaufrufe unumgänglich waren.
Die Inkompatibilität zwischen dem Python-2-basierten NAOqi-SDK und der
Python-3-Umgebung der KI-Node machte eine eigene Konvertierungsschicht
für den Kameradatenstrom notwendig. Diese Einschränkungen sind weniger
als Fehler des gewählten Ansatzes zu verstehen, sondern als
charakteristische Eigenheit der Plattform, die bei jeder ROS-basierten
NAO-Anwendung berücksichtigt werden muss.

== Future Work

// Mögliche Weiterentwicklungen: Objekterkennung, Bewegungssteuerung.

Ausgehend von den in Kapitel 5.2 beschriebenen Einschränkungen ergeben sich
mehrere Ansatzpunkte für zukünftige Arbeiten.

Wie in Kapitel 5.2 beschrieben, stößt der promptbasierte Ansatz zur
Objekterkennung an seine Grenzen. Ein naheliegender Verbesserungsansatz ist
daher der Einsatz eines auf das Zielobjekt trainierten, klassenbasierten
Modells (z. B. durch Finetuning einer YOLO-Variante), allerdings auf Kosten
der Flexibilität und des Aufwands für Datensammlung und Annotation.
Alternativ könnte auf sogenannte Fiducial Marker (z. B. AprilTag oder
ArUco) zurückgegriffen werden, wie sie in der Robotik häufig zur
zuverlässigen Objekt- und Posenerkennung eingesetzt werden. Ein am
Zielobjekt angebrachter Marker würde die Erkennung von einer inhaltlichen
Bildinterpretation auf ein robustes, klassisches Mustererkennungsproblem
reduzieren und wäre weitgehend unabhängig von Lichtverhältnissen,
Hintergrund und den visuellen Merkmalen des Objekts selbst. Dieser Ansatz
wäre allerdings nur in Szenarien praktikabel, in denen das Anbringen eines
Markers am Zielobjekt vorab möglich ist, und weniger geeignet für die
Erkennung beliebiger, unbekannter Objekte.

Auch die aktuell rein reaktive Bewegungssteuerung, bei der aus jedem
einzelnen Bild ein diskretes Korrekturkommando abgeleitet wird, bietet
Verbesserungspotenzial. Anstelle dessen könnte ein planerischer Ansatz
verfolgt werden. Aus einer anfänglichen Objekterkennung wird einmalig eine
geschätzte Zielposition relativ zum Roboter (Distanz und Winkel) berechnet,
etwa anhand der bekannten Objektgröße im Verhältnis zur Bounding-Box-Breite.
Auf dieser Grundlage könnte eine Trajektorie zum Ziel geplant und
ausgeführt werden, wobei nur in größeren Abständen anhand neuer Bilder
nachkorrigiert wird, statt bei jedem Bild vollständig neu zu reagieren.
Dies würde insbesondere der beobachteten Kurvenbildung durch das leichte
Wackeln beim Laufen entgegenwirken, da der Roboter nicht mehr fortlaufend
neu suchen, sondern gezielt auf eine bekannte Koordinate zulaufen könnte.
Da die Distanz- und Winkelschätzung aus einem einzelnen RGB-Bild ohne
Tiefeninformation fehlerbehaftet ist und mit zunehmender Entfernung
ungenauer wird, wäre eine vollständig planbasierte Lösung ohne jede
visuelle Nachkorrektur nicht robust genug. Die Kombination aus grober
Pfadplanung und gelegentlicher Nachkorrektur stellt daher den
praktikableren Mittelweg dar.

// geht das?
Für die in Kapitel 5.2 genannten Probleme bei den selbst programmierten
Bewegungssequenzen böte sich eine inverse-kinematik-basierte Ansteuerung
an, bei der lediglich die gewünschte Endeffektorposition vorgegeben und die
zugehörige, glatt interpolierte Gelenktrajektorie automatisch berechnet
wird, etwa über die kartesische Steuerung von NAOqi oder ein
ROS2-Bewegungsplanungs-Framework wie MoveIt2. Dies würde sowohl das
stockende Bewegungsbild und das damit verbundene Sturzrisiko reduzieren als
auch eine flexiblere, an die tatsächlich erkannte Objektposition angepasste
Greifbewegung ermöglichen.
