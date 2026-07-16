#import "../lib.typ": *

= Einleitung

// Motivation, Problemstellung, Zielsetzung des Projekts, kurze Nennung des
// eigenen Beitrags und Aufbau des Papers.

Autonome mobile Roboter gewinnen zunehmend an Bedeutung in Bereichen, in
denen Maschinen eigenständig mit ihrer Umgebung interagieren müssen. Eine
zentrale Herausforderung besteht dabei in der Verknüpfung von
Umgebungswahrnehmung, Entscheidungsfindung und physischer Bewegung zu einem
funktionierenden Gesamtsystem. Humanoide Roboter wie der Nao stellen hierbei
einen besonders anspruchsvollen Anwendungsfall dar, da sie im Vergleich zu
klassischen Radrobotern über deutlich eingeschränktere Rechenressourcen,
komplexere Kinematik und eine geringere Stabilität beim Laufen verfügen.

Im Rahmen des Moduls Autonome Mobile Roboter wurde ein Projekt durchgeführt, dessen Ziel es war, dem Nao-Roboter eine
möglichst autonome Aufgabe zu ermöglichen. Der Roboter sollte ein definiertes
Objekt erkennen, eigenständig zu diesem hinlaufen, es aufheben und
an die Ausgangsposition zurücktransportieren. Die zentrale Problemstellung lag dabei
weniger in der Entwicklung einzelner Komponenten als in deren Integration zu
einem robusten Gesamtsystem. Wie lässt sich eine moderne, promptbasierte
Bilderkennung mit den stark limitierten Bewegungsfähigkeiten und der
veralteten Softwarearchitektur des Nao so verbinden, dass eine zuverlässige
autonome Objektsuche und -manipulation entsteht?
